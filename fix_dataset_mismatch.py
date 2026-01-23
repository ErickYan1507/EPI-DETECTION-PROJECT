#!/usr/bin/env python3
"""
Script pour corriger le problème de mismatch entre images et labels
"""

import os
from pathlib import Path
from collections import defaultdict

def find_unmatched_files():
    """Trouver les images sans labels correspondants"""
    dataset_path = Path('dataset')
    images_dir = dataset_path / 'images' / 'train'
    labels_dir = dataset_path / 'labels' / 'train'

    # Obtenir tous les noms de fichiers images (sans extension)
    image_stems = set()
    for img_file in images_dir.glob('*'):
        if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            image_stems.add(img_file.stem)

    # Obtenir tous les noms de fichiers labels (sans extension)
    label_stems = set()
    for label_file in labels_dir.glob('*.txt'):
        label_stems.add(label_file.stem)

    # Trouver les images sans labels
    images_without_labels = image_stems - label_stems
    # Trouver les labels sans images
    labels_without_images = label_stems - image_stems

    return images_without_labels, labels_without_images

def main():
    print("🔍 Analyse des fichiers non correspondants...")

    images_without_labels, labels_without_images = find_unmatched_files()

    print(f"\n📊 Résultats:")
    print(f"  Images sans labels: {len(images_without_labels)}")
    print(f"  Labels sans images: {len(labels_without_images)}")

    if images_without_labels:
        print(f"\n❌ Images sans labels (à supprimer ou annoter):")
        for img in sorted(list(images_without_labels)[:10]):  # Montrer seulement les 10 premiers
            print(f"    {img}")
        if len(images_without_labels) > 10:
            print(f"    ... et {len(images_without_labels) - 10} autres")

    if labels_without_images:
        print(f"\n⚠️  Labels sans images (à supprimer):")
        for label in sorted(list(labels_without_images)[:10]):
            print(f"    {label}")
        if len(labels_without_images) > 10:
            print(f"    ... et {len(labels_without_images) - 10} autres")

    print(f"\n💡 Solutions recommandées:")
    print(f"1. Supprimer les {len(images_without_labels)} images sans labels")
    print(f"2. Supprimer les {len(labels_without_images)} labels orphelins")
    print(f"3. Ou annoter les images manquantes si elles contiennent des objets EPI")

if __name__ == "__main__":
    main()