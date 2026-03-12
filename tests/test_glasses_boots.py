#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import os
from pathlib import Path
from app.detection import EPIDetector
from app.constants import CLASS_MAP

print('TEST DETECTION - LUNETTES ET BOTTES')
print('=' * 60)

detector = EPIDetector()

# Test sur images de validation
val_images = list(Path('dataset/images/val').glob('*.jpg'))[:10]

print(f'\nTesting {len(val_images)} validation images...')

glasses_count = 0
boots_count = 0
correct_glasses = 0
correct_boots = 0

for img_path in val_images:
    # Get label
    label_path = Path(str(img_path).replace('images', 'labels').replace('.jpg', '.txt'))
    
    has_glasses = False
    has_boots = False
    
    if label_path.exists():
        with open(label_path) as f:
            for line in f:
                if line.strip():
                    try:
                        cls_id = int(float(line.split()[0]))
                        if cls_id == 1:  # glasses
                            has_glasses = True
                        elif cls_id == 4:  # boots
                            has_boots = True
                    except (ValueError, IndexError):
                        continue
    
    # Detect
    image = cv2.imread(str(img_path))
    if image is not None:
        detections, stats = detector.detect(image)
        
        det_glasses = stats['with_glasses'] > 0
        det_boots = stats['with_boots'] > 0
        
        if has_glasses:
            glasses_count += 1
            if det_glasses:
                correct_glasses += 1
        
        if has_boots:
            boots_count += 1
            if det_boots:
                correct_boots += 1
        
        status = 'OK' if (has_glasses == det_glasses) and (has_boots == det_boots) else 'FAIL'
        
        print(f'{status} {img_path.name}')
        if has_glasses or has_boots:
            print(f'    Label: glasses={has_glasses}, boots={has_boots}')
            print(f'    Detect: glasses={det_glasses}, boots={det_boots}')

print('\n' + '=' * 60)
print('RESULTS:')
print(f'Glasses: {correct_glasses}/{glasses_count} detected ({100*correct_glasses/glasses_count if glasses_count > 0 else 0:.1f}%)')
print(f'Boots: {correct_boots}/{boots_count} detected ({100*correct_boots/boots_count if boots_count > 0 else 0:.1f}%)')
