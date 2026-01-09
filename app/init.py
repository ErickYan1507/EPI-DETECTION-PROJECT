"""
Initialisation et setup de l'application Flask
"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import os
from config import config
from app.logger import logger
from app.utils import ensure_directories

# Initialiser les extensions
db = SQLAlchemy()
socketio = SocketIO()

def create_app(config_name='development'):
    """Factory pour créer et configurer l'application Flask"""
    
    logger.info(f"Création de l'application (mode: {config_name})")
    
    # Créer l'app
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['SECRET_KEY'] = config.SECRET_KEY
    
    # Extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Assurer les dossiers
    ensure_directories()
    
    # Contexte d'application
    with app.app_context():
        # Importer les models
        from app.database_unified import Detection, Alert
        
        # Créer les tables
        db.create_all()
        logger.info("Tables de base de données créées/vérifiées")
    
    logger.info("Application créée avec succès")
    
    return app

def init_components():
    """Initialiser les composants de l'application"""
    from app.detection import EPIDetector
    from app.notifications import NotificationManager
    from app.tinkercad_sim import TinkerCadSimulator
    from app.pdf_export import PDFExporter
    
    logger.info("Initialisation des composants...")
    
    detector = EPIDetector()
    notifier = NotificationManager()
    tinkercad = TinkerCadSimulator()
    pdf_exporter = PDFExporter()
    
    logger.info("Composants initialisés")
    
    return {
        'detector': detector,
        'notifier': notifier,
        'tinkercad': tinkercad,
        'pdf_exporter': pdf_exporter
    }
