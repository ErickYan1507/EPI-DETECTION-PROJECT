"""
Script d'augmentation de donnees pour augmenter la diversite du dataset
Genere des variations des images existantes sans perdre les annotations
"""

import cv2
import numpy as np
import os
from pathlib import Path
import shutil
from datetime import datetime

DATASET_PATH = 'dataset'
TRAIN_IMAGES = os.path.join(DATASET_PATH, 'images', 'train')
TRAIN_LABELS = os.path.join(DATASET_PATH, 'labels', 'train')
TEST_IMAGES = os.path.join(DATASET_PATH, 'images', 'test')
TEST_LABELS = os.path.join(DATASET_PATH, 'labels', 'test')

def augment_image_brightness(image, factor=0.2):
    """Ajuste la luminosite de l'image"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = hsv[:, :, 2] * (1 + np.random.uniform(-factor, factor))
    hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def augment_image_contrast(image, factor=0.2):
    """Ajuste le contraste de l'image"""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[:, :, 0] = lab[:, :, 0] * (1 + np.random.uniform(-factor, factor))
    lab[:, :, 0] = np.clip(lab[:, :, 0], 0, 255)
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

def augment_image_rotate(image, angle_range=15):
    """Rotation legere de l'image"""
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

def augment_image_noise(image, noise_level=0.02):
    """Ajoute du bruit Gaussien"""
    noise = np.random.normal(0, 255 * noise_level, image.shape)
    noisy = image.astype(np.float32) + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)

def augment_image_blur(image, kernel_size=3):
    """Ajoute du flou leger"""
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

def augment_dataset(source_images, source_labels, num_augmentations=4):
    """
    Augmente le dataset en creant plusieurs versions de chaque image
    """
    augmentation_count = 0
    
    image_files = [f for f in os.listdir(source_images) if f.endswith(('.jpg', '.jpeg', '.png'))]
    total_images = len(image_files)
    
    print("Augmentation de {} images avec {} variations chacune...".format(total_images, num_augmentations))
    
    for idx, img_file in enumerate(image_files, 1):
        img_path = os.path.join(source_images, img_file)
        label_file = img_file.rsplit('.', 1)[0] + '.txt'
        label_path = os.path.join(source_labels, label_file)
        
        # Lire l'image originale
        image = cv2.imread(img_path)
        if image is None:
            print("  SKIP: Cannot read {}".format(img_file))
            continue
        
        # Lire les labels
        if not os.path.exists(label_path):
            print("  WARN: No label for {}".format(img_file))
            continue
        
        with open(label_path, 'r') as f:
            labels = f.read()
        
        # Generer des augmentations
        augmentations = [
            ('brightness', augment_image_brightness, {}),
            ('contrast', augment_image_contrast, {}),
            ('rotate', augment_image_rotate, {}),
            ('flip_h', lambda img: augment_image_flip(img, 'h'), {}),
            ('noise', augment_image_noise, {}),
            ('blur', augment_image_blur, {}),
        ]
        
        # Appliquer les augmentations
        for aug_idx in range(num_augmentations):
            aug_type, aug_func, kwargs = augmentations[aug_idx % len(augmentations)]
            
            try:
                aug_image = aug_func(image, **kwargs)
                
                # Generer un nouveau nom de fichier
                base_name = img_file.rsplit('.', 1)[0]
                ext = img_file.rsplit('.', 1)[1]
                new_img_name = "{}_aug{}_{}.{}".format(base_name, aug_idx, aug_type, ext)
                new_label_name = "{}_aug{}_{}.txt".format(base_name, aug_idx, aug_type)
                
                new_img_path = os.path.join(source_images, new_img_name)
                new_label_path = os.path.join(source_labels, new_label_name)
                
                # Sauvegarder
                cv2.imwrite(new_img_path, aug_image)
                with open(new_label_path, 'w') as f:
                    f.write(labels)
                
                augmentation_count += 1
                
            except Exception as e:
                print("  ERR {} on {}: {}".format(aug_type, img_file, str(e)))
        
        if idx % 20 == 0:
            print("  Progress: {}/{} images processed...".format(idx, total_images))
    
    return augmentation_count

print("=" * 60)
print("AUGMENTATION DE DATASET")
print("=" * 60)

# Augmenter les images de train
if os.path.exists(TRAIN_IMAGES) and os.path.exists(TRAIN_LABELS):
    print("\n1. Augmentation des images d'entrainnement...")
    train_aug = augment_dataset(TRAIN_IMAGES, TRAIN_LABELS, num_augmentations=4)
    print("   OK: {} images augmentees generees".format(train_aug))
else:
    print("\n1. ERR: Repertoires train introuvables")

# Augmenter les images de test (moins d'augmentations)
if os.path.exists(TEST_IMAGES) and os.path.exists(TEST_LABELS):
    print("\n2. Augmentation des images de test...")
    test_aug = augment_dataset(TEST_IMAGES, TEST_LABELS, num_augmentations=2)
    print("   OK: {} images augmentees generees".format(test_aug))
else:
    print("\n2. WARN: Repertoires test introuvables")

# Compter le total
train_count = len([f for f in os.listdir(TRAIN_IMAGES) if f.endswith(('.jpg', '.jpeg', '.png'))])
print("\n" + "=" * 60)
print("OK: Dataset augmente avec succes!")
print("   Total images d'entrainnement: {}".format(train_count))
print("=" * 60)
