"""
Script d'augmentation équilibrée pour équilibrer les classes sans ajouter d'images externes
Applique plus d'augmentations aux classes sous-représentées
"""

import cv2
import numpy as np
import os
from pathlib import Path
from collections import defaultdict
import shutil
from datetime import datetime

DATASET_PATH = 'dataset'
TRAIN_IMAGES = os.path.join(DATASET_PATH, 'images', 'train')
TRAIN_LABELS = os.path.join(DATASET_PATH, 'labels', 'train')

CLASS_NAMES = ['helmet', 'vest', 'glasses', 'boots', 'person']

def analyze_class_distribution(labels_dir):
    """Analyse la distribution des classes dans les labels"""
    class_counts = defaultdict(int)
    image_class_map = {}  # image -> classes présentes

    for label_file in os.listdir(labels_dir):
        if label_file.endswith('.txt'):
            img_name = label_file.replace('.txt', '')
            classes_in_image = set()

            with open(os.path.join(labels_dir, label_file), 'r') as f:
                for line in f:
                    if line.strip():
                        class_id = int(line.split()[0])
                        class_counts[class_id] += 1
                        classes_in_image.add(class_id)

            image_class_map[img_name] = classes_in_image

    return class_counts, image_class_map

def calculate_augmentation_factors(class_counts, target_balance_ratio=0.9):
    """
    Calcule le facteur d'augmentation pour chaque classe
    target_balance_ratio: ratio minimum par rapport à la classe majoritaire
    """
    max_count = max(class_counts.values())
    min_target = int(max_count * target_balance_ratio)

    factors = {}
    for class_id, count in class_counts.items():
        if count >= min_target:
            factors[class_id] = 1  # Pas d'augmentation pour les classes équilibrées
        else:
            # Calculer le déficit et le facteur nécessaire
            deficit = min_target - count
            # Chaque image peut générer plusieurs augmentations
            # Facteur plus agressif pour les classes très sous-représentées
            if count < max_count * 0.5:  # Si moins de 50% du maximum
                factors[class_id] = max(3, deficit // (count * 2))  # Plus d'augmentations
            else:
                factors[class_id] = max(2, deficit // (count * 3))  # Augmentations modérées

    return factors, max_count, min_target

def augment_image_brightness(image, factor=0.3):
    """Ajuste la luminosité de l'image"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = hsv[:, :, 2] * (1 + np.random.uniform(-factor, factor))
    hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def augment_image_contrast(image, factor=0.3):
    """Ajuste le contraste de l'image"""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[:, :, 0] = lab[:, :, 0] * (1 + np.random.uniform(-factor, factor))
    lab[:, :, 0] = np.clip(lab[:, :, 0], 0, 255)
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

def augment_image_rotate(image, angle_range=20):
    """Rotation de l'image"""
    h, w = image.shape[:2]
    angle = np.random.uniform(-angle_range, angle_range)
    matrix = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
    return cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_REFLECT)

def augment_image_flip(image, flip_type='h'):
    """Flip horizontal ou vertical"""
    if flip_type == 'h':
        return cv2.flip(image, 1)
    else:
        return cv2.flip(image, 0)

def augment_image_noise(image, noise_level=0.03):
    """Ajoute du bruit Gaussien"""
    noise = np.random.normal(0, 255 * noise_level, image.shape)
    noisy = image.astype(np.float32) + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)

def augment_image_blur(image, kernel_size=5):
    """Ajoute du flou"""
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

def augment_image_saturation(image, factor=0.3):
    """Ajuste la saturation"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = hsv[:, :, 1] * (1 + np.random.uniform(-factor, factor))
    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def augment_balanced_dataset(source_images, source_labels, augmentation_factors):
    """
    Augmente le dataset de manière équilibrée selon les facteurs calculés
    """
    augmentation_count = 0
    total_new_instances = defaultdict(int)

    image_files = [f for f in os.listdir(source_images) if f.endswith(('.jpg', '.jpeg', '.png'))]
    total_images = len(image_files)

    print(f"Augmentation équilibrée de {total_images} images...")

    # Définir les types d'augmentation disponibles
    augmentations = [
        ('brightness', augment_image_brightness, {}),
        ('contrast', augment_image_contrast, {}),
        ('rotate', augment_image_rotate, {}),
        ('flip_h', lambda img: augment_image_flip(img, 'h'), {}),
        ('noise', augment_image_noise, {}),
        ('blur', augment_image_blur, {}),
        ('saturation', augment_image_saturation, {}),
    ]

    for idx, img_file in enumerate(image_files, 1):
        img_path = os.path.join(source_images, img_file)
        label_file = img_file.rsplit('.', 1)[0] + '.txt'
        label_path = os.path.join(source_labels, label_file)

        # Lire l'image originale
        image = cv2.imread(img_path)
        if image is None:
            print(f"  SKIP: Cannot read {img_file}")
            continue

        # Lire les labels
        if not os.path.exists(label_path):
            print(f"  WARN: No label for {img_file}")
            continue

        with open(label_path, 'r') as f:
            labels = f.read().strip()

        # Déterminer les classes présentes dans cette image
        classes_in_image = set()
        for line in labels.split('\n'):
            if line.strip():
                class_id = int(line.split()[0])
                classes_in_image.add(class_id)

        # Calculer le nombre d'augmentations pour cette image
        # Basé sur la classe qui nécessite le plus d'augmentations
        max_factor = max(augmentation_factors.get(cls, 1) for cls in classes_in_image)
        num_augmentations = max_factor

        if num_augmentations <= 1:
            continue  # Pas besoin d'augmenter cette image

        # Générer les augmentations
        for aug_idx in range(num_augmentations):
            aug_type, aug_func, kwargs = augmentations[aug_idx % len(augmentations)]

            try:
                aug_image = aug_func(image, **kwargs)

                # Générer un nouveau nom de fichier
                base_name = img_file.rsplit('.', 1)[0]
                ext = img_file.rsplit('.', 1)[1]
                new_img_name = f"{base_name}_bal{idx}_{aug_idx}_{aug_type}.{ext}"
                new_label_name = f"{base_name}_bal{idx}_{aug_idx}_{aug_type}.txt"

                new_img_path = os.path.join(source_images, new_img_name)
                new_label_path = os.path.join(source_labels, new_label_name)

                # Sauvegarder
                cv2.imwrite(new_img_path, aug_image)
                with open(new_label_path, 'w') as f:
                    f.write(labels)

                # Compter les nouvelles instances par classe
                for cls in classes_in_image:
                    total_new_instances[cls] += 1

                augmentation_count += 1

            except Exception as e:
                print(f"  ERR {aug_type} on {img_file}: {str(e)}")

        if idx % 50 == 0:
            print(f"  Progress: {idx}/{total_images} images processed...")

    return augmentation_count, total_new_instances

def main():
    print("=" * 70)
    print("AUGMENTATION ÉQUILIBRÉE DU DATASET")
    print("=" * 70)

    # Vérifier que les répertoires existent
    if not os.path.exists(TRAIN_IMAGES) or not os.path.exists(TRAIN_LABELS):
        print("ERR: Répertoires train introuvables")
        return

    # Analyser la distribution actuelle
    print("\n1. Analyse de la distribution des classes...")
    class_counts, image_class_map = analyze_class_distribution(TRAIN_LABELS)

    print("Distribution actuelle:")
    for i, name in enumerate(CLASS_NAMES):
        count = class_counts.get(i, 0)
        print(f"  {name} (id={i}): {count} instances")

    # Calculer les facteurs d'augmentation
    print("\n2. Calcul des facteurs d'équilibrage...")
    augmentation_factors, max_count, target_count = calculate_augmentation_factors(class_counts)

    print("Facteurs d'augmentation calculés:")
    for i, name in enumerate(CLASS_NAMES):
        factor = augmentation_factors.get(i, 1)
        current = class_counts.get(i, 0)
        target = current * factor if factor > 1 else current
        print(f"  {name}: {current} → {target} (facteur: {factor}x)")

    # Appliquer l'augmentation équilibrée
    print("\n3. Application de l'augmentation équilibrée...")
    aug_count, new_instances = augment_balanced_dataset(TRAIN_IMAGES, TRAIN_LABELS, augmentation_factors)

    # Résumé final
    print("\n" + "=" * 70)
    print("AUGMENTATION ÉQUILIBRÉE TERMINÉE!")
    print(f"  Images augmentées générées: {aug_count}")
    print("  Nouvelles instances par classe:")
    for i, name in enumerate(CLASS_NAMES):
        added = new_instances.get(i, 0)
        if added > 0:
            print(f"    {name}: +{added} instances")

    # Distribution finale
    final_counts, _ = analyze_class_distribution(TRAIN_LABELS)
    print("\nDistribution finale:")
    for i, name in enumerate(CLASS_NAMES):
        count = final_counts.get(i, 0)
        print(f"  {name}: {count} instances")

    total_images = len([f for f in os.listdir(TRAIN_IMAGES) if f.endswith(('.jpg', '.jpeg', '.png'))])
    print(f"\nTotal images d'entraînement: {total_images}")
    print("=" * 70)

if __name__ == "__main__":
    main()