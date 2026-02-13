#!/usr/bin/env python
from app.detection import EPIDetector
from app.multi_model_detector import MultiModelDetector
import cv2
import os

print('🧪 TEST DU FIX - MULTI-MODEL DETECTION')
print('=' * 50)

# Charger une image avec lunettes
test_image_path = 'dataset/images/val/1sher23c-main.jpg'

if os.path.exists(test_image_path):
    image = cv2.imread(test_image_path)
    
    # Test 1: Détecteur simple
    print('\n1️⃣ Détecteur simple (best.pt):')
    detector = EPIDetector()
    detections, stats = detector.detect(image)
    print(f'   Lunettes détectées: {stats["with_glasses"]}')
    print(f'   Stats: {stats}')
    
    # Test 2: Détecteur multi-modèles
    print('\n2️⃣ Détecteur multi-modèles:')
    try:
        multi_detector = MultiModelDetector(use_ensemble=True)
        detections_multi, stats_multi = multi_detector.detect(image, use_ensemble=True)
        print(f'   Lunettes détectées: {stats_multi["with_glasses"]}')
        print(f'   Stats: {stats_multi}')
    except Exception as e:
        print(f'   ⚠️  Erreur: {e}')
else:
    print(f'❌ Image non trouvée: {test_image_path}')
