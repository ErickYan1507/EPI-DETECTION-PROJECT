#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostic complet: Pourquoi lunettes et bottes ne sont pas détectées
"""
import cv2
import json
import os
from pathlib import Path

print('DIAGNOSTIC COMPLET - LUNETTES ET BOTTES')
print('=' * 70)

# 1. Vérifier la configuration du modèle
print('\nCONFIGURATION DU MODELE')
print('-' * 70)

from app.constants import CLASS_MAP, CLASS_COLORS
print(f'\n   CLASS_MAP: {CLASS_MAP}')
print(f'   CLASS_COLORS: {CLASS_COLORS}')

# 2. Charger les images d'exemple
print('\n\nIMAGES DE TEST')
print('-' * 70)

# Créer des
print('-' * 70)

from app.detection import EPIDetector

detector = EPIDetector()

# Chercher des images avec lunettes dans le dataset de training
glasses_images = list(Path('dataset/images/val').glob('*.jpg'))[:5]

print(f'\n   🧪 Test sur {len(glasses_images)} images de validation:')

for img_path in glasses_images:
    label_path = Path(str(img_path).replace('images', 'labels').replace('.jpg', '.txt'))
    
    # Vérifier le label
    has_glasses = False
    has_boots = False
    
    if label_path.exists():
        with open(label_path) as f:
            for line in f:
                cls_id = int(line.split()[0])
                if cls_id == 1:  # glasses
                    has_glasses = True
                elif cls_id == 4:  # boots
                    has_boots = True
    
    # Tester la détection
    image = cv2.imread(str(img_path))
    if image is not None:
        detections, stats = detector.detect(image)
        
        status = '✅' if (not has_glasses or stats['with_glasses'] > 0) and (not has_boots or stats['with_boots'] > 0) else '❌'
        
        print(f'\n   {status} {img_path.name}')
        print(f'      Label: glasses={has_glasses}, boots={has_boots}')
        print(f'      Détecté: glasses={stats["with_glasses"]}, boots={stats["with_boots"]}')
        
        # Afficher les détections détaillées
        glass_dets = [d for d in detections if d['class'] == 'glasses']
        boot_dets = [d for d in detections if d['class'] == 'boots']
        
        if glass_dets:
            print(f'      Lunettes détectées:')
            for g in glass_dets:
                print(f'        • Confiance: {g["confidence"]:.3f}')
        
        if boot_dets:
            print(f'      Bottes détectées:')
            for b in boot_dets:
                print(f'        • Confiance: {b["confidence"]:.3f}')
        
        if not glass_dets and not boot_dets and (has_glasses or has_boots):
            print(f'      ⚠️  Aucune détection malgré le label!')

# 4. Vérifier les seuils de confiance
print('\n\n4️⃣ SEUILS DE CONFIANCE')
print('-' * 70)

from config import config

print(f'   Seuil confiance global: {config.CONFIDENCE_THRESHOLD}')
print(f'   Seuil IoU: {config.IOU_THRESHOLD}')
print(f'   Mode ensemble: {config.USE_ENSEMBLE_FOR_CAMERA}')
print(f'   Stratégie agrégation: {config.ENSEMBLE_STRATEGY}')

print('\n✅ FIN DIAGNOSTIC')
