#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test du système après fixes
"""
import sys
from pathlib import Path

# Ajouter le projet au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app.main import app, process_image, process_video
from app.database_unified import db, Detection

def test_imports():
    """Tester les imports"""
    print("=" * 70)
    print("📦 TEST DES IMPORTS")
    print("=" * 70)
    
    tests = [
        ('app.main', 'app'),
        ('app.main', 'process_image'),
        ('app.main', 'process_video'),
        ('app.database_unified', 'db'),
        ('app.database_unified', 'Detection'),
    ]
    
    all_ok = True
    for module, name in tests:
        try:
            exec(f"from {module} import {name}")
            print(f"  ✅ {name:30s} from {module}")
        except ImportError as e:
            print(f"  ❌ {name:30s} from {module} - {e}")
            all_ok = False
    
    print("=" * 70)
    return all_ok

def test_routes():
    """Tester les routes"""
    print("\n🛣️  TEST DES ROUTES")
    print("=" * 70)
    
    routes_to_check = [
        '/upload',
        '/api/detect',
        '/api/detections',
        '/api/chart/alerts',
        '/api/chart/cumulative',
        '/training-results',
        '/api/training-results',
    ]
    
    app_routes = {rule.rule: rule.methods for rule in app.url_map.iter_rules()}
    
    all_found = True
    for route in routes_to_check:
        found = False
        for app_route in app_routes.keys():
            if route in app_route:
                methods = ', '.join(app_routes[app_route])
                print(f"  ✅ {app_route:40s} [{methods}]")
                found = True
                break
        
        if not found:
            print(f"  ❌ {route:40s} [NOT FOUND]")
            all_found = False
    
    print("=" * 70)
    return all_found

def test_functions():
    """Tester les fonctions critiques"""
    print("\n⚙️  TEST DES FONCTIONS")
    print("=" * 70)
    
    functions = [
        ('process_image', process_image),
        ('process_video', process_video),
    ]
    
    all_ok = True
    for name, func in functions:
        try:
            if callable(func):
                print(f"  ✅ {name:30s} est callable")
            else:
                print(f"  ❌ {name:30s} n'est pas callable")
                all_ok = False
        except Exception as e:
            print(f"  ❌ {name:30s} - {e}")
            all_ok = False
    
    print("=" * 70)
    return all_ok

def test_database():
    """Tester la BD"""
    print("\n🗄️  TEST DE LA BASE DE DONNÉES")
    print("=" * 70)
    
    with app.app_context():
        try:
            # Test connexion
            det_count = Detection.query.count()
            print(f"  ✅ Connexion BD OK")
            print(f"  ✅ Detection table: {det_count} enregistrements")
            
            print("=" * 70)
            return True
            
        except Exception as e:
            print(f"  ❌ Erreur BD: {e}")
            print("=" * 70)
            return False

def test_endpoints():
    """Tester les endpoints"""
    print("\n🧪 TEST DES ENDPOINTS")
    print("=" * 70)
    
    with app.test_client() as client:
        tests = [
            ('GET', '/api/chart/alerts'),
            ('GET', '/api/chart/cumulative'),
            ('GET', '/api/training-results'),
            ('GET', '/training-results'),
        ]
        
        all_ok = True
        for method, endpoint in tests:
            try:
                response = client.get(endpoint)
                status = response.status_code
                
                if status == 404:
                    print(f"  ❌ {endpoint:40s} → 404 NOT FOUND")
                    all_ok = False
                elif status == 200:
                    print(f"  ✅ {endpoint:40s} → 200 OK")
                else:
                    print(f"  ⚠️  {endpoint:40s} → {status}")
                        
            except Exception as e:
                print(f"  ❌ {endpoint:40s} → ERROR: {e}")
                all_ok = False
        
        print("=" * 70)
        return all_ok

def main():
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " TEST SYSTÈME COMPLET ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    # Tests
    imports_ok = test_imports()
    routes_ok = test_routes()
    functions_ok = test_functions()
    db_ok = test_database()
    endpoints_ok = test_endpoints()
    
    # Résumé final
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " RÉSUMÉ FINAL ".center(68) + "║")
    print("╠" + "═" * 68 + "╣")
    print(f"║ Imports:            {'✅ OK' if imports_ok else '❌ FAIL':50s} ║")
    print(f"║ Routes:             {'✅ OK' if routes_ok else '❌ FAIL':50s} ║")
    print(f"║ Fonctions:          {'✅ OK' if functions_ok else '❌ FAIL':50s} ║")
    print(f"║ Base de données:    {'✅ OK' if db_ok else '❌ FAIL':50s} ║")
    print(f"║ Endpoints:          {'✅ OK' if endpoints_ok else '❌ FAIL':50s} ║")
    print("╠" + "═" * 68 + "╣")
    
    all_ok = imports_ok and routes_ok and functions_ok and db_ok and endpoints_ok
    
    if all_ok:
        print("║" + " ✅ SYSTÈME PRÊT POUR LA PRODUCTION! ".center(68) + "║")
        exit_code = 0
    else:
        print("║" + " ⚠️  DES PROBLÈMES À CORRIGER ".center(68) + "║")
        exit_code = 1
    
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
