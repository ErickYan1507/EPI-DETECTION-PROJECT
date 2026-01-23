import random
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
from datetime import datetime, date, timedelta
import json
import sys
from pathlib import Path
import warnings
import threading
import time
from collections import deque
import cv2
import io
try:
    import colorama
    colorama.init()
except Exception:
    pass

warnings.filterwarnings('ignore', category=FutureWarning)

try:
    from config import config
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))
    from config import config

# === Utiliser la BD UNIFIÉE ===
from app.database_unified import db, Detection, Alert, TrainingResult, Worker, IoTSensor, SystemLog
from app.detection import EPIDetector
from app.multi_model_detector import MultiModelDetector
from app.notifications import NotificationManager
from app.tinkercad_sim import TinkerCadSimulator
from app.pdf_export import PDFExporter
from app.routes_api import api_routes
from app.routes_alerts import alert_bp
from app.routes_iot import iot_routes
from app.routes_physical_devices import physical_routes
from app.routes_stats import stats_bp
from app.dashboard import dashboard_bp
from app.routes_notifications import notifications_bp
from app.logger import logger
from app.camera_options import get_camera_manager
from app.audio_manager import get_audio_manager

# --- Camera Manager for background processing ---

class CameraManager:
    def __init__(self, app_context):
        self.app_context = app_context
        self.capture = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.latest_frame = None
        self.last_detection = {
            'detections': [],
            'statistics': {'compliance_rate': 0, 'total_persons': 0, 'with_helmet': 0, 'with_vest': 0, 'with_glasses': 0, 'alert_type': 'safe'}
        }
        self.performance_metrics = {
            'frame_times': deque(maxlen=30), 'inference_times': deque(maxlen=30), 'fps': 0, 'avg_frame_ms': 0, 'avg_inference_ms': 0
        }
        self.consecutive_capture_failures = 0
        self.current_backend = None

    def start(self, camera_index=0):
        if self.running:
            return False, "La caméra est déjà en cours d'exécution."

        # Essayer d'abord avec DirectShow (plus fiable sous Windows), puis fallback
        try_backends = [getattr(cv2, 'CAP_DSHOW', 0), 0]
        opened = False
        for backend in try_backends:
            try:
                cap = cv2.VideoCapture(camera_index, backend)
            except Exception:
                cap = cv2.VideoCapture(camera_index)

            if cap is not None and cap.isOpened():
                self.capture = cap
                self.current_backend = backend
                opened = True
                break

        if not opened:
            return False, f"Impossible d'ouvrir la caméra à l'index {camera_index}."

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_FRAME_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_FRAME_HEIGHT)
        self.capture.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"Thread de caméra démarré pour l'index {camera_index}")
        return True, f"Caméra {camera_index} démarrée"

    def stop(self):
        if not self.running:
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        
        if self.capture:
            self.capture.release()
            self.capture = None
        
        logger.info("Thread de caméra arrêté")
        return True

    def _run(self):
        frame_skip = config.FRAME_SKIP
        frame_idx = 0
        consecutive_failures = 0
        last_warn_time = 0

        while self.running and self.capture:
            frame_start = time.perf_counter()
            ret, frame = self.capture.read()
            if not ret:
                consecutive_failures += 1
                # attenuer les logs pour ne pas spammer
                if time.time() - last_warn_time > 5:
                    logger.warning(f"Échec lecture frame ({consecutive_failures}) - backend={self.current_backend}")
                    last_warn_time = time.time()

                # tenter de réouvrir la caméra après un certain nombre d'échecs
                if consecutive_failures >= getattr(config, 'CAMERA_RETRY_LIMIT', 5):
                    logger.info("Tentative de réouverture de la capture caméra...")
                    try:
                        # release et essayer un backend alternatif
                        try:
                            self.capture.release()
                        except Exception:
                            pass

                        # basculer backend si possible (sur Windows préférer CAP_DSHOW)
                        alt_backends = [getattr(cv2, 'CAP_DSHOW', 0), 0]
                        reopened = False
                        for backend in alt_backends:
                            try:
                                new_cap = cv2.VideoCapture(0, backend)
                            except Exception:
                                new_cap = cv2.VideoCapture(0)

                            if new_cap is not None and new_cap.isOpened():
                                self.capture = new_cap
                                self.current_backend = backend
                                reopened = True
                                break

                        if reopened:
                            logger.info(f"Réouverture caméra réussie (backend={self.current_backend})")
                            consecutive_failures = 0
                        else:
                            logger.error("Impossible de réouvrir la caméra après plusieurs tentatives; nouvelle tentative après délai")
                            time.sleep(getattr(config, 'CAMERA_RETRY_DELAY', 1))
                            consecutive_failures = 0
                    except Exception as e:
                        logger.error(f"Erreur lors de la tentative de réouverture: {e}")
                        time.sleep(getattr(config, 'CAMERA_RETRY_DELAY', 1))

                time.sleep(0.1)
                continue

            frame_idx += 1
            processed_frame = frame
            
            if frame_idx % frame_skip == 0:
                try:
                    # Utiliser multi_detector si disponible, sinon detector simple
                    if multi_detector:
                        # Mode single pour caméra (performance)
                        detections, stats = multi_detector.detect(frame, use_ensemble=config.USE_ENSEMBLE_FOR_CAMERA)
                        processed_frame = multi_detector.draw_detections(frame.copy(), detections)
                    elif detector:
                        detections, stats = detector.detect(frame)
                        processed_frame = detector.draw_detections(frame.copy(), detections)
                    else:
                        logger.warning("Aucun détecteur disponible")
                        continue
                        
                    with self.lock:
                        self.last_detection = {'detections': detections, 'statistics': stats}
                    
                    self.performance_metrics['inference_times'].append(stats.get('inference_ms', 0))
                    self._save_detection_async(stats)
                except Exception as e:
                    logger.error(f"Erreur durant la détection: {e}")

            # Draw stats on the frame
            with self.lock:
                stats = self.last_detection['statistics']
            
            cv2.putText(processed_frame, f"FPS: {self.performance_metrics['fps']:.1f} | {stats.get('total_ms', 0):.0f}ms", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            with self.lock:
                self.latest_frame = processed_frame.copy()

            frame_time = (time.perf_counter() - frame_start) * 1000
            self.performance_metrics['frame_times'].append(frame_time)
            self._update_performance_metrics()

    def _update_performance_metrics(self):
        frame_times = self.performance_metrics['frame_times']
        if not frame_times:
            return
            
        avg_frame_ms = sum(frame_times) / len(frame_times)
        self.performance_metrics['avg_frame_ms'] = avg_frame_ms
        self.performance_metrics['fps'] = 1000 / avg_frame_ms if avg_frame_ms > 0 else 0
        
        inference_times = self.performance_metrics['inference_times']
        if inference_times:
            self.performance_metrics['avg_inference_ms'] = sum(inference_times) / len(inference_times)

    def get_latest_frame_encoded(self):
        with self.lock:
            if self.latest_frame is None:
                return None
            frame = self.latest_frame
        
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, config.JPEG_QUALITY])
        return buffer.tobytes() if ret else None

    def _save_detection_async(self, stats):
        def worker():
            with self.app_context():
                try:
                    from app.database_unified import DailyPresence
                    import json
                    from datetime import date
                    
                    # Extraire les métadonnées multi-modèles
                    model_votes_json = None
                    if 'model_votes' in stats:
                        model_votes_json = json.dumps(stats['model_votes'])
                    
                    detection_record = Detection(
                        image_path='camera_live',
                        source='camera',
                        total_persons=stats['total_persons'],
                        with_helmet=stats['with_helmet'],
                        with_vest=stats['with_vest'],
                        with_glasses=stats['with_glasses'],
                        compliance_rate=stats['compliance_rate'],
                        alert_type=stats.get('alert_type', 'safe'),
                        compliance_level=stats.get('compliance_level', 'safe'),
                        raw_data=json.dumps(stats.get('raw_detections', [])),
                        inference_time_ms=stats.get('inference_ms'),
                        model_used=stats.get('model_used', 'best.pt'),
                        ensemble_mode=stats.get('ensemble_mode', False),
                        model_votes=model_votes_json,
                        aggregation_method=stats.get('aggregation_method')
                    )
                    db.session.add(detection_record)
                    db.session.commit()
                    
                    # Gestion des présences quotidiennes
                    today = date.today()
                    total_persons = stats['total_persons']
                    
                    if total_persons > 0:
                        # Pour chaque personne détectée, vérifier si déjà présente aujourd'hui
                        # Pour simplifier, on utilise un identifiant temporaire basé sur le nombre de détections
                        # Dans un vrai système, cela serait basé sur la reconnaissance faciale ou badge
                        
                        # Récupérer les présences d'aujourd'hui
                        existing_presences = DailyPresence.query.filter_by(date=today).all()
                        existing_count = len(existing_presences)
                        
                        # Si le nombre total de personnes détectées aujourd'hui est inférieur au nombre actuel,
                        # cela signifie qu'il y a de nouvelles personnes
                        new_persons = max(0, total_persons - existing_count)
                        
                        if new_persons > 0:
                            # Ajouter les nouvelles présences
                            equipment_status = {
                                'helmet': stats['with_helmet'] > 0,
                                'vest': stats['with_vest'] > 0,
                                'glasses': stats['with_glasses'] > 0,
                                'boots': stats.get('with_boots', 0) > 0
                            }
                            
                            for i in range(new_persons):
                                presence = DailyPresence(
                                    badge_id=f'temp_{existing_count + i + 1:03d}',  # ID temporaire
                                    date=today,
                                    first_detection=datetime.utcnow(),
                                    last_detection=datetime.utcnow(),
                                    detection_count=1,
                                    compliance_score=stats['compliance_rate'],
                                    equipment_status=json.dumps(equipment_status),
                                    source='camera'
                                )
                                db.session.add(presence)
                            
                            db.session.commit()
                            logger.info(f"Ajouté {new_persons} nouvelles présences pour aujourd'hui")
                        else:
                            # Mettre à jour les dernières détections pour les personnes existantes
                            for presence in existing_presences[:total_persons]:
                                presence.last_detection = datetime.utcnow()
                                presence.detection_count += 1
                                presence.compliance_score = (presence.compliance_score + stats['compliance_rate']) / 2  # Moyenne
                            
                            db.session.commit()
                    
                except Exception as e:
                    logger.error(f"Erreur sauvegarde détection en BDD: {e}")
                    db.session.rollback()
        
        threading.Thread(target=worker, daemon=True).start()

# --- Flask App Initialization ---

app = Flask(__name__, 
            template_folder=os.path.join(config.BASE_DIR, 'templates'),
            static_folder=os.path.join(config.BASE_DIR, 'static'))
app.config.from_object(config)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = getattr(config, 'SQLALCHEMY_ENGINE_OPTIONS', {})
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'epi_detection_secret_key'

CORS(app)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

detector = None
multi_detector = None

try:
    logger.info("Initialisation du MultiModelDetector...")
    multi_detector = MultiModelDetector(use_ensemble=config.DEFAULT_USE_ENSEMBLE)
    logger.info(f"MultiModelDetector initialisé: {len(multi_detector.models)} modèles")
    
    # Garder aussi detector simple pour compatibilité
    detector = multi_detector.models.get('best.pt', {}).get('detector') if multi_detector.models else None
    if detector:
        logger.info("Détecteur simple (best.pt) disponible pour compatibilité")
except Exception as e:
    logger.error(f"Erreur initialisation multi-détecteur: {e}")
    # Fallback sur détecteur simple
    try:
        logger.info("Fallback: Initialisation du détecteur simple EPIDetector...")
        detector = EPIDetector()
        logger.info("Détecteur simple initialisé")
    except Exception as e2:
        logger.error(f"Erreur initialisation détecteur simple: {e2}")

camera_manager = CameraManager(app.app_context)
notifier = NotificationManager()
tinkercad_sim = TinkerCadSimulator()
pdf_exporter = PDFExporter()

app.register_blueprint(api_routes)
app.register_blueprint(iot_routes)
app.register_blueprint(physical_routes)
app.register_blueprint(stats_bp)
app.register_blueprint(alert_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(notifications_bp)

@app.before_request
def init_tinkercad_db():
    if not tinkercad_sim.db_session:
        tinkercad_sim.set_db_session(db.session)

# --- Web Pages ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camera')
def camera_page():
    return render_template('camera.html')

@app.route('/dashboard')
def dashboard():
    # ... (existing dashboard code)
    return render_template('dashboard.html')


@app.route('/tinkercad')
def tinkercad_page():
    return render_template('tinkercad.html')

@app.route('/unified')
def unified_monitoring():
    """Afficher la page de monitoring unifiée (Caméra + Détection + IoT)"""
    return render_template('unified_monitoring.html')

@app.route('/training-results')
def training_results_page():
    """Afficher la page des résultats d'entraînement"""
    return render_template('training_results.html')

@app.route('/test-detection')
def test_detection_page():
    """Afficher la page de test de détection"""
    return render_template('test_detection.html')

# --- Camera API ---

@app.route('/api/camera/list', methods=['GET'])
def list_cameras():
    available_cameras = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append({'index': i, 'name': f'Caméra {i}'})
            cap.release()
    return jsonify(available_cameras)

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    camera_index = request.json.get('camera_index', 0)
    success, message = camera_manager.start(camera_index)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 500

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    camera_manager.stop()
    return jsonify({'success': True, 'message': 'Caméra arrêtée'})

@app.route('/api/camera/stream')
def camera_stream():
    def generate():
        while camera_manager.running:
            frame_bytes = camera_manager.get_latest_frame_encoded()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n' 
                       + frame_bytes + b'\r\n')
            time.sleep(1 / config.CAMERA_FPS) # Stream at target FPS

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/camera/detect')
def camera_detect():
    with camera_manager.lock:
        return jsonify(camera_manager.last_detection)

@app.route('/api/camera/frame')
def camera_frame():
    """Récupérer la dernière image de la caméra en JPEG"""
    frame_bytes = camera_manager.get_latest_frame_encoded()
    if frame_bytes:
        return send_file(
            io.BytesIO(frame_bytes),
            mimetype='image/jpeg'
        )
    return jsonify({'error': 'No frame available'}), 404

# --- Other APIs ---

@app.route('/api/performance')
def get_performance():
    return jsonify({
        'fps': round(camera_manager.performance_metrics['fps'], 2),
        'avg_frame_ms': round(camera_manager.performance_metrics['avg_frame_ms'], 2),
        'avg_inference_ms': round(camera_manager.performance_metrics['avg_inference_ms'], 2),
        'timestamp': datetime.now().isoformat()
    })

# ... (Keep other existing routes like /upload, /api/stats, etc. as they are)
# For brevity, I'm omitting the routes that don't need changes.
# You should ensure they are still in your final file.
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        from app.logger import logger
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Pas de fichier fourni'}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'Nom de fichier vide'}), 400
        
        file_type = request.form.get('type', 'image')
        
        if file:
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            subdir = 'images' if file_type == 'image' else 'videos'
            dest_dir = os.path.join(app.config['UPLOAD_FOLDER'], subdir)
            try:
                os.makedirs(dest_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Erreur création répertoire {dest_dir}: {e}")
                parent = os.path.dirname(dest_dir)
                os.makedirs(parent, exist_ok=True)
                os.makedirs(dest_dir, exist_ok=True)

            filepath = os.path.join(dest_dir, filename)
            logger.info(f"Sauvegarde du fichier: {filepath}")
            
            try:
                file.save(filepath)
                if not os.path.exists(filepath):
                    logger.error(f"Fichier non sauvegardé: {filepath}")
                    return jsonify({'success': False, 'error': f'Impossible de sauvegarder le fichier'}), 500
                
                logger.info(f"Fichier sauvegardé avec succès: {filepath}")
            except Exception as e:
                logger.error(f"Erreur sauvegarde fichier: {e}")
                return jsonify({'success': False, 'error': f'Erreur sauvegarde: {str(e)}'}), 500
            
            if file_type == 'image':
                result = process_image(filepath)
            else:
                result = process_video(filepath)
            
            return jsonify(result)
        
        return jsonify({'success': False, 'error': 'Fichier non valide'}), 400
    
    return render_template('upload.html')
    
# --- Socket.IO handlers pour simulateur / IoT ---------------------------------
@socketio.on('sensor_update')
def handle_sensor_update(data):
    """Reçoit les mises à jour capteurs depuis le simulateur et diffuse aux clients"""
    try:
        logger.info(f"Socket sensor_update received: {data}")
        # Sauvegarde asynchrone optionnelle en base
        def _save():
            try:
                from app.database_unified import IoTDataLog
                ts = data.get('timestamp')
                if ts:
                    try:
                        timestamp = datetime.utcfromtimestamp(float(ts))
                    except Exception:
                        timestamp = datetime.utcnow()
                else:
                    timestamp = datetime.utcnow()

                log = IoTDataLog(
                    sensor_id=None,
                    timestamp=timestamp,
                    motion_detected=bool(data.get('sensors', {}).get('motion')),
                    compliance_level=None,
                    led_green=None,
                    led_red=None,
                    buzzer_active=None,
                    worker_present=None,
                    raw_data=json.dumps(data.get('sensors', {}))
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                logger.error(f"Erreur sauvegarde IoTDataLog: {e}")
                try:
                    db.session.rollback()
                except Exception:
                    pass

        threading.Thread(target=_save, daemon=True).start()

        # Diffuser aux clients (pages web)
        socketio.emit('iot_update', data, broadcast=True)
    except Exception as e:
        logger.error(f"Erreur handle_sensor_update: {e}")


@socketio.on('serial_line')
def handle_serial_line(data):
    """Reçoit une ligne série simulée depuis l'Arduino virtuel et la diffuse / agit"""
    try:
        line = (data.get('line') or '')
        logger.info(f"Socket serial_line: {line}")

        # Si détection de mouvement
        if 'MOTION_DETECTED' in line.upper():
            socketio.emit('motion', {'simulator': data.get('simulator')}, broadcast=True)
            # also forward as an alert-like serial_line
            socketio.emit('serial_line', {'simulator': data.get('simulator'), 'line': 'MOTION_DETECTED'}, broadcast=True)
            return

        # Si ligne capteur type [SENSOR] temp=..,humidity=..
        if line.startswith('[SENSOR]') or 'temp=' in line:
            # essayer parser temp et humidity
            try:
                payload = {'simulator': data.get('simulator'), 'sensors': {}}
                # simple parse
                parts = line.replace('[SENSOR]', '').split(',')
                for p in parts:
                    if '=' in p:
                        k, v = p.split('=', 1)
                        k = k.strip().replace('[SENSOR]', '').replace('temp', 'temp').strip()
                        payload['sensors'][k] = float(v)
                socketio.emit('iot_update', payload, broadcast=True)
                return
            except Exception:
                pass

        # forward other serial lines to clients
        socketio.emit('serial_line', data, broadcast=True)
    except Exception as e:
        logger.error(f"Erreur handle_serial_line: {e}")


@socketio.on('led_control')
def handle_led_control(data):
    """Forward control commands from UI to simulators/clients"""
    try:
        logger.info(f"Forwarding led_control: {data}")
        socketio.emit('led_control', data, broadcast=True)
    except Exception as e:
        logger.error(f"Erreur handle_led_control: {e}")

def process_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Impossible de charger l'image: {image_path}")
        return {
            'success': False,
            'error': f'Impossible de charger l\'image: {image_path}',
            'statistics': {},
            'detections_count': 0
        }
    
    if image.size == 0:
        logger.error(f"Image vide: {image_path}")
        return {
            'success': False,
            'error': f'Image vide: {image_path}',
            'statistics': {},
            'detections_count': 0
        }
    
    # Utiliser multi_detector en priorité avec mode ensemble pour uploads
    if multi_detector is None and detector is None:
        logger.warning("Détecteur non initialisé, création d'une nouvelle instance...")
        try:
            det = EPIDetector()
        except Exception as e:
            logger.error(f"Erreur création détecteur: {e}")
            return {
                'success': False,
                'error': f'Erreur création détecteur: {str(e)}',
                'statistics': {},
                'detections_count': 0
            }
    else:
        det = multi_detector or detector
    
    try:
        # Utiliser ensemble pour uploads (meilleure précision, pas de contrainte temps réel)
        if hasattr(det, 'detect') and hasattr(det, 'use_ensemble'):
            detections, stats = det.detect(image, use_ensemble=True)
        else:
            detections, stats = det.detect(image)
    except Exception as e:
        logger.error(f"Erreur détection: {e}")
        return {
            'success': False,
            'error': f'Erreur détection: {str(e)}',
            'statistics': {},
            'detections_count': 0
        }
    
    try:
        if hasattr(det, 'draw_detections'):
            result_image = det.draw_detections(image, detections)
        else:
            result_image = image
        result_path = image_path.replace('.', '_result.')
        cv2.imwrite(result_path, result_image)
    except Exception as e:
        logger.error(f"Erreur sauvegarde résultat: {e}")
        result_path = image_path
    
    return {
        'success': True,
        'image_path': result_path,
        'statistics': stats,
        'detections_count': len(detections)
    }

def process_video(video_path):
    """Traiter une vidéo pour détecter les EPI"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Impossible d'ouvrir la vidéo: {video_path}")
            return {
                'success': False,
                'error': f'Impossible d\'ouvrir la vidéo: {video_path}',
                'statistics': {},
                'detections_count': 0,
                'frames_processed': 0
            }
        
        # Obtenir l'initialisation du détecteur
        global detector, multi_detector
        det = multi_detector or detector
        
        if det is None:
            logger.warning("Détecteur non initialisé, création d'une nouvelle instance...")
            try:
                det = EPIDetector()
            except Exception as e:
                logger.error(f"Erreur création détecteur: {e}")
                cap.release()
                return {
                    'success': False,
                    'error': f'Erreur création détecteur: {str(e)}',
                    'statistics': {},
                    'detections_count': 0,
                    'frames_processed': 0
                }
        
        # Récupérer les propriétés vidéo
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Définir le codec et créer VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_path = video_path.replace('.', '_result.')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Statistiques globales
        all_stats = {
            'total_persons': 0,
            'with_helmet': 0,
            'with_vest': 0,
            'with_glasses': 0,
            'frames_processed': 0,
            'average_compliance': 0.0
        }
        
        compliance_scores = []
        frame_count = 0
        
        # Traiter chaque frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Sauter des frames pour la performance (traiter 1 frame / 2)
            if frame_count % 2 != 0:
                out.write(frame)
                continue
            
            try:
                # Utiliser single mode pour vidéos (compromis performance/précision)
                if hasattr(det, 'detect') and hasattr(det, 'use_ensemble'):
                    detections, stats = det.detect(frame, use_ensemble=False)
                else:
                    detections, stats = det.detect(frame)
                
                # Accumuler les statistiques
                all_stats['total_persons'] += stats.get('total_persons', 0)
                all_stats['with_helmet'] += stats.get('with_helmet', 0)
                all_stats['with_vest'] += stats.get('with_vest', 0)
                all_stats['with_glasses'] += stats.get('with_glasses', 0)
                compliance_scores.append(stats.get('compliance_rate', 0))
                
                # Dessiner les détections
                if hasattr(det, 'draw_detections'):
                    result_frame = det.draw_detections(frame, detections)
                else:
                    result_frame = frame
                out.write(result_frame)
                
            except Exception as e:
                logger.warning(f"Erreur détection frame {frame_count}: {e}")
                out.write(frame)
            
            # Afficher la progression (tous les 30 frames)
            if frame_count % 30 == 0:
                progress = min(100, int((frame_count / total_frames) * 100)) if total_frames > 0 else 0
                logger.info(f"Traitement vidéo: {progress}% ({frame_count}/{total_frames} frames)")
        
        # Finir
        cap.release()
        out.release()
        
        # Calculer les moyennes
        all_stats['frames_processed'] = frame_count
        if compliance_scores:
            all_stats['average_compliance'] = round(sum(compliance_scores) / len(compliance_scores), 2)
        
        # Sauvegarder en base de données
        try:
            detection_record = Detection(
                video_path=video_path,
                total_persons=all_stats['total_persons'],
                with_helmet=all_stats['with_helmet'],
                with_vest=all_stats['with_vest'],
                with_glasses=all_stats['with_glasses'],
                compliance_rate=all_stats['average_compliance'],
                compliance_level=_get_compliance_level(all_stats['average_compliance']),
                alert_type=_get_alert_type(all_stats['average_compliance']),
                source='video'
            )
            db.session.add(detection_record)
            db.session.commit()
            logger.info(f"Détection vidéo sauvegardée en BD: {detection_record.id}")
        except Exception as e:
            logger.warning(f"Impossible de sauvegarder en BD: {e}")
        
        return {
            'success': True,
            'video_path': output_path,
            'statistics': all_stats,
            'detections_count': len(compliance_scores),
            'frames_processed': frame_count
        }
        
    except Exception as e:
        logger.error(f"Erreur traitement vidéo: {e}")
        return {
            'success': False,
            'error': f'Erreur traitement vidéo: {str(e)}',
            'statistics': {},
            'detections_count': 0,
            'frames_processed': 0
        }

def _get_compliance_level(compliance_rate):
    """Déterminer le niveau de conformité"""
    if compliance_rate >= 95:
        return 'excellent'
    elif compliance_rate >= 80:
        return 'good'
    elif compliance_rate >= 60:
        return 'warning'
    else:
        return 'critical'

def _get_alert_type(compliance_rate):
    """Déterminer le type d'alerte"""
    if compliance_rate >= 80:
        return 'safe'
    elif compliance_rate >= 60:
        return 'warning'
    else:
        return 'danger'

# --- TRAINING RESULTS APIs ---

@app.route('/api/training-results', methods=['GET'])
def get_training_results():
    """Récupérer tous les résultats d'entraînement"""
    try:
        limit = request.args.get('limit', 100, type=int)
        results = TrainingResult.query.order_by(TrainingResult.timestamp.desc()).limit(limit).all()
        
        training_results = []
        for result in results:
            training_results.append({
                'id': result.id,
                'timestamp': result.timestamp.isoformat() if result.timestamp else None,
                'model_name': result.model_name,
                'model_version': result.model_version,
                'model_family': result.model_family,
                'dataset_name': result.dataset_name,
                'dataset_size': result.dataset_size,
                'num_classes': result.num_classes,
                'class_names': json.loads(result.class_names) if result.class_names else [],
                'epochs': result.epochs,
                'batch_size': result.batch_size,
                'image_size': result.image_size,
                'training': {
                    'loss': round(result.train_loss, 4) if result.train_loss else None,
                    'accuracy': round(result.train_accuracy, 4) if result.train_accuracy else None,
                    'precision': round(result.train_precision, 4) if result.train_precision else None,
                    'recall': round(result.train_recall, 4) if result.train_recall else None,
                    'f1_score': round(result.train_f1_score, 4) if result.train_f1_score else None,
                },
                'validation': {
                    'loss': round(result.val_loss, 4) if result.val_loss else None,
                    'accuracy': round(result.val_accuracy, 4) if result.val_accuracy else None,
                    'precision': round(result.val_precision, 4) if result.val_precision else None,
                    'recall': round(result.val_recall, 4) if result.val_recall else None,
                    'f1_score': round(result.val_f1_score, 4) if result.val_f1_score else None,
                },
                'test': {
                    'loss': round(result.test_loss, 4) if result.test_loss else None,
                    'accuracy': round(result.test_accuracy, 4) if result.test_accuracy else None,
                    'precision': round(result.test_precision, 4) if result.test_precision else None,
                    'recall': round(result.test_recall, 4) if result.test_recall else None,
                    'f1_score': round(result.test_f1_score, 4) if result.test_f1_score else None,
                } if result.test_loss else None,
                'training_time_seconds': result.training_time_seconds,
                'inference_time_ms': result.inference_time_ms,
                'fps': result.fps,
                'status': result.status,
                'notes': result.notes,
                'created_at': result.created_at.isoformat() if result.created_at else None,
            })
        
        return jsonify({
            'success': True,
            'training_results': training_results,
            'total': len(training_results)
        })
    except Exception as e:
        logger.error(f"Erreur récupération résultats d'entraînement: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-results/<int:result_id>', methods=['GET'])
def get_training_result_detail(result_id):
    """Récupérer un résultat d'entraînement spécifique"""
    try:
        result = TrainingResult.query.get(result_id)
        if not result:
            return jsonify({'success': False, 'error': 'Résultat non trouvé'}), 404
        
        training_result = {
            'id': result.id,
            'timestamp': result.timestamp.isoformat() if result.timestamp else None,
            'model_name': result.model_name,
            'model_version': result.model_version,
            'model_family': result.model_family,
            'dataset_name': result.dataset_name,
            'dataset_path': result.dataset_path,
            'dataset_size': result.dataset_size,
            'num_classes': result.num_classes,
            'class_names': json.loads(result.class_names) if result.class_names else [],
            'epochs': result.epochs,
            'batch_size': result.batch_size,
            'image_size': result.image_size,
            'learning_rate': result.learning_rate,
            'optimizer': result.optimizer,
            'loss_function': result.loss_function,
            'patience': result.patience,
            'training': {
                'loss': round(result.train_loss, 4) if result.train_loss else None,
                'accuracy': round(result.train_accuracy, 4) if result.train_accuracy else None,
                'precision': round(result.train_precision, 4) if result.train_precision else None,
                'recall': round(result.train_recall, 4) if result.train_recall else None,
                'f1_score': round(result.train_f1_score, 4) if result.train_f1_score else None,
            },
            'validation': {
                'loss': round(result.val_loss, 4) if result.val_loss else None,
                'accuracy': round(result.val_accuracy, 4) if result.val_accuracy else None,
                'precision': round(result.val_precision, 4) if result.val_precision else None,
                'recall': round(result.val_recall, 4) if result.val_recall else None,
                'f1_score': round(result.val_f1_score, 4) if result.val_f1_score else None,
            },
            'test': {
                'loss': round(result.test_loss, 4) if result.test_loss else None,
                'accuracy': round(result.test_accuracy, 4) if result.test_accuracy else None,
                'precision': round(result.test_precision, 4) if result.test_precision else None,
                'recall': round(result.test_recall, 4) if result.test_recall else None,
                'f1_score': round(result.test_f1_score, 4) if result.test_f1_score else None,
            } if result.test_loss else None,
            'class_metrics': json.loads(result.class_metrics) if result.class_metrics else None,
            'confusion_matrix': json.loads(result.confusion_matrix) if result.confusion_matrix else None,
            'epoch_losses': json.loads(result.epoch_losses) if result.epoch_losses else None,
            'training_time_seconds': result.training_time_seconds,
            'inference_time_ms': result.inference_time_ms,
            'fps': result.fps,
            'gpu_memory_mb': result.gpu_memory_mb,
            'model_path': result.model_path,
            'weights_path': result.weights_path,
            'status': result.status,
            'notes': result.notes,
            'created_at': result.created_at.isoformat() if result.created_at else None,
            'updated_at': result.updated_at.isoformat() if result.updated_at else None,
        }
        
        return jsonify({
            'success': True,
            'training_result': training_result
        })
    except Exception as e:
        logger.error(f"Erreur récupération détail résultat: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training-summary', methods=['GET'])
def get_training_summary():
    """Récupérer un résumé des résultats d'entraînement"""
    try:
        # Total d'entraînements
        total_trainings = TrainingResult.query.count()
        
        # Moyennes
        results = TrainingResult.query.all()
        if not results:
            return jsonify({
                'success': True,
                'summary': {
                    'total_trainings': 0,
                    'avg_train_accuracy': 0.0,
                    'avg_val_accuracy': 0.0,
                    'avg_training_time': 0.0,
                    'latest_training': None
                }
            })
        
        avg_train_acc = sum(r.train_accuracy or 0 for r in results) / len(results)
        avg_val_acc = sum(r.val_accuracy or 0 for r in results) / len(results)
        avg_train_time = sum(r.training_time_seconds or 0 for r in results) / len(results)
        
        # Dernier entraînement
        latest = TrainingResult.query.order_by(TrainingResult.timestamp.desc()).first()
        
        return jsonify({
            'success': True,
            'summary': {
                'total_trainings': total_trainings,
                'avg_train_accuracy': round(avg_train_acc, 4),
                'avg_val_accuracy': round(avg_val_acc, 4),
                'avg_training_time': round(avg_train_time, 2),
                'latest_training': {
                    'timestamp': latest.timestamp.isoformat() if latest and latest.timestamp else None,
                    'model_name': latest.model_name if latest else None,
                    'model_version': latest.model_version if latest else None,
                    'val_accuracy': round(latest.val_accuracy, 4) if latest and latest.val_accuracy else None,
                } if latest else None
            }
        })
    except Exception as e:
        logger.error(f"Erreur récupération résumé d'entraînement: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# --- REAL-TIME DETECTION API (YOLOv5 best.pt inference) ---

@app.route('/api/detect', methods=['POST'])
def real_time_detection():
    """Effectuer une détection en temps réel sur une image en base64"""
    import base64
    import numpy as np
    
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'Image base64 requise'
            }), 400
        
        # Décoder l'image base64
        image_data = data['image']
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # Format: data:image/jpeg;base64,/9j/4AAQSkZ...
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({
                'success': False,
                'error': 'Impossible de décoder l\'image'
            }), 400
        
        # Effectuer la détection avec multi-détecteur ou détecteur simple
        det = multi_detector or detector
        if det is None:
            return jsonify({
                'success': False,
                'error': 'Détecteur non initialisé'
            }), 500
        
        # Mode ensemble pour API temps réel (optionnel via paramètre)
        use_ensemble_api = request.json.get('use_ensemble', False) if request.json else False
        
        if hasattr(det, 'detect') and hasattr(det, 'use_ensemble'):
            detections, stats = det.detect(image, use_ensemble=use_ensemble_api)
        else:
            detections, stats = det.detect(image)
        
        # Formater les détections pour le frontend
        detection_results = []
        for det in detections:
            detection_results.append({
                'class_name': det.get('class', 'unknown'),
                'confidence': round(det.get('confidence', 0), 3),
                'x1': int(det.get('x1', 0)),
                'y1': int(det.get('y1', 0)),
                'x2': int(det.get('x2', 0)),
                'y2': int(det.get('y2', 0))
            })
        
        # Préparer la réponse avec vraies statistiques
        response = {
            'success': True,
            'detections': detection_results,
            'statistics': {
                'total_persons': stats.get('total_persons', 0),
                'with_helmet': stats.get('with_helmet', 0),
                'with_vest': stats.get('with_vest', 0),
                'with_glasses': stats.get('with_glasses', 0),
                'with_boots': stats.get('with_boots', 0),
                'compliance_rate': round(stats.get('compliance_rate', 0), 2),
                'compliance_level': stats.get('compliance_level', 'non-conforme'),
                'alert_type': stats.get('alert_type', 'none'),
                'inference_ms': stats.get('inference_ms', 0),
                'total_ms': stats.get('total_ms', 0)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Optionnel: Stocker dans la BD (Detection model)
        try:
            if stats.get('total_persons', 0) > 0:
                detection_record = Detection(
                    timestamp=datetime.now(),
                    person_count=stats.get('total_persons', 0),
                    helmet_count=stats.get('with_helmet', 0),
                    vest_count=stats.get('with_vest', 0),
                    glasses_count=stats.get('with_glasses', 0),
                    boots_count=stats.get('with_boots', 0),
                    compliance_rate=stats.get('compliance_rate', 0),
                    confidence_scores=json.dumps({'avg': 0}),
                    alert_type=stats.get('alert_type', 'none')
                )
                db.session.add(detection_record)
                db.session.commit()
        except Exception as db_error:
            logger.warning(f"Erreur sauvegarde détection en BD: {db_error}")
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Erreur détection temps réel: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# --- ARDUINO/TINKERCAD Integration ---

@app.route('/api/arduino/send-detection', methods=['POST'])
def send_detection_to_arduino():
    """Envoyer les données de détection EPI à l'Arduino TinkerCAD"""
    try:
        data = request.json
        
        helmet = data.get('helmet', False)
        vest = data.get('vest', False)
        glasses = data.get('glasses', False)
        confidence = data.get('confidence', 0)
        
        # Format: "DETECT:helmet=1,vest=0,glasses=1,confidence=92"
        command = f"DETECT:helmet={1 if helmet else 0},vest={1 if vest else 0},glasses={1 if glasses else 0},confidence={confidence}\n"
        
        # Si vous avez une connexion série, envoyer ici
        # Pour la simulation, on retourne juste OK
        
        logger.info(f"[Arduino] Envoi: {command.strip()}")
        
        return jsonify({
            'success': True,
            'message': 'Données envoyées à l\'Arduino',
            'command': command.strip()
        })
    except Exception as e:
        logger.error(f"Erreur envoi Arduino: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/arduino/send-compliance', methods=['POST'])
def send_compliance_to_arduino():
    """Envoyer le niveau de conformité à l'Arduino"""
    try:
        data = request.json
        compliance_level = data.get('level', 50)
        compliance_level = max(0, min(100, compliance_level))  # Clamp 0-100
        
        # Format: "C85"
        command = f"C{compliance_level}\n"
        
        logger.info(f"[Arduino] Compliance Level: {compliance_level}%")
        
        return jsonify({
            'success': True,
            'message': f'Niveau de conformité {compliance_level}% envoyé',
            'compliance': compliance_level
        })
    except Exception as e:
        logger.error(f"Erreur envoi conformité: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# --- Arduino Code Serving ---

@app.route('/arduino_code/<filename>')
def serve_arduino_code(filename):
    """Servir le code Arduino"""
    try:
        arduino_dir = os.path.join(config.BASE_DIR, 'arduino_code')
        return send_file(os.path.join(arduino_dir, filename), mimetype='text/plain')
    except Exception as e:
        logger.error(f"Erreur chargement code Arduino: {e}")
        return jsonify({'error': 'Fichier non trouvé'}), 404

# --- Main Execution ---

if __name__ == '__main__':
    with app.app_context():
        try:
            db_dir = os.path.join(config.BASE_DIR, 'database')
            os.makedirs(db_dir, exist_ok=True)
            upload_folder = app.config.get('UPLOAD_FOLDER', os.path.join(config.BASE_DIR, 'static', 'uploads'))
            os.makedirs(os.path.join(upload_folder, 'images'), exist_ok=True)
            os.makedirs(os.path.join(upload_folder, 'videos'), exist_ok=True)
            db.create_all()
        except Exception as e:
            print(f"Erreur création base de données ou dossiers: {e}")
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)