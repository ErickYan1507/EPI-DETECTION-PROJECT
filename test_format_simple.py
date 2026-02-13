#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test simple pour vérifier le formatage des détections"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Désactiver Flask logging
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

from app.main import app
import base64
import cv2

# Charger l'image
img = cv2.imread("static/uploads/images/20251217_005256_e.jpg")

# Encoder en base64
ret, buffer = cv2.imencode('.jpg', img)
image_base64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode()

print("Envoi d'une requête POST à /api/detect...")

with app.test_client() as client:
    print(f"Appelant: POST /api/detect")
    response = client.post(
        '/api/detect',
        json={'image': image_base64},
        content_type='application/json'
    )
    
    print(f"Status reçu: {response.status_code}")
    print(f"Content-Type: {response.content_type}")
    print(f"URL appelée: /api/detect")
    
    result = response.get_json()
    
    print(f"\nReponse status: {response.status_code}")
    print(f"Success: {result.get('success')}")
    print(f"\nDetections reçues: {len(result.get('detections', []))}")
    
    if result.get('detections'):
        det = result['detections'][0]
        print(f"\nPremière détection:")
        print(f"  Clés: {list(det.keys())}")
        print(f"  Contenu: {json.dumps(det, indent=2)}")
        
        # Vérifier le formatage
        print(f"\nVérification du formatage:")
        print(f"  'x1' présent? {('x1' in det)}")
        print(f"  'y1' présent? {('y1' in det)}")
        print(f"  'x2' présent? {('x2' in det)}")
        print(f"  'y2' présent? {('y2' in det)}")
        print(f"  'bbox' présent? {('bbox' in det)}")
        print(f"  'class_name' présent? {('class_name' in det)}")
        print(f"  'class' présent? {('class' in det)}")
