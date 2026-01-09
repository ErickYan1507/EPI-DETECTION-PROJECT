import os
from urllib.parse import quote_plus

class Config:
    # Chemins
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_PATH = os.path.join(BASE_DIR, 'dataset')
    MODELS_FOLDER = os.path.join(BASE_DIR, 'models')
    MODEL_PATH = os.path.join(BASE_DIR, 'models', 'best.pt')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')
    TRAINING_RESULTS_FOLDER = os.path.join(BASE_DIR, 'runs', 'train')
    
    # Classes EPI
    CLASS_NAMES = ['helmet', 'vest', 'glasses', 'person']
    CLASS_COLORS = {
        'helmet': (0, 255, 0),    # Vert
        'vest': (255, 0, 0),      # Rouge
        'glasses': (0, 0, 255),   # Bleu
        'person': (255, 255, 0)   # Jaune
    }
    
    # Seuils
    CONFIDENCE_THRESHOLD = 0.25
    IOU_THRESHOLD = 0.45
    
    # ========== MULTI-MODÈLES & ENSEMBLE ==========
    # Activer le système multi-modèles (détection avec tous les modèles)
    MULTI_MODEL_ENABLED = os.getenv('MULTI_MODEL_ENABLED', 'True').lower() == 'true'
    
    # Stratégie d'agrégation des résultats multi-modèles
    # Options: 'union_nms', 'weighted_voting', 'average'
    ENSEMBLE_STRATEGY = os.getenv('ENSEMBLE_STRATEGY', 'weighted_voting')
    
    # Poids des modèles pour l'agrégation pondérée
    MODEL_WEIGHTS = {
        'best.pt': 1.0,
        'epi_detection_session_003.pt': 0.8,
        'epi_detection_session_004.pt': 0.9,
        'epi_detection_session_005.pt': 0.85
    }
    
    # Seuil IoU pour NMS dans l'ensemble
    NMS_IOU_THRESHOLD = 0.5
    
    # Nombre minimum de modèles qui doivent être d'accord (pour weighted_voting)
    MIN_ENSEMBLE_VOTES = 2
    
    # Mode ensemble par défaut (peut être overridé par requête)
    DEFAULT_USE_ENSEMBLE = True
    
    # Utiliser ensemble pour caméra (performance impact)
    USE_ENSEMBLE_FOR_CAMERA = False  # False pour performance temps réel
    
    # ========== BASE DE DONNÉES UNIFIÉE ==========
    # Supporte SQLite et MySQL - Choisir avec la variable d'environnement DB_TYPE
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()  # 'sqlite' ou 'mysql'
    
    if DB_TYPE == 'mysql':
        # MySQL
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = int(os.getenv('DB_PORT', 3306))
        DB_USER = os.getenv('DB_USER', 'epi_user')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DB_NAME = os.getenv('DB_NAME', 'epi_detection_db')
        DATABASE_URI = f'mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    else:
        # SQLite par défaut (plus simple pour développement)
        DB_PATH = os.path.join(BASE_DIR, 'database', 'epi_detection.db')
        DATABASE_URI = f'sqlite:///{DB_PATH}'
    
    # Paramètres SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # Pool de connexions
    if DB_TYPE == 'mysql':
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 10,
            'pool_recycle': 3600,
            'pool_pre_ping': True,
            'max_overflow': 20
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {'timeout': 30}
        }
    
    # TinkerCad
    TINKERCAD_API_URL = 'http://localhost:5000/api/tinkercad'
    
    # Notifications
    ENABLE_NOTIFICATIONS = True
    NOTIFICATION_INTERVAL = 30  # secondes
    
    CAMERA_FRAME_WIDTH = 320
    CAMERA_FRAME_HEIGHT = 240
    CAMERA_FPS = 5
    # Gestion de la capture caméra
    CAMERA_RETRY_LIMIT = 5
    CAMERA_RETRY_DELAY = 1  # secondes entre tentatives de réouverture
    YOLO_INPUT_WIDTH = 320
    YOLO_INPUT_HEIGHT = 240
    JPEG_QUALITY = 40
    FRAME_SKIP = 3
    
    ENABLE_HALF_PRECISION = True
    ENABLE_GPU = True
    INFERENCE_DTYPE = 'float16' if ENABLE_HALF_PRECISION else 'float32'
    
    USE_SMALLER_MODEL = True
    ENABLE_MODEL_OPTIMIZATION = True
    MAX_DETECTIONS = 30
    
config = Config()