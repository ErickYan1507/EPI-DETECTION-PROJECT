#!/usr/bin/env python3
"""
Script de vérification du système de notifications
Vérifie que tous les fichiers sont en place et que l'API est accessible
"""

import os
import sys
import json
from pathlib import Path
import subprocess

# Couleurs
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(title):
    """Print une en-tête"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{title:^60}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def check_file_exists(filepath, description):
    """Vérifier l'existence d'un fichier"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"{Colors.GREEN}✓{Colors.END} {description}")
        print(f"  Path: {filepath}")
        print(f"  Size: {size:,} bytes")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {description}")
        print(f"  Path: {filepath} (NOT FOUND)")
        return False

def check_imports():
    """Vérifier que les imports fonctionnent"""
    try:
        from app.notification_service import notification_service
        print(f"{Colors.GREEN}✓{Colors.END} notification_service.py importable")
        return True
    except ImportError as e:
        print(f"{Colors.RED}✗{Colors.END} Erreur import notification_service.py")
        print(f"  Error: {e}")
        return False

def check_database_files():
    """Vérifier les fichiers de données"""
    base_path = Path('.')
    
    files_to_check = [
        ('.notification_config.json', 'Configuration des notifications'),
        ('.notification_recipients', 'Fichier destinataires'),
        ('.notifications_db.json', 'Base de données historique'),
    ]
    
    results = []
    for filename, description in files_to_check:
        filepath = base_path / filename
        exists = filepath.exists()
        status = f"{Colors.GREEN}✓ EXISTS{Colors.END}" if exists else f"{Colors.YELLOW}○ NOT YET{Colors.END}"
        print(f"{status} {filename}")
        if exists:
            try:
                size = filepath.stat().st_size
                print(f"       ({size} bytes)")
            except:
                pass
        results.append((filename, exists))
    
    return all(exists for _, exists in results)

def check_main_py_integration():
    """Vérifier l'intégration dans main.py"""
    main_py_path = Path('app/main.py')
    
    if not main_py_path.exists():
        print(f"{Colors.RED}✗{Colors.END} app/main.py not found")
        return False
    
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('from app.routes_notification_api import notification_api_bp', 'Import blueprint'),
        ('app.register_blueprint(notification_api_bp)', 'Register blueprint'),
    ]
    
    results = []
    for search_str, description in checks:
        if search_str in content:
            print(f"{Colors.GREEN}✓{Colors.END} {description}")
            results.append(True)
        else:
            print(f"{Colors.RED}✗{Colors.END} {description}")
            print(f"  Expected: {search_str}")
            results.append(False)
    
    return all(results)

def check_python_version():
    """Vérifier la version Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print(f"{Colors.GREEN}✓{Colors.END} Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} Python {version.major}.{version.minor} (requires 3.6+)")
        return False

def check_flask():
    """Vérifier Flask"""
    try:
        import flask
        print(f"{Colors.GREEN}✓{Colors.END} Flask {flask.__version__}")
        return True
    except ImportError:
        print(f"{Colors.RED}✗{Colors.END} Flask not installed")
        return False

def test_api_endpoints():
    """Tester les endpoints API"""
    print(f"\n{Colors.YELLOW}Note: Run this after starting Flask app{Colors.END}")
    print("Command: python examples_notifications_api.py --quick")

def print_summary(results):
    """Imprimer un résumé"""
    print_header("RÉSUMÉ DE LA VÉRIFICATION")
    
    total = len(results)
    passed = sum(1 for r in results if r)
    failed = total - passed
    
    print(f"\nTotal: {total} checks")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    if failed > 0:
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}✓ Tout vérifié! Système prêt à être utilisé.{Colors.END}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"\n{Colors.BLUE}Prochaines étapes:{Colors.END}")
        print("1. Démarrez l'application: python run.py")
        print("2. Accédez à: http://localhost:5000/notifications")
        print("3. Configurez l'email expéditeur")
        print("4. Ajoutez les destinataires")
        print("5. Testez l'envoi!")
    else:
        print(f"\n{Colors.RED}{'='*60}{Colors.END}")
        print(f"{Colors.RED}✗ Certaines vérifications ont échoué.{Colors.END}")
        print(f"{Colors.RED}{'='*60}{Colors.END}")
        print(f"\n{Colors.BLUE}Actions recommandées:{Colors.END}")
        print("1. Vérifiez les messages d'erreur ci-dessus")
        print("2. Re-exécutez ce script après correction")
        print("3. Consultez QUICKSTART_NOTIFICATIONS.md pour l'aide")
    
    print()
    return failed == 0

def main():
    """Fonction principale"""
    
    print(f"""
{Colors.GREEN}
╔════════════════════════════════════════════════════════════╗
║     Vérification du Système de Notifications EPI Detection  ║
╚════════════════════════════════════════════════════════════╝
{Colors.END}
    """)
    
    results = []
    
    # Vérifications de fichiers
    print_header("FICHIERS PYTHON")
    
    files_to_check = [
        ('app/notification_service.py', 'Service de notifications'),
        ('app/routes_notification_api.py', 'Routes API'),
        ('templates/notifications.html', 'Interface web'),
    ]
    
    for filepath, description in files_to_check:
        results.append(check_file_exists(filepath, description))
    
    # Vérifications d'intégration
    print_header("INTÉGRATION")
    results.append(check_main_py_integration())
    
    # Vérifications de dépendances
    print_header("DÉPENDANCES")
    results.append(check_python_version())
    results.append(check_flask())
    results.append(check_imports())
    
    # Vérifications de fichiers de données
    print_header("FICHIERS DE DONNÉES")
    check_database_files()  # Ne compte pas pour le résumé (optionnel)
    
    # Test API
    print_header("TESTS API")
    test_api_endpoints()
    
    # Résumé
    all_passed = print_summary(results)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
