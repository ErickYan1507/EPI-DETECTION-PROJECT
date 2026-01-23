#!/usr/bin/env python3
"""
Script de debug pour les détections EPI
Permet de tester et diagnostiquer les problèmes de détection
"""

import os
import sys
import cv2
import torch
import numpy as np
from pathlib import Path
import json
from datetime import datetime

def check_model_exists():
    """Vérifier si un modèle entraîné existe"""
    model_paths = [
        'models/best.pt',
        'models/last.pt',
        'runs/train/exp/weights/best.pt',
        'runs/train/exp/weights/last.pt'
    ]

    for path in model_paths:
        if os.path.exists(path):
            print(f"✓ Modèle trouvé: {path}")
            return path

    print("❌ Aucun modèle trouvé")
    return None

def check_test_images():
    """Vérifier les images de test disponibles"""
    test_dirs = [
        'dataset/images/test',
        'dataset/images/val',
        'data/annotated'
    ]

    images = []
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            img_files = list(Path(test_dir).glob('*.[jp][pn][g]*'))
            images.extend(img_files)
            print(f"✓ Images trouvées dans {test_dir}: {len(img_files)}")

    if not images:
        print("❌ Aucune image de test trouvée")
        return []

    return images[:5]  # Retourner max 5 images

def test_model_inference(model_path, image_paths):
    """Tester l'inférence du modèle avec YOLOv5"""
    try:
        # Importer YOLOv5
        sys.path.append('yolov5')
        from models.common import DetectMultiBackend

        print(f"\n🔍 Chargement du modèle YOLOv5: {model_path}")

        # Initialiser le modèle YOLOv5
        device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        model = DetectMultiBackend(model_path, device=device)
        print(f"✓ Modèle YOLOv5 chargé avec succès sur {device}")

        # Tester sur quelques images
        for i, img_path in enumerate(image_paths[:3]):  # Tester seulement 3 images
            print(f"\n🖼️  Test image {i+1}: {img_path}")

            # Charger l'image
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"❌ Impossible de charger l'image {img_path}")
                continue

            print(f"   Dimensions: {img.shape}")

            # Prétraitement et inférence YOLOv5
            start_time = datetime.now()

            # Redimensionner pour l'inférence
            img_resized = cv2.resize(img, (416, 416))

            # Normaliser
            img_tensor = torch.from_numpy(img_resized).float().permute(2, 0, 1).unsqueeze(0) / 255.0
            img_tensor = img_tensor.to(device)

            # Inférence
            with torch.no_grad():
                pred = model(img_tensor)

            end_time = datetime.now()
            inference_time = (end_time - start_time).total_seconds() * 1000
            print(f"   Temps d'inférence: {inference_time:.2f}ms")

            # Analyser les prédictions
            if pred is not None and len(pred):
                print(f"   Prédictions: {len(pred)} détections")
                if hasattr(pred[0], 'shape'):
                    print(f"   Shape prédictions: {pred[0].shape}")
            else:
                print("   Aucune détection")

        return True

    except Exception as e:
        print(f"❌ Erreur lors du test d'inférence: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_config():
    """Vérifier la configuration"""
    print("\n⚙️  Vérification de la configuration:")

    # Vérifier config.py
    try:
        from config import Config
        print(f"✓ Classes configurées: {Config.CLASS_NAMES}")
        print(f"✓ Nombre de classes: {len(Config.CLASS_NAMES)}")
    except Exception as e:
        print(f"❌ Erreur config.py: {e}")

    # Vérifier data.yaml
    data_yaml_paths = ['dataset/data.yaml', 'data/data.yaml']
    for yaml_path in data_yaml_paths:
        if os.path.exists(yaml_path):
            try:
                import yaml
                with open(yaml_path, 'r') as f:
                    data = yaml.safe_load(f)
                print(f"✓ data.yaml trouvé: {yaml_path}")
                print(f"   Classes: {data.get('names', 'N/A')}")
                print(f"   Nombre de classes: {data.get('nc', 'N/A')}")
                break
            except Exception as e:
                print(f"❌ Erreur lecture {yaml_path}: {e}")
        else:
            print(f"❌ {yaml_path} non trouvé")

def main():
    """Fonction principale de debug"""
    print("=" * 60)
    print("🐛 DEBUG DÉTECTIONS EPI")
    print("=" * 60)

    # 1. Vérifier la configuration
    check_config()

    # 2. Vérifier le modèle
    model_path = check_model_exists()
    if not model_path:
        print("\n❌ Impossible de continuer sans modèle")
        return

    # 3. Vérifier les images de test
    test_images = check_test_images()
    if not test_images:
        print("\n❌ Impossible de continuer sans images de test")
        return

    # 4. Tester l'inférence
    print("\n🚀 Test d'inférence du modèle:")
    success = test_model_inference(model_path, test_images)

    if success:
        print("\n✅ Tests terminés avec succès!")
    else:
        print("\n❌ Tests échoués - vérifiez les erreurs ci-dessus")

if __name__ == "__main__":
    main()
    main()