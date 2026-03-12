#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Démarrage rapide du système Unified Monitoring
Avec diagnostic automatique
"""
import os
import sys
import subprocess
import time

print("""
╔════════════════════════════════════════════════════════════════╗
║         🎬 UNIFIED MONITORING - QUICK START                    ║
║                                                                ║
║    La détection a été CORRIGÉE! ✅                             ║
║    (global multi_detector et detector déclarés)                ║
║════════════════════════════════════════════════════════════════╝
""")

print("📋 Pré-lancement - Diagnostic rapide ...\n")

# Test 1: Configuration
try:
    from config import config
    print("✅ Configuration chargée")
    print(f"   • BASE_DIR: {config.BASE_DIR}")
    print(f"   • MODELS: {config.MODELS_FOLDER}")
except Exception as e:
    print(f"❌ Erreur config: {e}")
    sys.exit(1)

# Test 2: Modèles
try:
    import glob
    models = glob.glob(os.path.join(config.MODELS_FOLDER, '*.pt'))
    if models:
        print(f"✅ {len(models)} modèle(s) trouvé(s)")
        for m in models:
            print(f"   • {os.path.basename(m)}")
    else:
        print("❌ Aucun modèle .pt trouvé!")
        sys.exit(1)
except Exception as e:
    print(f"❌ Erreur modèles: {e}")
    sys.exit(1)

# Test 3: Caméra
try:
    import cv2
    cameras = []
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append(i)
            cap.release()
    
    if cameras:
        print(f"✅ Caméra(s) détectée(s): {cameras}")
    else:
        print("⚠️  Aucune caméra détectée (peut être OK si utilisation en image)")
except Exception as e:
    print(f"⚠️  Erreur caméra: {e}")

# Test 4: Dépendances
try:
    import torch
    import flask
    import flask_socketio
    print("✅ Dépendances principales présentes")
except ImportError as e:
    print(f"❌ Dépendance manquante: {e}")
    sys.exit(1)

print("\n" + "=" * 64)
print("\n🚀 Démarrage du serveur Flask...\n")
print("INFO: Le système utilisera AUTOMATIQUEMENT:")
print("      • MultiModelDetector pour la détection")
print("      • Détection temps réel sur la caméra")
print("      • Sauvegarde des détections en BDD")
print("      • Mode ensemble désactiv é pour caméra (perf)")
print("\n⚙️  Configuration actuelle:")
print(f"      • USE_ENSEMBLE_FOR_CAMERA: {config.USE_ENSEMBLE_FOR_CAMERA}")
print(f"      • FRAME_SKIP: {config.FRAME_SKIP}")
print(f"      • CAMERA_FPS: {config.CAMERA_FPS}")

print("\n" + "=" * 64)
print("\n📺 Une fois Flask lancé, accédez à:")
print("    ► http://localhost:5000/unified_monitoring.html")
print("\n✨ Puis cliquez sur 'Démarrer Caméra' pour voir les détections!")
print("\n" + "=" * 64 + "\n")

# Lancer Flask
os.system("python app/main.py")
