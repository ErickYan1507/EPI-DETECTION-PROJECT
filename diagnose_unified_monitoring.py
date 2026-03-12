#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔍 Diagnostic complet du système Unified Monitoring
"""
import os
import sys
from pathlib import Path

print("""
╔════════════════════════════════════════════════════════════════╗
║    DIAGNOSTIC UNIFIED MONITORING - EPI DETECTION              ║
╚════════════════════════════════════════════════════════════════╝
""")

# 1. Vérifier la configuration
print("1️⃣ Vérification de la configuration...")
try:
    from config import config
    print(f"   ✅ BASE_DIR: {config.BASE_DIR}")
    print(f"   ✅ MODELS_FOLDER: {config.MODELS_FOLDER}")
    print(f"   ✅ CAMERA_FRAME_WIDTH: {config.CAMERA_FRAME_WIDTH}")
    print(f"   ✅ CAMERA_FRAME_HEIGHT: {config.CAMERA_FRAME_HEIGHT}")
    print(f"   ✅ CAMERA_FPS: {config.CAMERA_FPS}")
    print(f"   ✅ DEFAULT_USE_ENSEMBLE: {config.DEFAULT_USE_ENSEMBLE}")
    print(f"   ✅ USE_ENSEMBLE_FOR_CAMERA: {config.USE_ENSEMBLE_FOR_CAMERA}")
except Exception as e:
    print(f"   ❌ Erreur config: {e}")
    sys.exit(1)

# 2. Vérifier les modèles
print("\n2️⃣ Vérification des modèles...")
try:
    import glob
    model_files = glob.glob(os.path.join(config.MODELS_FOLDER, '*.pt'))
    print(f"   ✅ Modèles trouvés: {len(model_files)}")
    for mf in model_files:
        print(f"      - {os.path.basename(mf)}")
    if not model_files:
        print("   ⚠️ AVERTISSEMENT: Aucun modèle trouvé!")
except Exception as e:
    print(f"   ❌ Erreur recherche modèles: {e}")

# 3. Vérifier EPIDetector
print("\n3️⃣ Vérification du EPIDetector...")
try:
    from app.detection import EPIDetector
    print("   ✅ EPIDetector importé")
    # Ne pas le charger ici pour gagner du temps
except Exception as e:
    print(f"   ❌ Erreur import EPIDetector: {e}")

# 4. Vérifier MultiModelDetector
print("\n4️⃣ Vérification du MultiModelDetector...")
try:
    from app.multi_model_detector import MultiModelDetector
    print("   ✅ MultiModelDetector importé")
except Exception as e:
    print(f"   ❌ Erreur import MultiModelDetector: {e}")

# 5. Vérifier CameraManager
print("\n5️⃣ Vérification de la CameraManager...")
try:
    import cv2
    print("   ✅ OpenCV (cv2) importé")
    
    # Lister les caméras disponibles
    cameras = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append(i)
            cap.release()
    
    if cameras:
        print(f"   ✅ Caméras détectées: {cameras}")
    else:
        print("   ❌ Aucune caméra détectée!")
except Exception as e:
    print(f"   ❌ Erreur vérification caméra: {e}")

# 6. Vérifier la base de données
print("\n6️⃣ Vérification de la base de données...")
try:
    from app.database_unified import db, Detection
    print("   ✅ Base de données importée")
except Exception as e:
    print(f"   ❌ Erreur import base de données: {e}")

# 7. Vérifier les routes API
print("\n7️⃣ Vérification des routes API...")
try:
    from app.routes_api import api_routes
    print("   ✅ Routes API importées")
except Exception as e:
    print(f"   ❌ Erreur import routes: {e}")

print("\n" + "=" * 64)
print("✅ Diagnostic terminé!")
print("=" * 64)
print("""
Pour démarrer le système:
  1. Lancez Flask: python app/main.py
  2. Allez à: http://localhost:5000/unified_monitoring.html
  3. Cliquez sur "Démarrer caméra"
  4. Les détections s'afficheront automatiquement
""")
