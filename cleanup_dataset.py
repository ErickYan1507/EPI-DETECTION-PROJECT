#!/usr/bin/env python3
"""
Nettoyer et réparer le dataset:
1. Supprimer les images sans labels
2. Supprimer les bounding boxes invalides
3. Rééquilibrer les classes
"""

import os
from pathlib import Path
from tqdm import tqdm
import shutil

def remove_orphan_images():
    """Supprimer les images qui n'ont pas de labels"""
    print("\n" + "="*70)
    print("1️⃣  SUPPRESSION DES IMAGES ORPHELINES (sans labels)")
    print("="*70)
    
    dataset_path = Path('dataset')
    images_train = list((dataset_path / 'images' / 'train').glob('*.*'))
    labels_train = set(f.stem for f in (dataset_path / 'labels' / 'train').glob('*.txt'))
    
    removed = 0
    for img_path in tqdm(images_train, desc="Vérification"):
        if img_path.stem not in labels_train:
            img_path.unlink()
            removed += 1
    
    print(f"\n✅ {removed} images orphelines supprimées")
    return removed

def remove_invalid_bboxes():
    """Supprimer les bounding boxes invalides"""
    print("\n" + "="*70)
    print("2️⃣  SUPPRESSION DES BOUNDING BOXES INVALIDES")
    print("="*70)
    
    dataset_path = Path('dataset')
    labels_train = dataset_path / 'labels' / 'train'
    
    total_removed = 0
    files_modified = 0
    
    for txt_file in tqdm(list(labels_train.glob('*.txt')), desc="Nettoyage"):
        with open(txt_file, 'r') as f:
            lines = f.readlines()
        
        valid_lines = []
        for line in lines:
            try:
                parts = line.strip().split()
                if len(parts) < 5:
                    total_removed += 1
                    continue
                
                cls, x, y, w, h = int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                
                # Vérifier validité
                if cls >= 5:  # class_5 est probablement une erreur
                    total_removed += 1
                    continue
                
                if not (0 <= cls <= 4):
                    total_removed += 1
                    continue
                
                if not (0 < w <= 1 and 0 < h <= 1):
                    total_removed += 1
                    continue
                
                if not (0 <= x <= 1 and 0 <= y <= 1):
                    total_removed += 1
                    continue
                
                valid_lines.append(line)
            except Exception as e:
                total_removed += 1
                continue
        
        if len(valid_lines) != len(lines):
            with open(txt_file, 'w') as f:
                f.writelines(valid_lines)
            files_modified += 1
    
    print(f"\n✅ {total_removed} bounding boxes invalides supprimés")
    print(f"✅ {files_modified} fichiers modifiés")

def remove_empty_label_files():
    """Supprimer les fichiers labels vides et leurs images correspondantes"""
    print("\n" + "="*70)
    print("3️⃣  SUPPRESSION DES FICHIERS LABELS VIDES")
    print("="*70)
    
    dataset_path = Path('dataset')
    labels_train = dataset_path / 'labels' / 'train'
    images_train = dataset_path / 'images' / 'train'
    
    removed_labels = 0
    removed_images = 0
    
    for txt_file in tqdm(list(labels_train.glob('*.txt')), desc="Vérification"):
        if txt_file.stat().st_size == 0:
            # Supprimer l'image correspondante
            stem = txt_file.stem
            for img in images_train.glob(f"{stem}.*"):
                img.unlink()
                removed_images += 1
            
            txt_file.unlink()
            removed_labels += 1
    
    print(f"\n✅ {removed_labels} labels vides supprimés")
    print(f"✅ {removed_images} images correspondantes supprimées")

def fix_data_yaml():
    """Corriger le data.yaml pour n'avoir que 5 classes"""
    print("\n" + "="*70)
    print("4️⃣  CORRECTION DATA.YAML")
    print("="*70)
    
    import yaml
    
    yaml_path = Path('dataset/data.yaml')
    with open(yaml_path) as f:
        config = yaml.safe_load(f)
    
    config['nc'] = 5
    config['names'] = ['helmet', 'vest', 'glasses', 'boots', 'person']
    
    with open(yaml_path, 'w') as f:
        yaml.dump(config, f)
    
    print(f"\n✅ data.yaml corrigé: 5 classes seulement")

def verify_cleanup():
    """Vérifier l'état final du dataset"""
    print("\n" + "="*70)
    print("5️⃣  VÉRIFICATION FINALE")
    print("="*70)
    
    dataset_path = Path('dataset')
    
    img_count = len(list((dataset_path / 'images' / 'train').glob('*.*')))
    lbl_count = len(list((dataset_path / 'labels' / 'train').glob('*.txt')))
    
    print(f"\n📊 Statistiques finales:")
    print(f"  Images train: {img_count}")
    print(f"  Labels train: {lbl_count}")
    print(f"  Mismatch: {abs(img_count - lbl_count)}")
    
    if img_count == lbl_count:
        print(f"\n✅ Dataset PROPRE et COHÉRENT!")
    else:
        print(f"\n⚠️  Encore {abs(img_count - lbl_count)} fichiers non alignés")

def main():
    print("\n" + "🧹 "*20)
    print("NETTOYAGE ET RÉPARATION DU DATASET")
    print("🧹 "*20)
    
    remove_orphan_images()
    remove_invalid_bboxes()
    remove_empty_label_files()
    fix_data_yaml()
    verify_cleanup()
    
    print("\n" + "="*70)
    print("✅ NETTOYAGE TERMINÉ!")
    print("="*70)
    print("\nProchaines étapes:")
    print("1. Rééquilibrer les classes (oversampling)")
    print("2. Augmenter les données")
    print("3. Réentraîner le modèle")

if __name__ == '__main__':
    main()
