#!/usr/bin/env python3
"""
Lanceur optimisé - Supprime les warnings OpenCV inutiles
Utilise: python start_clean.py
"""
import os
import sys
import io

# Supprimer TOUS les logs AVANT d'importer quoi que ce soit
os.environ['OPENCV_LOG_LEVEL'] = 'OFF'
os.environ['OPENCV_LOGGING_LEVEL'] = 'OFF'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # TensorFlow aussi
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Éviter les logs CUDA

# Supprimer les stderr pour OpenCV (ils affichent les erreurs)
import contextlib

# Rediriger les stderr temporairement
devnull = open(os.devnull, 'w')
old_stderr = sys.stderr
sys.stderr = devnull

try:
    # Importer OpenCV maintenant
    import cv2
finally:
    sys.stderr = old_stderr
    devnull.close()

# Importer l'app
from app.main import app

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 EPI DETECTION - DÉMARRAGE")
    print("=" * 60)
    print("\n✅ Configuration optimisée (logs OpenCV supprimés)")
    print("📍 Adresse: http://127.0.0.1:5000")
    print("🛑 Arrêter: Ctrl+C")
    print("=" * 60 + "\n")
    
    try:
        app.run(
            debug=False,
            host='127.0.0.1',
            port=5000,
            use_reloader=False,  # Éviter les rechargements multiples
            use_debugger=False   # Pas besoin du debugger ici
        )
    except KeyboardInterrupt:
        print("\n\n✋ Arrêt de l'application...")
        sys.exit(0)
