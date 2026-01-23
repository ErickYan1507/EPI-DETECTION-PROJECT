#!/usr/bin/env python3
"""
Script d'augmentation et rééquilibrage des données
Pour améliorer les résultats d'entraînement du modèle EPI
"""

import os
import shutil
import random
from pathlib import Path
from tqdm import tqdm
import cv2
import numpy as np

def oversample_underrepresented_classes():
    """
    Rééquilibrer les classes en sursamplant les classes sous-représentées
    Person est drastiquement sous-représenté (1% vs 33% pour glasses)
    """
    print("\n" + "="*70)
    print("📈 RÉÉQUILIBRAGE DES CLASSES")
    print("="*70)
    
    dataset_path = Path('dataset')
    
    # Analyser la distribution
    class_counts = [0, 0, 0, 0, 0]  # 5 classes
    class_to_files = [[], [], [], [], []]
    
    labels_train = dataset_path / 'labels' / 'train'
    
    # Mapper chaque image à ses classes
    image_to_classes = {}
    
    for txt_file in labels_train.glob('*.txt'):
        with open(txt_file, 'r') as f:
            classes_in_file = []
            for line in f:
                try:
                    cls = int(line.split()[0])
                    if 0 <= cls < 5:
                        classes_in_file.append(cls)
                        class_counts[cls] += 1
                except:
                    pass
        
        image_to_classes[txt_file.stem] = list(set(classes_in_file))
    
    print("\n📊 Distribution actuelle:")
    for cls_id, count in enumerate(class_counts):
        class_names = ['helmet', 'vest', 'glasses', 'boots', 'person']
        print(f"  {class_names[cls_id]:10}: {count:5d}")
    
    # Identifier classe minoritaire
    min_class = min(range(5), key=lambda i: class_counts[i])
    max_class = max(range(5), key=lambda i: class_counts[i])
    class_names = ['helmet', 'vest', 'glasses', 'boots', 'person']
    
    print(f"\n⚠️  Classe minoritaire: {class_names[min_class]} ({class_counts[min_class]})")
    print(f"    Classe majoritaire: {class_names[max_class]} ({class_counts[max_class]})")
    
    # Seulement si déséquilibre extrême
    ratio = class_counts[max_class] / max(class_counts[min_class], 1)
    print(f"    Ratio: {ratio:.1f}x")
    
    if ratio < 10:
        print(f"\n✅ Déséquilibre acceptable, pas besoin de réechantillonnage agressif")
        return
    
    # Copier les images de la classe minoritaire pour équilibrer
    images_train = dataset_path / 'images' / 'train'
    labels_train = dataset_path / 'labels' / 'train'
    
    target_count = int(class_counts[max_class] * 0.5)  # Viser 50% de la classe max
    multiply_factor = max(1, (target_count - class_counts[min_class]) // class_counts[min_class])
    
    if multiply_factor > 0:
        print(f"\n🔄 Sursampling {class_names[min_class]}: ×{multiply_factor + 1}")
        
        # Trouver toutes les images avec la classe minoritaire
        files_with_min_class = []
        for stem, classes in image_to_classes.items():
            if min_class in classes:
                files_with_min_class.append(stem)
        
        print(f"   {len(files_with_min_class)} images contiennent {class_names[min_class]}")
        
        # Dupliquer les images
        for idx in range(multiply_factor):
            for stem in tqdm(files_with_min_class, desc=f"  Iteration {idx+1}/{multiply_factor}"):
                # Image source
                for img_ext in ['.jpg', '.png', '.jpeg', '.bmp']:
                    img_src = images_train / f"{stem}{img_ext}"
                    if img_src.exists():
                        # Nouveau nom
                        new_stem = f"{stem}_dup_{idx}"
                        img_dst = images_train / f"{new_stem}{img_ext}"
                        
                        # Copier image
                        shutil.copy(img_src, img_dst)
                        
                        # Copier label
                        lbl_src = labels_train / f"{stem}.txt"
                        lbl_dst = labels_train / f"{new_stem}.txt"
                        shutil.copy(lbl_src, lbl_dst)
                        break

def augment_on_disk():
    """
    Augmentation simple d'images (flip, rotation)
    Utile pour augmenter le dataset
    """
    print("\n" + "="*70)
    print("📸 AUGMENTATION DES IMAGES (OPTIONNEL)")
    print("="*70)
    
    print("\n⚠️  Cette étape est OPTIONNELLE")
    print("   YOLOv5 fait déjà l'augmentation pendant l'entraînement")
    print("   Utiliser seulement si dataset trop petit (< 500 images)")
    
    response = input("\nAugmenter les images? (y/n): ").lower()
    if response != 'y':
        return
    
    print("\nAugmentation par flip horizontal et vertical...")
    
    dataset_path = Path('dataset')
    images_train = dataset_path / 'images' / 'train'
    labels_train = dataset_path / 'labels' / 'train'
    
    augmented = 0
    
    for img_path in tqdm(list(images_train.glob('*.*')), desc="Augmentation"):
        if img_path.suffix.lower() not in ['.jpg', '.png', '.jpeg', '.bmp']:
            continue
        
        try:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            # Flip horizontal
            img_flip_h = cv2.flip(img, 1)
            stem = img_path.stem
            ext = img_path.suffix
            
            # Sauvegarder image flippée
            new_img_path = images_train / f"{stem}_fliph{ext}"
            cv2.imwrite(str(new_img_path), img_flip_h)
            
            # Copier label identique (flip H ne change pas les bbox YOLO)
            lbl_src = labels_train / f"{stem}.txt"
            lbl_dst = labels_train / f"{stem}_fliph.txt"
            if lbl_src.exists():
                shutil.copy(lbl_src, lbl_dst)
            
            augmented += 1
        except:
            pass
    
    print(f"\n✅ {augmented} images augmentées par flip")

def final_stats():
    """Afficher les stats finales du dataset"""
    print("\n" + "="*70)
    print("📊 STATS FINALES DU DATASET")
    print("="*70)
    
    from collections import defaultdict
    
    dataset_path = Path('dataset')
    class_names = ['helmet', 'vest', 'glasses', 'boots', 'person']
    
    for split in ['train', 'val']:
        print(f"\n{split.upper()}:")
        
        images_count = len(list((dataset_path / 'images' / split).glob('*.*')))
        labels_dir = dataset_path / 'labels' / split
        
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
        print(f"  Avg/image: {total_boxes/max(1, images_count):.2f}")
        
        for cls_id in range(5):
            count = class_counts[cls_id]
            pct = (count / total_boxes * 100) if total_boxes > 0 else 0
            bar = "█" * int(pct / 2)
            print(f"    {class_names[cls_id]:10}: {count:5d} ({pct:5.1f}%) {bar}")

def main():
    print("\n" + "📈 "*20)
    print("AUGMENTATION ET RÉÉQUILIBRAGE DU DATASET")
    print("📈 "*20)
    
    oversample_underrepresented_classes()
    # augment_on_disk()  # Optionnel
    final_stats()
    
    print("\n" + "="*70)
    print("✅ AUGMENTATION TERMINÉE")
    print("="*70)
    print(f"\nProchaine étape:")
    print(f"  python train_optimized_fixed.py")

if __name__ == '__main__':
    main()
