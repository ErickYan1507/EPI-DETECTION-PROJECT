#!/usr/bin/env python3
"""
Script pour corriger les fichiers de labels corrompus
"""

from pathlib import Path

def fix_corrupted_labels():
    """Corriger les labels corrompus"""
    dataset_path = Path('dataset')
    labels_train = dataset_path / 'labels' / 'train'

    corrupted_files = [
        '13f34e2b533e12c6166f88368dcd8c07_XL_aug0_brightness.txt',
        '13f34e2b533e12c6166f88368dcd8c07_XL_aug1_contrast.txt',
        '13f34e2b533e12c6166f88368dcd8c07_XL_aug2_rotate.txt',
        '13f34e2b533e12c6166f88368dcd8c07_XL_aug3_flip_h.txt'
    ]

    for filename in corrupted_files:
        filepath = labels_train / filename
        if filepath.exists():
            print(f"🔧 Correction de {filename}")

            # Lire le fichier
            with open(filepath, 'r') as f:
                lines = f.readlines()

            # Corriger la ligne 2
            if len(lines) >= 2:
                # La ligne corrompue devrait être "2 0.647761 0.379104 0.283582 0.163433"
                lines[1] = "2 0.647761 0.379104 0.283582 0.163433\n"

            # Écrire le fichier corrigé
            with open(filepath, 'w') as f:
                f.writelines(lines)

            print(f"  ✅ Corrigé: {lines[1].strip()}")

if __name__ == "__main__":
    fix_corrupted_labels()
    print("\n🎉 Correction terminée!")