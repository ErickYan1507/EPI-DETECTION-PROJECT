#!/usr/bin/env python3
"""
Test SMTP Gmail - diagnostic détaillé
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
EMAIL = "ainaerickandrianavalona@gmail.com"
PASSWORD = "mqoc zsrh lrsh zhhn"  # Clé d'application (avec espaces)

print("=" * 70)
print("🔍 TEST SMTP GMAIL - DIAGNOSTIC DÉTAILLÉ")
print("=" * 70)

print(f"\n📋 Configuration:")
print(f"  Email: {EMAIL}")
print(f"  Clé: {PASSWORD}")
print(f"  Serveur: smtp.gmail.com:587")

# Test 1: Connexion basique
print(f"\n1️⃣  TEST: Connexion basique...")
try:
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
    print(f"  ✅ Connexion TCP établie")
except Exception as e:
    print(f"  ❌ Impossible de se connecter: {e}")
    exit(1)

# Test 2: STARTTLS
print(f"\n2️⃣  TEST: STARTTLS (chiffrement)...")
try:
    server.starttls()
    print(f"  ✅ STARTTLS OK")
except Exception as e:
    print(f"  ❌ Erreur STARTTLS: {e}")
    server.quit()
    exit(1)

# Test 3: LOGIN
print(f"\n3️⃣  TEST: Authentification LOGIN...")
try:
    server.login(EMAIL, PASSWORD)
    print(f"  ✅ Authentification RÉUSSIE!")
except smtplib.SMTPAuthenticationError as e:
    print(f"  ❌ ERREUR AUTHENTIFICATION: {e}")
    print(f"\n  Problèmes possibles:")
    print(f"     1. Clé d'application incorrecte")
    print(f"     2. Vérification 2FA pas activée")
    print(f"     3. Email incorrect")
    server.quit()
    exit(1)
except Exception as e:
    print(f"  ❌ Erreur: {e}")
    server.quit()
    exit(1)

# Test 4: Envoyer un email
print(f"\n4️⃣  TEST: Envoi d'un email de test...")
try:
    msg = MIMEMultipart()
    msg['Subject'] = "🧪 Test SMTP Gmail"
    msg['From'] = EMAIL
    msg['To'] = EMAIL
    
    body = "Ceci est un email de test du système de notifications EPI Detection."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    server.sendmail(EMAIL, EMAIL, msg.as_string())
    print(f"  ✅ Email envoyé AVEC SUCCÈS!")
    print(f"\n  Vérifiez votre boîte email: {EMAIL}")
    
except smtplib.SMTPException as e:
    print(f"  ❌ Erreur SMTP: {e}")
    server.quit()
    exit(1)
except Exception as e:
    print(f"  ❌ Erreur: {e}")
    server.quit()
    exit(1)

# Fermer
server.quit()

print(f"\n" + "=" * 70)
print(f"✅ TOUS LES TESTS RÉUSSIS!")
print(f"=" * 70)
print(f"\n✓ Votre configuration Gmail est CORRECTE!")
print(f"✓ Les emails peuvent être envoyés!")
print(f"\nAllez maintenant à: http://localhost:5000/notifications")
print(f"et testez l'envoi de notifications!")
