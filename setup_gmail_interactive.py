#!/usr/bin/env python3
"""
Configuration interactive de l'email avec test de connexion
"""
import json
import sys
from pathlib import Path

CONFIG_FILE = Path('.notification_config.json')

print("=" * 70)
print("🔐 CONFIGURATION INTERACTIVE - EMAIL GMAIL")
print("=" * 70)

print("\n📝 Entrez vos informations Gmail:")
print("\nℹ️  IMPORTANT:")
print("   • Utilisez votre EMAIL GMAIL complet (ex: votremail@gmail.com)")
print("   • Utilisez une CLÉ D'APPLICATION, pas votre mot de passe!")
print("   • Générez la clé ici: https://myaccount.google.com/apppasswords")
print("   • Format de la clé: 16 caractères avec espaces (ex: abcd efgh ijkl mnop)")

print("\n" + "-" * 70)

# Demander l'email
email = input("\n📧 Votre email Gmail: ").strip()
if not email:
    print("❌ Email vide!")
    sys.exit(1)

if '@gmail.com' not in email:
    print(f"⚠️  ATTENTION: Ce n'est pas un email @gmail.com!")
    confirm = input("Continuer quand même? (oui/non): ").strip().lower()
    if confirm != 'oui':
        sys.exit(1)

# Demander le mot de passe / clé
print(f"\n🔑 Votre clé d'application Gmail (16 caractères avec espaces)")
print(f"   Exemple: abcd efgh ijkl mnop")
password = input("Clé d'application: ").strip()

if not password:
    print("❌ Clé vide!")
    sys.exit(1)

# Sauvegarde
print(f"\n" + "-" * 70)
print(f"📋 Configuration à sauvegarder:")
print(f"   Email: {email}")
print(f"   Clé: {password}")

# Charger la configuration actuelle
if CONFIG_FILE.exists():
    config = json.loads(CONFIG_FILE.read_text())
else:
    config = {}

# Mettre à jour
config['sender_email'] = email
config['sender_password'] = password

# Sauvegarder
CONFIG_FILE.write_text(json.dumps(config, indent=2))

print(f"\n✅ Configuration SAUVEGARDÉE!")
print(f"   Fichier: {CONFIG_FILE.absolute()}")

print(f"\n" + "-" * 70)
print(f"📋 Vérification:")
new_config = json.loads(CONFIG_FILE.read_text())
print(f"   Email: {new_config.get('sender_email')}")
print(f"   Clé: {'*' * len(new_config.get('sender_password', ''))}")

print("\n" + "=" * 70)
print("Testez maintenant avec l'interface web:")
print("http://localhost:5000/notifications")
print("\n1. Cliquez 'Tester Connexion' dans l'interface")
print("2. Si ✅, vous pouvez envoyer des emails!")
print("3. Si ❌, vérifiez votre clé d'application")
print("=" * 70)
