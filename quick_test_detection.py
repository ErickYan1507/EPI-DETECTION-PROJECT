#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test quick detection with camera
"""
import cv2
import time

print("🔍 Test détection caméra...")
print("=" * 60)

try:
    # Test 1: Camera
    print("\n1️⃣ Teste d'accès à la caméra...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        # Essayer avec DirectShow sur Windows
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"   ✅ Caméra accessible - taille: {frame.shape}")
        else:
            print("   ❌ Impossible de lire un frame")
        cap.release()
    else:
        print("   ❌ Impossible d'ouvrir la caméra")
except Exception as e:
    print(f"   ❌ Erreur caméra: {e}")

try:
    # Test 2: MultiDetector
    print("\n2️⃣ Test MultiModelDetector...")
    from app.multi_model_detector import MultiModelDetector
    
    md = MultiModelDetector(use_ensemble=False)
    print(f"   ✅ MultiModelDetector créé ({len(md.models)} modèles)")
    
    # Créer une image test
    test_image = cv2.imread('test.png') or cv2.imread('test_image.png')
    if test_image is None:
        print("   ⚠️ Pas d'image de test disponible, création image vide...")
        test_image = cv2.imread('static/uploads/images/test_image_generated.jpg')
        if test_image is None:
            import numpy as np
            test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    if test_image is not None:
        print(f"   ✅ Image test chargée: {test_image.shape}")
        
        start = time.perf_counter()
        detections, stats = md.detect(test_image, use_ensemble=False)
        elapsed = time.perf_counter() - start
        
        print(f"   ✅ Détection en {elapsed*1000:.0f}ms")
        print(f"   📊 Résultats:")
        print(f"      - Personnes détectées: {stats['total_persons']}")
        print(f"      - Avec casque: {stats['with_helmet']}")
        print(f"      - Avec gilet: {stats['with_vest']}")
        print(f"      - Avec lunettes: {stats['with_glasses']}")
        print(f"      - Conformité: {stats['compliance_rate']}%")
    else:
        print("   ❌ Impossible de charger une image de test")
        
except Exception as e:
    print(f"   ❌ Erreur MultiModelDetector: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Tests terminés!")
