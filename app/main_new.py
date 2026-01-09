"""
Application principale Flask - EPI Detection
"""
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
from config import config
from app.logger import logger, setup_logging
from app.utils import ensure_directories

# Initialiser les extensions
db = None
socketio = None

def create_app(config_name='development'):
    """Factory pour créer l'application Flask"""
    global db, socketio
    
    logger.info(f"=== Création de l'application (mode: {config_name}) ===")
    
    # Créer l'app Flask
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    
    # Extensions
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    db.init_app(app)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Assurer les dossiers
    ensure_directories()
    
    # Enregistrer les blueprints
    from app.routes_api import api_routes
    from app.dashboard import dashboard_bp
    
    app.register_blueprint(api_routes)
    app.register_blueprint(dashboard_bp)
    
    # Routes statiques
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/api/info')
    def app_info():
        return jsonify({
            'name': 'EPI Detection System',
            'version': '1.0.0',
            'status': 'running'
        })
    
    # Contexte d'application
    with app.app_context():
        from app.database_unified import Detection, Alert, Worker, SystemLog
        db.create_all()
        logger.info("Tables de base de données vérifiées/créées")
    
    logger.info("=== Application créée avec succès ===")
    
    return app, db, socketio

# Initialisation différée
app = None
db = None
socketio = None

def get_app():
    """Récupérer ou créer l'application"""
    global app, db, socketio
    if app is None:
        app, db, socketio = create_app()
    return app, db, socketio

if __name__ == '__main__':
    app, db, socketio = get_app()
    logger.info("Démarrage du serveur Flask...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=config.DEBUG)
