#!/usr/bin/env python3
"""
Debug deep - Test SMTP réel en dehors Flask pour voir si les emails sont VRAIMENT envoyés
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import sys

# Charger config
sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv

# Charger .env.email
load_dotenv('d:\\projet\\EPI-DETECTION-PROJECT\\.env.email')

SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
RECIPIENT = "ainaerickandrianavalona@gmail.com"

print("="*70)
print("TEST SMTP DIRECT EN DEHORS DE FLASK")
print("="*70)
print(f"\n📋 Configuration:")
print(f"  SMTP Server: {SMTP_SERVER}")
print(f"  SMTP Port: {SMTP_PORT}")
print(f"  Sender Email: {SENDER_EMAIL}")
print(f"  Sender Password: {'*' * 10 if SENDER_PASSWORD else 'NOT SET'}")
print(f"  Recipient: {RECIPIENT}")

if not SENDER_EMAIL or not SENDER_PASSWORD:
    print("\n❌ ERREUR: Email ou mot de passe non configurés dans .env.email")
    exit(1)

print("\n🔧 Étape 1: Créer connexion SMTP...")
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
    print("  ✓ Connexion créée")
except Exception as e:
    print(f"  ✗ Erreur: {e}")
    exit(1)

print("\n🔐 Étape 2: Démarrer TLS...")
try:
    server.starttls()
    print("  ✓ TLS démarré")
except Exception as e:
    print(f"  ✗ Erreur: {e}")
    server.quit()
    exit(1)

print(f"\n🔑 Étape 3: Login avec {SENDER_EMAIL}...")
try:
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    print("  ✓ Login réussi")
except smtplib.SMTPAuthenticationError as e:
    print(f"  ✗ Erreur d'authentification: {e}")
    server.quit()
    exit(1)
except Exception as e:
    print(f"  ✗ Erreur: {e}")
    server.quit()
    exit(1)

print("\n📧 Étape 4: Créer le message email...")
try:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "🧪 TEST DEBUG SMTP DIRECT"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT
    
    html_content = """
    <html>
    <body>
        <h1 style="color: red;">🧪 TEST DEBUG SMTP DIRECT</h1>
        <p>Cet email a été envoyé via SMTP direct en dehors de Flask.</p>
        <p>Si tu recois ce email, c'est que SMTP fonctionne!</p>
        <p>Si tu ne le recois pas, alors il y a un problème (spam, délai, etc.)</p>
        <hr>
        <p><strong>Heure d'envoi:</strong> {}</p>
        <p><strong>Destinataire:</strong> {}</p>
    </body>
    </html>
    """.format(__import__('datetime').datetime.now(), RECIPIENT)
    
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    print("  ✓ Message créé")
except Exception as e:
    print(f"  ✗ Erreur: {e}")
    server.quit()
    exit(1)

print(f"\n📤 Étape 5: Envoyer l'email à {RECIPIENT}...")
try:
    response = server.sendmail(SENDER_EMAIL, RECIPIENT, msg.as_string())
    print(f"  ✓ Email envoyé!")
    print(f"    Réponse serveur: {response}")
except Exception as e:
    print(f"  ✗ Erreur d'envoi: {e}")
    server.quit()
    exit(1)

print("\n🔌 Étape 6: Fermer la connexion...")
try:
    server.quit()
    print("  ✓ Connexion fermée proprement")
except Exception as e:
    print(f"  ⚠ Erreur: {e}")

print("\n" + "="*70)
print("✅ RÉSULTAT: Email envoyé avec succès!")
print("="*70)
print("\n📍 Vérification:")
print("  1. Regarde entre 1-5 minutes si l'email arrive dans ta boîte")
print("  2. Vérifie aussi le dossier SPAM/Promotions de Gmail")
print("  3. Si tu recois ce email, SMTP fonctionne correctement")
print("  4. Si tu ne le recois pas, il y a un problème avec:")
print("     - Authentification Gmail (contrôle d'accès aux apps)")
print("     - Paramètres de sécurité Gmail")
print("     - Pare-feu réseau")
print("\n" + "="*70)
