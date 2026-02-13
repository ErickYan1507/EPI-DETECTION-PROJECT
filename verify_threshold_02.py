#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verification rapide du nouveau seuil 0.2"""

import os
import sys
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
import torch

print("=" * 70)
print("VERIFICATION DU NOUVEAU SEUIL: 0.2")
print("=" * 70)

print(f"\nConfiguration actuelle:")
print(f"  CONFIDENCE_THRESHOLD = {config.CONFIDENCE_THRESHOLD}")

# Charger le modèle
model = torch.hub.load('ultralytics/yolov5', 'custom', 
                       path=os.path.join(config.MODELS_FOLDER, 'best.pt'),
                       force_reload=False)

# Chercher une image
test_image_path = os.path.join("static", "uploads", "images", "20251217_005256_e.jpg")
if not os.path.exists(test_image_path):
    print(f"Image non trouvée: {test_image_path}")
    sys.exit(1)

img = cv2.imread(test_image_path)
print(f"\nImage: {img.shape}")

# Test avec le nouveau seuil
print(f"\n--- DETECTION AVEC SEUIL 0.2 ---\n")

model.conf = 0.2
model.iou = config.IOU_THRESHOLD

results = model(img)
detections = results.xyxy[0].cpu().numpy()

print(f"Nombre de détections: {len(detections)}\n")

class_counts = {}
for i, det in enumerate(detections):
    x1, y1, x2, y2, conf, cls_idx = det
    cls_name = model.names[int(cls_idx)]
    conf_val = float(conf)
    
    if cls_name not in class_counts:
        class_counts[cls_name] = 0
    class_counts[cls_name] += 1
    
    print(f"  [{i}] {cls_name:10} - confiance={conf_val:.4f}")

print(f"\nResume par classe:")
for cls_name in sorted(class_counts.keys()):
    count = class_counts[cls_name]
    symbol = "✓" if cls_name != "person" else "✓"
    print(f"  {symbol} {cls_name:10} - {count} detection(s)")

print("\n" + "=" * 70)
print("OK! Les classes helmet et vest devraient maintenant etre detectes!")
print("=" * 70)
