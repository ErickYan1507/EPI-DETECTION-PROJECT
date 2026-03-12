"""
Application principale Flask - EPI Detection
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
import os
import base64
from datetime import datetime
from pathlib import Path
from config import config
from app.logger import logger, setup_logging
from app.utils import ensure_directories
from app.database_unified import db

# Initialiser les extensions (socketio uniquement ici)
socketio = SocketIO()

def create_app(config_name='development'):
    """Factory pour créer l'application Flask"""
    global socketio
    
    logger.info(f"=== Création de l'application (mode: {config_name}) ===")
    
    # Déterminer le chemin racine du projet
    project_root = Path(__file__).parent.parent
    template_folder = os.path.join(project_root, 'templates')
    static_folder = os.path.join(project_root, 'static')
    
    # Créer l'app Flask avec chemins explicites
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    
    # Configuration
    app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    
    # Extensions
    db.init_app(app)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode=os.getenv('SOCKETIO_ASYNC_MODE', 'threading'),
        logger=False,
        engineio_logger=False,
    )
    
    # Assurer les dossiers
    ensure_directories()
    
    # Enregistrer les blueprints
    from app.routes_api import api_routes
    from app.dashboard import dashboard_bp
    from app.routes_stats import stats_bp

    app.register_blueprint(api_routes)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(stats_bp)

    # Enregistrer le backend notifications unifié (nouvelle implémentation)
    try:
        from app.routes_notifications_center import notifications_center_api
        app.register_blueprint(notifications_center_api)
        logger.info("Blueprint notifications_center_api enregistré")
    except Exception as e:
        logger.warning(f"notifications_center_api non disponible: {e}")

    # Enregistrer routes Arduino si présentes (après enregistrement des blueprints principaux)
    try:
        from app.dashboard import ArduinoRoutes
        app.register_blueprint(ArduinoRoutes.get_blueprint())
        logger.info("ArduinoRoutes enregistré")
    except Exception as e:
        logger.debug(f"ArduinoRoutes non disponible ou erreur import: {e}")
    
    # Routes statiques
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/notifications')
    def notifications_page():
        return render_template('notifications.html')
    
    @app.route('/upload', methods=['POST'])
    def upload_and_detect():
        """Upload image et lancer détection DIRECTEMENT (pas d'appel HTTP récursif)"""
        try:
            from werkzeug.utils import secure_filename
            import cv2
            import numpy as np
            
            logger.info("📤 Reception upload...")
            
            # Vérifier si fichier présent
            if 'file' not in request.files:
                logger.warning("Pas de fichier dans la requête")
                return jsonify({'success': False, 'error': 'No file provided'}), 400
            
            file = request.files['file']
            if not file or file.filename == '':
                logger.warning("Fichier vide")
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            # Sauvegarder le fichier
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_with_ts = f"{timestamp}_{filename}"
            
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'images')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename_with_ts)
            
            file.save(filepath)
            logger.info(f"✅ Fichier sauvegardé: {filepath}")
            
            # Charger l'image avec OpenCV
            logger.info("🔍 Lancement détection...")
            image = cv2.imread(filepath)
            if image is None:
                return jsonify({'success': False, 'error': 'Impossible de lire l\'image'}), 400
            
            # ===== DÉTECTION DIRECTE (pas d'appel HTTP) =====
            try:
                from app.routes_api import get_multi_detector
                multi_detector = get_multi_detector()
                detections, stats = multi_detector.detect(image, use_ensemble=True)
                logger.info(f"✅ Détection réussie: {len(detections)} détections")
            except Exception as e:
                logger.warning(f"Erreur détecteur: {e}")
                from app.routes_api import get_detector
                detector = get_detector()
                detections, stats = detector.detect(image)
            
            # Sauvegarder en base de données
            from app.database_unified import Detection
            
            detection_record = Detection(
                image_path=filepath,
                total_persons=stats.get('total_persons', 0),
                with_helmet=stats.get('with_helmet', 0),
                with_vest=stats.get('with_vest', 0),
                with_glasses=stats.get('with_glasses', 0),
                with_boots=stats.get('with_boots', 0),
                compliance_rate=stats.get('compliance_rate', 0),
                alert_type=stats.get('alert_type', 'none'),
                source='upload'
            )
            db.session.add(detection_record)
            db.session.commit()
            
            # ===== INTÉGRATION ARDUINO =====
            try:
                if hasattr(app, 'arduino') and app.arduino and app.arduino.connected:
                    # Envoyer les COMPTAGES à Arduino (nouveau format)
                    # Arduino calculera lui-même la conformité
                    total_persons = stats.get('total_persons', 0)
                    with_helmet = stats.get('with_helmet', 0)
                    with_vest = stats.get('with_vest', 0)
                    with_glasses = stats.get('with_glasses', 0)
                    with_boots = stats.get('with_boots', 0)
                    
                    app.arduino.send_detection_data(
                        total_persons=total_persons,
                        with_helmet=with_helmet,
                        with_vest=with_vest,
                        with_glasses=with_glasses,
                        with_boots=with_boots
                    )
                    logger.info(f"✅ Arduino notifié: P={total_persons} H={with_helmet} V={with_vest} G={with_glasses} B={with_boots}")
            except Exception as e:
                logger.error(f"Erreur Arduino: {e}")
            
            # Retourner résultats
            return jsonify({
                'success': True,
                'filename': filename_with_ts,
                'filepath': filepath,
                'statistics': {
                    'total_persons': stats.get('total_persons', 0),
                    'helmet_count': stats.get('with_helmet', 0),
                    'vest_count': stats.get('with_vest', 0),
                    'glasses_count': stats.get('with_glasses', 0),
                    'compliance_rate': stats.get('compliance_rate', 0),
                    'alert_type': stats.get('alert_type', 'none')
                },
                'detections': detections[:100] if detections else []
            }), 200
            
        except Exception as e:
            logger.error(f"❌ Erreur upload/détection: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/info')
    def app_info():
        return jsonify({
            'name': 'EPI Detection System',
            'version': '1.0.0',
            'status': 'running'
        })

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

    @app.route('/arduino')
    def arduino_page():
        """Page de monitoring simple pour l'Arduino"""
        try:
            return render_template('arduino_status.html')
        except Exception as e:
            logger.error(f"Erreur rendu page Arduino: {e}")
            return ("Erreur affichage page Arduino", 500)
    
    # Contexte d'application
    with app.app_context():
        from app.database_unified import Detection, Alert, Worker, SystemLog
        db.create_all()
        logger.info("Tables de base de données vérifiées/créées")

    # Lancer la connexion Arduino en arrière-plan (non bloquant)
    try:
        from app.arduino_integration import ArduinoSessionManager
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

                logger.info(f"🔌 Initialisation Arduino: ARDUINO_PORT={port}, ARDUINO_BAUD={baud}")

                session = ArduinoSessionManager(port=port if port else 'COM3')

                # Assign session early so routes can access it
                app.arduino = session

                # Tentatives immédiates (retry) avant de laisser l'auto-reconnect
                retries = int(os.getenv('ARDUINO_START_RETRIES', '5'))
                delay_s = float(os.getenv('ARDUINO_START_RETRY_DELAY', '1.0'))
                connected = False
                for attempt in range(1, retries + 1):
                    logger.info(f"🔄 Tentative Arduino {attempt}/{retries} sur port {session.controller.port}...")
                    try:
                        if session.connect():
                            connected = True
                            logger.info(f"✅ ArduinoSession connecté avec succès sur {session.controller.port}")
                            break
                    except Exception as e:
                        logger.debug(f"  ❌ Erreur: {type(e).__name__}: {e}")
                    import time
                    time.sleep(delay_s)

                if not connected:
                    logger.warning(f"⚠️ Arduino non connecté sur {session.controller.port} après {retries} tentatives")
                    logger.info("➡️ Activation de l'auto-reconnect (nouvelle tentative toutes les 5 secondes)")
                    session.start_auto_reconnect(scan_interval=5.0)

            except Exception as e:
                logger.error(f"❌ Erreur initialisation Arduino: {e}")
                logger.debug(f"Traceback: {e}", exc_info=True)
                app.arduino = None

        threading.Thread(target=_start_arduino, daemon=True).start()
    except Exception as e:
        logger.debug(f"Module Arduino non chargé: {e}")

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
    
    logger.info("=== Application créée avec succès ===")
    
    return app

# Créer l'app et les extensions globalement
app = create_app()

if __name__ == '__main__':
    logger.info("Démarrage du serveur Flask...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=config.DEBUG)
