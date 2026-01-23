#!/usr/bin/env python3
"""Test la vraie vitesse du système"""
import cv2
import numpy as np
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.detection import EPIDetector
from config import config

def test_detection_speed():
    print("=" * 70)
    print("SPEED TEST - Performance Réelle")
    print("=" * 70)
    
    print(f"\n📋 Configuration Actuelle:")
    print(f"  Camera: {config.CAMERA_FRAME_WIDTH}x{config.CAMERA_FRAME_HEIGHT}")
    print(f"  YOLO Input: {config.YOLO_INPUT_WIDTH}x{config.YOLO_INPUT_HEIGHT}")
    print(f"  FRAME_SKIP: {config.FRAME_SKIP}")
    print(f"  JPEG Quality: {config.JPEG_QUALITY}")
    
    try:
        print(f"\n🔄 Chargement du modèle...")
        detector = EPIDetector()
        print(f"✅ Modèle chargé\n")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    times = []
    inference_times = []
    
    print("🎯 Test avec 10 images aléatoires...\n")
    
    for i in range(10):
        fake_frame = np.random.randint(0, 255, 
                                      (config.CAMERA_FRAME_HEIGHT, 
                                       config.CAMERA_FRAME_WIDTH, 3), 
                                      dtype=np.uint8)
        
        start = time.perf_counter()
        detections, stats = detector.detect(fake_frame)
        elapsed = (time.perf_counter() - start) * 1000
        
        times.append(elapsed)
        inf_time = stats.get('inference_ms', 0)
        inference_times.append(inf_time)
        
        print(f"  Frame {i+1:2d}: {elapsed:6.1f}ms | Inference: {inf_time:6.1f}ms | Détections: {len(detections)}")
    
    avg_time = np.mean(times)
    min_time = np.min(times)
    max_time = np.max(times)
    avg_inf = np.mean(inference_times)
    fps = 1000 / avg_time if avg_time > 0 else 0
    
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS")
    print("=" * 70)
    print(f"Temps moyen: {avg_time:.1f}ms")
    print(f"Temps min:   {min_time:.1f}ms")
    print(f"Temps max:   {max_time:.1f}ms")
    print(f"Inférence:   {avg_inf:.1f}ms")
    print(f"FPS:         {fps:.1f}")
    
    print("\n" + "=" * 70)
    print("✅ VERDICT")
    print("=" * 70)
    
    if avg_time < 100:
        print("🚀 EXCELLENT! Système ultra-rapide")
        print("   Vous pouvez augmenter la résolution ou réduire FRAME_SKIP")
    elif avg_time < 200:
        print("✅ BON! Système rapide")
        print("   Performance acceptable pour monitoring en temps réel")
    elif avg_time < 350:
        print("⚠️  ACCEPTABLE mais avec latence")
        print("   Envisager de réduire résolution ou augmenter FRAME_SKIP")
    elif avg_time < 500:
        print("⚠️⚠️ LENT! Système ramant")
        print("   RÉDUCTIONS RECOMMANDÉES:")
        print("   - CAMERA_FRAME_WIDTH: 160")
        print("   - CAMERA_FRAME_HEIGHT: 120")
        print("   - FRAME_SKIP: 5")
        print("   - JPEG_QUALITY: 20")
    else:
        print("❌ TRÈS LENT! Système gravement ramant")
        print("   VÉRIFIER:")
        print("   - GPU disponible? python check_system.py")
        print("   - Si CPU seulement: FRAME_SKIP = 20+")
        print("   - Résolution maximale: 160x120")
    
    print("=" * 70)
    
    return {
        'avg_ms': round(avg_time, 1),
        'inf_ms': round(avg_inf, 1),
        'fps': round(fps, 1),
        'min_ms': round(min_time, 1),
        'max_ms': round(max_time, 1)
    }

if __name__ == '__main__':
    test_detection_speed()
