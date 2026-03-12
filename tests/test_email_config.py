#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration email Gmail SMTP
Teste la connexion et l'envoi d'un email test
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from app.email_notifications import EmailNotifier
from app.logger import logger

def test_smtp_connection():
    """Test de connexion au serveur SMTP"""
    
    print("\n" + "="*60)
    print("TEST DE CONFIGURATION EMAIL")
    print("="*60)
    
    # Vérifier les variables
    print("\n1️⃣  VÉRIFICATION DES PARAMÈTRES:")
    print(f"   SMTP Server: {config.SMTP_SERVER}")
    print(f"   SMTP Port: {config.SMTP_PORT}")
    print(f"   Sender Email: {config.SENDER_EMAIL}")
    print(f"   Password: {'*' * len(config.SENDER_PASSWORD) if config.SENDER_PASSWORD else 'NON CONFIGURÉ'}")
    
    # Validations
    if not config.SENDER_EMAIL:
        print("\n❌ ERREUR: SENDER_EMAIL n'est pas configuré dans .env.email")
        return False
    
    if not config.SENDER_PASSWORD:
        print("\n❌ ERREUR: SENDER_PASSWORD n'est pas configuré dans .env.email")
        return False
    
    print("\n✅ Paramètres trouvés")
    
    # Test de connexion SMTP
    print("\n2️⃣  TEST DE CONNEXION SMTP:")
    try:
        import smtplib
        
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        print(f"   ✅ Connexion établie avec {config.SMTP_SERVER}:{config.SMTP_PORT}")
        
        server.starttls()
        print("   ✅ TLS activé")
        
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        print(f"   ✅ Authentification réussie avec {config.SENDER_EMAIL}")
        
        server.quit()
        print("   ✅ Déconnexion")
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ ERREUR: Authentification échouée")
        print("   → Vérifiez votre email et votre mot de passe d'application")
        print("   → Assurez-vous d'avoir activé la 2FA sur votre compte Google")
        print("   → Régénérez votre mot de passe d'application")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ ERREUR SMTP: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False
    
    # Test d'envoi
    print("\n3️⃣  TEST D'ENVOI D'EMAIL:")
    try:
        notifier = EmailNotifier()
        
        subject = "Test Email - EPI Detection System"
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>🎉 Test Email</h1>
            <p>Si vous recevez cet email, votre configuration SMTP est correcte!</p>
            <hr>
            <p style="color: green; font-weight: bold;">✅ Configuration validée</p>
            <p>Vous pouvez maintenant configurer les rapports automatiques.</p>
        </body>
        </html>
        """
        
        # Envoyer à l'adresse de l'expéditeur par défaut
        recipient = config.SENDER_EMAIL
        
        success = notifier.send_email(recipient, subject, html_content)
        
        if success:
            print(f"   ✅ Email envoyé à {recipient}")
        else:
            print(f"   ❌ Erreur lors de l'envoi de l'email")
            return False
            
    except Exception as e:
        print(f"   ❌ ERREUR: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ TOUS LES TESTS RÉUSSIS!")
    print("="*60)
    print("\nProchaines étapes:")
    print("1. Vérifiez que vous avez reçu l'email de test")
    print("2. Configurez les destinataires dans .env.email")
    print("3. Définissez les horaires d'envoi des rapports")
    print("4. Activez les notifications automatiques")
    print("\n")
    
    return True

if __name__ == '__main__':
    success = test_smtp_connection()
    sys.exit(0 if success else 1)
