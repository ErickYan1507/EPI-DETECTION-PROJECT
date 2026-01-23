"""
Configuration pour les tests
"""
import os
import tempfile
from pathlib import Path

class TestConfig:
    """Configuration de test"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Dossiers temporaires
    UPLOAD_FOLDER = tempfile.mkdtemp()
    
    # Modèles
    MODELS_FOLDER = Path(__file__).parent / 'models'
    
    # Configuration détection
    CONFIDENCE_THRESHOLD = 0.5
    IOU_THRESHOLD = 0.45

if __name__ == '__main__':
    print("Test configuration loaded")
