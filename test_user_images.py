#!/usr/bin/env python
"""
Test de détection sur les images de l'utilisateur
Image 1: Personne avec lunettes de soleil
Image 2: Ouvrier avec casque, gilet, chaussures de sécurité
"""
import cv2
import os
from app.detection import EPIDetector
from app.multi_model_detector import MultiModelDetector

print('🧪 TEST DÉTECTION SUR IMAGES UTILISATEUR')
print('=' * 60)

# Images d'exemple (à remplacer par les vraies images)
test_images = {
    'image1_lunettes.jpg': 'Personne avec lunettes de soleil',
    'image2_bottes.jpg': 'Ouvrier avec casque/gilet/bottes'
}

# Tester avec les détecteurs
detector = EPIDetector()

try:
    multi_detector = MultiModelDetector(use_ensemble=True)
    multi_enabled = True
except Exception as e:
    print(f'⚠️  Multi-modèles non disponible: {e}')
    multi_enabled = False

for img_name, description in test_images.items():
    print(f'\n📸 {img_name} - {description}')
    print('-' * 60)
    
    # Vérifier si l'image existe dans les uploads
    img_path = f'uploads/{img_name}'
    
    if not os.path.exists(img_path):
        print(f'  ❌ Image non trouvée: {img_path}')
        continue
    
    image = cv2.imread(img_path)
    if image is None:
        print(f'  ❌ Impossible de charger l\'image')
        continue
    
    print(f'  ✅ Image chargée: {image.shape}')
    
    # Test 1: Détecteur simple
    print(f'\n  1️⃣ Détecteur simple:')
    detections, stats = detector.detect(image)
    
    print(f'     👓 Lunettes: {stats["with_glasses"]}')
    print(f'     👢 Bottes: {stats["with_boots"]}')
    print(f'     Détections brutes: {len(detections)}')
    for det in detections:
        print(f'       • {det["class"]}: {det["confidence"]:.3f}')
    
    # Test 2: Détecteur multi-modèles (si disponible)
    if multi_enabled:
        print(f'\n  2️⃣ Détecteur multi-modèles (ensemble):')
        detections_m, stats_m = multi_detector.detect(image, use_ensemble=True)
        
        print(f'     👓 Lunettes: {stats_m["with_glasses"]}')
        print(f'     👢 Bottes: {stats_m["with_boots"]}')
        print(f'     Détections brutes: {len(detections_m)}')
        for det in detections_m:
            print(f'       • {det["class"]}: {det["confidence"]:.3f}')
