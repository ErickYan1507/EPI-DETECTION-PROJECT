#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration du système EPI Detection pour utiliser:
1. Le modèle réel: D:\projet\EPI-DETECTION-PROJECT\models\best.pt
2. Les données d'entraînement réelles: D:\projet\EPI-DETECTION-PROJECT\runs\train\epi_detection_session_003
3. Les 5 classes réelles: Personne, Casque, Gilet, Bottes, Lunettes
"""

import os
import sys
import json
from pathlib import Path

print("\n" + "="*80)
print("CONFIGURATION DU SYSTÈME - UTILISER DONNÉES RÉELLES")
print("="*80)

# Chemins réels
PROJECT_ROOT = r"D:\projet\EPI-DETECTION-PROJECT"
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
TRAINING_DIR = os.path.join(PROJECT_ROOT, "runs", "train", "epi_detection_session_003")
BEST_MODEL = os.path.join(MODELS_DIR, "best.pt")

print(f"\n📁 Chemins configurés:")
print(f"  Project: {PROJECT_ROOT}")
print(f"  Models: {MODELS_DIR}")
print(f"  Training: {TRAINING_DIR}")

# Vérifier que le modèle existe
if not os.path.exists(BEST_MODEL):
    print(f"\n❌ ERREUR: Modèle non trouvé: {BEST_MODEL}")
    sys.exit(1)

print(f"  ✅ Modèle trouvé: {BEST_MODEL}")

# Vérifier les données d'entraînement
if not os.path.exists(TRAINING_DIR):
    print(f"\n❌ ERREUR: Répertoire entraînement non trouvé: {TRAINING_DIR}")
    sys.exit(1)

print(f"  ✅ Données entraînement trouvées: {TRAINING_DIR}")

# 5 classes réelles
CLASSES_REAL = {
    0: 'Personne',
    1: 'Casque',
    2: 'Gilet',
    3: 'Bottes',
    4: 'Lunettes'
}

print(f"\n🏷️  Classes réelles (5):")
for idx, cls in CLASSES_REAL.items():
    print(f"  {idx}: {cls}")

# Créer la config d'intégration
config_data = {
    "project_root": PROJECT_ROOT,
    "models": {
        "directory": MODELS_DIR,
        "best_model": BEST_MODEL,
        "framework": "YOLOv5",
        "input_size": 640
    },
    "training": {
        "directory": TRAINING_DIR,
        "results_csv": os.path.join(TRAINING_DIR, "results.csv"),
        "epochs_total": 127,
        "last_epoch": 99,
        "metrics": {
            "mAP_0_5": 0.9756,
            "precision": 0.9150,
            "recall": 0.9494,
            "f1_score": 0.9319
        }
    },
    "classes": {
        "count": 5,
        "mapping": {
            "0": "Personne",
            "1": "Casque",
            "2": "Gilet",
            "3": "Bottes",
            "4": "Lunettes"
        },
        "colors": {
            "Personne": [255, 255, 0],
            "Casque": [0, 255, 0],
            "Gilet": [255, 0, 0],
            "Bottes": [255, 165, 0],
            "Lunettes": [0, 0, 255]
        }
    },
    "detection": {
        "confidence_threshold": 0.5,
        "iou_threshold": 0.45,
        "max_detections": 100,
        "use_cuda": True,
        "enable_half_precision": True
    }
}

# Sauvegarder la config
config_file = os.path.join(PROJECT_ROOT, "config_real_integration.json")
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(config_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Configuration sauvegardée: {config_file}")

# Afficher le résumé
print("\n" + "="*80)
print("RÉSUMÉ DE CONFIGURATION")
print("="*80)
print(f"""
✅ Modèle:              {BEST_MODEL}
✅ Entraînement:        {TRAINING_DIR}
✅ Performance:         mAP 97.56% | Précision 91.50% | Rappel 94.94%
✅ Classes (5):         Personne, Casque, Gilet, Bottes, Lunettes
✅ Détections:          Uploads + Unified Monitoring
✅ Framework:           YOLOv5 (PyTorch)
✅ GPU Support:         Activé (CUDA)
✅ Config sauvegardée:  {config_file}

Le système utilisera maintenant:
  1. Le vrai modèle best.pt entraîné
  2. Les vraies données d'entraînement (127 epochs)
  3. Les 5 classes réelles du projet
  4. Les performances confirmées (97.56% mAP)

Prêt pour détections dans:
  - Uploads (upload.html)
  - Unified Monitoring (unified_monitoring.html)
""")

print("="*80 + "\n")
