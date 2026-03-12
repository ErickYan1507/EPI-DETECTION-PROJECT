#!/usr/bin/env python3
"""
DIAGNOSTIC COMPLET - Identifie EXACTEMENT le problème
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from app.notification_service import notification_service
import json

print("=" * 70)
print("🔍 DIAGNOSTIC COMPLET")
print("=" * 70)

# Check 1: Configuration
print("\n1️⃣ CONFIGURATION:")
config = notification_service.get_config()
print(f"   Email: {config.get('sender_email') or '❌ VIDE'}")
print(f"   Clé: {('*' * len(config.get('sender_password', ''))) if config.get('sender_password') else '❌ VIDE'}")
print(f"   Serveur: {config.get('smtp_server', 'smtp.gmail.com')}")

if not config.get('sender_email'):
    print(f"\n❌ ERREUR: Email expéditeur vide!")
    print(f"   Solution: Configurez l'email dans l'interface")
    sys.exit(1)

if not config.get('sender_password'):
    print(f"\n❌ ERREUR: Mot de passe vide!")
    print(f"   Solution: Configurez le mot de passe")
    sys.exit(1)

# Check 2: Destinataires
print("\n2️⃣ DESTINATAIRES:")
recipients = notification_service.get_recipients()
if recipients:
    print(f"   ✅ {len(recipients)} destinataire(s) trouvé(s):")
    for r in recipients:
        print(f"      • {r}")
else:
    print(f"   ⚠️  AUCUN destinataire!")
    print(f"   Solution: Ajoutez des destinataires")

# Check 3: Test connexion
print("\n3️⃣ TEST CONNEXION SMTP:")
result = notification_service.test_connection()
if result.get('success'):
    print(f"   ✅ Connexion OK!")
else:
    print(f"   ❌ Erreur: {result.get('error')}")
    print(f"\n   Problème identifié:")
    if 'Username and Password not accepted' in str(result.get('error', '')):
        print(f"   → Clé ou email incorrect")
        print(f"   → 2FA pas activé sur Gmail")
        print(f"\n   Solutions:")
        print(f"   1. Vérifiez votre clé d'application Gmail")
        print(f"   2. Activez 2FA: https://myaccount.google.com/security")
        print(f"   3. Générez une nouvelle clé: https://myaccount.google.com/apppasswords")
    else:
        print(f"   → {result.get('error')}")
    sys.exit(1)

# Check 4: Envoi test
if recipients:
    print(f"\n4️⃣ ENVOI D'EMAIL TEST:")
    test_recipient = recipients[0]
    success = notification_service.send_manual_notification(
        "🧪 Test EPI Detection",
        "Ceci est un email de test du système de notifications.",
        test_recipient
    )
    
    if success:
        print(f"   ✅ Email envoyé à {test_recipient}!")
        print(f"\n   ✔ Vérifiez votre email pour confirmer!")
    else:
        print(f"   ❌ Erreur lors de l'envoi")
        print(f"   Consultez les logs pour plus de détails")
else:
    print(f"\n4️⃣ ENVOI D'EMAIL TEST: IGNORÉ (aucun destinataire)")

# Check 5: Historique
print(f"\n5️⃣ HISTORIQUE:")
history = notification_service.get_history(limit=3)
if history:
    print(f"   ✅ {len(history)} notification(s) enregistrée(s):")
    for h in history:
        status = "✅" if h.get('status') == 'success' else "❌"
        print(f"      {status} {h.get('timestamp')}: {h.get('subject')} → {h.get('recipient')}")
else:
    print(f"   (Aucune historique)")

print("\n" + "=" * 70)
print("✅ DIAGNOSTIC TERMINÉ")
print("=" * 70)
