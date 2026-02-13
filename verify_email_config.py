#!/usr/bin/env python3
"""
Vérification complète de la configuration email
Exécute tous les checks et affiche un rapport détaillé
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_section(title):
    """Affiche un titre de section"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_files_exist():
    """Vérifie que tous les fichiers existent"""
    print_section("✅ VÉRIFICATION DES FICHIERS")
    
    files = {
        '.env.email': '.env.email (Configuration)',
        'app/email_notifications.py': 'Code d\'envoi email',
        'app/report_scheduler.py': 'Scheduler des rapports',
        'config.py': 'Configuration Flask',
        'run.py': 'Script de démarrage',
        'test_email_config.py': 'Test SMTP',
        'setup_email_interactive.py': 'Assistant interactif',
        'GUIDE_EMAIL_SETUP.md': 'Documentation'
    }
    
    missing = []
    for filepath, description in files.items():
        full_path = project_root / filepath
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {description:40} {filepath}")
        if not exists:
            missing.append(filepath)
    
    return len(missing) == 0

def check_env_config():
    """Vérifie la configuration .env.email"""
    print_section("✅ VÉRIFICATION DE LA CONFIGURATION")
    
    env_file = project_root / '.env.email'
    if not env_file.exists():
        print("  ❌ Le fichier .env.email n'existe pas!")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'SENDER_EMAIL': 'Email d\'expédition',
        'SENDER_PASSWORD': 'Mot de passe app',
        'RECIPIENT_EMAILS': 'Email(s) destinataire(s)',
        'DAILY_REPORT_HOUR': 'Heure rapport quotidien',
    }
    
    all_good = True
    for key, description in checks.items():
        has_key = key in content
        has_value = f'{key}=' in content and f'{key}=votre' not in content
        
        if has_key and has_value:
            print(f"  ✅ {description:40} ({key})")
        else:
            print(f"  ❌ {description:40} ({key}) - NON CONFIGURÉ")
            all_good = False
    
    return all_good

def check_imports():
    """Vérifie que les imports fonctionnent"""
    print_section("✅ VÉRIFICATION DES IMPORTS")
    
    imports = [
        ('config', 'Config'),
        ('app.email_notifications', 'EmailNotifier'),
        ('app.report_scheduler', 'ReportScheduler'),
        ('apscheduler.schedulers.background', 'BackgroundScheduler'),
        ('dotenv', 'load_dotenv'),
    ]
    
    all_good = True
    for module_name, class_name in imports:
        try:
            if module_name == 'dotenv':
                __import__(module_name)
            else:
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
            print(f"  ✅ {module_name:50} ({class_name})")
        except ImportError as e:
            print(f"  ❌ {module_name:50} - {str(e)}")
            all_good = False
        except Exception as e:
            print(f"  ⚠️  {module_name:50} - {str(e)}")
    
    return all_good

def check_smtp_connection():
    """Teste la connexion SMTP"""
    print_section("✅ VÉRIFICATION DE LA CONNEXION SMTP")
    
    try:
        from config import config
    except Exception as e:
        print(f"  ❌ Impossible de charger config: {e}")
        return False
    
    # Vérifier les paramètres
    if not config.SENDER_EMAIL or not config.SENDER_PASSWORD:
        print("  ❌ SENDER_EMAIL ou SENDER_PASSWORD non configurés")
        return False
    
    print(f"  Email: {config.SENDER_EMAIL}")
    print(f"  Serveur: {config.SMTP_SERVER}:{config.SMTP_PORT}")
    
    try:
        import smtplib
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        print(f"  ✅ Connexion établie")
        
        server.starttls()
        print(f"  ✅ TLS activé")
        
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        print(f"  ✅ Authentification réussie")
        
        server.quit()
        print(f"  ✅ Déconnexion propre")
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("  ❌ Erreur d'authentification")
        print("     → Vérifiez 2FA sur Gmail")
        print("     → Régénérez le mot de passe application")
        return False
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def check_email_methods():
    """Vérifie les méthodes d'envoi email"""
    print_section("✅ VÉRIFICATION DES MÉTHODES EMAIL")
    
    try:
        from app.email_notifications import EmailNotifier
        
        methods = [
            'send_email',
            'generate_daily_report',
            'generate_weekly_report',
            'generate_monthly_report',
        ]
        
        all_good = True
        for method in methods:
            if hasattr(EmailNotifier, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method} - MANQUANT")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"  ❌ Impossible charger EmailNotifier: {e}")
        return False

def check_scheduler():
    """Vérifie le scheduler"""
    print_section("✅ VÉRIFICATION DU SCHEDULER")
    
    try:
        from app.report_scheduler import ReportScheduler
        
        methods = [
            'setup_jobs',
            'send_daily_report',
            'send_weekly_report',
            'send_monthly_report',
            'start',
            'stop',
        ]
        
        all_good = True
        for method in methods:
            if hasattr(ReportScheduler, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method} - MANQUANT")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"  ❌ Impossible charger ReportScheduler: {e}")
        return False

def check_run_py():
    """Vérifie que run.py a été mis à jour"""
    print_section("✅ VÉRIFICATION DE run.py")
    
    run_file = project_root / 'run.py'
    with open(run_file, 'r') as f:
        content = f.read()
    
    checks = {
        'init_report_scheduler': 'Initialiseur du scheduler',
        'get_report_scheduler': 'Getter du scheduler',
        'shutdown_scheduler': 'Arrêt du scheduler',
        'atexit': 'Hook d\'arrêt',
    }
    
    all_good = True
    for keyword, description in checks.items():
        if keyword in content:
            print(f"  ✅ {description:40} ({keyword})")
        else:
            print(f"  ❌ {description:40} ({keyword}) - MANQUANT")
            all_good = False
    
    return all_good

def main():
    """Fonction principale"""
    
    print("\n" + "="*70)
    print("  📧 VÉRIFICATION COMPLÈTE - CONFIGURATION EMAIL")
    print("="*70)
    
    results = {
        'Fichiers': check_files_exist(),
        'Configuration': check_env_config(),
        'Imports': check_imports(),
        'SMTP': check_smtp_connection(),
        'Méthodes Email': check_email_methods(),
        'Scheduler': check_scheduler(),
        'run.py': check_run_py(),
    }
    
    # Résumé
    print_section("📊 RÉSUMÉ FINAL")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for check, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    print(f"\n  Score: {passed}/{total} vérifications réussies")
    
    if passed == total:
        print("\n" + "="*70)
        print("  ✅ CONFIGURATION COMPLÈTE ET OPÉRATIONNELLE!")
        print("="*70)
        print("\n  Prochaines étapes:")
        print("  1. Éditer .env.email avec votre config")
        print("  2. Exécuter: python setup_email_interactive.py")
        print("  3. Lancer: python run.py --mode run")
        print("\n")
        return 0
    else:
        print("\n" + "="*70)
        print("  ❌ CERTAINES VÉRIFICATIONS ONT ÉCHOUÉ")
        print("="*70)
        print("\n  Vérifiez les erreurs ci-dessus et relancez cette vérification\n")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
