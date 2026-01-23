#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test des routes 404 fixées
"""
import sys
from pathlib import Path

# Ajouter le projet au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app.main import app
from app.database_unified import db, Detection, Alert, TrainingResult

def test_routes():
    """Vérifier que les routes existent"""
    print("=" * 70)
    print("🔍 VÉRIFICATION DES ROUTES FIXES")
    print("=" * 70)
    
    routes_to_check = [
        '/api/chart/alerts',
        '/api/chart/cumulative',
        '/training-results',
        '/api/training-results',
        '/api/training-results/latest',
    ]
    
    app_routes = {rule.rule: rule.methods for rule in app.url_map.iter_rules()}
    
    print("\n📋 Routes trouvées:\n")
    
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
    
    print("\n" + "=" * 70)
    
    if all_found:
        print("✅ TOUTES LES ROUTES EXISTENT!")
        print("=" * 70)
        return True
    else:
        print("❌ CERTAINES ROUTES MANQUENT!")
        print("=" * 70)
        return False

def test_database():
    """Vérifier la BD"""
    print("\n🗄️  VÉRIFICATION DE LA BASE DE DONNÉES")
    print("=" * 70)
    
    with app.app_context():
        try:
            # Test Detection
            det_count = Detection.query.count()
            print(f"  ✅ Detection table: {det_count} enregistrements")
            
            # Test Alert
            alert_count = Alert.query.count()
            print(f"  ✅ Alert table: {alert_count} enregistrements")
            
            # Test TrainingResult
            training_count = TrainingResult.query.count()
            print(f"  ✅ TrainingResult table: {training_count} enregistrements")
            
            print("\n✅ BD accessible et opérationnelle!")
            print("=" * 70)
            return True
            
        except Exception as e:
            print(f"❌ Erreur BD: {e}")
            print("=" * 70)
            return False

def test_endpoints():
    """Tester les endpoints avec le client de test"""
    print("\n🧪 TEST DES ENDPOINTS")
    print("=" * 70)
    
    with app.test_client() as client:
        tests = [
            ('GET', '/api/chart/alerts', {'days': '7'}),
            ('GET', '/api/chart/cumulative', {'days': '7'}),
            ('GET', '/api/training-results', {'limit': '10'}),
            ('GET', '/api/training-results/latest', {}),
            ('GET', '/training-results', {}),
        ]
        
        all_ok = True
        for method, endpoint, params in tests:
            try:
                if method == 'GET':
                    # Construire la query string
                    query = '&'.join([f"{k}={v}" for k, v in params.items()])
                    url = f"{endpoint}?{query}" if query else endpoint
                    
                    response = client.get(url)
                    status = response.status_code
                    
                    if status == 404:
                        print(f"  ❌ GET {endpoint:40s} → 404 NOT FOUND")
                        all_ok = False
                    elif status == 200:
                        print(f"  ✅ GET {endpoint:40s} → 200 OK")
                    else:
                        print(f"  ⚠️  GET {endpoint:40s} → {status}")
                        
            except Exception as e:
                print(f"  ❌ GET {endpoint:40s} → ERROR: {e}")
                all_ok = False
        
        print("\n" + "=" * 70)
        if all_ok:
            print("✅ TOUS LES ENDPOINTS RÉPONDENT!")
        else:
            print("⚠️  CERTAINS ENDPOINTS RETOURNENT DES ERREURS")
        print("=" * 70)
        return all_ok

if __name__ == '__main__':
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " FIX ROUTES 404 - TEST COMPLET ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    # Tests
    routes_ok = test_routes()
    db_ok = test_database()
    endpoints_ok = test_endpoints()
    
    # Résumé final
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " RÉSUMÉ ".center(68) + "║")
    print("╠" + "═" * 68 + "╣")
    print(f"║ Routes définies:        {'✅ OUI' if routes_ok else '❌ NON':50s} ║")
    print(f"║ Base de données:        {'✅ OUI' if db_ok else '❌ NON':50s} ║")
    print(f"║ Endpoints fonctionnels: {'✅ OUI' if endpoints_ok else '❌ NON':50s} ║")
    print("╠" + "═" * 68 + "╣")
    
    if routes_ok and db_ok and endpoints_ok:
        print("║" + " ✅ TOUT EST OPÉRATIONNEL! ".center(68) + "║")
        exit_code = 0
    else:
        print("║" + " ⚠️  DES PROBLÈMES À CORRIGER ".center(68) + "║")
        exit_code = 1
    
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    sys.exit(exit_code)
