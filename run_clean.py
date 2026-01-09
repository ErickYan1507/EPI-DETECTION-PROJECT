#!/usr/bin/env python3
"""
Lanceur ultra-propre avec suppression complète des logs OpenCV
Meilleure approche: redirection au niveau système
"""
import subprocess
import sys
import os

# Créer un script Python qui s'exécute dans un nouvel environnement
script_content = '''
import os
import sys

# Variables d'environnement AVANT tout import
os.environ['OPENCV_LOG_LEVEL'] = 'OFF'
os.environ['OPENCV_LOGGING_LEVEL'] = 'OFF'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['PYTHONWARNINGS'] = 'ignore'

# Rediriger stderr AVANT tout import
import io
sys.stderr = open(os.devnull, 'w')

# Imports
from app.main import app

# Restaurer stderr
sys.stderr = sys.__stderr__

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 EPI DETECTION - DÉMARRAGE")
    print("=" * 60)
    print("\\n✅ Configuration optimisée (logs supprimés)")
    print("📍 Adresse: http://127.0.0.1:5000")
    print("🛑 Arrêter: Ctrl+C")
    print("=" * 60 + "\\n")
    
    try:
        app.run(
            debug=False,
            host='127.0.0.1',
            port=5000,
            use_reloader=False,
            use_debugger=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\\n✋ Arrêt...")
        sys.exit(0)
'''

if __name__ == '__main__':
    # Exécuter directement dans ce processus
    import os
    os.environ['OPENCV_LOG_LEVEL'] = 'OFF'
    os.environ['OPENCV_LOGGING_LEVEL'] = 'OFF'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    os.environ['PYTHONWARNINGS'] = 'ignore'
    
    # Rediriger stderr AVANT les imports
    import io
    devnull = open(os.devnull, 'w')
    sys.stderr = devnull
    
    from app.main import app
    
    # Restaurer stderr pour les messages de l'app
    sys.stderr = sys.__stderr__
    devnull.close()
    
    print("=" * 60)
    print("🚀 EPI DETECTION - DÉMARRAGE")
    print("=" * 60)
    print("\n✅ Configuration optimisée (logs supprimés)")
    print("📍 Adresse: http://127.0.0.1:5000")
    print("🛑 Arrêter: Ctrl+C")
    print("=" * 60 + "\n")
    
    try:
        app.run(
            debug=False,
            host='127.0.0.1',
            port=5000,
            use_reloader=False,
            use_debugger=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n✋ Arrêt de l'application...")
        sys.exit(0)
