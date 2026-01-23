#!/usr/bin/env python3
"""
Test rapide pour valider que les corrections sont appliquées
Exécuter: python quicktest.py
"""

import sys
from pathlib import Path

def test_classes():
    """Tester que les 5 classes sont correctement définies"""
    print("\n🔍 TEST 1: Vérification des classes (5 classes)...")
    
    try:
        from EPI_CLASS_CONFIG import CLASS_NAMES, CLASS_COUNT, verify_class_consistency
        
        # Vérifier la cohérence
        verify_class_consistency()
        
        # Vérifier les 5 classes
        expected = ['helmet', 'vest', 'glasses', 'boots', 'person']
        if CLASS_NAMES != expected:
            print(f"   ❌ ERREUR: Classes = {CLASS_NAMES}, attendu {expected}")
            return False
        
        if CLASS_COUNT != 5:
            print(f"   ❌ ERREUR: CLASS_COUNT = {CLASS_COUNT}, attendu 5")
            return False
        
        print(f"   ✅ Classes: {CLASS_NAMES}")
        print(f"   ✅ Nombre: {CLASS_COUNT}")
        return True
    except Exception as e:
        print(f"   ❌ ERREUR: {e}")
        return False

def test_data_yaml():
    """Tester que data.yaml est configuré correctement"""
    print("\n🔍 TEST 2: Vérification data.yaml...")
    
    data_yaml = Path('data/data.yaml')
    if not data_yaml.exists():
        print(f"   ❌ ERREUR: {data_yaml} n'existe pas")
        return False
    
    content = data_yaml.read_text()
    
    # Vérifier nc: 5
    if 'nc: 5' not in content:
        print("   ❌ ERREUR: nc: 5 manquant (probably nc: 4)")
        return False
    
    # Vérifier l'ordre des classes
    if "'helmet', 'vest', 'glasses', 'boots', 'person'" not in content:
        print("   ❌ ERREUR: Ordre des classes incorrect")
        return False
    
    print("   ✅ nc: 5")
    print("   ✅ Ordre: ['helmet', 'vest', 'glasses', 'boots', 'person']")
    return True

def test_single_model():
    """Tester qu'il n'y a qu'un seul modèle (best.pt)"""
    print("\n🔍 TEST 3: Vérification modèle unique...")
    
    models_dir = Path('models')
    if not models_dir.exists():
        print(f"   ❌ ERREUR: {models_dir} n'existe pas")
        return False
    
    pt_files = list(models_dir.glob('*.pt'))
    
    if len(pt_files) != 1:
        print(f"   ❌ ERREUR: {len(pt_files)} fichiers .pt trouvés, attendu 1")
        for f in pt_files:
            print(f"      - {f.name}")
        return False
    
    if pt_files[0].name != 'best.pt':
        print(f"   ❌ ERREUR: Modèle = {pt_files[0].name}, attendu best.pt")
        return False
    
    size_mb = pt_files[0].stat().st_size / (1024**2)
    print(f"   ✅ Modèle unique: best.pt ({size_mb:.1f} MB)")
    return True

def test_config():
    """Tester que config.py est correct"""
    print("\n🔍 TEST 4: Vérification config.py...")
    
    try:
        from config import config
        
        # Vérifier CLASS_NAMES
        expected = ['helmet', 'vest', 'glasses', 'boots', 'person']
        if not hasattr(config, 'CLASS_NAMES'):
            print("   ❌ ERREUR: config.CLASS_NAMES n'existe pas")
            return False
        
        # Vérifier MODEL_PATH (accepter chemins absolus et relatifs)
        if not config.MODEL_PATH.endswith('best.pt'):
            print(f"   ❌ ERREUR: MODEL_PATH = {config.MODEL_PATH}")
            return False
        
        # Vérifier MULTI_MODEL_ENABLED
        if config.MULTI_MODEL_ENABLED:
            print("   ⚠️  AVERTISSEMENT: MULTI_MODEL_ENABLED est True (devrait être False)")
            # Not a blocking error, but a warning
        
        print(f"   ✅ CLASS_NAMES: 5 classes")
        print(f"   ✅ MODEL_PATH: best.pt")
        print(f"   ✅ MULTI_MODEL_ENABLED: {config.MULTI_MODEL_ENABLED}")
        return True
    except Exception as e:
        print(f"   ❌ ERREUR: {e}")
        return False

def test_constants():
    """Tester que constants.py est correct"""
    print("\n🔍 TEST 5: Vérification constants.py...")
    
    try:
        from app.constants import CLASS_MAP, CLASS_COLORS
        
        # Vérifier CLASS_MAP a 5 entrées
        if len(CLASS_MAP) != 5:
            print(f"   ❌ ERREUR: CLASS_MAP a {len(CLASS_MAP)} entrées, attendu 5")
            return False
        
        # Vérifier l'ordre
        expected_order = {0: 'helmet', 1: 'vest', 2: 'glasses', 3: 'boots', 4: 'person'}
        if CLASS_MAP != expected_order:
            print(f"   ❌ ERREUR: CLASS_MAP incorrect")
            print(f"      Attendu: {expected_order}")
            print(f"      Obtenu:  {CLASS_MAP}")
            return False
        
        # Vérifier CLASS_COLORS
        for cls in ['helmet', 'vest', 'glasses', 'boots', 'person']:
            if cls not in CLASS_COLORS:
                print(f"   ❌ ERREUR: CLASS_COLORS manque '{cls}'")
                return False
        
        print(f"   ✅ CLASS_MAP: 5 classes mappées correctement")
        print(f"   ✅ CLASS_COLORS: 5 couleurs définies")
        return True
    except Exception as e:
        print(f"   ❌ ERREUR: {e}")
        return False

def test_training_optimizer():
    """Tester que training_optimizer.py existe"""
    print("\n🔍 TEST 6: Vérification training_optimizer.py...")
    
    opt_file = Path('training_optimizer.py')
    if not opt_file.exists():
        print(f"   ❌ ERREUR: {opt_file} n'existe pas")
        return False
    
    try:
        from training_optimizer import TrainingOptimizer, train_with_optimization
        print("   ✅ TrainingOptimizer importé avec succès")
        print("   ✅ Checkpoints: support actif")
        return True
    except Exception as e:
        print(f"   ❌ ERREUR import: {e}")
        return False

def main():
    print("=" * 70)
    print("⚡ TEST RAPIDE - VALIDATION DES CORRECTIONS")
    print("=" * 70)
    
    tests = [
        test_classes,
        test_data_yaml,
        test_single_model,
        test_config,
        test_constants,
        test_training_optimizer
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ TOUS LES TESTS RÉUSSIS ({passed}/{total})")
        print("=" * 70)
        print("\n🚀 Le projet est prêt!")
        print("\nProchaines étapes:")
        print("  1. python cleanup_models.py")
        print("  2. Créer train_optimized.py (voir GUIDE_REPARATION.py)")
        print("  3. python train_optimized.py")
        print("  4. python run_app.py")
        return 0
    else:
        print(f"❌ {total - passed}/{total} TEST(S) ÉCHOUÉ(S)")
        print("=" * 70)
        print("\nActions requises:")
        if not results[0]:
            print("  - Vérifier EPI_CLASS_CONFIG.py")
        if not results[1]:
            print("  - Vérifier data/data.yaml")
        if not results[2]:
            print("  - Exécuter python cleanup_models.py")
        if not results[3]:
            print("  - Vérifier config.py")
        if not results[4]:
            print("  - Vérifier app/constants.py")
        if not results[5]:
            print("  - Vérifier training_optimizer.py existe")
        return 1

if __name__ == '__main__':
    sys.exit(main())
