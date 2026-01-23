#!/usr/bin/env python3
"""
Restructurer complètement le dataset:
1. Nettoyer images/train (supprimer .npy et orphelines)
2. Aplatir la structure si nécessaire
3. Synchroniser avec les labels
"""

import os
import shutil
from pathlib import Path
from tqdm import tqdm
import random

def flatten_and_clean_images():
    """Aplatir et nettoyer la structure des images"""
    print("\n" + "="*70)
    print("🧹 NETTOYAGE DES IMAGES")
    print("="*70)
    
    dataset_path = Path('dataset')
    
    for split in ['train', 'val']:
        images_dir = dataset_path / 'images' / split
        labels_dir = dataset_path / 'labels' / split
        
        print(f"\n▶️  Nettoyage {split}:")
        
        # Récupérer les noms de labels valides
        valid_stems = set(f.stem for f in labels_dir.glob('*.txt'))
        print(f"  Labels trouvés: {len(valid_stems)}")
        
        # Supprimer les fichiers non-image et orphelines
        removed_files = 0
        for file_path in tqdm(list(images_dir.glob('*')), desc=f"  Nettoyage"):
            # Ignorer les dossiers
            if file_path.is_dir():
                continue
            
            # Supprimer les .npy et autres fichiers
            if file_path.suffix.lower() in ['.npy', '.pyc', '.pth']:
                file_path.unlink()
                removed_files += 1
                continue
            
            # Supprimer si pas de label correspondant
            if file_path.stem not in valid_stems:
                file_path.unlink()
                removed_files += 1
        
        print(f"  ✅ {removed_files} fichiers supprimés")
        
        # Vérifier le résultat
        final_images = len([f for f in images_dir.glob('*') if f.is_file() and f.suffix.lower() in ['.jpg', '.png', '.jpeg', '.bmp']])
        final_labels = len(list(labels_dir.glob('*.txt')))
        
        print(f"  ✅ Résultat: {final_images} images, {final_labels} labels")

def remove_bad_labels():
    """Supprimer les labels sans contenu valide"""
    print("\n" + "="*70)
    print("🔍 SUPPRESSION DES LABELS INVALIDES")
    print("="*70)
    
    dataset_path = Path('dataset')
    
    for split in ['train', 'val']:
        labels_dir = dataset_path / 'labels' / split
        images_dir = dataset_path / 'images' / split
        
        print(f"\n▶️  {split}:")
        
        removed = 0
        for txt_file in tqdm(list(labels_dir.glob('*.txt')), desc=f"  Vérification"):
            # Vérifier si le fichier est vide
            if txt_file.stat().st_size == 0:
                # Supprimer l'image correspondante
                for img in images_dir.glob(f"{txt_file.stem}.*"):
                    if img.is_file():
                        img.unlink()
                txt_file.unlink()
                removed += 1
                continue
            
            # Vérifier le contenu
            try:
                with open(txt_file, 'r') as f:
                    lines = f.readlines()
                
                valid_lines = []
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    
                    try:
                        cls = int(parts[0])
                        if 0 <= cls <= 4:  # Seulement 5 classes valides
                            valid_lines.append(line)
                    except:
                        pass
                
                # Si aucune ligne valide, supprimer
                if not valid_lines:
                    for img in images_dir.glob(f"{txt_file.stem}.*"):
                        if img.is_file():
                            img.unlink()
                    txt_file.unlink()
                    removed += 1
                elif len(valid_lines) != len(lines):
                    with open(txt_file, 'w') as f:
                        f.writelines(valid_lines)
            except:
                # Fichier corrompu, supprimer
                for img in images_dir.glob(f"{txt_file.stem}.*"):
                    if img.is_file():
                        img.unlink()
                txt_file.unlink()
                removed += 1
        
        print(f"  ✅ {removed} labels invalides/vides supprimés")

def final_sync():
    """Synchronisation finale stricte"""
    print("\n" + "="*70)
    print("🔄 SYNCHRONISATION FINALE")
    print("="*70)
    
    dataset_path = Path('dataset')
    
    for split in ['train', 'val']:
        images_dir = dataset_path / 'images' / split
        labels_dir = dataset_path / 'labels' / split
        
        image_stems = set(f.stem for f in images_dir.glob('*.*'))
        label_stems = set(f.stem for f in labels_dir.glob('*.txt'))
        
        # Supprimer images sans labels
        for stem in list(image_stems - label_stems):
            for f in images_dir.glob(f"{stem}.*"):
                f.unlink()
        
        # Supprimer labels sans images
        for stem in list(label_stems - image_stems):
            (labels_dir / f"{stem}.txt").unlink()
        
        final_count = len(list(images_dir.glob('*.*')))
        print(f"\n{split.upper()}: {final_count} images/labels synchronisés")

def analyze_final_stats():
    """Analyser les stats finales"""
    print("\n" + "="*70)
    print("📊 STATS FINALES")
    print("="*70)
    
    dataset_path = Path('dataset')
    class_names = ['helmet', 'vest', 'glasses', 'boots', 'person']
    
    for split in ['train', 'val']:
        print(f"\n{split.upper()}:")
        
        images_count = len(list((dataset_path / 'images' / split).glob('*.*')))
        labels_dir = dataset_path / 'labels' / split
        
        from collections import defaultdict
        class_counts = defaultdict(int)
        total_boxes = 0
        
        for txt_file in labels_dir.glob('*.txt'):
            with open(txt_file, 'r') as f:
                for line in f:
                    try:
                        cls = int(line.split()[0])
                        if cls < 5:
                            class_counts[cls] += 1
                            total_boxes += 1
                    except:
                        pass
        
        print(f"  Images: {images_count}")
        print(f"  Total boxes: {total_boxes}")
        print(f"  Avg boxes/image: {total_boxes/max(1, images_count):.2f}")
        
        for cls_id in range(5):
            count = class_counts[cls_id]
            pct = (count / total_boxes * 100) if total_boxes > 0 else 0
            print(f"    {class_names[cls_id]:10}: {count:5d} ({pct:5.1f}%)")

def main():
    print("\n" + "🔧 "*20)
    print("RESTRUCTURATION COMPLÈTE DU DATASET")
    print("🔧 "*20)
    
    flatten_and_clean_images()
    remove_bad_labels()
    final_sync()
    analyze_final_stats()
    
    print("\n" + "="*70)
    print("✅ RESTRUCTURATION TERMINÉE!")
    print("="*70)

if __name__ == '__main__':
    main()
