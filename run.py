#!/usr/bin/env python3
"""
Script principal pour lancer l'application EPI Detection
"""

import sys
import os
import argparse
from app.main import app, socketio

def main():
    parser = argparse.ArgumentParser(description='Système de Détection EPI')
    parser.add_argument('--mode', choices=['train', 'run', 'test'], 
                       default='run', help='Mode d\'exécution')
    parser.add_argument('--port', type=int, default=5000, help='Port du serveur')
    parser.add_argument('--host', default='0.0.0.0', help='Hôte du serveur')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        print("Lancement de l'entraînement du modèle...")
        os.system('python train.py')
    
    elif args.mode == 'run':
        print(f"""
        ========================================
        SYSTÈME DE DÉTECTION EPI - DASHBOARD
        ========================================
        Serveur démarré sur: http://{args.host}:{args.port}
        Dashboard: http://{args.host}:{args.port}/dashboard
        API: http://{args.host}:{args.port}/api/detect
        ========================================
        """)
        
        socketio.run(app, host=args.host, port=args.port, debug=True)
    
    elif args.mode == 'test':
        print("Lancement des tests...")
        os.system('python -m pytest tests/')

if __name__ == '__main__':
    main()