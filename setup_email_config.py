#!/usr/bin/env python3
"""
Configure automatiquement l'email expéditeur et teste l'envoi
"""
import sys
import json
from pathlib import Path

# Configuration à utiliser
SENDER_EMAIL = "ainaerickandrianavalona09@gmail.com"
SENDER_PASSWORD = "mqoc zsrh lrsh zhhn"  # Clé d'application Gmail

CONFIG_FILE = Path('.notification_config.json')

print("=" * 70)
print("⚙️  CONFIGURATION AUTOMATIQUE - EMAIL EXPÉDITEUR")
print("=" * 70)

# Charger la configuration actuelle
if CONFIG_FILE.exists():
    config = json.loads(CONFIG_FILE.read_text())
    print(f"\n📂 Configuration actuelle trouvée")
else:
    config = {}
    print(f"\n📂 Nouvelle configuration")

# Mettre à jour
print(f"\n🔧 Configuration:")
print(f"   Email: {SENDER_EMAIL}")
print(f"   Clé: {SENDER_PASSWORD}")

config['sender_email'] = SENDER_EMAIL
config['sender_password'] = SENDER_PASSWORD

# Sauvegarder
CONFIG_FILE.write_text(json.dumps(config, indent=2))
print(f"\n✅ Configuration SAUVEGARDÉE dans {CONFIG_FILE}")

print(f"\n📋 Vérification:")
new_config = json.loads(CONFIG_FILE.read_text())
print(f"   Email: {new_config.get('sender_email')}")
print(f"   Clé: {new_config.get('sender_password')}")

print("\n" + "=" * 70)
print("✅ Configuration prête!")
print("=" * 70)
print("\nProchaine étape: tester l'envoi...")
print("Exécutez: python test_send_email.py")
