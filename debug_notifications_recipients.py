#!/usr/bin/env python3
"""
Script de débogage pour les destinataires des notifications
Teste les opérations CRUD sur les destinataires
"""

import json
import requests
from pathlib import Path

BASE_URL = 'http://localhost:5000'
API_BASE = f'{BASE_URL}/api/notifications'

# Fichiers de données
RECIPIENTS_FILE = Path('.notification_recipients')
CONFIG_FILE = Path('.notification_config.json')

print("=" * 60)
print("🔍 DIAGNOSTIC DES DESTINATAIRES - NOTIFICATION SYSTEM")
print("=" * 60)

# Test 1: Vérifier les fichiers
print("\n📁 1. Vérification des fichiers de données:")
print(f"  • .notification_recipients existe: {RECIPIENTS_FILE.exists()}")
if RECIPIENTS_FILE.exists():
    content = RECIPIENTS_FILE.read_text()
    lines = content.strip().split('\n') if content.strip() else []
    print(f"    → Contenu: {content if content.strip() else '(VIDE)'}")
    print(f"    → Nombre d'emails: {len([l for l in lines if l.strip()])}")
else:
    print(f"    → ⚠️  Fichier n'existe pas!")

print(f"\n  • .notification_config.json existe: {CONFIG_FILE.exists()}")
if CONFIG_FILE.exists():
    try:
        config = json.loads(CONFIG_FILE.read_text())
        print(f"    → Sender email: {config.get('sender_email', '(VIDE)')}")
        print(f"    → Config chargée OK")
    except:
        print(f"    → ⚠️  Erreur lecture JSON!")

# Test 2: Tester l'API GET recipients
print("\n\n🌐 2. Test API GET /api/notifications/recipients:")
try:
    response = requests.get(f'{API_BASE}/recipients')
    print(f"  • Status: {response.status_code}")
    print(f"  • Response headers: {dict(response.headers)}")
    
    data = response.json()
    print(f"  • Response JSON:\n{json.dumps(data, indent=2)}")
    
    if data.get('success'):
        recipients = data.get('recipients', [])
        print(f"\n  ✅ Nombre de destinataires retourné: {len(recipients)}")
        for r in recipients:
            print(f"     - {r}")
    else:
        print(f"\n  ❌ Erreur: {data.get('error')}")
except Exception as e:
    print(f"  ❌ Erreur connexion: {e}")


# Test 3: Ajouter un email de test
print("\n\n🌐 3. Test API POST /api/notifications/recipients (ajouter email):")
test_email = "test@example.com"
try:
    response = requests.post(
        f'{API_BASE}/recipients',
        json={'email': test_email},
        headers={'Content-Type': 'application/json'}
    )
    print(f"  • Status: {response.status_code}")
    data = response.json()
    print(f"  • Response: {json.dumps(data, indent=2)}")
    
    if data.get('success'):
        print(f"\n  ✅ Email ajouté avec succès")
    else:
        print(f"\n  ❌ Erreur: {data.get('error')}")
except Exception as e:
    print(f"  ❌ Erreur connexion: {e}")


# Test 4: Vérifier que l'email a été sauvegardé
print("\n\n📁 4. Vérification du fichier .notification_recipients après ajout:")
if RECIPIENTS_FILE.exists():
    content = RECIPIENTS_FILE.read_text()
    lines = content.strip().split('\n') if content.strip() else []
    print(f"  • Contenu actuel:\n{content if content.strip() else '(VIDE)'}")
    print(f"  • Nombre d'emails: {len([l for l in lines if l.strip()])}")
else:
    print(f"  • ⚠️  Fichier n'existe pas!")


# Test 5: Recharger les destinataires
print("\n\n🌐 5. Test API GET /api/notifications/recipients (après ajout):")
try:
    response = requests.get(f'{API_BASE}/recipients')
    print(f"  • Status: {response.status_code}")
    
    data = response.json()
    if data.get('success'):
        recipients = data.get('recipients', [])
        print(f"  • Nombre de destinataires: {len(recipients)}")
        for r in recipients:
            print(f"     - {r}")
    else:
        print(f"  • ❌ Erreur: {data.get('error')}")
except Exception as e:
    print(f"  ❌ Erreur connexion: {e}")


# Test 6: Supprimer le test email
print("\n\n🌐 6. Test API DELETE /api/notifications/recipients (supprimer email):")
try:
    response = requests.delete(
        f'{API_BASE}/recipients',
        json={'email': test_email},
        headers={'Content-Type': 'application/json'}
    )
    print(f"  • Status: {response.status_code}")
    data = response.json()
    print(f"  • Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"  ❌ Erreur connexion: {e}")


print("\n" + "=" * 60)
print("✅ Diagnostic terminé!")
print("=" * 60)
print("\n💡 Prochaines étapes si ça ne marche pas:")
print("   1. Vérifiez que Flask est en train de tourner (port 5000)")
print("   2. Vérifiez la console Flask pour les erreurs")
print("   3. Vérifiez les permissions du fichier .notification_recipients")
print("   4. Vérifiez que app/notification_service.py n'a pas d'erreur")
