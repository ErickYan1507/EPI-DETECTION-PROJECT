#!/usr/bin/env python3
"""
Synchroniser parfaitement images et labels
"""

import os
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict

def sync_images_and_labels():
    """Synchroniser strictement images et labels"""
    print("\n" + "="*70)
    print("🔄 SYNCHRONISATION STRICTE IMAGES/LABELS")
    print("="*70)
    
    dataset_path = Path('dataset')
    for split in ['train', 'val']:
        images_dir = dataset_path / 'images' / split
        labels_dir = dataset_path / 'labels' / split
        
        print(f"\n▶️  Traitement split: {split}")
        
        # Récupérer les noms de fichiers
        image_stems = set(f.stem for f in images_dir.glob('*.*'))
        label_stems = set(f.stem for f in labels_dir.glob('*.txt'))
        
        # Images sans labels
        orphan_images = image_stems - label_stems
        # Labels sans images
        orphan_labels = label_stems - image_stems
        
        print(f"  Images: {len(image_stems)}, Labels: {len(label_stems)}")
        print(f"  Images orphelines: {len(orphan_images)}")
        print(f"  Labels orphelines: {len(orphan_labels)}")
        
        # Supprimer les images orphelines
        for stem in tqdm(orphan_images, desc=f"Suppression images {split}"):
            for img in images_dir.glob(f"{stem}.*"):
                img.unlink()
        
        # Supprimer les labels orphelines
        for stem in tqdm(orphan_labels, desc=f"Suppression labels {split}"):
            label_file = labels_dir / f"{stem}.txt"
            label_file.unlink()
        
        # Vérifier le résultat
        final_images = len(list(images_dir.glob('*.*')))
        final_labels = len(list(labels_dir.glob('*.txt')))
        
        print(f"  ✅ Résultat: {final_images} images, {final_labels} labels")
        
        if final_images == final_labels:
            print(f"  ✅ {split.upper()} SYNCHRONIZED!")
        else:
            print(f"  ⚠️  Mismatch: {abs(final_images - final_labels)}")

def analyze_class_distribution():
    """Analyser la distribution des classes"""
    print("\n" + "="*70)
    print("📊 DISTRIBUTION DES CLASSES (APRÈS NETTOYAGE)")
    print("="*70)
    
    dataset_path = Path('dataset')
    class_names = ['helmet', 'vest', 'glasses', 'boots', 'person']
    
    for split in ['train', 'val']:
        class_counts = defaultdict(int)
        labels_dir = dataset_path / 'labels' / split
        
        for txt_file in labels_dir.glob('*.txt'):
            with open(txt_file, 'r') as f:
                for line in f:
                    try:
                        cls = int(line.split()[0])
                        if cls < 5:  # Vérifier cls valide
                            class_counts[cls] += 1
                    except:
                        pass
        
        total = sum(class_counts.values())
        print(f"\n{split.upper()} ({total} instances):")
        
        for cls_id in range(5):
            count = class_counts.get(cls_id, 0)
            pct = (count / total * 100) if total > 0 else 0
            bar = "█" * int(pct / 2)
            print(f"  {class_names[cls_id]:10} {count:5d} ({pct:5.1f}%) {bar}")

def main():
    print("\n" + "🔄 "*20)
    print("SYNCHRONISATION STRICTE DU DATASET")
    print("🔄 "*20)
    
    sync_images_and_labels()
    analyze_class_distribution()
    
    print("\n" + "="*70)
    print("✅ SYNCHRONISATION TERMINÉE")
    print("="*70)

if __name__ == '__main__':
    main()
