#!/usr/bin/env python3
"""
Quick Start - Configuration Email Interactive
Guidance interactive pour configurer l'envoi d'emails
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def display_banner():
    """Affiche le banner"""
    print("\n" + "="*70)
    print("📧 ASSISTANT DE CONFIGURATION EMAIL - EPI DETECTION")
    print("="*70 + "\n")

def step1_gmail_prep():
    """Étape 1: Préparer Gmail"""
    print("ÉTAPE 1: Préparer votre compte Gmail")
    print("-" * 70)
    print("""
✅ Vous devez avoir un compte Gmail avec:
   1. Vérification en 2 étapes ACTIVÉE
   2. Un mot de passe d'application généré (16 caractères)

📍 Si ce n'est pas fait:
   1. Allez sur https://myaccount.google.com/
   2. Cliquez "Sécurité" → "Vérification en 2 étapes" → Activez
   3. Cliquez "Sécurité" → "Mots de passe des applications"
   4. Sélectionnez "Mail" et "Windows"
   5. Cliquez "Générer"
   6. Copiez le mot de passe (format: abcd efgh ijkl mnop)

Avez-vous généré votre mot de passe d'application? (oui/non): """)
    
    response = input().lower().strip()
    return response in ['oui', 'o', 'yes', 'y']

def step2_config_env():
    """Étape 2: Configuration du fichier .env.email"""
    print("\nÉTAPE 2: Configurer le fichier .env.email")
    print("-" * 70)
    
    env_file = Path(__file__).parent / '.env.email'
    
    if not env_file.exists():
        print("❌ Le fichier .env.email n'existe pas!")
        return False
    
    print(f"📍 Fichier à éditer: {env_file}\n")
    
    # Lire le fichier actuel
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Afficher le modèle
    print("Voici les champs à remplir:")
    print("""
    SENDER_EMAIL=votre.email@gmail.com
    SENDER_PASSWORD=abcdefghijklmnop
    RECIPIENT_EMAILS=admin@company.com,manager@company.com
    DAILY_REPORT_HOUR=08
    """)
    
    print("""
💡 AIDE:
   • SENDER_EMAIL: Votre email Gmail (celui avec 2FA)
   • SENDER_PASSWORD: Le mot de passe d'application (16 caractères)
   • RECIPIENT_EMAILS: Emails pour recevoir rapports (séparés par virgules)
   • DAILY_REPORT_HOUR: Heure d'envoi (0-23, ex: 08 = 8h du matin)

📝 Modifiez le fichier: .env.email
   Puis revenez ici et tapez "oui"

Avez-vous configuré .env.email? (oui/non): """)
    
    response = input().lower().strip()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("Ouvrez le fichier avec: notepad .env.email (sous Windows)")
        return False
    
    return True

def step3_test_connection():
    """Étape 3: Tester la connexion"""
    print("\nÉTAPE 3: Tester la connexion SMTP")
    print("-" * 70)
    print("Lancement du test de connexion...\n")
    
    # Charger la config
    from config import config
    
    # Vérifier les paramètres
    if not config.SENDER_EMAIL or not config.SENDER_PASSWORD:
        print("❌ ERREUR: Email ou mot de passe not configurés dans .env.email")
        return False
    
    print(f"✅ Email: {config.SENDER_EMAIL}")
    print(f"✅ Serveur: {config.SMTP_SERVER}:{config.SMTP_PORT}")
    
    # Tester la connexion
    try:
        import smtplib
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        server.quit()
        print("\n✅ CONNEXION RÉUSSIE!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ ERREUR: Authentification échouée")
        print("   → Vérifiez l'email et le mot de passe d'application")
        print("   → Assurez-vous d'avoir activé la 2FA sur Gmail")
        return False
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False

def step4_send_test_email():
    """Étape 4: Envoyer un email test"""
    print("\nÉTAPE 4: Envoyer un email test")
    print("-" * 70)
    
    from config import config
    from app.email_notifications import EmailNotifier
    
    print("Envoi d'un email test...\n")
    
    try:
        notifier = EmailNotifier()
        
        subject = "🎉 Test Email - EPI Detection System"
        html = """
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <h1 style="color: #8B1538;">🎉 Configuration Réussie</h1>
            <p>Cet email confirme que votre configuration SMTP fonctionne correctement!</p>
            <hr>
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
                <p><strong>Prochaines étapes:</strong></p>
                <ul>
                    <li>✅ Configuration SMTP testée</li>
                    <li>📧 Rapports quotidiens configurés</li>
                    <li>🔔 Alertes automatiques activées</li>
                    <li>📊 Rapports attendus selon l'horaire défini</li>
                </ul>
            </div>
            <p style="color: green; margin-top: 20px;"><strong>Vous pouvez maintenant fermer cet assistant!</strong></p>
        </body>
        </html>
        """
        
        recipient = config.SENDER_EMAIL
        success = notifier.send_email(recipient, subject, html)
        
        if success:
            print(f"✅ Email envoyé à {recipient} avec succès!")
            print("\n📬 Vérifiez votre boîte mail (Gmail ou SPAM)")
            return True
        else:
            print("❌ Erreur lors de l'envoi")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

def step5_final_setup():
    """Étape 5: Configuration finale"""
    print("\nÉTAPE 5: Configuration Finale")
    print("-" * 70)
    print("""
🎉 Configuration Email Complétée!

Les rapports suivants seront envoyés automatiquement:

📊 RAPPORTS CONFIGURÉS:
   • Rapport quotidien → Chaque jour à DAILY_REPORT_HOUR
   • Rapport hebdomadaire → Chaque WEEKLY_REPORT_DAY à WEEKLY_REPORT_HOUR
   • Rapport mensuel → Le MONTHLY_REPORT_DAY à MONTHLY_REPORT_HOUR
   • Alertes d'alerte → Quand compliance < ALERT_THRESHOLD

📧 DESTINATAIRES:
   • Les emails iront à: RECIPIENT_EMAILS (configurés dans .env.email)

🔧 POUR MODIFIER:
   • Éditez le fichier: .env.email
   • Puis redémarrez le serveur Flask

📝 DOCUMENTATION:
   Pour plus d'aide, consultez: GUIDE_EMAIL_SETUP.md

✅ Tout est prêt!
""")

def main():
    """Fonction principale"""
    display_banner()
    
    # Étape 1
    if not step1_gmail_prep():
        print("\n❌ Veuillez d'abord préparer votre compte Gmail")
        print("   Voir: https://myaccount.google.com/")
        sys.exit(1)
    
    # Étape 2
    if not step2_config_env():
        print("\n❌ Veuillez configurer le fichier .env.email")
        print("   Ouvrez: .env.email (avec notepad ou VS Code)")
        sys.exit(1)
    
    # Étape 3
    if not step3_test_connection():
        print("\n❌ La connexion SMTP n'a pas fonctionné")
        print("   Vérifiez .env.email et relancez ce script")
        sys.exit(1)
    
    # Étape 4
    if not step4_send_test_email():
        print("\n⚠️  Impossible d'envoyer l'email test")
        print("   Vérifiez les logs: logs/app.log")
        sys.exit(1)
    
    # Étape 5
    step5_final_setup()
    
    print("\n" + "="*70)
    print("✅ CONFIGURATION TERMINÉE!")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Configuration annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
