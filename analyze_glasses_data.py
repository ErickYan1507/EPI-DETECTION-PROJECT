#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyser la distribution des classes dans les données d'entraînement"""

import os
from pathlib import Path

def count_class_instances(label_dir):
    if not label_dir.exists():
        print(f"❌ Dossier {label_dir} n'existe pas")
        return {}

    counts = {'helmet': 0, 'glasses': 0, 'person': 0, 'vest': 0, 'boots': 0}
    label_files = list(label_dir.glob('*.txt'))
    print(f'  📁 {len(label_files)} fichiers labels trouvés')

    total_annotations = 0
    for label_file in label_files:
        try:
            with open(label_file, 'r') as f:
                content = f.read().strip()
                if content:
                    lines = content.split('\n')
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            class_names = ['helmet', 'glasses', 'person', 'vest', 'boots']
                            if 0 <= class_id < len(class_names):
                                counts[class_names[class_id]] += 1
                                total_annotations += 1
        except Exception as e:
            print(f'    ⚠️ Erreur lecture {label_file.name}: {e}')

    print(f'  📊 {total_annotations} annotations totales')
    return counts

def main():
    print('🔍 ANALYSE DE LA DISTRIBUTION DES CLASSES')
    print('=' * 50)

    # Chemins des données
    dataset_dir = Path('dataset')
    train_labels = dataset_dir / 'labels' / 'train'
    val_labels = dataset_dir / 'labels' / 'val'

    print(f'\\n📂 TRAIN: {train_labels}')
    train_counts = count_class_instances(train_labels)

    print(f'\\n📂 VAL: {val_labels}')
    val_counts = count_class_instances(val_labels)

    print('\\n📊 RÉSUMÉ:')
    print('Classe      | Train    | Val      | Total')
    print('------------|----------|----------|----------')

    total_train = 0
    total_val = 0
    for cls in ['helmet', 'glasses', 'person', 'vest', 'boots']:
        t_count = train_counts.get(cls, 0)
        v_count = val_counts.get(cls, 0)
        total = t_count + v_count
        total_train += t_count
        total_val += v_count
        print(f'{cls:11} | {t_count:8} | {v_count:8} | {total:8}')

    print('------------|----------|----------|----------')
    print(f'{"TOTAL":11} | {total_train:8} | {total_val:8} | {total_train + total_val:8}')

    # Analyse des lunettes spécifiquement
    glasses_train = train_counts.get('glasses', 0)
    glasses_val = val_counts.get('glasses', 0)
    glasses_total = glasses_train + glasses_val

    print(f'\\n🔍 ANALYSE DES LUNETTES:')
    print(f'  • Train: {glasses_train} instances')
    print(f'  • Val: {glasses_val} instances')
    print(f'  • Total: {glasses_total} instances')

    if glasses_total == 0:
        print('  ❌ AUCUNE DONNÉE DE LUNETTES TROUVÉE!')
        print('  💡 Cause possible: Pas d\'annotations de lunettes dans le dataset')
    elif glasses_total < 100:
        print('  ⚠️ PEU DE DONNÉES DE LUNETTES!')
        print(f'  💡 Seulement {glasses_total} instances - insuffisant pour un entraînement fiable')
    else:
        print('  ✅ Données suffisantes pour les lunettes')

if __name__ == '__main__':
    main()