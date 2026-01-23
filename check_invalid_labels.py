#!/usr/bin/env python3
"""
Script pour identifier les fichiers de labels avec format invalide
"""

from pathlib import Path

def check_invalid_labels():
    """Vérifier les labels avec format invalide"""
    dataset_path = Path('dataset')
    labels_train = dataset_path / 'labels' / 'train'

    invalid_files = []

    for txt_file in labels_train.glob('*.txt'):
        with open(txt_file, 'r') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            parts = line.strip().split()
            if len(parts) < 5:
                invalid_files.append((txt_file.name, line_num, line.strip()))
                break  # Only report first error per file

    return invalid_files

def main():
    print("🔍 Recherche des fichiers de labels avec format invalide...")

    invalid_files = check_invalid_labels()

    if invalid_files:
        print(f"\n❌ {len(invalid_files)} fichiers avec format invalide:")
        for filename, line_num, content in invalid_files:
            print(f"  📄 {filename} (ligne {line_num}): '{content}'")
    else:
        print("\n✅ Aucun fichier avec format invalide trouvé")

if __name__ == "__main__":
    main()