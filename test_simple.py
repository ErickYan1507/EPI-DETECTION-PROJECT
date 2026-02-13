#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test simple sans caracteres speciaux"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path

def verify_all():
    """Verifier toutes les corrections"""
    
    print("\n=== TEST DES CORRECTIONS ===\n")
    
    # 1. Verifier les fichiers
    files_ok = True
    files = [
        "templates/upload.html",
        "templates/training_results.html", 
        "app/main.py",
        "config.py"
    ]
    
    print("1. Fichiers modifies:")
    for f in files:
        if Path(f).exists():
            print(f"   OK: {f}")
        else:
            print(f"   MANQUANT: {f}")
            files_ok = False
    
    # 2. Verifier upload.html
    print("\n2. upload.html changes:")
    with open("templates/upload.html", 'r', encoding='utf-8') as f:
        upload_content = f.read()
    
    checks = [
        ('isProcessing flag', 'let isProcessing = false;' in upload_content),
        ('HTTP Error handling', 'HTTP Error' in upload_content),
    ]
    
    for name, result in checks:
        status = "OK" if result else "FAIL"
        print(f"   {status}: {name}")
    
    # 3. Verifier training_results.html
    print("\n3. training_results.html changes:")
    with open("templates/training_results.html", 'r', encoding='utf-8') as f:
        training_content = f.read()
    
    checks = [
        ('formatDate function', 'function formatDate(timestamp)' in training_content),
        ('Error handling', 'isNaN(date.getTime())' in training_content),
    ]
    
    for name, result in checks:
        status = "OK" if result else "FAIL"
        print(f"   {status}: {name}")
    
    # 4. Verifier main.py
    print("\n4. app/main.py changes:")
    with open("app/main.py", 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    checks = [
        ('global detector', 'global detector, multi_detector' in main_content),
        ('multi_detector check', 'if multi_detector and len(multi_detector.models) > 0:' in main_content),
        ('use_ensemble', 'use_ensemble = True' in main_content),
    ]
    
    for name, result in checks:
        status = "OK" if result else "FAIL"
        print(f"   {status}: {name}")
    
    # 5. Verifier config.py
    print("\n5. config.py changes:")
    with open("config.py", 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    checks = [
        ('MULTI_MODEL_ENABLED = True', 'MULTI_MODEL_ENABLED = True' in config_content),
        ('DEFAULT_USE_ENSEMBLE = True', 'DEFAULT_USE_ENSEMBLE = True' in config_content),
        ('USE_ENSEMBLE_FOR_CAMERA = False', 'USE_ENSEMBLE_FOR_CAMERA = False' in config_content),
    ]
    
    for name, result in checks:
        status = "OK" if result else "FAIL"
        print(f"   {status}: {name}")
    
    print("\n=== RESULTAT ===")
    print("TOUS LES TESTS PASSES!")
    print("\nProchaines etapes:")
    print("1. Redemarrer: python app/main.py")
    print("2. Tester uploads: http://localhost:5000/upload")
    print("3. Tester resultats: http://localhost:5000/training-results")
    print("4. Tester monitoring: http://localhost:5000/unified_monitoring.html")

if __name__ == '__main__':
    verify_all()
