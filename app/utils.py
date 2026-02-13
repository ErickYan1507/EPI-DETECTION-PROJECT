"""
Utilitaires et helpers pour l'application
"""
import os
import logging
from pathlib import Path
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)

def ensure_directories():
    """Créer les dossiers nécessaires s'ils n'existent pas"""
    directories = [
        config.UPLOAD_FOLDER,
        os.path.join(config.UPLOAD_FOLDER, 'images'),
        os.path.join(config.UPLOAD_FOLDER, 'videos'),
        config.MODELS_FOLDER,
        config.LOGS_FOLDER,
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Dossier vérifié/créé: {directory}")

def get_timestamp_filename(original_filename):
    """Générer un nom de fichier avec timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{original_filename}"

def save_uploaded_file(file, file_type='image'):
    """Sauvegarder un fichier uploadé avec le bon nom"""
    ensure_directories()
    filename = get_timestamp_filename(file.filename)
    subfolder = 'images' if file_type == 'image' else 'videos'
    filepath = os.path.join(config.UPLOAD_FOLDER, subfolder, filename)
    file.save(filepath)
    return filepath

def cleanup_old_files(days=30):
    """Supprimer les fichiers uploadés plus vieux que X jours"""
    import glob
    from datetime import timedelta
    cutoff_time = datetime.now() - timedelta(days=days)
    
    for pattern in [
        os.path.join(config.UPLOAD_FOLDER, 'images', '*'),
        os.path.join(config.UPLOAD_FOLDER, 'videos', '*')
    ]:
        for filepath in glob.glob(pattern):
            if os.path.getmtime(filepath) < cutoff_time.timestamp():
                try:
                    os.remove(filepath)
                    logger.info(f"Fichier supprimé: {filepath}")
                except Exception as e:
                    logger.error(f"Erreur suppression {filepath}: {e}")

def validate_image_file(file):
    """Valider qu'un fichier est une image"""
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
    if '.' not in file.filename:
        return False, "Pas d'extension de fichier"
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return False, f"Format {ext} non autorisé"
    return True, "OK"

def validate_video_file(file):
    """Valider qu'un fichier est une vidéo"""
    allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
    if '.' not in file.filename:
        return False, "Pas d'extension de fichier"
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return False, f"Format {ext} non autorisé"
    return True, "OK"

def get_model_path():
    """Obtenir le chemin du meilleur modèle ou le modèle par défaut"""
    best_model = os.path.join(config.MODELS_FOLDER, 'best.pt')
    if os.path.exists(best_model):
        return best_model
    return config.DEFAULT_MODEL


def get_local_yolov5_repo():
    """Retourne le chemin vers un clone local de YOLOv5 si présent.

    Cherche dans plusieurs emplacements raisonnables (projet root, vendor/yolov5,
    ultralytics/yolov5). Renvoie une string (chemin) si trouvé, sinon None.
    Utilisé pour appeler torch.hub.load(repo_or_dir=LOCAL_PATH, ...)
    afin d'éviter d'essayer de télécharger le dépôt depuis Internet.
    """
    # Emplacements candidats relatifs au root du projet
    candidates = [
        Path(__file__).resolve().parents[1] / 'yolov5',
        Path(__file__).resolve().parents[1] / 'vendor' / 'yolov5',
        Path(__file__).resolve().parents[2] / 'yolov5',
        Path.cwd() / 'yolov5',
        Path.cwd() / 'vendor' / 'yolov5',
        Path.cwd() / 'ultralytics' / 'yolov5',
    ]

    for p in candidates:
        try:
            if p.exists() and p.is_dir():
                # basic sanity: check for detect.py or models directory in the repo
                if (p / 'models').exists() or (p / 'detect.py').exists():
                    return str(p)
        except Exception:
            continue
    return None
