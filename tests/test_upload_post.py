#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test complet de la route /upload avec fichier"""

import os
import sys
import json
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("TEST COMPLET DE LA ROUTE /upload")
print("=" * 70)

# Importer Flask app
print("\n[1] Chargement de l'application Flask...")
try:
    from app.main import app
    print("  [OK] Application importée")
except Exception as e:
    print(f"  [ERREUR] Impossible d'importer app: {e}")
    sys.exit(1)

# Trouver une image de test
print("\n[2] Recherche d'une image de test...")
test_images_dir = os.path.join("static", "uploads", "images")
test_image_path = None

if os.path.exists(test_images_dir):
    image_files = [f for f in os.listdir(test_images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if image_files:
        test_image_path = os.path.join(test_images_dir, image_files[0])
        print(f"  [OK] Image trouvée: {test_image_path}")
    else:
        print(f"  [WARN] Pas d'images dans {test_images_dir}")
else:
    print(f"  [WARN] Répertoire non trouvé: {test_images_dir}")

# Créer une image de test si nécessaire
if not test_image_path:
    print("\n[3] Création d'une image de test...")
    import cv2
    import numpy as np
    
    # Créer un répertoire
    os.makedirs(test_images_dir, exist_ok=True)
    
    # Créer une image simple (personne avec équipement)
    test_image = np.ones((640, 640, 3), dtype=np.uint8) * 200
    test_image[100:400, 200:400] = [0, 0, 255]  # Rectangle rouge (personne)
    
    test_image_path = os.path.join(test_images_dir, "test_image.jpg")
    cv2.imwrite(test_image_path, test_image)
    print(f"  [OK] Image de test créée: {test_image_path}")
else:
    print("\n[3] Utilisation de l'image trouvée")

# Test 4: POST /upload avec l'image
print("\n[4] Test POST /upload...")
try:
    with app.test_client() as client:
        # Lire l'image
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        
        # Créer une requête multipart
        response = client.post(
            '/upload',
            data={
                'file': (BytesIO(image_data), os.path.basename(test_image_path)),
                'type': 'image'
            }
        )
        
        print(f"  [OK] Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.get_json()
            print(f"  [OK] Response JSON:")
            print(f"    - success: {result.get('success', False)}")
            print(f"    - detections_count: {result.get('detections_count', 0)}")
            
            if 'detections' in result:
                print(f"    - detections: {len(result['detections'])} détections")
                for i, det in enumerate(result['detections'][:3]):
                    print(f"      [{i}] {det.get('class_name', 'unknown')}: confidence={det.get('confidence', 0)}")
            else:
                print(f"    - detections: non fourni dans la réponse")
            
            if 'statistics' in result:
                stats = result['statistics']
                print(f"    - statistics:")
                print(f"      - total_persons: {stats.get('total_persons', 0)}")
                print(f"      - with_helmet: {stats.get('with_helmet', 0)}")
                print(f"      - compliance_rate: {stats.get('compliance_rate', 0):.1f}%")
                print(f"      - total_ms: {stats.get('total_ms', 0):.0f}ms")
            
            if result.get('success'):
                print("\n  [SUCCESS] Upload et détection réussis!")
            else:
                print(f"\n  [WARN] Erreur: {result.get('error', 'Erreur inconnue')}")
        else:
            print(f"  [ERREUR] Response status {response.status_code}: {response.data}")
            
except Exception as e:
    print(f"  [ERREUR] Test POST: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("TEST TERMINE")
print("=" * 70)
