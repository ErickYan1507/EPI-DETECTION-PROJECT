#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnostic: Pourquoi les autres classes ne sont pas détectées"""

import os
import sys
import json
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("DIAGNOSTIC: DETECTION DES CLASSES")
print("=" * 70)

# Importer les configs
from config import config
from app.detection import EPIDetector
import torch

print("\n[1] Configuration des Seuils:")
print(f"  - CONFIDENCE_THRESHOLD: {config.CONFIDENCE_THRESHOLD}")
print(f"  - IOU_THRESHOLD: {config.IOU_THRESHOLD}")
print(f"  - MAX_DETECTIONS: {config.MAX_DETECTIONS}")

# Charger le modèle directement
print("\n[2] Chargement du modèle YOLO...")
try:
    model = torch.hub.load('ultralytics/yolov5', 'custom', 
                           path=os.path.join(config.MODELS_FOLDER, 'best.pt'),
                           force_reload=False)
    print("  [OK] Modèle chargé")
    print(f"  - Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    print(f"  - Classe names: {model.names}")
    print(f"  - Nombre de classes: {len(model.names)}")
except Exception as e:
    print(f"  [ERREUR] {e}")
    sys.exit(1)

# Chercher une image de test
print("\n[3] Recherche d'une image de test...")
test_image_path = None
test_images_dir = os.path.join("static", "uploads", "images")

if os.path.exists(test_images_dir):
    image_files = [f for f in os.listdir(test_images_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if image_files:
        test_image_path = os.path.join(test_images_dir, image_files[0])
        print(f"  [OK] Image trouvée: {test_image_path}")

if not test_image_path:
    print("  [ERREUR] Pas d'image de test trouvée")
    sys.exit(1)

# Charger l'image
print("\n[4] Chargement de l'image...")
img = cv2.imread(test_image_path)
if img is None:
    print(f"  [ERREUR] Impossible de charger {test_image_path}")
    sys.exit(1)

print(f"  [OK] Image chargée: {img.shape}")

# Test 1: Avec le seuil par défaut
print("\n[5] Test 1: DETECTION AVEC SEUIL PAR DEFAUT")
print(f"  Seuil de confiance: {config.CONFIDENCE_THRESHOLD}")

model.conf = config.CONFIDENCE_THRESHOLD
model.iou = config.IOU_THRESHOLD

results = model(img)
detections = results.xyxy[0].cpu().numpy()

print(f"  Nombre de détections: {len(detections)}")
if len(detections) > 0:
    print("\n  Détections trouvées:")
    for i, det in enumerate(detections):
        x1, y1, x2, y2, conf, cls_idx = det
        cls_name = model.names[int(cls_idx)]
        print(f"    [{i}] {cls_name}: confiance={float(conf):.4f}, bbox=[{int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}]")
else:
    print("  AUCUNE DETECTION!")

# Test 2: Avec seuil plus bas
print("\n[6] Test 2: DETECTION AVEC SEUIL PLUS BAS (0.3)")
print(f"  Ancien seuil: {config.CONFIDENCE_THRESHOLD}")
print(f"  Nouveau seuil: 0.3")

model.conf = 0.3
results = model(img)
detections = results.xyxy[0].cpu().numpy()

print(f"  Nombre de détections: {len(detections)}")
if len(detections) > 0:
    print("\n  Détections trouvées:")
    class_counts = {}
    for i, det in enumerate(detections):
        x1, y1, x2, y2, conf, cls_idx = det
        cls_name = model.names[int(cls_idx)]
        conf_val = float(conf)
        
        if cls_name not in class_counts:
            class_counts[cls_name] = 0
        class_counts[cls_name] += 1
        
        print(f"    [{i}] {cls_name:10} confiance={conf_val:.4f}")
    
    print(f"\n  Résumé par classe:")
    for cls_name, count in sorted(class_counts.items()):
        print(f"    - {cls_name}: {count} détection(s)")
else:
    print("  AUCUNE DETECTION AVEC SEUIL 0.3 NON PLUS!")

# Test 3: Avec seuil très bas
print("\n[7] Test 3: DETECTION AVEC SEUIL TRES BAS (0.1)")
print(f"  Nouveau seuil: 0.1")

model.conf = 0.1
results = model(img)
detections = results.xyxy[0].cpu().numpy()

print(f"  Nombre de détections: {len(detections)}")
if len(detections) > 0:
    print("\n  Détections trouvées (Top 20):")
    class_counts = {}
    for i, det in enumerate(detections[:20]):
        x1, y1, x2, y2, conf, cls_idx = det
        cls_name = model.names[int(cls_idx)]
        conf_val = float(conf)
        
        if cls_name not in class_counts:
            class_counts[cls_name] = 0
        class_counts[cls_name] += 1
        
        print(f"    [{i}] {cls_name:10} confiance={conf_val:.4f}")
    
    print(f"\n  Résumé par classe:")
    for cls_name, count in sorted(class_counts.items()):
        print(f"    - {cls_name}: {count} détection(s)")
else:
    print("  AUCUNE DETECTION AVEC SEUIL 0.1 NON PLUS!")

# Analyse des résultats bruts
print("\n[8] ANALYSE RAW (SANS FILTRE)")
model.conf = 0.0  # Pas de filtrage
results = model(img)
detections = results.xyxy[0].cpu().numpy()

print(f"  Total détections brutes (avant IOU): {len(detections)}")

# Compter par classe
class_counts_raw = {}
for det in detections:
    x1, y1, x2, y2, conf, cls_idx = det
    cls_name = model.names[int(cls_idx)]
    conf_val = float(conf)
    
    if cls_name not in class_counts_raw:
        class_counts_raw[cls_name] = []
    class_counts_raw[cls_name].append(conf_val)

print("\n  Détections par classe (avant filtrage):")
for cls_name in sorted(class_counts_raw.keys()):
    confs = class_counts_raw[cls_name]
    print(f"    - {cls_name:10}: {len(confs):3} fois, conf_max={max(confs):.4f}, conf_min={min(confs):.4f}, conf_mean={sum(confs)/len(confs):.4f}")

print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)

# Analyse et recommandations
print("\nProblemes potentiels:")

# Vérifier si le modèle détecte rien
model.conf = 0.0
results = model(img)
detections = results.xyxy[0].cpu().numpy()

if len(detections) == 0:
    print("  [CRITIQUE] Le modèle ne détecte RIEN du tout!")
    print("    Possible: Mauvais modèle, image invalide, ou modèle mal entraîné")
elif all(model.names[int(det[5])] == 'person' for det in detections):
    print("  [ALERTE] Le modèle détecte SEULEMENT 'person'!")
    print("    Possible causes:")
    print("      1. Le modèle best.pt n'a pas été bien entraîné sur les équipements")
    print("      2. Les équipements dans l'image sont trop petits ou floue")
    print("      3. Les équipements ne ressemblent pas à l'entraînement")
    print("    Solutions:")
    print("      - Réentraîner le modèle avec plus d'exemples d'équipements")
    print("      - Augmenter la résolution des images")
    print("      - Réduire le seuil de confiance (actuellement: " + str(config.CONFIDENCE_THRESHOLD) + ")")
else:
    print("  [OK] Le modèle détecte plusieurs classes")

# Vérifier la configuration
if config.CONFIDENCE_THRESHOLD > 0.5:
    print(f"  [INFO] Le seuil de confiance est élevé ({config.CONFIDENCE_THRESHOLD})")
    print("    Les équipements avec confiance faible seront filtrés")

print("\n" + "=" * 70)
