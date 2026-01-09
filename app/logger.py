"""
Configuration du logging centralisée
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from config import config

def setup_logging(name=__name__):
    """Configurer un logger avec fichier et console"""
    logger = logging.getLogger(name)
    
    if logger.handlers:  # Logger déjà configuré
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Formateur
    formatter = logging.Formatter(
        '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler console -> écrire sur stdout pour éviter wrappers stderr fermés
    # Utiliser UTF-8 explicitement sur Windows pour éviter les erreurs d'encodage
    console_handler = logging.StreamHandler(sys.stdout)
    if hasattr(console_handler.stream, 'reconfigure'):
        try:
            console_handler.stream.reconfigure(encoding='utf-8')
        except Exception:
            pass
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier avec UTF-8
    log_file = Path(config.LOGS_FOLDER) / f'{name}.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Logger global
logger = setup_logging('epi_detection')
