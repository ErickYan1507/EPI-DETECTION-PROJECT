#!/usr/bin/env python3
"""
Test de l'API Flask pour les destinataires
Vérifiez que Flask tourne avant de lancer ce script!
"""

import requests
import json
import sys

BASE_URL = 'http://localhost:5000'

print("=" * 60)
print("🌐 TEST DE L'API FLASK - DESTINATAIRES")
print("=" * 60)

# Vérifier que Flask tourne
print("\n👁️  Vérification que Flask est en cours d'exécution...")
try:
    response = requests.get(f'{BASE_URL}/', timeout=2)
    print("   ✅ Flask est actif!")
except:
    print("   ❌ Flask n'est pas accessible sur http://localhost:5000")
    print("   ➡️  Assurez-vous que Flask tourne!")
    print("      Exécutez: python run_app.py")
    sys.exit(1)

# Test 1: GET /api/notifications/recipients
print("\n1️⃣  TEST: GET /api/notifications/recipients")
try:
    response = requests.get(f'{BASE_URL}/api/notifications/recipients')
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response:\n{json.dumps(data, indent=3)}")
    
    # Vérifier la structure
    if 'success' in data:
        print(f"   ✅ Structure correcte (clé 'success' presente)")
    else:
        print(f"   ⚠️  Clé 'success' manquante!")
        
    if 'recipients' in data:
        print(f"   ✅ Clé 'recipients' presente")
    else:
        print(f"   ⚠️  Clé 'recipients' manquante!")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 2: POST /api/notifications/recipients (ajouter)
print("\n2️⃣  TEST: POST /api/notifications/recipients (ajouter test@example.com)")
try:
    response = requests.post(
        f'{BASE_URL}/api/notifications/recipients',
        json={'email': 'test@example.com'},
        headers={'Content-Type': 'application/json'}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response:\n{json.dumps(data, indent=3)}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 3: Vérifier l'ajout
print("\n3️⃣  TEST: GET /api/notifications/recipients (après ajout)")
try:
    response = requests.get(f'{BASE_URL}/api/notifications/recipients')
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    if 'recipients' in data:
        recipients = data['recipients']
        print(f"   Nombre de destinataires: {len(recipients)}")
        for r in recipients:
            print(f"      • {r}")
    else:
        print(f"   Réponse: {json.dumps(data, indent=3)}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 4: DELETE
print("\n4️⃣  TEST: DELETE /api/notifications/recipients (supprimer test@example.com)")
try:
    response = requests.delete(
        f'{BASE_URL}/api/notifications/recipients',
        json={'email': 'test@example.com'},
        headers={'Content-Type': 'application/json'}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response:\n{json.dumps(data, indent=3)}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "=" * 60)
print("✅ Test API terminé!")
print("=" * 60)
