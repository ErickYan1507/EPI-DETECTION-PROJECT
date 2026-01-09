#!/usr/bin/env python3
import cv2
import numpy as np
import time
import sys
from pathlib import Path
from app.detection import EPIDetector
from config import config

def benchmark_detection(model_path=None, num_frames=10, image_width=640, image_height=480):
    """Benchmark the detection performance"""
    
    print("=" * 60)
    print("EPI DETECTION PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    detector = EPIDetector(model_path)
    
    frame_times = []
    inference_times = []
    preprocessing_times = []
    postprocessing_times = []
    
    for i in range(num_frames):
        fake_frame = np.random.randint(0, 255, (image_height, image_width, 3), dtype=np.uint8)
        
        start_total = time.perf_counter()
        
        start_preprocess = time.perf_counter()
        resized = detector._resize_for_inference(fake_frame)
        preprocess_ms = (time.perf_counter() - start_preprocess) * 1000
        preprocessing_times.append(preprocess_ms)
        
        start_infer = time.perf_counter()
        detections, stats = detector.detect(fake_frame)
        infer_ms = (time.perf_counter() - start_infer) * 1000
        inference_times.append(stats.get('total_ms', infer_ms))
        
        total_ms = (time.perf_counter() - start_total) * 1000
        frame_times.append(total_ms)
        
        print(f"Frame {i+1}/{num_frames}: {total_ms:.2f}ms (Inference: {stats.get('total_ms', infer_ms):.2f}ms)")
    
    avg_frame = sum(frame_times) / len(frame_times)
    avg_inference = sum(inference_times) / len(inference_times)
    avg_preprocess = sum(preprocessing_times) / len(preprocessing_times)
    
    min_frame = min(frame_times)
    max_frame = max(frame_times)
    fps = 1000 / avg_frame if avg_frame > 0 else 0
    
    print("\n" + "=" * 60)
    print("RÉSULTATS")
    print("=" * 60)
    print(f"Nombre de frames testés: {num_frames}")
    print(f"Résolution: {image_width}x{image_height}")
    print(f"\nTEMPS DE RÉPONSE (en millisecondes):")
    print(f"  Temps moyen par frame: {avg_frame:.2f}ms")
    print(f"  Temps moyen d'inférence: {avg_inference:.2f}ms")
    print(f"  Temps moyen de prétraitement: {avg_preprocess:.2f}ms")
    print(f"  Temps minimum: {min_frame:.2f}ms")
    print(f"  Temps maximum: {max_frame:.2f}ms")
    print(f"\nPERFORMANCE:")
    print(f"  FPS moyen: {fps:.2f} FPS")
    print(f"  Latence: {avg_frame:.2f}ms")
    print("=" * 60)
    
    return {
        'avg_frame_ms': round(avg_frame, 2),
        'avg_inference_ms': round(avg_inference, 2),
        'fps': round(fps, 2),
        'min_ms': round(min_frame, 2),
        'max_ms': round(max_frame, 2)
    }

def benchmark_with_real_image(image_path):
    """Benchmark with a real image"""
    print("\n" + "=" * 60)
    print("BENCHMARK AVEC IMAGE RÉELLE")
    print("=" * 60)
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"Erreur: Impossible de charger {image_path}")
        return
    
    print(f"Image: {image_path}")
    print(f"Dimensions: {image.shape}")
    
    detector = EPIDetector()
    
    start = time.perf_counter()
    detections, stats = detector.detect(image)
    total_time = (time.perf_counter() - start) * 1000
    
    print(f"\nTEMPS D'EXÉCUTION:")
    print(f"  Temps total: {stats.get('total_ms', total_time):.2f}ms")
    print(f"  Temps d'inférence: {stats.get('inference_ms', 0):.2f}ms")
    print(f"  Détections: {len(detections)}")
    print(f"  Conformité: {stats['compliance_rate']:.1f}%")
    print("=" * 60)

if __name__ == '__main__':
    results = benchmark_detection(num_frames=20)
    
    image_dir = Path('images')
    if image_dir.exists():
        images = list(image_dir.glob('*.jpg'))
        if images:
            benchmark_with_real_image(str(images[0]))
