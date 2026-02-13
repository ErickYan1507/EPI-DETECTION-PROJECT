#!/usr/bin/env python3
"""
Vérification de l'intégration complète du système email
"""

import sys
from pathlib import Path

def check_integration():
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION DE L'INTÉGRATION EMAIL")
    print("="*60 + "\n")
    
    checks = {
        "✅ Email routes registered": check_email_routes,
        "✅ API endpoints available": check_api_endpoints,
        "✅ Configuration files exist": check_config_files,
        "✅ Python packages installed": check_packages,
        "✅ .env.email filled in": check_env_filled,
    }
    
    results = {}
    for check_name, check_func in checks.items():
        try:
            success, message = check_func()
            status = "✅" if success else "❌"
            print(f"{status} {check_name}")
            if message:
                print(f"   └─ {message}\n")
            results[check_name] = success
        except Exception as e:
            print(f"❌ {check_name}")
            print(f"   └─ Erreur: {str(e)}\n")
            results[check_name] = False
    
    # Résumé
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("="*60)
    print(f"RÉSUMÉ: {passed}/{total} vérifications réussies\n")
    
    if passed == total:
        print("✅ L'intégration email est COMPLÈTE!")
        print("\n📋 PROCHAINES ÉTAPES:")
        print("  1. Lancez le serveur: python run.py --mode run")
        print("  2. Allez sur: http://127.0.0.1:5000/notifications")
        print("  3. Configurez SMTP Gmail dans l'interface")
        print("  4. Cliquez sur 'Test de connexion SMTP'")
        return True
    else:
        print("❌ Des vérifications ont échoué. Voir détails ci-dessus.")
        return False

def check_email_routes():
    """Vérifier que les routes email sont importées dans main.py"""
    main_file = Path("app/main.py").read_text(encoding='utf-8', errors='ignore')
    
    if "from app.routes_email_config import email_bp" in main_file:
        if "app.register_blueprint(email_bp)" in main_file:
            return True, "Routes email correctement intégrées dans main.py"
        return False, "Blueprint importé mais pas enregistré"
    return False, "Blueprint email_bp non importé dans main.py"

def check_api_endpoints():
    """Vérifier que le fichier des routes email existe et contient les endpoints"""
    routes_file = Path("app/routes_email_config.py")
    if not routes_file.exists():
        return False, "Fichier routes_email_config.py manquant"
    
    content = routes_file.read_text()
    endpoints = [
        '/config',
        '/test-connection',
        '/send-test',
        '/recipients',
        '/schedules',
        '/send-report',
        '/status',
        '/scheduler-status'
    ]
    
    found = sum(1 for ep in endpoints if ep in content)
    return found >= 7, f"{found}/8 endpoints trouvés"

def check_config_files():
    """Vérifier que les fichiers de configuration existent"""
    files_ok = True
    files = {
        ".env.email": "Configuration SMTP",
        "config.py": "Configuration Flask",
        "app/email_notifications.py": "Logique d'envoi email",
        "app/report_scheduler.py": "Scheduler APScheduler",
        "templates/notifications.html": "Interface web"
    }
    
    for file_path, description in files.items():
        p = Path(file_path)
        if not p.exists():
            print(f"   ❌ {file_path} - {description}")
            files_ok = False
    
    if files_ok:
        return True, "Tous les fichiers de configuration présents"
    return False, "Certains fichiers manquent (voir ci-dessus)"

def check_packages():
    """Vérifier que les packages Python requis sont installés"""
    packages = {
        'dotenv': 'python-dotenv',
        'apscheduler': 'APScheduler',
        'flask_sqlalchemy': 'Flask-SQLAlchemy'
    }
    
    missing = []
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        return False, f"Packages manquants: {', '.join(missing)}"
    return True, "Tous les packages requis sont installés"

def check_env_filled():
    """Vérifier que .env.email contient les vraies valeurs"""
    env_file = Path(".env.email")
    if not env_file.exists():
        return False, ".env.email n'existe pas"
    
    content = env_file.read_text(encoding='utf-8', errors='ignore')
    
    # Vérifier que ce ne sont pas des placeholders
    if "votremail@gmail.com" in content:
        return False, "SENDER_EMAIL contient encore un placeholder 'votremail@gmail.com'"
    
    if "SENDER_EMAIL=" in content:
        lines = content.split('\n')
        email_line = [l for l in lines if l.startswith('SENDER_EMAIL=')]
        if email_line and email_line[0].strip() == "SENDER_EMAIL=":
            return False, "SENDER_EMAIL est vide"
    
    return True, ".env.email semble être configuré"

if __name__ == "__main__":
    success = check_integration()
    sys.exit(0 if success else 1)
