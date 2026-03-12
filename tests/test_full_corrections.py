#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test complet: uploads + monitoring avec le nouveau seuil et formatage"""

import os
import sys
import json
import base64
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from config import config

print("=" * 70)
print("TEST COMPLET: UPLOADS + MONITORING")
print("=" * 70)

print(f"\nConfiguration:")
print(f"  CONFIDENCE_THRESHOLD = {config.CONFIDENCE_THRESHOLD}")
print(f"  MULTI_MODEL_ENABLED = {config.MULTI_MODEL_ENABLED}")

# Trouver une image de test
test_image_path = os.path.join("static", "uploads", "images", "20251217_005256_e.jpg")
if not os.path.exists(test_image_path):
    print(f"Image non trouvée: {test_image_path}")
    sys.exit(1)

img = cv2.imread(test_image_path)
print(f"  Image: {img.shape}")

# TEST 1: Upload
print("\n" + "=" * 70)
print("TEST 1: ROUTE /upload (POST)")
print("=" * 70)

with app.test_client() as client:
    with open(test_image_path, 'rb') as f:
        from io import BytesIO
        image_data = f.read()
    
    response = client.post(
        '/upload',
        data={
            'file': (BytesIO(image_data), os.path.basename(test_image_path)),
            'type': 'image'
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.get_json()
        print(f"Success: {result.get('success')}")
        print(f"Detections: {result.get('detections_count')}")
        
        if 'detections' in result:
            print(f"\nDetections returned:")
            for i, det in enumerate(result['detections']):
                print(f"  [{i}] {det['class_name']:10} - confidence={det['confidence']:.4f}")
        
        if 'statistics' in result:
            stats = result['statistics']
            print(f"\nStatistics:")
            print(f"  - total_persons: {stats.get('total_persons')}")
            print(f"  - with_helmet: {stats.get('with_helmet')}")
            print(f"  - with_vest: {stats.get('with_vest')}")
            print(f"  - compliance_rate: {stats.get('compliance_rate'):.1f}%")
            print(f"  - total_ms: {stats.get('total_ms'):.0f}ms")

# TEST 2: Monitoring API /api/detect
print("\n" + "=" * 70)
print("TEST 2: ROUTE /api/detect (POST - Unified Monitoring)")
print("=" * 70)

# Encoder l'image en base64
ret, buffer = cv2.imencode('.jpg', img)
image_base64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode()

with app.test_client() as client:
    response = client.post(
        '/api/detect',
        json={'image': image_base64},
        content_type='application/json'
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.get_json()
        print(f"Success: {result.get('success')}")
        
        if 'detections' in result:
            print(f"Detections: {len(result['detections'])}")
            print(f"\nDetections returned:")
            print(f"Sample detection keys: {list(result['detections'][0].keys()) if result['detections'] else 'N/A'}")
            print(f"Full first detection: {result['detections'][0] if result['detections'] else 'N/A'}")
            
            for i, det in enumerate(result['detections']):
                print(f"  [{i}] {det.get('class_name', 'N/A'):10} - confidence={det.get('confidence', 'N/A')}, bbox=[{det.get('x1', 'N/A')}, {det.get('y1', 'N/A')}, {det.get('x2', 'N/A')}, {det.get('y2', 'N/A')}]")
        
        if 'statistics' in result:
            stats = result['statistics']
            print(f"\nStatistics:")
            print(f"  - total_persons: {stats.get('total_persons')}")
            print(f"  - with_helmet: {stats.get('with_helmet')}")
            print(f"  - with_vest: {stats.get('with_vest')}")
            print(f"  - compliance_rate: {stats.get('compliance_rate'):.1f}%")

print("\n" + "=" * 70)
print("TEST TERMINE")
print("=" * 70)
