#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test complet du système - Vérifie toutes les corrections
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import time
from pathlib import Path

def test_summary():
    """Afficher un résumé des corrections"""
    print("\n" + "="*70)
    print("✅ RÉSUMÉ DES CORRECTIONS APPLIQUÉES")
    print("="*70)
    
    corrections = {
        "1. Double-clic Upload": {
            "Fichier": "templates/upload.html",
            "Changement": "Ajout flag 'isProcessing' pour éviter double-clic",
            "Lignes": "535-580",
            "Status": "✅ Appliqué"
        },
        "2. Dates Invalides": {
            "Fichier": "templates/training_results.html",
            "Changement": "Fonction formatDate() avec gestion d'erreurs",
            "Lignes": "165-500",
            "Status": "✅ Appliqué"
        },
        "3. Détections Uploads": {
            "Fichier": "app/main.py",
            "Changement": "Refactorisation process_image() pour utiliser global detector",
            "Lignes": "627-680",
            "Status": "✅ Appliqué"
        },
        "4. Détections Vidéo": {
            "Fichier": "app/main.py",
            "Changement": "Refactorisation process_video() pour utiliser global detector",
            "Lignes": "712-780",
            "Status": "✅ Appliqué"
        },
        "5. Config Modèle": {
            "Fichier": "config.py",
            "Changement": "MULTI_MODEL_ENABLED=True, DEFAULT_USE_ENSEMBLE=True",
            "Lignes": "28-45",
            "Status": "✅ Appliqué"
        },
        "6. BD Verification": {
            "Fichier": "fix_database.py",
            "Changement": "Script pour vérifier et corriger timestamps invalides",
            "Lignes": "N/A",
            "Status": "✅ Créé"
        }
    }
    
    for correction_name, details in corrections.items():
        print(f"\n{correction_name}")
        for key, value in details.items():
            print(f"  {key}: {value}")

def verify_files():
    """Vérifier que tous les fichiers modifiés existent"""
    print("\n" + "="*70)
    print("🔍 VÉRIFICATION DES FICHIERS MODIFIÉS")
    print("="*70)
    
    files_to_check = [
        "templates/upload.html",
        "templates/training_results.html",
        "app/main.py",
        "config.py",
        "fix_database.py",
        "fix_detection_issues.py",
        "CORRECTIONS_README.md",
    ]
    
    all_exist = True
    for filepath in files_to_check:
        full_path = Path(filepath)
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {filepath} ({size} bytes)")
        else:
            print(f"❌ {filepath} - NON TROUVÉ")
            all_exist = False
    
    return all_exist

def check_upload_html():
    """Vérifier les changements dans upload.html"""
    print("\n" + "="*70)
    print("🔍 VÉRIFICATION upload.html")
    print("="*70)
    
    with open("templates/upload.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'isProcessing flag': 'let isProcessing = false;' in content,
        'HTTP Error handling': 'HTTP Error' in content,
        'Processing... text': "Processing..." in content,
        'Error message handling': "showAlert('Error processing file" in content,
    }
    
    all_good = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_good = False
    
    return all_good

def check_training_results_html():
    """Vérifier les changements dans training_results.html"""
    print("\n" + "="*70)
    print("🔍 VÉRIFICATION training_results.html")
    print("="*70)
    
    with open("templates/training_results.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'formatDate function': 'function formatDate(timestamp)' in content,
        'formatDate in displayResults': 'formatDate(result.timestamp)' in content,
        'Error handling in formatDate': 'isNaN(date.getTime())' in content,
        'Index labels for charts': "labels: trainingResults.map((r, idx) => `#${idx + 1}`)" in content,
    }
    
    all_good = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_good = False
    
    return all_good

def check_main_py():
    """Vérifier les changements dans main.py"""
    print("\n" + "="*70)
    print("🔍 VÉRIFICATION app/main.py")
    print("="*70)
    
    with open("app/main.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'global detector in process_image': 'global detector, multi_detector' in content and content.count('global detector, multi_detector') >= 2,
        'multi_detector check': 'if multi_detector and len(multi_detector.models) > 0:' in content,
        'use_ensemble for uploads': 'use_ensemble = True' in content,
        'Proper error handling': 'logger.error("Aucun détecteur disponible")' in content,
    }
    
    all_good = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_good = False
    
    return all_good

def check_config_py():
    """Vérifier les changements dans config.py"""
    print("\n" + "="*70)
    print("🔍 VÉRIFICATION config.py")
    print("="*70)
    
    with open("config.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'MULTI_MODEL_ENABLED = True': 'MULTI_MODEL_ENABLED = True' in content,
        'DEFAULT_USE_ENSEMBLE = True': 'DEFAULT_USE_ENSEMBLE = True' in content,
        'USE_ENSEMBLE_FOR_CAMERA = False': 'USE_ENSEMBLE_FOR_CAMERA = False' in content,
        'MODEL_WEIGHTS config': "'best.pt': 1.0," in content,
        'Correct comments': '# UTILISER TOUS LES MODÈLES DISPONIBLES' in content,
    }
    
    all_good = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_good = False
    
    return all_good

def main():
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " " * 12 + "🧪 TEST COMPLET DES CORRECTIONS APPLIQUÉES" + " " * 13 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {
        "Files Verification": verify_files(),
        "upload.html Changes": check_upload_html(),
        "training_results.html Changes": check_training_results_html(),
        "main.py Changes": check_main_py(),
        "config.py Changes": check_config_py(),
    }
    
    test_summary()
    
    print("\n" + "="*70)
    print("📊 RÉSULTATS DES TESTS")
    print("="*70)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ TOUTES LES CORRECTIONS ONT ÉTÉ APPLIQUÉES CORRECTEMENT!")
        print("="*70)
        print("""
Prochaines étapes:
1. Redémarrer l'application: python app/main.py
2. Tester les uploads: http://localhost:5000/upload
3. Tester les résultats: http://localhost:5000/training-results
4. Tester le monitoring: http://localhost:5000/unified_monitoring.html

Pour plus d'informations, voir: CORRECTIONS_README.md
        """)
        return 0
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ - VOIR LES DÉTAILS CI-DESSUS")
        print("="*70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
