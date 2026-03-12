import random
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import csv
from datetime import datetime, date, timedelta, timezone
import json
import sys
from pathlib import Path
import warnings
import threading
import time
import base64
import binascii
from collections import deque
from types import SimpleNamespace
import cv2
import numpy as np
import io
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

# === Utiliser la BD UNIFIEE ===
from app.database_unified import (
    db,
    Detection,
    Alert,
    TrainingResult,
    Worker,
    IoTSensor,
    SystemLog,
    NotificationRecipient,
    NotificationHistory,
    NotificationConfig,
    ReportSchedule,
    DailyPresence,
    PersonIdentity,
    AttendanceRecord,
    AttendanceLog,
    AdminUser,
    User,
    TIMEZONE_OFFSET,
    utc_to_local,
)
from app.detection import EPIDetector
from app.constants import calculate_compliance_score, get_alert_type, get_compliance_level
from app.attendance_service import (
    DEFAULT_SIMILARITY_THRESHOLD,
    create_person_with_placeholder_embedding,
    process_face_detection,
)
# === Real-time sync imports ===
from app.realtime_sync import init_realtime_sync, register_sync_for_models, get_sync_manager
from app.multi_model_detector import MultiModelDetector
from app.notifications import NotificationManager
from app.notifications_manager_sqlalchemy import NotificationsManagerSQLAlchemy
from app.tinkercad_sim import TinkerCadSimulator
from app.pdf_export import PDFExporter
from app.routes_api import api_routes
from app.routes_alerts import alert_bp
from app.routes_iot import iot_routes
from app.routes_physical_devices import physical_routes
from app.routes_stats import stats_bp
from app.dashboard import dashboard_bp
from app.routes_notifications_center import notifications_center_api
from app.routes_admin import admin_bp
from app.logger import logger
from app.camera_options import get_camera_manager
from app.audio_manager import get_audio_manager
from sqlalchemy import inspect, text
from app.face_reid import InsightFaceReIdentifier

# === Import optionnel Arduino ===
try:
    from app.arduino_integration import ArduinoSessionManager
    ARDUINO_AVAILABLE = True
except ImportError:
    logger.warning("[WARN] Module Arduino non disponible - Arduino sera desactive")
    ArduinoSessionManager = None
    ARDUINO_AVAILABLE = False

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
        self.embedding_miss_streak = 0
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
        global multi_detector, detector
        
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
                    logger.warning(f"Echec lecture frame ({consecutive_failures}) - backend={self.current_backend}")
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
                        
                    stats = dict(stats or {})
                    if (
                        face_reid_manager
                        and config.FACE_REID_ENABLED
                        and stats.get('total_persons', 0) > 0
                    ):
                        embeddings = face_reid_manager.extract_embeddings(frame)
                        if not embeddings and detections:
                            # Fallback: run face re-id on head-focused person crops to improve hit-rate.
                            person_crops = []
                            for det in detections:
                                try:
                                    if (det or {}).get('class') != 'person':
                                        continue
                                    x1, y1, x2, y2 = (det or {}).get('bbox') or [0, 0, 0, 0]
                                    x1 = max(0, int(x1))
                                    y1 = max(0, int(y1))
                                    x2 = min(frame.shape[1], int(x2))
                                    y2 = min(frame.shape[0], int(y2))
                                    w = x2 - x1
                                    h = y2 - y1
                                    if w < 40 or h < 60:
                                        continue
                                    # Head region heuristic: top ~42% of person bbox + slight horizontal margin.
                                    head_h = max(40, int(h * 0.42))
                                    pad_x = max(0, int(w * 0.08))
                                    hx1 = max(0, x1 - pad_x)
                                    hx2 = min(frame.shape[1], x2 + pad_x)
                                    hy1 = y1
                                    hy2 = min(frame.shape[0], y1 + head_h)
                                    if hx2 - hx1 < 40 or hy2 - hy1 < 40:
                                        continue
                                    person_crops.append(frame[hy1:hy2, hx1:hx2])
                                except Exception:
                                    continue
                            for crop in person_crops:
                                crop_embeddings = face_reid_manager.extract_embeddings(crop)
                                if crop_embeddings:
                                    embeddings.extend(crop_embeddings)
                            if (
                                not embeddings
                                and person_crops
                                and getattr(config, "FACE_REID_ALLOW_PSEUDO_EMBEDDING", True)
                            ):
                                # Deterministic pseudo-embedding fallback (512 dims)
                                # to avoid total pipeline blockage when InsightFace misses.
                                for crop in person_crops:
                                    try:
                                        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                                        vec = cv2.resize(gray, (32, 16), interpolation=cv2.INTER_AREA).astype('float32').flatten()
                                        norm = float((vec ** 2).sum()) ** 0.5
                                        if norm > 1e-8:
                                            vec = vec / norm
                                        embeddings.append(vec.tolist())
                                    except Exception:
                                        continue
                        if embeddings:
                            stats['face_embeddings'] = embeddings
                            stats['face_embeddings_count'] = len(embeddings)
                            self.embedding_miss_streak = 0
                            stats['embedding_miss_streak'] = 0
                            logger.debug(f"Face embeddings extracted: {len(embeddings)}")
                        else:
                            stats['face_embeddings_count'] = 0
                            if stats.get('total_persons', 0) > 0:
                                self.embedding_miss_streak += 1
                            else:
                                self.embedding_miss_streak = 0
                            stats['embedding_miss_streak'] = self.embedding_miss_streak
                            if stats.get('total_persons', 0) > 0:
                                logger.debug("No face embeddings extracted for current frame despite person detections.")

                    with self.lock:
                        self.last_detection = {'detections': detections, 'statistics': stats}
                    
                    self.performance_metrics['inference_times'].append(stats.get('inference_ms', 0))
                    self._save_detection_async(stats)
                    
                    # === INTÉGRATION ARDUINO ===
                    try:
                        # Accéder à l'app global pour obtenir la session Arduino
                        import sys
                        main_module = sys.modules.get('__main__')
                        if hasattr(main_module, 'app') and hasattr(main_module.app, 'arduino'):
                            arduino = main_module.app.arduino
                            if arduino and arduino.connected:
                                # Envoyer les COMPTAGES à Arduino (nouveau format)
                                # Arduino calculera lui-même la conformité
                                total_persons = stats.get('total_persons', 0)
                                with_helmet = stats.get('with_helmet', 0)
                                with_vest = stats.get('with_vest', 0)
                                with_glasses = stats.get('with_glasses', 0)
                                with_boots = stats.get('with_boots', 0)
                                
                                arduino.send_detection_data(
                                    total_persons=total_persons,
                                    with_helmet=with_helmet,
                                    with_vest=with_vest,
                                    with_glasses=with_glasses,
                                    with_boots=with_boots
                                )
                                
                                logger.debug(f"✅ Arduino notifié: P={total_persons} H={with_helmet} V={with_vest} G={with_glasses} B={with_boots}")
                    except Exception as e:
                        logger.debug(f"Erreur Arduino lors détection: {e}")
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
                    import json
                    
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
                    
                    # Gestion des presences quotidiennes
                    total_persons = stats['total_persons']
                    face_embeddings = stats.get('face_embeddings') or []

                    if face_embeddings:
                        processed_count = 0
                        for emb in face_embeddings:
                            try:
                                person, attendance, confidence, created_new_person = process_face_detection(
                                    db_session=db.session,
                                    embedding=emb,
                                    camera_id='camera_live',
                                    source='AUTO',
                                    compliance_rate=stats.get('compliance_rate'),
                                    equipment_flags={
                                        'helmet': stats.get('with_helmet', 0) > 0,
                                        'vest': stats.get('with_vest', 0) > 0,
                                        'glasses': stats.get('with_glasses', 0) > 0,
                                        'boots': stats.get('with_boots', 0) > 0,
                                    },
                                    equipment_status=stats.get('compliance_level'),
                                    similarity_threshold=DEFAULT_SIMILARITY_THRESHOLD,
                                )
                                if person and attendance:
                                    socketio.emit('attendance_detected', {
                                        'person_id': person.id,
                                        'full_name': person.full_name,
                                        'short_id': f"{person.id:06d}" if person.id else None,
                                        'present_today': True,
                                        'is_new_person': bool(created_new_person),
                                        'confidence': confidence,
                                        'attendance_date': attendance.attendance_date.isoformat() if attendance.attendance_date else None,
                                        'equipment_status': attendance.equipment_status,
                                        'compliance_rate': attendance.compliance_rate,
                                    })
                                    processed_count += 1
                            except Exception as emb_err:
                                logger.debug(f"Face re-id ignore pour un embedding: {emb_err}")
                        db.session.commit()
                        logger.info(f"Presence mise a jour via re-identification: {processed_count} visage(s)")
                        if processed_count == 0:
                            logger.warning(
                                "Face embeddings detectes mais aucune presence creee/mise a jour. "
                                f"Vérifier ATTENDANCE_MIN_COMPLIANCE ({getattr(config, 'ATTENDANCE_MIN_COMPLIANCE', 0)}) "
                                "et la qualite des embeddings."
                            )
                    elif total_persons > 0:
                        allow_fallback = bool(getattr(config, "ATTENDANCE_ALLOW_NO_EMBEDDING_FALLBACK", False))
                        force_embedding = bool(getattr(config, "FACE_REID_FORCE_EMBEDDING", True))
                        hybrid_enabled = bool(getattr(config, "FACE_REID_HYBRID_ENABLED", True))
                        fallback_after_frames = max(1, int(getattr(config, "FACE_REID_FALLBACK_AFTER_FRAMES", 8)))
                        miss_streak = int(stats.get('embedding_miss_streak', 0))
                        should_fallback = False
                        if allow_fallback and not force_embedding:
                            should_fallback = True
                        elif allow_fallback and force_embedding and hybrid_enabled and miss_streak >= fallback_after_frames:
                            should_fallback = True

                        if should_fallback:
                            # Fallback pragmatique: garantir qu'une presence du jour est enregistree
                            # meme si l'embedding facial n'a pas pu etre extrait.
                            try:
                                person = PersonIdentity.query.filter_by(full_name="AUTO_UNIDENTIFIED", is_active=True).first()
                                if not person:
                                    person = create_person_with_placeholder_embedding(
                                        db.session,
                                        full_name="AUTO_UNIDENTIFIED",
                                    )
                                now_dt = datetime.utcnow()
                                attendance = AttendanceRecord.query.filter_by(
                                    person_id=person.id,
                                    attendance_date=now_dt.date(),
                                ).first()
                                if attendance:
                                    attendance.last_seen_at = now_dt
                                else:
                                    attendance = AttendanceRecord(
                                        person_id=person.id,
                                        attendance_date=now_dt.date(),
                                        first_seen_at=now_dt,
                                        last_seen_at=now_dt,
                                        source='AUTO',
                                    )
                                    db.session.add(attendance)
                                attendance.compliance_rate = stats.get('compliance_rate')
                                attendance.helmet_detected = stats.get('with_helmet', 0) > 0
                                attendance.vest_detected = stats.get('with_vest', 0) > 0
                                attendance.glasses_detected = stats.get('with_glasses', 0) > 0
                                attendance.boots_detected = stats.get('with_boots', 0) > 0
                                epi_count = (
                                    int(bool(attendance.helmet_detected))
                                    + int(bool(attendance.vest_detected))
                                    + int(bool(attendance.glasses_detected))
                                    + int(bool(attendance.boots_detected))
                                )
                                epi_percent = (epi_count / 4.0) * 100.0
                                level_txt = (stats.get('compliance_level') or '').upper() or 'UNKNOWN'
                                attendance.equipment_status = f"{level_txt} ({epi_percent:.0f}%)"
                                db.session.commit()
                                socketio.emit('attendance_detected', {
                                    'person_id': person.id,
                                    'full_name': person.full_name,
                                    'short_id': f"{person.id:06d}" if person.id else None,
                                    'present_today': True,
                                    'is_new_person': True,
                                    'confidence': None,
                                    'attendance_date': attendance.attendance_date.isoformat() if attendance.attendance_date else None,
                                    'equipment_status': attendance.equipment_status,
                                    'compliance_rate': attendance.compliance_rate,
                                })
                                logger.info(
                                    "Presence fallback creee sans embedding (AUTO_UNIDENTIFIED). "
                                    f"miss_streak={miss_streak}, threshold={fallback_after_frames}"
                                )
                            except Exception as fb_exc:
                                db.session.rollback()
                                logger.warning(f"Fallback no-embedding echoue: {fb_exc}")
                        else:
                            # Strict mode: embedding obligatoire.
                            logger.warning(
                                "Presence AUTO ignoree: embedding obligatoire "
                                "(FACE_REID_FORCE_EMBEDDING=True) et aucun embedding extrait."
                            )
                            socketio.emit('attendance_embedding_missing', {
                                'present_persons': int(total_persons or 0),
                                'message': "Embedding facial non extrait. Presence non enregistree en mode strict.",
                                'miss_streak': miss_streak,
                                'fallback_after_frames': fallback_after_frames,
                            })
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
SOCKETIO_ASYNC_MODE = os.getenv('SOCKETIO_ASYNC_MODE', 'threading')
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode=SOCKETIO_ASYNC_MODE,
    logger=False,
    engineio_logger=False,
)

# ===== Initialize Real-Time Database Synchronization =====
# Simple wrapper to provide .session interface for SQLite engine (for sync manager)
class SqliteSessionWrapper:
    def __init__(self, sqlite_uri):
        self.engine = create_engine(sqlite_uri, future=True)
        self.Session = sessionmaker(bind=self.engine)
    
    @property
    def session(self):
        return self.Session()

try:
    logger.info("Initializing real-time SQLite -> MySQL sync...")
    
    # Create SQLite local cache engine for sync source
    sqlite_uri = f'sqlite:///{config.BASE_DIR}/database/epi_detection.db'
    sqlite_wrapper = SqliteSessionWrapper(sqlite_uri)
    
    # Initialize sync: SQLite -> MySQL
    # sqlite_wrapper = local SQLite cache, db = MySQL/configured DB
    sync_manager = init_realtime_sync(sqlite_wrapper, db, app)
    register_sync_for_models([
        Detection,
        Alert,
        TrainingResult,
        Worker,
        DailyPresence,
        PersonIdentity,
        AttendanceRecord,
        AttendanceLog,
        User,
        AdminUser,
        IoTSensor,
        SystemLog,
        # Notifications models - enable replication to MySQL/phpMyAdmin
        NotificationRecipient,
        NotificationHistory,
        NotificationConfig,
        ReportSchedule
    ])
    logger.info(f"✓ Real-time sync initialized: {sync_manager.sync_direction}")
    logger.info(f"  Source: SQLite ({sqlite_uri})")
    logger.info(f"  Target: {config.DATABASE_URI[:50]}...")
except Exception as e:
    logger.warning(f"Could not initialize sync (MySQL may not be available): {e}")
    logger.info("⊘ App will continue with primary database only")
# ===================================================

detector = None
multi_detector = None
face_reid_manager = None
api_embedding_miss_streak = 0

try:
    logger.info("Initialisation du MultiModelDetector...")
    multi_detector = MultiModelDetector(use_ensemble=config.DEFAULT_USE_ENSEMBLE)
    logger.info(f"✅ MultiModelDetector initialisé: {len(multi_detector.models)} modèles disponibles")
    logger.info(f"   Modèles: {list(multi_detector.models.keys())}")
    
    # Garder aussi detector simple pour compatibilité
    detector = multi_detector.models.get('best.pt', {}).get('detector') if multi_detector.models else None
    if detector:
        logger.info("✅ Détecteur simple (best.pt) disponible pour compatibilité")
except Exception as e:
    logger.error(f"[ERROR] Erreur initialisation multi-detecteur: {e}", exc_info=True)
    logger.info("Tentative de fallback sur détecteur simple...")
    # Fallback sur détecteur simple
    try:
        logger.info("Fallback: Initialisation du détecteur simple EPIDetector...")
        detector = EPIDetector()
        logger.info("✅ Détecteur simple initialisé avec succès")
    except Exception as e2:
        logger.error(f"[ERROR] Erreur initialisation detecteur simple: {e2}", exc_info=True)
        logger.warning("[WARN] Aucun detecteur n'a pu etre charge. La detection ne fonctionnera pas.")

try:
    face_reid_manager = InsightFaceReIdentifier(
        enabled=config.FACE_REID_ENABLED,
        model_name=config.FACE_REID_MODEL,
        det_size=(config.FACE_REID_DET_W, config.FACE_REID_DET_H),
        ctx_id=config.FACE_REID_CTX_ID,
        max_faces=config.FACE_REID_MAX_FACES,
    )
except Exception as reid_exc:
    face_reid_manager = None
    logger.warning(f"Face re-id manager not initialized: {reid_exc}")

camera_manager = CameraManager(app.app_context)
# Utiliser le nouveau système de notifications avec SQLAlchemy
api_notif_manager = NotificationsManagerSQLAlchemy(app)
# Ancien système (conservé pour compatibilité temporaire)
notifier = NotificationManager()
tinkercad_sim = TinkerCadSimulator()
pdf_exporter = PDFExporter()

app.register_blueprint(api_routes)
app.register_blueprint(iot_routes)
app.register_blueprint(physical_routes)
app.register_blueprint(stats_bp)
app.register_blueprint(alert_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(notifications_center_api)
app.register_blueprint(admin_bp)

@app.before_request
def init_tinkercad_db():
    if not tinkercad_sim.db_session:
        tinkercad_sim.set_db_session(db.session)
    if not getattr(app, "_attendance_schema_ready", False):
        try:
            _migrate_attendance_tables_if_needed()
        finally:
            app._attendance_schema_ready = True


def _migrate_attendance_tables_if_needed():
    inspector = inspect(db.engine)

    def ensure_table_columns(table_name, column_specs):
        tables = inspector.get_table_names()
        if table_name not in tables:
            return
        existing_cols = {c["name"] for c in inspector.get_columns(table_name)}
        for col_name, col_def in column_specs.items():
            if col_name in existing_cols:
                continue
            try:
                db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"))
                db.session.commit()
            except Exception:
                db.session.rollback()

    ensure_table_columns(
        "person_identities",
        {
            "job_title": "VARCHAR(120)",
            "address": "VARCHAR(255)",
            "identity_photo_path": "VARCHAR(255)",
            "manual_presence_today": "BOOLEAN NULL",
            "qr_code_data": "VARCHAR(255)",
        },
    )
    ensure_table_columns(
        "attendance_records",
        {
            "compliance_rate": "FLOAT NULL",
            "helmet_detected": "BOOLEAN NULL",
            "vest_detected": "BOOLEAN NULL",
            "glasses_detected": "BOOLEAN NULL",
            "boots_detected": "BOOLEAN NULL",
            "equipment_status": "VARCHAR(30)",
        },
    )


def _save_identity_photo_from_base64(photo_data, person_uuid):
    if not photo_data:
        return None
    raw = str(photo_data).strip()
    if not raw:
        return None
    if "," in raw and raw.lower().startswith("data:image"):
        raw = raw.split(",", 1)[1]
    try:
        image_bytes = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError):
        return None
    if not image_bytes:
        return None

    upload_root = app.config.get('UPLOAD_FOLDER', os.path.join(config.BASE_DIR, 'static', 'uploads'))
    identity_dir = os.path.join(upload_root, 'identity')
    os.makedirs(identity_dir, exist_ok=True)
    filename = f"{person_uuid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    abs_path = os.path.join(identity_dir, filename)
    with open(abs_path, "wb") as fp:
        fp.write(image_bytes)

    rel_path = os.path.relpath(abs_path, config.BASE_DIR).replace("\\", "/")
    return rel_path


def _save_identity_photo_from_crop(image_crop, person_uuid):
    if image_crop is None:
        return None
    try:
        if getattr(image_crop, "size", 0) == 0:
            return None
    except Exception:
        return None

    upload_root = app.config.get('UPLOAD_FOLDER', os.path.join(config.BASE_DIR, 'static', 'uploads'))
    identity_dir = os.path.join(upload_root, 'identity')
    os.makedirs(identity_dir, exist_ok=True)
    filename = f"{person_uuid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    abs_path = os.path.join(identity_dir, filename)
    ok, buffer = cv2.imencode('.jpg', image_crop)
    if not ok:
        return None
    with open(abs_path, "wb") as fp:
        fp.write(buffer.tobytes())
    return os.path.relpath(abs_path, config.BASE_DIR).replace("\\", "/")


def _extract_primary_person_crop(image, detections):
    if image is None or not detections:
        return None
    best = None
    best_area = 0
    h, w = image.shape[:2]
    for det in detections:
        try:
            cls = (det or {}).get('class') or (det or {}).get('class_name')
            if str(cls).lower() != 'person':
                continue
            bbox = (det or {}).get('bbox') or [
                (det or {}).get('x1', 0),
                (det or {}).get('y1', 0),
                (det or {}).get('x2', 0),
                (det or {}).get('y2', 0),
            ]
            x1, y1, x2, y2 = [int(v) for v in bbox[:4]]
            x1 = max(0, min(w, x1))
            x2 = max(0, min(w, x2))
            y1 = max(0, min(h, y1))
            y2 = max(0, min(h, y2))
            if x2 <= x1 or y2 <= y1:
                continue
            area = (x2 - x1) * (y2 - y1)
            if area > best_area:
                best_area = area
                best = (x1, y1, x2, y2)
        except Exception:
            continue
    if not best:
        return None
    x1, y1, x2, y2 = best
    return image[y1:y2, x1:x2].copy()

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

@app.route('/notifications')
def notifications_page():
    """Afficher la page du centre de notifications"""
    return render_template('notifications.html')

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

@app.route('/api/system/socketio-mode', methods=['GET'])
def socketio_mode():
    return jsonify({
        'success': True,
        'async_mode': getattr(socketio, 'async_mode', None),
        'pid': os.getpid(),
    })


def _parse_iso_datetime(value, field_name):
    if not value:
        raise ValueError(f"{field_name} requis")
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        # Naive datetime is treated as local time and converted to UTC for storage.
        return parsed - TIMEZONE_OFFSET
    except Exception as exc:
        raise ValueError(f"{field_name} invalide: {exc}")


def _parse_bool_oui_non(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    txt = str(value).strip().lower()
    if txt in {"1", "true", "vrai", "yes", "oui", "o"}:
        return True
    if txt in {"0", "false", "faux", "no", "non", "n", ""}:
        return False
    return bool(value)


@app.route('/api/attendance/persons', methods=['GET'])
def attendance_persons_list():
    persons = PersonIdentity.query.order_by(PersonIdentity.id.desc()).all()
    today = (datetime.utcnow() + TIMEZONE_OFFSET).date()
    today_present_ids = {
        row.person_id for row in AttendanceRecord.query.filter_by(attendance_date=today).with_entities(AttendanceRecord.person_id).all()
    }
    rows = []
    for person in persons:
        item = person.to_dict()
        if person.manual_presence_today is None:
            item['present_today'] = person.id in today_present_ids
        else:
            item['present_today'] = bool(person.manual_presence_today)
        rows.append(item)
    return jsonify({
        'success': True,
        'rows': rows
    })


@app.route('/api/attendance/persons', methods=['POST'])
def attendance_persons_create():
    payload = request.get_json(silent=True) or {}
    full_name = (payload.get('full_name') or '').strip() or None
    person = create_person_with_placeholder_embedding(
        db.session,
        full_name=full_name,
        job_title=(payload.get('job_title') or '').strip() or None,
        address=(payload.get('address') or '').strip() or None,
        manual_presence_today=payload.get('manual_presence_today'),
    )
    photo_path = _save_identity_photo_from_base64(payload.get('identity_photo_base64'), person.uuid)
    if photo_path:
        person.identity_photo_path = photo_path
    if 'qr_code_data' in payload:
        person.qr_code_data = (payload.get('qr_code_data') or '').strip() or None
    if not person.qr_code_data:
        person.qr_code_data = f"EPI-PER-{person.uuid}"
    db.session.commit()
    return jsonify({'success': True, 'row': person.to_dict()})


@app.route('/api/attendance/persons/<int:person_id>', methods=['PATCH'])
def attendance_persons_update(person_id):
    person = PersonIdentity.query.get(person_id)
    if not person:
        return jsonify({'success': False, 'error': 'Personne introuvable'}), 404

    payload = request.get_json(silent=True) or {}
    if 'full_name' in payload:
        person.full_name = (payload.get('full_name') or '').strip() or None
    if 'job_title' in payload:
        person.job_title = (payload.get('job_title') or '').strip() or None
    if 'address' in payload:
        person.address = (payload.get('address') or '').strip() or None
    if 'manual_presence_today' in payload:
        value = payload.get('manual_presence_today')
        person.manual_presence_today = None if value is None else bool(value)
    photo_path = _save_identity_photo_from_base64(payload.get('identity_photo_base64'), person.uuid)
    if photo_path:
        person.identity_photo_path = photo_path
    if 'is_active' in payload:
        person.is_active = bool(payload.get('is_active'))
    if 'qr_code_data' in payload:
        person.qr_code_data = (payload.get('qr_code_data') or '').strip() or None
    if not person.qr_code_data:
        person.qr_code_data = f"EPI-PER-{person.uuid}"

    db.session.commit()
    return jsonify({'success': True, 'row': person.to_dict()})


@app.route('/api/attendance/identify', methods=['POST'])
def attendance_identify():
    payload = request.get_json(silent=True) or {}
    embedding = payload.get('embedding')
    if embedding is None:
        return jsonify({'success': False, 'error': 'embedding requis'}), 400

    try:
        person, attendance, confidence, created_new_person = process_face_detection(
            db_session=db.session,
            embedding=embedding,
            camera_id=payload.get('camera_id'),
            source='AUTO',
            full_name=(payload.get('full_name') or '').strip() or None,
            identity_photo_path=None,
            compliance_rate=payload.get('compliance_rate'),
            equipment_flags=payload.get('equipment_flags') or {},
            equipment_status=payload.get('equipment_status'),
            similarity_threshold=float(payload.get('similarity_threshold', DEFAULT_SIMILARITY_THRESHOLD)),
        )
        if person is None:
            return jsonify({
                'success': True,
                'ignored': True,
                'reason': 'compliance_below_threshold',
                'min_compliance': 40.0,
            })
        if payload.get('identity_photo_base64') and not person.identity_photo_path:
            person.identity_photo_path = _save_identity_photo_from_base64(payload.get('identity_photo_base64'), person.uuid)
        db.session.commit()
        return jsonify({
            'success': True,
            'person': person.to_dict(),
            'attendance': attendance.to_dict(),
            'confidence': confidence,
            'is_new_person': created_new_person,
            'popup': {
                'show': True,
                'message': f"{person.full_name or 'Personne'} detecte(e) et present(e) aujourd'hui.",
                'present_today': True,
            }
        })
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 400


@app.route('/api/attendance/records', methods=['GET'])
def attendance_records_list():
    query = AttendanceRecord.query
    filter_date = request.args.get('attendance_date')
    person_id = request.args.get('person_id', type=int)
    source = (request.args.get('source') or '').strip().upper()
    if filter_date:
        try:
            parsed = date.fromisoformat(filter_date[:10])
            query = query.filter(AttendanceRecord.attendance_date == parsed)
        except Exception:
            return jsonify({'success': False, 'error': 'attendance_date invalide'}), 400
    if person_id:
        query = query.filter(AttendanceRecord.person_id == person_id)
    if source in {'AUTO', 'MANUAL'}:
        query = query.filter(AttendanceRecord.source == source)

    rows = query.order_by(AttendanceRecord.attendance_date.desc(), AttendanceRecord.last_seen_at.desc()).limit(2000).all()
    return jsonify({'success': True, 'rows': [r.to_dict() for r in rows]})


@app.route('/api/attendance/records', methods=['POST'])
def attendance_records_create():
    payload = request.get_json(silent=True) or {}
    person_id = payload.get('person_id')
    attendance_date = payload.get('attendance_date')
    first_seen_at = payload.get('first_seen_at')
    last_seen_at = payload.get('last_seen_at')

    if not person_id or not attendance_date:
        return jsonify({'success': False, 'error': 'person_id et attendance_date requis'}), 400

    person = PersonIdentity.query.get(int(person_id))
    if not person:
        return jsonify({'success': False, 'error': 'Personne introuvable'}), 404

    try:
        parsed_date = date.fromisoformat(str(attendance_date)[:10])
        first_dt = _parse_iso_datetime(first_seen_at, 'first_seen_at')
        last_dt = _parse_iso_datetime(last_seen_at, 'last_seen_at')
        if last_dt < first_dt:
            return jsonify({'success': False, 'error': 'last_seen_at doit etre >= first_seen_at'}), 400

        record = AttendanceRecord.query.filter_by(
            person_id=person.id,
            attendance_date=parsed_date,
        ).first()

        if record:
            record.first_seen_at = first_dt
            record.last_seen_at = last_dt
            record.source = payload.get('source') or 'MANUAL'
        else:
            record = AttendanceRecord(
                person_id=person.id,
                attendance_date=parsed_date,
                first_seen_at=first_dt,
                last_seen_at=last_dt,
                source=payload.get('source') or 'MANUAL',
            )
            db.session.add(record)
        if 'compliance_rate' in payload:
            record.compliance_rate = payload.get('compliance_rate')
        if 'helmet_detected' in payload:
            record.helmet_detected = _parse_bool_oui_non(payload.get('helmet_detected'))
        if 'vest_detected' in payload:
            record.vest_detected = _parse_bool_oui_non(payload.get('vest_detected'))
        if 'glasses_detected' in payload:
            record.glasses_detected = _parse_bool_oui_non(payload.get('glasses_detected'))
        if 'boots_detected' in payload:
            record.boots_detected = _parse_bool_oui_non(payload.get('boots_detected'))
        if 'equipment_status' in payload:
            record.equipment_status = (payload.get('equipment_status') or '').strip().upper() or None

        db.session.commit()
        return jsonify({'success': True, 'row': record.to_dict()})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 400


@app.route('/api/attendance/records/<int:record_id>', methods=['PUT', 'PATCH'])
def attendance_records_update(record_id):
    record = AttendanceRecord.query.get(record_id)
    if not record:
        return jsonify({'success': False, 'error': 'Presence introuvable'}), 404

    payload = request.get_json(silent=True) or {}
    try:
        if 'first_seen_at' in payload:
            record.first_seen_at = _parse_iso_datetime(payload.get('first_seen_at'), 'first_seen_at')
        if 'last_seen_at' in payload:
            record.last_seen_at = _parse_iso_datetime(payload.get('last_seen_at'), 'last_seen_at')
        if record.last_seen_at < record.first_seen_at:
            return jsonify({'success': False, 'error': 'last_seen_at doit etre >= first_seen_at'}), 400
        if 'source' in payload:
            record.source = payload.get('source') or record.source
        if 'compliance_rate' in payload:
            record.compliance_rate = payload.get('compliance_rate')
        if 'helmet_detected' in payload:
            record.helmet_detected = _parse_bool_oui_non(payload.get('helmet_detected'))
        if 'vest_detected' in payload:
            record.vest_detected = _parse_bool_oui_non(payload.get('vest_detected'))
        if 'glasses_detected' in payload:
            record.glasses_detected = _parse_bool_oui_non(payload.get('glasses_detected'))
        if 'boots_detected' in payload:
            record.boots_detected = _parse_bool_oui_non(payload.get('boots_detected'))
        if 'equipment_status' in payload:
            record.equipment_status = (payload.get('equipment_status') or '').strip().upper() or None
        db.session.commit()
        return jsonify({'success': True, 'row': record.to_dict()})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 400


@app.route('/api/attendance/records/<int:record_id>', methods=['DELETE'])
def attendance_records_delete(record_id):
    record = AttendanceRecord.query.get(record_id)
    if not record:
        return jsonify({'success': False, 'error': 'Presence introuvable'}), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/attendance/records/<int:record_id>/print', methods=['GET'])
def attendance_record_print(record_id):
    record = AttendanceRecord.query.get(record_id)
    if not record:
        return jsonify({'success': False, 'error': 'Presence introuvable'}), 404
    generated_at = datetime.now()
    company_name = os.getenv('COMPANY_NAME', 'TAO_TRANO')
    sheet_no = f"FP-{record_id:06d}"
    return render_template(
        'attendance_print.html',
        record=record,
        records=None,
        generated_at=generated_at,
        utc_to_local_fn=utc_to_local,
        company_name=company_name,
        sheet_no=sheet_no,
        list_sheet_no=None,
    )


@app.route('/api/attendance/records/print', methods=['GET'])
def attendance_records_print():
    query = AttendanceRecord.query
    filter_date = request.args.get('attendance_date')
    person_id = request.args.get('person_id', type=int)
    source = (request.args.get('source') or '').strip().upper()
    parsed_date = None

    if filter_date:
        try:
            parsed_date = date.fromisoformat(filter_date[:10])
            query = query.filter(AttendanceRecord.attendance_date == parsed_date)
        except Exception:
            return jsonify({'success': False, 'error': 'attendance_date invalide'}), 400
    if person_id:
        query = query.filter(AttendanceRecord.person_id == person_id)
    if source in {'AUTO', 'MANUAL'}:
        query = query.filter(AttendanceRecord.source == source)

    rows = query.order_by(AttendanceRecord.attendance_date.desc(), AttendanceRecord.last_seen_at.desc()).limit(2000).all()

    # Pour la fiche du jour: inclure toutes les personnes actives et marquer ABSENT
    # celles qui n'ont aucune detection/presence pour la date demandee.
    if parsed_date and not person_id and source not in {'AUTO', 'MANUAL'}:
        active_people = (
            PersonIdentity.query
            .filter_by(is_active=True)
            .order_by(PersonIdentity.full_name.asc(), PersonIdentity.id.asc())
            .all()
        )
        existing_by_person = {r.person_id: r for r in rows}
        expanded_rows = []
        for person in active_people:
            row = existing_by_person.get(person.id)
            if row:
                setattr(row, 'is_absent_entry', False)
                expanded_rows.append(row)
                continue
            expanded_rows.append(SimpleNamespace(
                id=None,
                person_id=person.id,
                person=person,
                attendance_date=parsed_date,
                first_seen_at=None,
                last_seen_at=None,
                source='ABSENT',
                helmet_detected=False,
                vest_detected=False,
                glasses_detected=False,
                boots_detected=False,
                is_absent_entry=True,
            ))
        rows = expanded_rows

    generated_at = datetime.now()
    company_name = os.getenv('COMPANY_NAME', 'TAO_TRANO')
    list_sheet_no = f"LST-{generated_at.strftime('%Y%m%d%H%M%S')}"
    return render_template(
        'attendance_print.html',
        record=None,
        records=rows,
        generated_at=generated_at,
        utc_to_local_fn=utc_to_local,
        company_name=company_name,
        sheet_no=None,
        list_sheet_no=list_sheet_no,
        filters={
            'attendance_date': filter_date,
            'person_id': person_id,
            'source': source if source in {'AUTO', 'MANUAL'} else None,
        },
    )


@app.route('/api/attendance/records/export/csv', methods=['GET'])
def attendance_records_export_csv():
    query = AttendanceRecord.query
    filter_date = request.args.get('attendance_date')
    person_id = request.args.get('person_id', type=int)
    source = (request.args.get('source') or '').strip().upper()

    if filter_date:
        try:
            parsed = date.fromisoformat(filter_date[:10])
            query = query.filter(AttendanceRecord.attendance_date == parsed)
        except Exception:
            return jsonify({'success': False, 'error': 'attendance_date invalide'}), 400
    if person_id:
        query = query.filter(AttendanceRecord.person_id == person_id)
    if source in {'AUTO', 'MANUAL'}:
        query = query.filter(AttendanceRecord.source == source)

    rows = query.order_by(AttendanceRecord.attendance_date.desc(), AttendanceRecord.last_seen_at.desc()).limit(5000).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['id', 'person_id', 'person_uuid', 'full_name', 'attendance_date', 'first_seen_at', 'last_seen_at', 'source'])
    for record in rows:
        row = record.to_dict()
        writer.writerow([
            row.get('id'),
            row.get('person_id'),
            row.get('person_uuid'),
            row.get('full_name'),
            row.get('attendance_date'),
            row.get('first_seen_at'),
            row.get('last_seen_at'),
            row.get('source'),
        ])

    csv_bytes = io.BytesIO(buffer.getvalue().encode('utf-8-sig'))
    filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(
        csv_bytes,
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv',
    )


@app.route('/api/attendance/summary', methods=['GET'])
def attendance_summary():
    today = (datetime.utcnow() + TIMEZONE_OFFSET).date()
    today_count = AttendanceRecord.query.filter_by(attendance_date=today).count()
    active_people = PersonIdentity.query.filter_by(is_active=True).count()
    return jsonify({
        'success': True,
        'summary': {
            'attendance_date': today.isoformat(),
            'present_today': today_count,
            'active_people': active_people,
        }
    })


@app.route('/api/attendance/functional-needs', methods=['GET'])
def attendance_functional_needs():
    return jsonify({
        'success': True,
        'functional_needs': [
            {
                'category': 'Gestion des personnes',
                'items': [
                    "Enregistrement automatique via re-identification faciale",
                    "Creation manuelle d'une personne par l'administrateur",
                    "Activation / desactivation d'une personne",
                    "Suppression conforme (RGPD) et anonymisation si necessaire",
                ],
            },
            {
                'category': 'Reconnaissance faciale',
                'items': [
                    "Extraction d'embeddings (FaceNet / ArcFace / InsightFace)",
                    "Matching cosine avec seuil configurable",
                    "Re-identification multi-cameras",
                    "Journalisation des detections et niveau de confiance",
                ],
            },
            {
                'category': 'Presence quotidienne',
                'items': [
                    "Une seule presence par personne et par jour (contrainte UNIQUE)",
                    "Mise a jour de last_seen_at lors des detections repetitives",
                    "CRUD manuel (ajout, modification, suppression)",
                    "Historique consultable avec filtres date/personne/source",
                ],
            },
            {
                'category': 'Interface administrateur',
                'items': [
                    "Table DataTables (recherche, tri, pagination)",
                    "Modals pour CRUD presence et creation de personne",
                    "Impression fiche (unitaire et liste filtree)",
                    "Export CSV pour reporting externe",
                ],
            },
            {
                'category': 'Reporting',
                'items': [
                    "Nombre de presents par jour",
                    "Analyse des heures d'entree/sortie",
                    "Export PDF/CSV par periode",
                    "Indicateurs par source AUTO vs MANUAL",
                ],
            },
            {
                'category': 'Securite et conformite',
                'items': [
                    "Consentement utilisateur et base legale",
                    "Stockage securise des embeddings",
                    "Politique de retention et purge",
                    "Journalisation des acces administrateur",
                ],
            },
            {
                'category': 'Technique',
                'items': [
                    "API REST pour operations attendance",
                    "Temps reel optionnel (WebSocket)",
                    "Tolerance aux pics de charge",
                    "Scalabilite multi-cameras",
                ],
            },
        ]
    })

# --- Database Synchronization Status ---
@app.route('/api/sync/status', methods=['GET'])
def sync_status():
    """Get real-time database synchronization status"""
    try:
        sync_mgr = get_sync_manager()
        if sync_mgr:
            return jsonify({
                'success': True,
                'status': sync_mgr.get_stats()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Sync manager not initialized'
            }), 503
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
    
    def _run_detect(detector_obj, img, use_ensemble=True):
        if hasattr(detector_obj, 'detect') and hasattr(detector_obj, 'use_ensemble'):
            return detector_obj.detect(img, use_ensemble=use_ensemble)
        return detector_obj.detect(img)

    def _set_temp_confidence(detector_obj, conf_value):
        """Set temporairement model.conf sur detecteur simple ou multi-detecteur."""
        changed = []
        try:
            if hasattr(detector_obj, 'models') and isinstance(detector_obj.models, dict):
                for model_info in detector_obj.models.values():
                    sub_det = model_info.get('detector')
                    mdl = getattr(sub_det, 'model', None)
                    if mdl is not None and hasattr(mdl, 'conf'):
                        old = mdl.conf
                        mdl.conf = conf_value
                        changed.append((mdl, old))
            else:
                mdl = getattr(detector_obj, 'model', None)
                if mdl is not None and hasattr(mdl, 'conf'):
                    old = mdl.conf
                    mdl.conf = conf_value
                    changed.append((mdl, old))
        except Exception as conf_err:
            logger.debug(f"Impossible de modifier model.conf temporairement: {conf_err}")
        return changed

    def _restore_confidence(changed):
        for mdl, old in changed:
            try:
                mdl.conf = old
            except Exception:
                pass

    def _enhance_low_quality_image(img):
        """Amélioration rapide pour images difficiles."""
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        y = clahe.apply(y)
        merged = cv2.merge((y, cr, cb))
        enhanced = cv2.cvtColor(merged, cv2.COLOR_YCrCb2BGR)
        # Éviter fastNlMeansDenoisingColored (très coûteux CPU).
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        return enhanced

    def _target_score(stat_dict, det_count):
        return (
            int(stat_dict.get('with_glasses', 0)) * 4
            + int(stat_dict.get('with_boots', 0)) * 4
            + int(stat_dict.get('with_helmet', 0))
            + int(stat_dict.get('with_vest', 0))
            + int(det_count > 0)
        )

    def _recompute_stats_from_detections(dets):
        class_counts = {'person': 0, 'helmet': 0, 'vest': 0, 'glasses': 0, 'boots': 0}
        for d in dets:
            name = (d or {}).get('class')
            if name in class_counts:
                class_counts[name] += 1
        total_persons = class_counts['person']
        helmets = class_counts['helmet']
        vests = class_counts['vest']
        glasses = class_counts['glasses']
        boots = class_counts['boots']
        if total_persons == 0:
            compliance_rate = 0.0
        else:
            compliance_rate = calculate_compliance_score(
                total_persons=total_persons,
                with_helmet=helmets,
                with_vest=vests,
                with_glasses=glasses,
                with_boots=boots,
            )
        return {
            'total_persons': int(total_persons),
            'with_helmet': int(helmets),
            'with_vest': int(vests),
            'with_glasses': int(glasses),
            'with_boots': int(boots),
            'compliance_rate': round(compliance_rate, 2),
            'compliance_level': get_compliance_level(compliance_rate).value,
            'alert_type': get_alert_type(compliance_rate).value,
        }

    def _glasses_roi_pass(detector_obj, img, base_dets, max_people=2):
        # Chercher des lunettes dans les zones tête/visage des personnes détectées.
        person_boxes = []
        for d in base_dets:
            if (d or {}).get('class') != 'person':
                continue
            bb = d.get('bbox') or []
            if len(bb) != 4:
                continue
            x1, y1, x2, y2 = bb
            person_boxes.append((x1, y1, x2, y2))

        if not person_boxes:
            return []

        # Limiter pour ne pas exploser le temps d'inférence.
        person_boxes = person_boxes[:max_people]
        glasses_dets = []

        changed = _set_temp_confidence(detector_obj, 0.03)
        try:
            for (x1, y1, x2, y2) in person_boxes:
                x1 = max(0, int(x1))
                y1 = max(0, int(y1))
                x2 = min(img.shape[1], int(x2))
                y2 = min(img.shape[0], int(y2))
                w = x2 - x1
                h = y2 - y1
                if w < 40 or h < 60:
                    continue

                # Zone tête/visage: ~45% du haut + marge horizontale
                head_h = max(40, int(h * 0.45))
                pad_x = max(0, int(w * 0.12))
                hx1 = max(0, x1 - pad_x)
                hx2 = min(img.shape[1], x2 + pad_x)
                hy1 = y1
                hy2 = min(img.shape[0], y1 + head_h)
                if hx2 - hx1 < 40 or hy2 - hy1 < 40:
                    continue

                crop = img[hy1:hy2, hx1:hx2]
                # Upscale small head crops to help tiny glasses detection.
                ch, cw = crop.shape[:2]
                scale = 1.0
                target = 320
                if max(ch, cw) < target:
                    scale = float(target) / float(max(ch, cw))
                    crop = cv2.resize(crop, (int(cw * scale), int(ch * scale)), interpolation=cv2.INTER_LINEAR)
                try:
                    crop_dets, _ = _run_detect(detector_obj, crop, use_ensemble=False)
                except Exception:
                    continue

                for cd in crop_dets:
                    if (cd or {}).get('class') != 'glasses':
                        continue
                    bb2 = cd.get('bbox') or []
                    if len(bb2) != 4:
                        continue
                    gx1, gy1, gx2, gy2 = bb2
                    if scale != 1.0:
                        gx1, gy1, gx2, gy2 = gx1 / scale, gy1 / scale, gx2 / scale, gy2 / scale
                    glasses_dets.append({
                        'class': 'glasses',
                        'confidence': cd.get('confidence', 0),
                        'bbox': [
                            max(0, int(gx1 + hx1)),
                            max(0, int(gy1 + hy1)),
                            min(img.shape[1], int(gx2 + hx1)),
                            min(img.shape[0], int(gy2 + hy1)),
                        ],
                        'color': cd.get('color', (255, 255, 255)),
                    })
        finally:
            _restore_confidence(changed)

        return glasses_dets

    try:
        detections, stats = _run_detect(det, image, use_ensemble=True)
        image_for_drawing = image

        # Fallback: pour images dégradées, refaire une passe optimisée objets difficiles.
        need_retry = (
            int(stats.get('total_persons', 0)) > 0
            and (int(stats.get('with_glasses', 0)) == 0 or int(stats.get('with_boots', 0)) == 0)
        )
        if need_retry:
            # Redimensionner pour accélérer la 2e passe.
            h, w = image.shape[:2]
            max_side = max(h, w)
            scale = 1.0
            if max_side > 960:
                scale = 960.0 / float(max_side)
                retry_input = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
            else:
                retry_input = image

            enhanced_image = _enhance_low_quality_image(retry_input)
            changed = _set_temp_confidence(det, 0.05)
            try:
                # 2e passe rapide: single model (pas ensemble).
                retry_detections, retry_stats = _run_detect(det, enhanced_image, use_ensemble=False)
            finally:
                _restore_confidence(changed)

            # Remapper les bbox au format image originale si redimensionnée.
            if scale != 1.0:
                inv = 1.0 / scale
                for d in retry_detections:
                    bb = d.get('bbox')
                    if isinstance(bb, list) and len(bb) == 4:
                        d['bbox'] = [
                            max(0, int(bb[0] * inv)),
                            max(0, int(bb[1] * inv)),
                            min(w, int(bb[2] * inv)),
                            min(h, int(bb[3] * inv)),
                        ]

            if _target_score(retry_stats, len(retry_detections)) > _target_score(stats, len(detections)):
                logger.info(
                    "Fallback image dégradée activé: lunettes/bottes améliorées "
                    f"({stats.get('with_glasses', 0)}/{stats.get('with_boots', 0)} -> "
                    f"{retry_stats.get('with_glasses', 0)}/{retry_stats.get('with_boots', 0)})."
                )
                detections, stats = retry_detections, retry_stats
                image_for_drawing = image

        # 3e passe ciblée lunettes: ROI sur visage/tête.
        if int(stats.get('total_persons', 0)) > 0 and int(stats.get('with_glasses', 0)) == 0:
            roi_glasses = _glasses_roi_pass(det, image, detections, max_people=2)
            if roi_glasses:
                detections = detections + roi_glasses
                stats = _recompute_stats_from_detections(detections)
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
            result_image = det.draw_detections(image_for_drawing, detections)
        else:
            result_image = image_for_drawing
        base, ext = os.path.splitext(image_path)
        result_path = f"{base}_result{ext}"
        cv2.imwrite(result_path, result_image)
    except Exception as e:
        logger.error(f"Erreur sauvegarde résultat: {e}")
        result_path = image_path
    
    # Construire une URL publique si l'image est sous /static
    image_url = None
    try:
        static_root = os.path.join(config.BASE_DIR, 'static')
        rel = os.path.relpath(result_path, static_root)
        if not rel.startswith('..'):
            image_url = '/static/' + rel.replace('\\', '/')
    except Exception:
        image_url = None

    return {
        'success': True,
        'image_path': result_path,
        'image_url': image_url,
        'detections': [
            {
                'class_name': d.get('class'),
                'confidence': d.get('confidence', 0),
                'bbox': d.get('bbox', []),
            }
            for d in detections
        ],
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
            'with_boots': 0,
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
                all_stats['with_boots'] += stats.get('with_boots', 0)
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
                with_boots=all_stats['with_boots'],
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

@app.route('/api/detect-realtime', methods=['POST'])
def real_time_detection():
    """Effectuer une detection en temps reel sur une image base64."""
    import base64
    import numpy as np
    global api_embedding_miss_streak

    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'Image base64 requise'}), 400

        image_data = data['image']
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            image_data = image_data.split(',', 1)[1]

        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return jsonify({'success': False, 'error': "Impossible de decoder l'image"}), 400

        detector_instance = multi_detector or detector
        if detector_instance is None:
            return jsonify({'success': False, 'error': 'Detecteur non initialise'}), 500

        use_ensemble_api = request.json.get('use_ensemble', False) if request.json else False
        if hasattr(detector_instance, 'detect') and hasattr(detector_instance, 'use_ensemble'):
            detections, stats = detector_instance.detect(image, use_ensemble=use_ensemble_api)
        else:
            detections, stats = detector_instance.detect(image)

        stats = dict(stats or {})

        if face_reid_manager and config.FACE_REID_ENABLED and stats.get('total_persons', 0) > 0:
            embeddings = face_reid_manager.extract_embeddings(image)
            if not embeddings and detections:
                person_crops = []
                for det in detections:
                    try:
                        if (det or {}).get('class') != 'person':
                            continue
                        bbox = (det or {}).get('bbox') or [
                            (det or {}).get('x1', 0),
                            (det or {}).get('y1', 0),
                            (det or {}).get('x2', 0),
                            (det or {}).get('y2', 0),
                        ]
                        x1, y1, x2, y2 = bbox
                        x1 = max(0, int(x1)); y1 = max(0, int(y1))
                        x2 = min(image.shape[1], int(x2)); y2 = min(image.shape[0], int(y2))
                        w = x2 - x1; h = y2 - y1
                        if w < 40 or h < 60:
                            continue
                        head_h = max(40, int(h * 0.42))
                        pad_x = max(0, int(w * 0.08))
                        hx1 = max(0, x1 - pad_x); hx2 = min(image.shape[1], x2 + pad_x)
                        hy1 = y1; hy2 = min(image.shape[0], y1 + head_h)
                        if hx2 - hx1 < 40 or hy2 - hy1 < 40:
                            continue
                        person_crops.append(image[hy1:hy2, hx1:hx2])
                    except Exception:
                        continue

                for crop in person_crops:
                    crop_embeddings = face_reid_manager.extract_embeddings(crop)
                    if crop_embeddings:
                        embeddings.extend(crop_embeddings)

                if (not embeddings and person_crops and getattr(config, 'FACE_REID_ALLOW_PSEUDO_EMBEDDING', True)):
                    for crop in person_crops:
                        try:
                            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                            vec = cv2.resize(gray, (32, 16), interpolation=cv2.INTER_AREA).astype('float32').flatten()
                            norm = float((vec ** 2).sum()) ** 0.5
                            if norm > 1e-8:
                                vec = vec / norm
                            embeddings.append(vec.tolist())
                        except Exception:
                            continue

            if embeddings:
                stats['face_embeddings'] = embeddings
                stats['face_embeddings_count'] = len(embeddings)
                api_embedding_miss_streak = 0
            else:
                stats['face_embeddings_count'] = 0
                if stats.get('total_persons', 0) > 0:
                    api_embedding_miss_streak += 1
                else:
                    api_embedding_miss_streak = 0
            stats['embedding_miss_streak'] = int(api_embedding_miss_streak)

        detection_results = []
        for det in detections:
            bbox = det.get('bbox') or [det.get('x1', 0), det.get('y1', 0), det.get('x2', 0), det.get('y2', 0)]
            detection_results.append({
                'class_name': det.get('class', 'unknown'),
                'confidence': round(det.get('confidence', 0), 3),
                'x1': int(bbox[0] if len(bbox) > 0 else 0),
                'y1': int(bbox[1] if len(bbox) > 1 else 0),
                'x2': int(bbox[2] if len(bbox) > 2 else 0),
                'y2': int(bbox[3] if len(bbox) > 3 else 0),
            })

        debug_payload = {
            'miss_streak': int(stats.get('embedding_miss_streak', 0) or 0),
            'fallback_after_frames': max(1, int(getattr(config, 'FACE_REID_FALLBACK_AFTER_FRAMES', 8))),
            'person_id_created': None,
            'last_person_id': None,
            'attendance_update_ok': None,
            'attendance_error': None,
        }

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
                'total_ms': stats.get('total_ms', 0),
                'face_embeddings_count': stats.get('face_embeddings_count', 0),
                'embedding_miss_streak': stats.get('embedding_miss_streak', 0),
                'fallback_after_frames': debug_payload['fallback_after_frames'],
            },
            'debug': debug_payload,
            'timestamp': datetime.now().isoformat(),
        }

        # 1) Detection logging should not block attendance pipeline.
        try:
            detection_record = Detection(
                image_path='api_realtime',
                source='api',
                total_persons=stats.get('total_persons', 0),
                with_helmet=stats.get('with_helmet', 0),
                with_vest=stats.get('with_vest', 0),
                with_glasses=stats.get('with_glasses', 0),
                compliance_rate=stats.get('compliance_rate', 0),
                alert_type=stats.get('alert_type', 'safe'),
                compliance_level=stats.get('compliance_level', 'safe'),
                raw_data=json.dumps(detection_results),
                inference_time_ms=stats.get('inference_ms'),
                model_used=stats.get('model_used', 'best.pt'),
                ensemble_mode=stats.get('ensemble_mode', False),
                model_votes=json.dumps(stats.get('model_votes')) if stats.get('model_votes') else None,
                aggregation_method=stats.get('aggregation_method'),
            )
            db.session.add(detection_record)
            db.session.commit()
        except Exception as db_error:
            db.session.rollback()
            logger.warning(f'Erreur sauvegarde detection en BD (non bloquant): {db_error}')

        # 2) Attendance pipeline (must continue even if detection logging failed).
        try:
            total_persons = int(stats.get('total_persons', 0) or 0)
            face_embeddings = stats.get('face_embeddings') or []
            primary_person_crop = _extract_primary_person_crop(image, detections)
            miss_streak = int(stats.get('embedding_miss_streak', 0))
            fallback_after_frames = max(1, int(getattr(config, 'FACE_REID_FALLBACK_AFTER_FRAMES', 8)))
            debug_payload['miss_streak'] = miss_streak
            debug_payload['fallback_after_frames'] = fallback_after_frames

            if face_embeddings:
                for emb in face_embeddings:
                    person, attendance, confidence, created_new_person = process_face_detection(
                        db_session=db.session,
                        embedding=emb,
                        camera_id='api_detect',
                        source='AUTO',
                        identity_photo_path=None,
                        compliance_rate=stats.get('compliance_rate'),
                        equipment_flags={
                            'helmet': stats.get('with_helmet', 0) > 0,
                            'vest': stats.get('with_vest', 0) > 0,
                            'glasses': stats.get('with_glasses', 0) > 0,
                            'boots': stats.get('with_boots', 0) > 0,
                        },
                        equipment_status=stats.get('compliance_level'),
                        similarity_threshold=DEFAULT_SIMILARITY_THRESHOLD,
                    )
                    if person and attendance:
                        if not person.identity_photo_path and primary_person_crop is not None:
                            photo_path = _save_identity_photo_from_crop(primary_person_crop, person.uuid)
                            if photo_path:
                                person.identity_photo_path = photo_path
                        if not person.qr_code_data:
                            person.qr_code_data = f"EPI-PER-{person.uuid}"
                        debug_payload['last_person_id'] = person.id
                        if bool(created_new_person):
                            debug_payload['person_id_created'] = person.id
                        socketio.emit('attendance_detected', {
                            'person_id': person.id,
                            'full_name': person.full_name,
                            'short_id': f"{person.id:06d}" if person.id else None,
                            'present_today': True,
                            'is_new_person': bool(created_new_person),
                            'confidence': confidence,
                            'attendance_date': attendance.attendance_date.isoformat() if attendance.attendance_date else None,
                            'equipment_status': attendance.equipment_status,
                            'compliance_rate': attendance.compliance_rate,
                            'miss_streak': miss_streak,
                            'fallback_after_frames': fallback_after_frames,
                            'person_id_created': person.id if bool(created_new_person) else None,
                        })
            elif total_persons > 0:
                allow_fallback = bool(getattr(config, 'ATTENDANCE_ALLOW_NO_EMBEDDING_FALLBACK', False))
                force_embedding = bool(getattr(config, 'FACE_REID_FORCE_EMBEDDING', True))
                hybrid_enabled = bool(getattr(config, 'FACE_REID_HYBRID_ENABLED', True))
                should_fallback = False
                if allow_fallback and not force_embedding:
                    should_fallback = True
                elif allow_fallback and force_embedding and hybrid_enabled and miss_streak >= fallback_after_frames:
                    should_fallback = True

                if should_fallback:
                    person = PersonIdentity.query.filter_by(full_name='AUTO_UNIDENTIFIED', is_active=True).first()
                    created_placeholder_person = False
                    if not person:
                        person = create_person_with_placeholder_embedding(db.session, full_name='AUTO_UNIDENTIFIED')
                        created_placeholder_person = True
                    now_dt = datetime.utcnow()
                    local_today = (now_dt + TIMEZONE_OFFSET).date()
                    attendance = AttendanceRecord.query.filter_by(person_id=person.id, attendance_date=local_today).first()
                    if attendance:
                        attendance.last_seen_at = now_dt
                    else:
                        attendance = AttendanceRecord(
                            person_id=person.id,
                            attendance_date=local_today,
                            first_seen_at=now_dt,
                            last_seen_at=now_dt,
                            source='AUTO',
                        )
                        db.session.add(attendance)
                    attendance.compliance_rate = stats.get('compliance_rate')
                    attendance.helmet_detected = stats.get('with_helmet', 0) > 0
                    attendance.vest_detected = stats.get('with_vest', 0) > 0
                    attendance.glasses_detected = stats.get('with_glasses', 0) > 0
                    attendance.boots_detected = stats.get('with_boots', 0) > 0
                    epi_count = (
                        int(bool(attendance.helmet_detected))
                        + int(bool(attendance.vest_detected))
                        + int(bool(attendance.glasses_detected))
                        + int(bool(attendance.boots_detected))
                    )
                    epi_percent = (epi_count / 4.0) * 100.0
                    level_txt = (stats.get('compliance_level') or '').upper() or 'UNKNOWN'
                    attendance.equipment_status = f"{level_txt} ({epi_percent:.0f}%)"
                    if not person.identity_photo_path and primary_person_crop is not None:
                        photo_path = _save_identity_photo_from_crop(primary_person_crop, person.uuid)
                        if photo_path:
                            person.identity_photo_path = photo_path
                    if not person.qr_code_data:
                        person.qr_code_data = f"EPI-PER-{person.uuid}"
                    debug_payload['last_person_id'] = person.id
                    if created_placeholder_person:
                        debug_payload['person_id_created'] = person.id
                    socketio.emit('attendance_detected', {
                        'person_id': person.id,
                        'full_name': person.full_name,
                        'short_id': f"{person.id:06d}" if person.id else None,
                        'present_today': True,
                        'is_new_person': False,
                        'confidence': None,
                        'attendance_date': attendance.attendance_date.isoformat() if attendance.attendance_date else None,
                        'equipment_status': attendance.equipment_status,
                        'compliance_rate': attendance.compliance_rate,
                        'miss_streak': miss_streak,
                        'fallback_after_frames': fallback_after_frames,
                        'person_id_created': person.id if created_placeholder_person else None,
                    })
                else:
                    socketio.emit('attendance_embedding_missing', {
                        'present_persons': int(total_persons or 0),
                        'message': 'Embedding facial non extrait. Presence non enregistree en mode strict.',
                        'miss_streak': miss_streak,
                        'fallback_after_frames': fallback_after_frames,
                    })

            db.session.commit()
            debug_payload['attendance_update_ok'] = True
            debug_payload['attendance_error'] = None
        except Exception as db_error:
            db.session.rollback()
            debug_payload['attendance_update_ok'] = False
            debug_payload['attendance_error'] = str(db_error)
            logger.warning(f'Erreur pipeline attendance /api/detect: {db_error}')

        return jsonify(response)

    except Exception as e:
        logger.error(f'Erreur detection temps reel: {e}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# --- ARDUINO/TINKERCAD Integration ---

@app.route('/api/arduino/status')
def arduino_status():
    """Retourne l'état courant de la connexion Arduino et dernières métriques"""
    try:
        ar = getattr(app, 'arduino', None)
        if not ar:
            return jsonify({'connected': False, 'port': None, 'baud': None, 'metrics': None, 'history': []}), 200

        connected = bool(getattr(ar, 'connected', False))
        port = None
        baud = None
        metrics = None
        history = []
        try:
            port = getattr(getattr(ar, 'controller', None), 'port', None)
            baud = getattr(getattr(ar, 'controller', None), 'baudrate', None)
            if hasattr(ar, 'get_current_metrics'):
                metrics = ar.get_current_metrics()
            if hasattr(ar, 'get_history'):
                history = ar.get_history(20)
        except Exception:
            pass

        return jsonify({
            'connected': connected,
            'port': port,
            'baud': baud,
            'metrics': metrics,
            'history': history
        }), 200
    except Exception as e:
        logger.error(f"Erreur endpoint /api/arduino/status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/arduino/connect', methods=['POST'])
def arduino_connect():
    """Forcer une tentative de connexion manuelle à l'Arduino"""
    try:
        ar = getattr(app, 'arduino', None)
        if not ar:
            return jsonify({'success': False, 'error': 'Arduino session not initialized'}), 400

        if ar.connected:
            return jsonify({'success': True, 'connected': True, 'message': 'Already connected'}), 200

        # Try connect and capture low-level error if possible
        try:
            ok = ar.connect()
        except Exception as e:
            # Return exception message for diagnosis
            return jsonify({'success': False, 'connected': False, 'message': 'Connect failed', 'error': str(e)}), 500

        if ok:
            return jsonify({'success': True, 'connected': True, 'message': 'Connected'}), 200
        else:
            # Try a direct low-level open using pyserial to get the exception message
            try:
                import serial
                port = getattr(getattr(ar, 'controller', None), 'port', None)
                baud = getattr(getattr(ar, 'controller', None), 'baudrate', None) or 9600
                ser = None
                try:
                    ser = serial.Serial(port=port, baudrate=baud, timeout=1)
                    ser.close()
                    extra = 'Opened and closed low-level serial port successfully (unexpected)'
                except Exception as e2:
                    extra = str(e2)
            except Exception as e3:
                extra = f'pyserial not available or error: {e3}'

            return jsonify({'success': False, 'connected': False, 'message': 'Connect failed', 'error': extra}), 500
    except Exception as e:
        logger.error(f"Erreur /api/arduino/connect: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/arduino/scan')
def arduino_scan():
    """Lister les ports série disponibles et leurs descriptions (diagnostic)"""
    try:
        ports_info = []
        try:
            from serial.tools import list_ports
            for p in list_ports.comports():
                ports_info.append({'device': p.device, 'description': p.description, 'hwid': p.hwid})
        except Exception as e:
            return jsonify({'success': False, 'error': f'list_ports not available: {e}'}), 500

        return jsonify({'success': True, 'ports': ports_info}), 200
    except Exception as e:
        logger.error(f"Erreur /api/arduino/scan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/arduino/send-detection', methods=['POST'])
def send_detection_to_arduino():
    """Envoyer les données de détection EPI à l'Arduino
    
    Format JSON attendu:
    {
        "total_persons": 5,
        "with_helmet": 3,
        "with_vest": 4,
        "with_glasses": 2,
        "with_boots": 1
    }
    """
    try:
        data = request.json
        
        # Get counts (new format)
        total_persons = data.get('total_persons', 0)
        with_helmet = data.get('with_helmet', 0)
        with_vest = data.get('with_vest', 0)
        with_glasses = data.get('with_glasses', 0)
        with_boots = data.get('with_boots', 0)
        
        # Utiliser la session Arduino si disponible
        ar = getattr(app, 'arduino', None)
        if ar and ar.connected:
            ar.send_detection_data(
                total_persons=total_persons,
                with_helmet=with_helmet,
                with_vest=with_vest,
                with_glasses=with_glasses,
                with_boots=with_boots
            )
            logger.info(f"✅ Arduino notifié: P={total_persons} H={with_helmet} V={with_vest} G={with_glasses} B={with_boots}")
            return jsonify({
                'success': True,
                'message': 'Données envoyées à l\'Arduino',
                'connected': True
            })
        else:
            # Format attendu Arduino v2: "DETECT:person=5,helmet=3,vest=4,glasses=2,boots=1"
            command = (
                f"DETECT:person={int(total_persons)},helmet={int(with_helmet)},"
                f"vest={int(with_vest)},glasses={int(with_glasses)},boots={int(with_boots)}\n"
            )
            logger.info(f"[Arduino] Envoi (pas connecté): {command.strip()}")
            return jsonify({
                'success': True,
                'message': 'Données formatées (Arduino non connecté)',
                'command': command.strip(),
                'connected': False
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
        
        # Convertir en int et vérifier la plage
        try:
            compliance_level = int(compliance_level)
        except (ValueError, TypeError):
            logger.error(f"Conformité invalide: {compliance_level} - utilisation de 50 par défaut")
            compliance_level = 50
        
        compliance_level = max(0, min(100, compliance_level))  # Clamp 0-100
        
        # Utiliser la session Arduino si disponible
        ar = getattr(app, 'arduino', None)
        if ar and ar.connected:
            ar.send_compliance_level(compliance_level)
            logger.info(f"[OK] Niveau de conformite envoye: {compliance_level}%")
            return jsonify({
                'success': True,
                'message': f'Niveau de conformité {compliance_level}% envoyé',
                'compliance': compliance_level,
                'connected': True
            })
        else:
            # Format: "C85"
            command = f"C{compliance_level}\n"
            logger.info(f"[Arduino] Compliance Level (pas connecté): {compliance_level}%")
            return jsonify({
                'success': True,
                'message': f'Niveau de conformité {compliance_level}% formaté (Arduino non connecté)',
                'compliance': compliance_level,
                'connected': False
            })
    except Exception as e:
        logger.error(f"Erreur envoi conformité: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/arduino')
def arduino_page():
    """Page de monitoring simple pour l'Arduino"""
    try:
        return render_template('arduino_status.html')
    except Exception as e:
        logger.error(f"Erreur rendu page Arduino: {e}")
        return ("Erreur affichage page Arduino", 500)

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

# --- Initialisation Arduino ---

def init_arduino():
    """Initialiser la connexion Arduino en arrière-plan (non bloquant)"""
    # Vérifier si Arduino est activé via variable d'environnement
    arduino_enabled = os.getenv('ARDUINO_ENABLED', 'true').lower() in ('true', '1', 'yes')
    
    if not arduino_enabled:
        logger.info("[INFO] Arduino desactive via ARDUINO_ENABLED=false")
        app.arduino = None
        return
    
    if not ARDUINO_AVAILABLE:
        logger.warning("[WARN] Arduino non disponible - module ArduinoSessionManager indisponible")
        app.arduino = None
        return
    
    try:
        import threading

        def _start_arduino():
            try:
                # Configuration du port Arduino (env var en priorité)
                port = os.getenv('ARDUINO_PORT', None)
                baud = int(os.getenv('ARDUINO_BAUD', '9600'))

                # Ignore legacy 'SIMULATION' value - simulation mode removed
                if isinstance(port, str) and port.upper() == 'SIMULATION':
                    logger.warning("ARDUINO_PORT set to 'SIMULATION' is deprecated and ignored (simulation mode removed)")
                    port = None

                logger.info(f"DEBUG: ARDUINO_PORT env var = {port}")
                logger.info(f"DEBUG: ARDUINO_BAUD env var = {baud}")

                session = ArduinoSessionManager(port=port if port else 'COM3')

                # Assign session early so routes can access it
                app.arduino = session

                # Tentatives immédiates (retry) avant de laisser l'auto-reconnect
                retries = int(os.getenv('ARDUINO_START_RETRIES', '5'))
                delay_s = float(os.getenv('ARDUINO_START_RETRY_DELAY', '1.0'))
                connected = False
                for attempt in range(1, retries + 1):
                    logger.info(f"Tentative connexion Arduino (attempt {attempt}/{retries}) -> port={session.controller.port}")
                    try:
                        if session.connect():
                            connected = True
                            logger.info(f"✅ ArduinoSession initialisé et connecté (port={session.controller.port})")
                            # Display navigation links
                            logger.info("\n" + "="*60)
                            logger.info("[INFO] Accedez a l'application via le navigateur:")
                            logger.info("   → http://127.0.0.1:5000")
                            logger.info("   → http://localhost:5000")
                            logger.info("   → Dashboard: http://127.0.0.1:5000/dashboard")
                            logger.info("   → Détections: http://127.0.0.1:5000/detections")
                            logger.info("   → Alertes: http://127.0.0.1:5000/alerts")
                            logger.info("="*60 + "\n")
                            break
                    except Exception as e:
                        logger.debug(f"Erreur tentative connexion Arduino: {e}")
                    import time
                    time.sleep(delay_s)

                if not connected:
                    logger.info("[INFO] Arduino non connecte immediatement - activation de l'auto-reconnect")
                    session.start_auto_reconnect(scan_interval=5.0)

            except Exception as e:
                logger.error(f"[ERROR] Erreur initialisation Arduino: {e}")
                logger.debug(f"Traceback: {e}", exc_info=True)
                app.arduino = None

        threading.Thread(target=_start_arduino, daemon=True).start()
    except Exception as e:
        logger.debug(f"Module Arduino non chargé: {e}")

def log_project_links(host=None, port=None):
    """Log useful project links for users (printed at startup)."""
    try:
        # Determine printable host/port defaults
        try:
            port = int(port) if port is not None else int(os.getenv('PORT', '5000'))
        except Exception:
            port = 5000

        if not host:
            env_host = os.getenv('APP_HOST') or os.getenv('FLASK_HOST') or os.getenv('HOST')
            host = env_host if env_host else '127.0.0.1'

        # If host is 0.0.0.0, use localhost for printed links
        printable_host = 'localhost' if str(host) in ('0.0.0.0', '') else host
        base = f"http://{printable_host}:{port}"

        logger.info("\n" + "="*60)
        logger.info("Acc\u00e9dez \u00e0 l'application via le navigateur:")
        logger.info(f"   \u2192 {base}")
        logger.info(f"   \u2192 http://127.0.0.1:{port}")
        logger.info(f"   \u2192 Dashboard: {base}/dashboard")
        logger.info(f"   \u2192 D\u00e9tections: {base}/detections")
        logger.info(f"   \u2192 Alertes: {base}/alerts")
        logger.info(f"   \u2192 Upload: {base}/upload")
        logger.info(f"   \u2192 R\u00e9sultats entrainement: {base}/training-results")
        logger.info("="*60 + "\n")
    except Exception as e:
        logger.debug(f"Erreur affichage liens projet: {e}")

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
    
    # Initialiser Arduino
    # Afficher les liens utiles de l'application au démarrage
    try:
        log_project_links()
    except Exception:
        pass

    # Initialiser Arduino
    init_arduino()
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
