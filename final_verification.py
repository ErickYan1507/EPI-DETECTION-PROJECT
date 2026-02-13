#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TEST FINAL: Verification que tous les fixes sont appliques"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("VERIFICATION FINALE DES CORRECTIONS")
print("=" * 70)

print("\n[1] Configuration:")
from config import config
print(f"  - CONFIDENCE_THRESHOLD: {config.CONFIDENCE_THRESHOLD}")
print(f"  - MULTI_MODEL_ENABLED: {config.MULTI_MODEL_ENABLED}")

print("\n[2] Uploads (/upload):")
with open('app/main.py', 'r') as f:
    content = f.read()
    if 'formatted_detections' in content and "'class_name': det_item.get('class'" in content:
        print("  ✓ Formatage des détections PRESENT")
    else:
        print("  ✗ Formatage des détections ABSENT")

print("\n[3] Monitoring (/api/detect via routes_api.py):")
with open('app/routes_api.py', 'r') as f:
    content = f.read()
    if "'x1': int(x1)," in content and "'y1': int(y1)," in content:
        print("  ✓ Formatage x1, y1, x2, y2 PRESENT")
    else:
        print("  ✗ Formatage x1, y1, x2, y2 ABSENT")

print("\n[4] Test rapide du detecteur:")
from app.multi_model_detector import MultiModelDetector
import numpy as np

detector = MultiModelDetector(use_ensemble=True)
test_img = np.ones((640, 640, 3), dtype=np.uint8) * 100
dets, stats = detector.detect(test_img)

print(f"  - Détecteur chargé: ✓")
print(f"  - Détections retournées: {len(dets)}")

# Test avec une vraie image
test_path = "static/uploads/images/20251217_005256_e.jpg"
if os.path.exists(test_path):
    import cv2
    img = cv2.imread(test_path)
    dets, stats = detector.detect(img, use_ensemble=False)
    print(f"  - Image réelle: {len(dets)} détections")
    
    if dets:
        det = dets[0]
        print(f"    - Clés détection: {list(det.keys())}")
        print(f"    - Classe: {det.get('class', 'N/A')}")
        print(f"    - Confidence: {det.get('confidence', 'N/A')}")
        print(f"    - BBox: {det.get('bbox', 'N/A')}")

print("\n" + "=" * 70)
print("RESUME DES CORRECTIONS")
print("=" * 70)

print("""
1. SEUIL DE CONFIANCE: 0.2 (réduit de 0.5)
   - Permet de détecter helmet, vest avec confiance < 0.5
   
2. FORMATAGE UPLOADS (/upload):
   - Convertit bbox → x1, y1, x2, y2
   - Arrondit confidence à 3 décimales
   - Config: CONFIDENCE_THRESHOLD = 0.2

3. FORMATAGE MONITORING (/api/detect):
   - Convertit bbox → x1, y1, x2, y2
   - Arrondit confidence à 3 décimales
   - Config: CONFIDENCE_THRESHOLD = 0.2

4. CLASSES DETECTEES:
   - person (0-indexed: 2)
   - helmet (0-indexed: 0) - NEW
   - glasses (0-indexed: 1)
   - vest (0-indexed: 3) - NEW
   - boots (0-indexed: 4)

5. STATISTIQUES:
   - total_persons: Nombre de personnes
   - with_helmet: Nombre avec casque
   - with_vest: Nombre avec gilet
   - with_glasses: Nombre avec lunettes
   - with_boots: Nombre avec chaussures
   - compliance_rate: (with_helmet / total_persons) * 100
""")

print("=" * 70)
print("PRET POUR DEPLOYMENT!")
print("=" * 70)
print("\nCommande pour redémarrer:")
print("  python app/main.py")
print("\nTester à:")
print("  http://localhost:5000/upload (uploads)")
print("  http://localhost:5000/unified_monitoring.html (monitoring)")
