import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env.email
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.email'))

class Config:
    # Chemins
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_PATH = os.path.join(BASE_DIR, 'dataset')
    MODELS_FOLDER = os.path.join(BASE_DIR, 'models')
    MODEL_PATH = os.path.join(BASE_DIR, 'models', 'best.pt')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')
    TRAINING_RESULTS_FOLDER = os.path.join(BASE_DIR, 'runs', 'train')
    
    # Classes EPI (5 classes obligatoires: HELMET, GLASSES, PERSON, VEST, BOOTS)
    CLASS_NAMES = ['helmet', 'glasses', 'person', 'vest', 'boots']
    CLASS_COLORS = {
        'helmet': (0, 255, 0),     # Vert
        'glasses': (0, 0, 255),    # Bleu
        'person': (255, 255, 0),   # Jaune
        'vest': (255, 0, 0),       # Rouge
        'boots': (255, 165, 0)     # Orange
    }
    
    # Seuils - OPTIMISÉS POUR RÉDUIRE NMS TIME LIMIT
    CONFIDENCE_THRESHOLD = 0.2  # Seuil de confiance pour les détections (réduit à 0.2 pour détecter helmet, vest)
    IOU_THRESHOLD = 0.65  # Augmenté de 0.45 pour moins de fusions
    
    # ========== MULTI-MODÈLES & ENSEMBLE ==========
    # Activer le système multi-modèles (détection avec tous les modèles)
    MULTI_MODEL_ENABLED = True  # UTILISER TOUS LES MODÈLES DISPONIBLES
    
    # Stratégie d'agrégation des résultats multi-modèles
    # Options: 'union_nms' (combine toutes les détections), 'weighted_voting' (nécessite MIN_ENSEMBLE_VOTES), 'average'
    # BUG FIX: Utiliser 'union_nms' car 'weighted_voting' avec MIN_ENSEMBLE_VOTES=2 rejette les détections d'un seul modèle
    ENSEMBLE_STRATEGY = os.getenv('ENSEMBLE_STRATEGY', 'union_nms')
    
    # Poids des modèles pour l'agrégation pondérée
    MODEL_WEIGHTS = {
        'best.pt': 1.0,  # Modèle principal avec poids maximal
        'epi_detection_session_003.pt': 0.8,
        'epi_detection_session_004.pt': 0.9,
        'epi_detection_session_005.pt': 0.85
    }
    
    # Seuil IoU pour NMS dans l'ensemble - OPTIMISÉ
    NMS_IOU_THRESHOLD = 0.65  # Augmenté de 0.5 pour NMS plus efficace
    
    # Nombre minimum de modèles qui doivent être d'accord (pour weighted_voting)
    # BUG: Avec MIN_ENSEMBLE_VOTES=2, un seul modèle n'est pas suffisant, donc toutes les détections sont rejetées
    # SOLUTION: Utiliser 'union_nms' au lieu de 'weighted_voting'
    MIN_ENSEMBLE_VOTES = 1  # Réduit de 2 à 1 au cas où weighted_voting serait réactivé
    
    # Mode ensemble par défaut (peut être overridé par requête)
    # Pour uploads: True (meilleure précision)
    # Pour caméra: False (performance)
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
    
    # ========== ACCÉLÉRATION MATÉRIELLE ==========
    # Backend d'inférence préféré: 'openvino', 'onnx', 'pytorch', 'auto'
    PREFERRED_BACKEND = os.getenv('PREFERRED_BACKEND', 'auto')
    
    # Activer l'accélération matérielle Intel OpenVINO
    USE_OPENVINO = os.getenv('USE_OPENVINO', 'True').lower() == 'true'
    
    # Device OpenVINO: 'AUTO', 'GPU', 'CPU'
    OPENVINO_DEVICE = os.getenv('OPENVINO_DEVICE', 'AUTO')
    
    # Activer ONNX Runtime comme fallback
    USE_ONNX_RUNTIME = os.getenv('USE_ONNX_RUNTIME', 'True').lower() == 'true'
    
    # Providers ONNX Runtime (par ordre de priorité)
    ONNX_PROVIDERS = [
        'DmlExecutionProvider',  # DirectML (GPU Intel/AMD)
        'CPUExecutionProvider'    # CPU fallback
    ]
    
    # Optimisations CPU multi-threading
    CPU_NUM_THREADS = os.getenv('CPU_NUM_THREADS', '0')  # 0 = auto-detect
    OMP_NUM_THREADS = os.getenv('OMP_NUM_THREADS', '0')  # OpenMP threads
    
    # ========== NOTIFICATIONS EMAIL ==========
    # Configuration SMTP pour les notifications
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
    
    # Adresse email par défaut pour les notifications
    DEFAULT_NOTIFICATION_EMAIL = os.getenv('DEFAULT_NOTIFICATION_EMAIL', 'admin@epidetection.com')
    
config = Config()