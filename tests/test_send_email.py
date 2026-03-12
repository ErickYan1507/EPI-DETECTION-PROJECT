#!/usr/bin/env python3
"""
Test d'envoi d'email directement
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from app.notification_service import notification_service
import json

print("=" * 70)
print("📧 TEST DIRECT D'ENVOI D'EMAIL")
print("=" * 70)

# Vérifions la configuration actuelle
print("\n1️⃣ Configuration actuelle:")
config = notification_service.get_config()
print(f"   Email: {config.get('sender_email', '(vide)')}")
print(f"   Mot de passe: {'*' * len(config.get('sender_password', '')) if config.get('sender_password') else '(vide)'}")

# Vérifiez les destinataires
print("\n2️⃣ Destinataires configurés:")
recipients = notification_service.get_recipients()
if recipients:
    for r in recipients:
        print(f"   ✓ {r}")
else:
    print(f"   ❌ AUCUN destinataire!")

if not config.get('sender_email'):
    print("\n" + "=" * 70)
    print("❌ ERREUR: Email expéditeur non configuré!")
    print("\nVous devez d'abord:")
    print("1. Aller à http://localhost:5000/notifications")
    print("2. Entrer votre email Gmail")
    print("3. Entrer votre clé d'application")
    print("4. Cliquer 'Sauvegarder'")
    print("=" * 70)
    sys.exit(1)

if not recipients:
    print("\n" + "=" * 70)
    print("❌ ERREUR: Aucun destinataire!")
    print("\nVous devez d'abord ajouter des destinataires.")
    print("=" * 70)
    sys.exit(1)

# Tester l'envoi
print("\n3️⃣ Test de connexion SMTP:")
if notification_service.test_connection():
    print("   ✅ Connexion SMTP OK!")
else:
    print("   ❌ ERREUR de connexion SMTP!")
    print("   Vérifiez votre email et votre clé d'application")
    sys.exit(1)

# Tester l'envoi d'un email
print("\n4️⃣ Envoi d'un email de test...")
recipient = recipients[0]  # Premier destinataire
subject = "🧪 Test Notification EPI Detection"
message = "Ceci est un email de test du système de notifications."

print(f"   À: {recipient}")
print(f"   Sujet: {subject}")

if notification_service.send_manual_notification(subject, message, recipient):
    print(f"   ✅ Email envoyé avec succès!")
    
    # Vérifier l'historique
    print("\n5️⃣ Vérification de l'historique:")
    history = notification_service.get_history(limit=5)
    if history:
        print(f"   ✓ {len(history)} notifications enregistrées")
        for h in history[-3:]:
            print(f"     - {h.get('timestamp', '?')}: {h.get('subject', '?')} → {h.get('recipient', '?')}")
    else:
        print(f"   (Aucune historique)")
else:
    print(f"   ❌ ERREUR lors de l'envoi!")
    print(f"   Vérifiez la configuration")

print("\n" + "=" * 70)
print("✅ Test terminé!")
print("=" * 70)
