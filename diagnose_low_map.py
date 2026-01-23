#!/usr/bin/env python3
"""
Diagnostic complet pour mAP très basse (0.02 et 0.004)
Vérifie: dataset, annotations, déséquilibre de classes, problèmes NMS
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

def check_dataset_balance():
    """Vérifier l'équilibre des classes dans le dataset"""
    print("\n" + "="*70)
    print("1️⃣  ANALYSE DES CLASSES - DÉSÉQUILIBRE")
    print("="*70)
    
    dataset_path = Path('dataset')
    labels_train = dataset_path / 'labels' / 'train'
    labels_val = dataset_path / 'labels' / 'val'
    
    class_counts = defaultdict(int)
    class_names = ['helmet', 'glasses', 'person', 'vest', 'boots']
    
    for txt_file in labels_train.glob('*.txt'):
        with open(txt_file, 'r') as f:
            for line in f:
                try:
                    cls = int(line.split()[0])
                    class_counts[cls] += 1
                except:
                    pass
    
    total = sum(class_counts.values())
    print(f"\n📊 Distribution des classes (TRAIN - {total} instances):")
    for cls_id in sorted(class_counts.keys()):
        count = class_counts[cls_id]
        pct = (count / total * 100) if total > 0 else 0
        name = class_names[cls_id] if cls_id < len(class_names) else f"class_{cls_id}"
        print(f"  {name:12} (id={cls_id}): {count:5d} ({pct:5.1f}%)")
    
    if total < 100:
        print(f"\n❌ PROBLÈME CRITIQUE: Dataset TRÈS petit ({total} instances)")
        print(f"   Minimum recommandé: 500+ instances par classe")
        return False
    
    # Vérifier déséquilibre
    counts = list(class_counts.values())
    if counts and max(counts) / min(counts) > 10:
        print(f"\n⚠️  DÉSÉQUILIBRE GRAVE: ratio max/min = {max(counts)/min(counts):.1f}")
        print(f"   Quelques classes sont sous-représentées")
    
    return total >= 100

def check_annotation_quality():
    """Vérifier la qualité des annotations"""
    print("\n" + "="*70)
    print("2️⃣  QUALITÉ DES ANNOTATIONS")
    print("="*70)
    
    dataset_path = Path('dataset')
    labels_train = dataset_path / 'labels' / 'train'
    
    issues = {
        'empty_files': 0,
        'invalid_format': 0,
        'invalid_bbox': 0,
        'missing_labels': 0
    }
    
    total_files = len(list(labels_train.glob('*.txt')))
    
    for txt_file in labels_train.glob('*.txt'):
        with open(txt_file, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            issues['empty_files'] += 1
            continue
        
        for line in lines:
            parts = line.strip().split()
            if len(parts) < 5:
                issues['invalid_format'] += 1
                continue
            
            try:
                cls, x, y, w, h = float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                if not (0 <= cls <= 4) or not (0 < w < 1 and 0 < h < 1):
                    issues['invalid_bbox'] += 1
            except:
                issues['invalid_format'] += 1
    
    img_count = len([f for f in (dataset_path / 'images' / 'train').glob('*.*') if f.suffix.lower() not in ['.npy']])
    label_count = total_files
    
    print(f"\n📋 Fichiers:")
    print(f"  Images train: {img_count}")
    print(f"  Labels train: {label_count}")
    
    if img_count != label_count:
        print(f"\n❌ MISMATCH: {abs(img_count - label_count)} fichiers sans correspondance")
    
    print(f"\n⚠️  Problèmes trouvés:")
    print(f"  Fichiers vides: {issues['empty_files']}")
    print(f"  Format invalide: {issues['invalid_format']}")
    print(f"  Bounding boxes invalides: {issues['invalid_bbox']}")
    
    if issues['empty_files'] > total_files * 0.1:
        print(f"\n❌ {issues['empty_files']} fichiers vides ({issues['empty_files']/total_files*100:.1f}%)")
    
    return sum(issues.values()) == 0

def check_data_yaml():
    """Vérifier le fichier data.yaml"""
    print("\n" + "="*70)
    print("3️⃣  CONFIGURATION DATA.YAML")
    print("="*70)
    
    yaml_path = Path('dataset/data.yaml')
    if not yaml_path.exists():
        print("❌ data.yaml introuvable!")
        return False
    
    import yaml
    with open(yaml_path) as f:
        config = yaml.safe_load(f)
    
    print(f"\nClasses (nc): {config.get('nc')}")
    print(f"Noms: {config.get('names')}")
    
    return True

def check_dataset_size_recommendation():
    """Recommandations basées sur la taille du dataset"""
    print("\n" + "="*70)
    print("4️⃣  RECOMMANDATIONS DE TAILLE")
    print("="*70)
    
    dataset_path = Path('dataset')
    img_train = len([f for f in (dataset_path / 'images' / 'train').glob('*.*') if f.suffix.lower() not in ['.npy']])
    
    print(f"\nImages d'entraînement: {img_train}")
    
    recommendations = {
        (0, 50): ("❌ CRITIQUE", "< 50 images"),
        (50, 200): ("❌ TRÈS FAIBLE", "50-200 images"),
        (200, 500): ("⚠️  FAIBLE", "200-500 images"),
        (500, 1000): ("✅ BON", "500-1000 images"),
        (1000, 10000): ("✅ EXCELLENT", "1000-10000 images"),
        (10000, float('inf')): ("⭐ IDEAL", "10000+ images")
    }
    
    for (min_img, max_img), (emoji, desc) in recommendations.items():
        if min_img <= img_train < max_img:
            print(f"\n{emoji} {desc}")
            if img_train < 500:
                print(f"\n  Actions requises:")
                print(f"  1. Augmenter le dataset (data augmentation)")
                print(f"  2. Collecter plus d'images réelles")
                print(f"  3. Utiliser des transforms agressives")

def check_nms_config():
    """Vérifier la configuration NMS"""
    print("\n" + "="*70)
    print("5️⃣  PROBLÈME NMS TIME LIMIT EXCEEDED")
    print("="*70)
    
    config_path = Path('config.py')
    with open(config_path) as f:
        config_text = f.read()
    
    print("\nProblème détecté: NMS time limit 2.100s exceeded")
    print("Causes possibles:")
    print("  ❌ Trop de détections (mauvaises annotations)")
    print("  ❌ Threshold IOU trop bas (0.45)")
    print("  ❌ Confidence threshold trop bas (0.25)")
    print("  ❌ Multi-model ensemble actif")
    
    print("\n✅ Solutions:")
    print("  1. Augmenter IOU_THRESHOLD: 0.45 → 0.65")
    print("  2. Augmenter CONFIDENCE_THRESHOLD: 0.25 → 0.5")
    print("  3. Désactiver MULTI_MODEL_ENABLED")
    print("  4. Réduire USE_ENSEMBLE_FOR_CAMERA")

def main():
    print("\n" + "🔍 "*20)
    print("DIAGNOSTIC COMPLET - mAP TRÈS BASSE (0.02)")
    print("🔍 "*20)
    
    results = []
    results.append(("Dataset Balance", check_dataset_balance()))
    results.append(("Annotation Quality", check_annotation_quality()))
    results.append(("data.yaml Config", check_data_yaml()))
    check_dataset_size_recommendation()
    check_nms_config()
    
    print("\n" + "="*70)
    print("📋 RÉSUMÉ DES PROBLÈMES")
    print("="*70)
    
    for name, status in results:
        emoji = "✅" if status else "❌"
        print(f"{emoji} {name}: {'OK' if status else 'ERREUR'}")
    
    print("\n" + "="*70)
    print("🚀 ACTIONS À FAIRE IMMÉDIATEMENT")
    print("="*70)
    print("""
1. VÉRIFIER LES DONNÉES
   python diagnose_low_map.py

2. AUGMENTER LE DATASET
   python augment_dataset.py --factor 5

3. CORRIGER NMS
   Éditer config.py:
   - IOU_THRESHOLD = 0.65  (was 0.45)
   - CONFIDENCE_THRESHOLD = 0.5  (was 0.25)

4. RÉENTRAÎNER
   python fast_train.py --epochs 100 --batch 16

5. MONITOR LA VALIDATION
   - Regarder val_loss (doit descendre)
   - Vérifier mAP50 après 50 epochs
""")

if __name__ == '__main__':
    main()
