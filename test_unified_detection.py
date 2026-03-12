#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔍 Diagnostic rapide de la détection Unified Monitoring
Pour vérifier que /api/detect fonctionne correctement
"""

import requests
import base64
import json
import time
from pathlib import Path
import cv2

print("""
╔═══════════════════════════════════════════════════════════════╗
║         Test Détection - Unified Monitoring                  ║
╚═══════════════════════════════════════════════════════════════╝
""")

# Configuration
API_URL = "http://127.0.0.1:5000"
API_DETECT = f"{API_URL}/api/detect"
TEST_IMAGE = Path("static/uploads/images/test.jpg")

print(f"🔗 API endpoint: {API_DETECT}")
print(f"📸 Image de test: {TEST_IMAGE}\n")

# 1. Vérifier la connectivité API
print("1️⃣  Vérification de la connectivité API...")
try:
    response = requests.get(f"{API_URL}/", timeout=2)
    print(f"   ✅ Serveur Flask: En ligne (HTTP {response.status_code})")
except Exception as e:
    print(f"   ❌ Serveur Flask: Hors ligne")
    print(f"   Erreur: {e}")
    print(f"\n⚠️  Assurez-vous que Flask est lancé:")
    print(f"   python app/main.py\n")
    exit(1)

# 2. Vérifier l'état du détecteur
print("\n2️⃣  Vérification du détecteur...")
try:
    response = requests.get(f"{API_URL}/api/model-info", timeout=2)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Détecteur initialisé")
        if 'model_name' in data:
            print(f"   Modèle: {data.get('model_name', '?')}")
    else:
        print(f"   ⚠️  Erreur: HTTP {response.status_code}")
except Exception as e:
    print(f"   ⚠️  Endpoint /api/model-info indisponible")
    print(f"   Note: C'est normal si cet endpoint n'existe pas")

# 3. Tester avec une image si disponible
print("\n3️⃣  Test de détection avec image base64...")

if TEST_IMAGE.exists():
    print(f"   📸 Image trouvée: {TEST_IMAGE}")
    
    try:
        # Lire l'image
        with open(TEST_IMAGE, 'rb') as f:
            image_bytes = f.read()
        
        # Convertir en base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        print(f"   ✅ Image encodée ({len(image_base64)//1000}KB)")
        
        # Envoyer la requête
        print(f"   📤 Envoi de la requête à {API_DETECT}...")
        
        start_time = time.time()
        response = requests.post(
            API_DETECT,
            headers={'Content-Type': 'application/json'},
            json={
                'image': image_base64,
                'use_ensemble': False
            },
            timeout=30
        )
        elapsed = time.time() - start_time
        
        print(f"   ✅ Réponse reçue en {elapsed:.2f}s (HTTP {response.status_code})")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"\n   ✅ SUCCÈS - Détection fonctionnelle!")
                
                detections = result.get('detections', [])
                stats = result.get('statistics', {})
                
                print(f"\n   📊 Résultats:")
                print(f"      • Détections: {len(detections)}")
                print(f"      • Personnes: {stats.get('total_persons', 0)}")
                print(f"      • Casques: {stats.get('with_helmet', 0)}")
                print(f"      • Gilets: {stats.get('with_vest', 0)}")
                print(f"      • Lunettes: {stats.get('with_glasses', 0)}")
                print(f"      • Conformité: {stats.get('compliance_rate', 0)}%")
                
                if detections:
                    print(f"\n   Classes détectées:")
                    for det in detections[:5]:  # Afficher les 5 premières
                        print(f"      - {det.get('class_name')}: {det.get('confidence')*100:.1f}%")
            else:
                print(f"\n   ❌ Erreur API: {result.get('error', 'Erreur inconnue')}")
        else:
            print(f"\n   ❌ Erreur HTTP {response.status_code}")
            print(f"   Réponse: {response.text[:500]}")
    
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout - La détection prend trop longtemps (>30s)")
        print(f"       Essayez avec use_ensemble=False pour plus de rapidité")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
else:
    print(f"   ⚠️  Aucune image de test trouvée")
    print(f"   Path: {TEST_IMAGE}")
    print(f"\n   Pour tester, placez une image (test.jpg) dans {TEST_IMAGE.parent}/")
    print(f"   Ou lancez Unified Monitoring et ajoutez une détection")

# 4. Simuler un test desde le navigateur  
print(f"\n4️⃣  Test manuel depuis le navigateur:")
print(f"   1. Rendez-vous sur http://127.0.0.1:5000/unified_monitoring.html")
print(f"   2. Cliquez sur 'Démarrer Webcam'")
print(f"   3. Vérifiez que les détections apparaissent")
print(f"   4. Vérifiez la console du navigateur (F12) pour les erreurs")

print(f"\n5️⃣  Vérification des logs:")
print(f"   Pour voir si le détecteur est chargé:")
print(f"   tail -f logs/app.log | grep -i '(multi|detector|détect)'")

print(f"\n{'='*65}\n")
