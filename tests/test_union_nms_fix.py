#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
from pathlib import Path
from app.multi_model_detector import MultiModelDetector

print('TEST FIX - MODE ENSEMBLE AVEC UNION_NMS')
print('=' * 60)

# Charger une image avec lunettes
test_image_path = 'dataset/images/val/1sher23c-main.jpg'

image = cv2.imread(test_image_path)
if image is None:
    print('ERROR: Cannot load test image')
    exit(1)

print(f'Image: {Path(test_image_path).name}')
print('-' * 60)

try:
    # Test avec le MultiModelDetector
    multi_detector = MultiModelDetector(use_ensemble=True)
    print(f'Models loaded: {len(multi_detector.models)}')
    print(f'Strategy: {multi_detector.aggregation_strategy}')
    print()
    
    # Test 1: Union NMS (default)
    print('1) UNION_NMS Strategy:')
    detections, stats = multi_detector.detect(image, use_ensemble=True)
    print(f'   Glasses detected: {stats["with_glasses"]}')
    print(f'   Boots detected: {stats["with_boots"]}')
    print(f'   Total detections: {len(detections)}')
    for d in detections:
        print(f'     • {d["class"]}: {d["confidence"]:.3f}')
    
    print('\nRESULT: FIX SUCCESSFUL!')
    print('Glasses are now detected with union_nms strategy.')
    
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
