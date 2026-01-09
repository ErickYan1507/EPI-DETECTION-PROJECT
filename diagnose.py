#!/usr/bin/env python
"""
Script de diagnostic automatique pour problèmes de détection
"""
import os
import sys
import subprocess
from pathlib import Path
import glob

def check_header(title):
    """Afficher un en-tête"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}\n")

def check_success(condition, message_ok, message_fail):
    """Vérifier une condition et afficher le résultat"""
    if condition:
        print(f"✓ {message_ok}")
        return True
    else:
        print(f"✗ {message_fail}")
        return False

def main():
    """Diagnostic complet"""
    print("\n" + "="*60)
    print("DIAGNOSTIC AUTOMATIQUE - EPI DETECTION")
    print("="*60)
    
    results = []
    
    # 1. Vérifier Python
    check_header("1. Version Python")
    python_version = sys.version.split()[0]
    print(f"Python version: {python_version}")
    py_ok = sys.version_info >= (3, 8)
    results.append(check_success(py_ok, "Python >= 3.8", "Python trop ancien"))
    
    # 2. Vérifier les fichiers essentiels
    check_header("2. Fichiers Essentiels")
    essential_files = [
        'config.py',
        'app/main.py',
        'app/detection.py',
        'app/multi_model_detector.py',
        'templates/unified_monitoring.html'
    ]
    files_ok = True
    for file in essential_files:
        exists = Path(file).exists()
        check_success(exists, f"{file} existe", f"{file} MANQUANT")
        files_ok = files_ok and exists
    results.append(files_ok)
    
    # 3. Vérifier les modèles
    check_header("3. Modèles Disponibles")
    models_dir = Path('models')
    if models_dir.exists():
        model_files = list(models_dir.glob('*.pt'))
        print(f"Dossier models/ existe: {len(model_files)} modèles trouvés")
        for model in model_files:
            print(f"  - {model.name} ({model.stat().st_size / 1024 / 1024:.1f} MB)")
        models_ok = len(model_files) > 0
        check_success(models_ok, f"{len(model_files)} modèle(s) disponible(s)", "AUCUN modèle trouvé!")
        results.append(models_ok)
    else:
        print("✗ Dossier models/ n'existe pas!")
        results.append(False)
    
    # 4. Vérifier les dépendances
    check_header("4. Dépendances Python")
    dependencies = {
        'torch': 'PyTorch',
        'cv2': 'OpenCV',
        'flask': 'Flask',
        'numpy': 'NumPy'
    }
    deps_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} installé")
        except ImportError:
            print(f"✗ {name} MANQUANT")
            deps_ok = False
    results.append(deps_ok)
    
    # 5. Vérifier la configuration
    check_header("5. Configuration")
    try:
        from config import config
        print(f"✓ config.py chargé")
        print(f"  - MULTI_MODEL_ENABLED: {config.MULTI_MODEL_ENABLED}")
        print(f"  - MODELS_FOLDER: {config.MODELS_FOLDER}")
        print(f"  - CONFIDENCE_THRESHOLD: {config.CONFIDENCE_THRESHOLD}")
        print(f"  - USE_ENSEMBLE_FOR_CAMERA: {config.USE_ENSEMBLE_FOR_CAMERA}")
        results.append(True)
    except Exception as e:
        print(f"✗ Erreur chargement config: {e}")
        results.append(False)
    
    # 6. Test du MultiModelDetector
    check_header("6. Test MultiModelDetector")
    try:
        from app.multi_model_detector import MultiModelDetector
        detector = MultiModelDetector(use_ensemble=False)
        print(f"✓ MultiModelDetector créé")
        print(f"  - Nombre de modèles: {len(detector.models)}")
        print(f"  - Mode ensemble: {detector.use_ensemble}")
        
        model_list = detector.get_model_list()
        for model in model_list:
            print(f"  - {model['name']} (poids: {model['weight']})")
        
        results.append(True)
    except Exception as e:
        print(f"✗ Erreur initialisation: {e}")
        import traceback
        traceback.print_exc()
        results.append(False)
    
    # 7. Test de détection sur image
    check_header("7. Test Détection sur Image")
    test_images = ['images/aa.jpg', 'aa.jpg', 'a.jpg']
    test_image = None
    for img in test_images:
        if Path(img).exists():
            test_image = img
            break
    
    if test_image:
        print(f"Image de test: {test_image}")
        try:
            import cv2
            from app.multi_model_detector import MultiModelDetector
            
            detector = MultiModelDetector(use_ensemble=False)
            image = cv2.imread(test_image)
            
            if image is not None:
                detections, stats = detector.detect(image)
                print(f"✓ Détection réussie")
                print(f"  - Détections: {len(detections)}")
                print(f"  - Personnes: {stats.get('total_persons', 0)}")
                print(f"  - Casques: {stats.get('with_helmet', 0)}")
                print(f"  - Conformité: {stats.get('compliance_rate', 0):.1f}%")
                print(f"  - Temps: {stats.get('total_ms', 0):.1f}ms")
                results.append(True)
            else:
                print(f"✗ Impossible de charger l'image")
                results.append(False)
        except Exception as e:
            print(f"✗ Erreur détection: {e}")
            results.append(False)
    else:
        print("⚠ Aucune image de test trouvée (optionnel)")
        results.append(None)
    
    # 8. Vérifier le serveur Flask
    check_header("8. Serveur Flask")
    try:
        import requests
        response = requests.get('http://localhost:5000/api/health', timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Serveur Flask en ligne")
            print(f"  - Status: {data.get('status')}")
            print(f"  - Version: {data.get('version')}")
            print(f"  - Models loaded: {data.get('models_loaded')}")
            results.append(True)
        else:
            print(f"✗ Serveur répond avec code {response.status_code}")
            results.append(False)
    except requests.exceptions.ConnectionError:
        print(f"✗ Serveur Flask non démarré")
        print(f"  Démarrer avec: python run_app.py")
        results.append(False)
    except Exception as e:
        print(f"✗ Erreur: {e}")
        results.append(False)
    
    # Résumé
    check_header("RÉSUMÉ DU DIAGNOSTIC")
    
    checks = [
        "Python version",
        "Fichiers essentiels",
        "Modèles disponibles",
        "Dépendances",
        "Configuration",
        "MultiModelDetector",
        "Test détection",
        "Serveur Flask"
    ]
    
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)
    
    for check, result in zip(checks, results):
        if result is True:
            print(f"✓ {check}")
        elif result is False:
            print(f"✗ {check}")
        else:
            print(f"⊘ {check} (ignoré)")
    
    print(f"\nRésultat: {passed} réussis, {failed} échecs, {skipped} ignorés")
    
    if failed == 0:
        print("\n✓ Tous les tests essentiels ont réussi!")
        print("\nSi unified_monitoring.html ne détecte toujours pas:")
        print("1. Ouvrir http://localhost:5000/test-detection")
        print("2. Appuyer sur F12 dans le navigateur")
        print("3. Vérifier les erreurs dans la console")
        return 0
    else:
        print("\n✗ Des problèmes ont été détectés")
        print("\nActions recommandées:")
        
        if not results[2]:  # Modèles
            print("  - Entraîner un modèle: python train.py")
        if not results[3]:  # Dépendances
            print("  - Installer les dépendances: pip install -r requirements.txt")
        if not results[7]:  # Serveur
            print("  - Démarrer le serveur: python run_app.py")
        
        print("\nConsulter: TROUBLESHOOTING_DETECTION.md")
        return 1

if __name__ == '__main__':
    exit(main())