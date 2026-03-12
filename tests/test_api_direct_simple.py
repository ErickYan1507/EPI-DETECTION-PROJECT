#!/usr/bin/env python3
"""
Test d'ajout de destinataire - DIRECT
"""
import requests
import json
import time

BASE = 'http://localhost:5000'

print("=" * 70)
print("🧪 TEST DIRECT DE L'API - AJOUT DE DESTINATAIRE")
print("=" * 70)

# Test 1: Vérifier que Flask réagit
print("\n1️⃣ Vérification que Flask tourne...")
try:
    r = requests.get(f'{BASE}/', timeout=2)
    print(f"   ✅ Flask actif (status {r.status_code})")
except:
    print(f"   ❌ Flask n'est pas accessible!")
    exit(1)

# Test 2: GET recipients initial
print("\n2️⃣ Récupérer les destinataires (GET)...")
r = requests.get(f'{BASE}/api/notifications/recipients')
print(f"   Status: {r.status_code}")
data = r.json()
print(f"   Réponse: {json.dumps(data, indent=2)}")
initial_count = len(data.get('recipients', []))
print(f"   Nombre initial: {initial_count}")

# Test 3: Ajouter un email
test_email = f"test-{int(time.time())}@example.com"
print(f"\n3️⃣ Ajouter l'email: {test_email}")
r = requests.post(
    f'{BASE}/api/notifications/recipients',
    json={'email': test_email},
    headers={'Content-Type': 'application/json'}
)
print(f"   Status: {r.status_code}")
data = r.json()
print(f"   Réponse:\n{json.dumps(data, indent=2)}")

# Test 4: Récupérer à nouveau
print(f"\n4️⃣ Récupérer les destinataires (GET) - APRÈS AJOUT...")
r = requests.get(f'{BASE}/api/notifications/recipients')
print(f"   Status: {r.status_code}")
data = r.json()
print(f"   Réponse: {json.dumps(data, indent=2)}")
final_count = len(data.get('recipients', []))
print(f"   Nombre maintenant: {final_count}")

# Vérifier le changement
print(f"\n5️⃣ RÉSULTAT:")
print(f"   Avant: {initial_count} destinataires")
print(f"   Après: {final_count} destinataires")

if final_count > initial_count:
    print(f"   ✅ SUCCÈS! L'email a bien été ajouté!")
    
    # Vérifier que c'est notre email
    if test_email in data.get('recipients', []):
        print(f"   ✅ Notre email '{test_email}' est dans la liste!")
    else:
        print(f"   ⚠️  L'email n'est pas dans la liste retournée!")
else:
    print(f"   ❌ ÉCHEC! Le compteur n'a pas changé!")

print("\n" + "=" * 70)
