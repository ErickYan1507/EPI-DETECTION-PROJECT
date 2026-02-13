#!/usr/bin/env python3
"""Test de l'upload en un seul essai"""

import requests
import sys
from pathlib import Path

# Chercher une image de test
test_image = None
for path in [
    Path('data/annotated/test_image.jpg'),
    Path('aa.jpg'),
    Path('test_image_generated.jpg'),
    Path('a.py'),
]:
    if path.exists() and path.suffix.lower() in ['.jpg', '.png']:
        test_image = path
        break

if not test_image:
    print("❌ Aucune image de test trouvée!")
    sys.exit(1)

print(f"📷 Image trouvée: {test_image}")

# Test du premier upload
print("\n" + "="*60)
print("TEST 1 - Premier upload")
print("="*60)

try:
    with open(test_image, 'rb') as f:
        files = {'file': f}
        data = {'type': 'image'}
        
        print(f"📤 Envoi de {test_image.name}...")
        response = requests.post(
            'http://localhost:5000/upload',
            files=files,
            data=data,
            timeout=60
        )
        
        print(f"📥 Statut: {response.status_code}")
        
        result = response.json()
        print(f"✅ Succès: {result.get('success')}")
        
        if result.get('success'):
            print(f"📊 Statistiques:")
            stats = result.get('statistics', {})
            print(f"   - Personnes: {stats.get('total_persons', 0)}")
            print(f"   - Casques: {stats.get('with_helmet', 0)}")
            print(f"   - Gilets: {stats.get('with_vest', 0)}")
            print(f"   - Lunettes: {stats.get('with_glasses', 0)}")
            print(f"   - Bottes: {stats.get('with_boots', 0)}")
            print(f"   - Conformité: {stats.get('compliance_rate', 0)}%")
        else:
            print(f"❌ Erreur: {result.get('error')}")

except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)

# Test du deuxième upload
print("\n" + "="*60)
print("TEST 2 - Deuxième upload (devrait marcher aussi!)")
print("="*60)

try:
    with open(test_image, 'rb') as f:
        files = {'file': f}
        data = {'type': 'image'}
        
        print(f"📤 Envoi de {test_image.name}...")
        response = requests.post(
            'http://localhost:5000/upload',
            files=files,
            data=data,
            timeout=60
        )
        
        print(f"📥 Statut: {response.status_code}")
        
        result = response.json()
        print(f"✅ Succès: {result.get('success')}")
        
        if result.get('success'):
            print(f"📊 Statistiques:")
            stats = result.get('statistics', {})
            print(f"   - Personnes: {stats.get('total_persons', 0)}")
            print(f"   - Casques: {stats.get('with_helmet', 0)}")
            print(f"   - Gilets: {stats.get('with_vest', 0)}")
            print(f"   - Lunettes: {stats.get('with_glasses', 0)}")
            print(f"   - Bottes: {stats.get('with_boots', 0)}")
            print(f"   - Conformité: {stats.get('compliance_rate', 0)}%")
        else:
            print(f"❌ Erreur: {result.get('error')}")

except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)

print("\n" + "="*60)
if result.get('success'):
    print("✅ LES DEUX UPLOADS RÉUSSISSENT!")
else:
    print("❌ Le deuxième upload a échoué")
print("="*60)
