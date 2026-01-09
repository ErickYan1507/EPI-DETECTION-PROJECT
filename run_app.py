#!/usr/bin/env python3
"""
Lanceur principal de l'application EPI Detection
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au PATH
sys.path.insert(0, str(Path(__file__).parent))

from app.main_new import app, socketio
from app.logger import logger
from config import config

def run_development():
    """Lancer en mode développement"""
    logger.info("Mode développement activé")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

def run_production():
    """Lancer en mode production (avec gunicorn)"""
    logger.info("Mode production - utiliser gunicorn")
    print("Lancer avec: gunicorn --worker-class eventlet -w 1 app.main_new:app")

def run_training():
    """Lancer l'entraînement du modèle"""
    logger.info("Lancement de l'entraînement...")
    os.system('python train.py')

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='EPI Detection System')
    parser.add_argument('command', choices=['run', 'train', 'dev', 'prod'],
                       help='Commande à exécuter')
    parser.add_argument('--port', type=int, default=5000, help='Port du serveur')
    
    args = parser.parse_args()
    
    logger.info(f"Commande: {args.command}")
    
    if args.command in ['run', 'dev']:
        run_development()
    elif args.command == 'prod':
        run_production()
    elif args.command == 'train':
        run_training()
