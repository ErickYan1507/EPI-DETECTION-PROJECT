#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test réel du problème des uploads"""

import os
import sys
import json
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("TEST REEL DES UPLOADS")
print("=" * 70)

# Test 1: Vérifier que les modules importent
print("\n[1] Vérification des imports...")
try:
    from config import config
    print("  [OK] config importé")
except Exception as e:
    print(f"  [ERREUR] config: {e}")
    sys.exit(1)

try:
    from app.detection import EPIDetector
    print("  [OK] EPIDetector importé")
except Exception as e:
    print(f"  [ERREUR] EPIDetector: {e}")
    sys.exit(1)

try:
    from app.multi_model_detector import MultiModelDetector
    print("  [OK] MultiModelDetector importé")
except Exception as e:
    print(f"  [ERREUR] MultiModelDetector: {e}")
    sys.exit(1)

# Test 2: Vérifier la configuration
print("\n[2] Vérification de la configuration...")
print(f"  MULTI_MODEL_ENABLED: {config.MULTI_MODEL_ENABLED}")
print(f"  DEFAULT_USE_ENSEMBLE: {config.DEFAULT_USE_ENSEMBLE}")
print(f"  USE_ENSEMBLE_FOR_CAMERA: {config.USE_ENSEMBLE_FOR_CAMERA}")
print(f"  MODELS_FOLDER: {config.MODELS_FOLDER}")
print(f"  CONFIDENCE_THRESHOLD: {config.CONFIDENCE_THRESHOLD}")

# Test 3: Vérifier le dossier des modèles
print("\n[3] Vérification des modèles...")
model_dir = config.MODELS_FOLDER
if not os.path.exists(model_dir):
    print(f"  [ERREUR] Dossier modèles n'existe pas: {model_dir}")
    sys.exit(1)
    
models = [f for f in os.listdir(model_dir) if f.endswith('.pt')]
print(f"  [OK] Dossier modèles: {model_dir}")
print(f"  [OK] Modèles trouvés: {models}")

for model in models:
    model_path = os.path.join(model_dir, model)
    size = os.path.getsize(model_path) / (1024 * 1024)
    print(f"    - {model}: {size:.2f} MB")

# Test 4: Charger MultiModelDetector
print("\n[4] Chargement de MultiModelDetector...")
try:
    detector = MultiModelDetector(use_ensemble=True)
    print(f"  [OK] MultiModelDetector chargé")
    print(f"    - Nombre de modèles: {len(detector.models)}")
    print(f"    - Modèles disponibles: {list(detector.models.keys())}")
    print(f"    - Mode ensemble: {detector.use_ensemble}")
    
    if len(detector.models) == 0:
        print("  [ERREUR] Aucun modèle chargé!")
        sys.exit(1)
        
except Exception as e:
    print(f"  [ERREUR] Chargement MultiModelDetector: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Tester la détection sur une image de test
print("\n[5] Test de détection...")
import cv2
import numpy as np

# Créer une image de test
test_image = np.ones((640, 640, 3), dtype=np.uint8) * 128
print("  - Image de test créée: 640x640")

try:
    detections, stats = detector.detect(test_image, use_ensemble=True)
    print(f"  [OK] Détection exécutée")
    print(f"    - Détections: {len(detections)}")
    print(f"    - Stats: {json.dumps(stats, indent=2, default=str)}")
    
    if len(detections) == 0:
        print("  [WARN] Aucune détection sur l'image de test (normal si image est vide)")
    
except Exception as e:
    print(f"  [ERREUR] Détection: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Tester avec une image réelle si elle existe
print("\n[6] Test avec image réelle...")
test_images_dir = os.path.join("static", "uploads", "images")
if os.path.exists(test_images_dir):
    image_files = [f for f in os.listdir(test_images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if image_files:
        test_img_path = os.path.join(test_images_dir, image_files[0])
        print(f"  - Image trouvée: {test_img_path}")
        
        try:
            img = cv2.imread(test_img_path)
            if img is not None:
                print(f"  - Image chargée: {img.shape}")
                
                detections, stats = detector.detect(img, use_ensemble=True)
                print(f"  [OK] Détection sur image réelle:")
                print(f"    - Détections: {len(detections)}")
                print(f"    - Personnes: {stats.get('total_persons', 0)}")
                print(f"    - Compliance: {stats.get('compliance_rate', 0):.1f}%")
                
                if len(detections) > 0:
                    print(f"    - Classes détectées: {list(set([d.get('class', 'unknown') for d in detections]))}")
            else:
                print("  [WARN] Impossible de charger l'image")
        except Exception as e:
            print(f"  [ERREUR]: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("  [WARN] Pas d'images de test trouvées")
else:
    print(f"  [WARN] Répertoire de test non trouvé: {test_images_dir}")

# Test 7: Vérifier la route Flask
print("\n[7] Vérification de la route Flask...")
try:
    from app.main import app
    print(f"  [OK] Application Flask importée")
    
    # Vérifier la route /upload
    with app.test_client() as client:
        response = client.get('/upload')
        print(f"  [OK] Route GET /upload: status={response.status_code}")
        
except Exception as e:
    print(f"  [ERREUR] Flask: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ TEST COMPLÉTÉ")
print("=" * 70)
