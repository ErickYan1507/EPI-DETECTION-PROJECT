"""
Script de test pour le système multi-modèles
Test le MultiModelDetector avec différentes stratégies d'agrégation
"""
import sys
import os
import cv2
import time
from pathlib import Path

# Ajouter le répertoire parent au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app.multi_model_detector import MultiModelDetector
from app.logger import logger

def test_single_mode():
    """Tester le mode single (un seul modèle)"""
    print("\n" + "="*60)
    print("TEST 1: Mode Single (best.pt)")
    print("="*60)
    
    try:
        detector = MultiModelDetector(use_ensemble=False)
        
        # Charger une image de test
        test_image_path = 'images/aa.jpg'
        if not os.path.exists(test_image_path):
            test_image_path = 'aa.jpg'
        
        if not os.path.exists(test_image_path):
            print(f"❌ Image de test non trouvée: {test_image_path}")
            return False
        
        image = cv2.imread(test_image_path)
        if image is None:
            print(f"❌ Impossible de charger l'image: {test_image_path}")
            return False
        
        print(f"✓ Image chargée: {test_image_path} ({image.shape})")
        
        # Détection
        start = time.perf_counter()
        detections, stats = detector.detect(image, use_ensemble=False)
        elapsed = (time.perf_counter() - start) * 1000
        
        # Résultats
        print(f"\nRésultats:")
        print(f"  - Modèle utilisé: {stats.get('model_used', 'N/A')}")
        print(f"  - Mode ensemble: {stats.get('ensemble_mode', False)}")
        print(f"  - Détections: {len(detections)}")
        print(f"  - Personnes: {stats.get('total_persons', 0)}")
        print(f"  - Casques: {stats.get('with_helmet', 0)}")
        print(f"  - Gilets: {stats.get('with_vest', 0)}")
        print(f"  - Lunettes: {stats.get('with_glasses', 0)}")
        print(f"  - Conformité: {stats.get('compliance_rate', 0):.1f}%")
        print(f"  - Temps total: {elapsed:.1f}ms")
        
        # Sauvegarder l'image avec détections
        result_image = detector.draw_detections(image, detections)
        output_path = test_image_path.replace('.', '_single.')
        cv2.imwrite(output_path, result_image)
        print(f"✓ Image sauvegardée: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ensemble_mode():
    """Tester le mode ensemble (tous les modèles)"""
    print("\n" + "="*60)
    print("TEST 2: Mode Ensemble (tous les modèles)")
    print("="*60)
    
    try:
        detector = MultiModelDetector(use_ensemble=True)
        
        # Charger une image de test
        test_image_path = 'images/aa.jpg'
        if not os.path.exists(test_image_path):
            test_image_path = 'aa.jpg'
        
        if not os.path.exists(test_image_path):
            print(f"❌ Image de test non trouvée: {test_image_path}")
            return False
        
        image = cv2.imread(test_image_path)
        if image is None:
            print(f"❌ Impossible de charger l'image: {test_image_path}")
            return False
        
        print(f"✓ Image chargée: {test_image_path}")
        print(f"✓ Nombre de modèles: {len(detector.models)}")
        print(f"✓ Stratégie: {detector.aggregation_strategy}")
        
        # Détection
        start = time.perf_counter()
        detections, stats = detector.detect(image, use_ensemble=True)
        elapsed = (time.perf_counter() - start) * 1000
        
        # Résultats
        print(f"\nRésultats:")
        print(f"  - Modèle utilisé: {stats.get('model_used', 'N/A')}")
        print(f"  - Mode ensemble: {stats.get('ensemble_mode', False)}")
        print(f"  - Méthode agrégation: {stats.get('aggregation_method', 'N/A')}")
        print(f"  - Nombre de modèles: {stats.get('num_models', 0)}")
        print(f"  - Détections: {len(detections)}")
        print(f"  - Personnes: {stats.get('total_persons', 0)}")
        print(f"  - Casques: {stats.get('with_helmet', 0)}")
        print(f"  - Gilets: {stats.get('with_vest', 0)}")
        print(f"  - Lunettes: {stats.get('with_glasses', 0)}")
        print(f"  - Conformité: {stats.get('compliance_rate', 0):.1f}%")
        print(f"  - Temps total: {elapsed:.1f}ms")
        
        # Afficher les votes des modèles
        if 'model_votes' in stats and stats['model_votes']:
            print(f"\nVotes des modèles:")
            for model_name, votes in stats['model_votes'].items():
                print(f"  {model_name}:")
                print(f"    - Personnes: {votes.get('total_persons', 0)}")
                print(f"    - Conformité: {votes.get('compliance_rate', 0):.1f}%")
        
        # Sauvegarder l'image avec détections
        result_image = detector.draw_detections(image, detections)
        output_path = test_image_path.replace('.', '_ensemble.')
        cv2.imwrite(output_path, result_image)
        print(f"\n✓ Image sauvegardée: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_comparison():
    """Comparer les performances de tous les modèles"""
    print("\n" + "="*60)
    print("TEST 3: Comparaison des modèles")
    print("="*60)
    
    try:
        detector = MultiModelDetector(use_ensemble=False)
        
        # Charger une image de test
        test_image_path = 'images/aa.jpg'
        if not os.path.exists(test_image_path):
            test_image_path = 'aa.jpg'
        
        if not os.path.exists(test_image_path):
            print(f"❌ Image de test non trouvée")
            return False
        
        image = cv2.imread(test_image_path)
        if image is None:
            print(f"❌ Impossible de charger l'image")
            return False
        
        print(f"✓ Image chargée: {test_image_path}")
        print(f"\nComparaison de {len(detector.models)} modèles:\n")
        
        results = []
        for model_name, model_info in detector.models.items():
            print(f"Test de {model_name}...", end=' ')
            
            det = model_info['detector']
            start = time.perf_counter()
            detections, stats = det.detect(image)
            elapsed = (time.perf_counter() - start) * 1000
            
            results.append({
                'model': model_name,
                'weight': model_info['weight'],
                'detections': len(detections),
                'persons': stats.get('total_persons', 0),
                'helmets': stats.get('with_helmet', 0),
                'compliance': stats.get('compliance_rate', 0),
                'time_ms': elapsed
            })
            
            print(f"✓ {elapsed:.1f}ms")
        
        # Afficher le tableau comparatif
        print(f"\n{'Modèle':<35} {'Poids':<8} {'Dét.':<6} {'Pers.':<6} {'Casq.':<6} {'Conf.':<8} {'Temps':<8}")
        print("-" * 85)
        for r in results:
            print(f"{r['model']:<35} {r['weight']:<8.2f} {r['detections']:<6} {r['persons']:<6} {r['helmets']:<6} {r['compliance']:<7.1f}% {r['time_ms']:<7.1f}ms")
        
        # Moyennes
        avg_detections = sum(r['detections'] for r in results) / len(results)
        avg_compliance = sum(r['compliance'] for r in results) / len(results)
        avg_time = sum(r['time_ms'] for r in results) / len(results)
        
        print("-" * 85)
        print(f"{'MOYENNE':<35} {'-':<8} {avg_detections:<6.1f} {'-':<6} {'-':<6} {avg_compliance:<7.1f}% {avg_time:<7.1f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_list():
    """Tester la récupération de la liste des modèles"""
    print("\n" + "="*60)
    print("TEST 4: Liste des modèles")
    print("="*60)
    
    try:
        detector = MultiModelDetector(use_ensemble=False)
        
        model_list = detector.get_model_list()
        
        print(f"\nModèles disponibles ({len(model_list)}):\n")
        for model in model_list:
            primary = " [PRIMARY]" if model['is_primary'] else ""
            print(f"  - {model['name']}{primary}")
            print(f"    Poids: {model['weight']}")
            print(f"    Chemin: {model['path']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("\n" + "="*60)
    print("TESTS DU SYSTÈME MULTI-MODÈLES")
    print("="*60)
    
    tests = [
        ("Liste des modèles", test_model_list),
        ("Mode Single", test_single_mode),
        ("Mode Ensemble", test_ensemble_mode),
        ("Comparaison", test_model_comparison)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Exception dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    total_pass = sum(1 for _, s in results if s)
    total_tests = len(results)
    
    print(f"\nRésultat: {total_pass}/{total_tests} tests réussis")
    
    if total_pass == total_tests:
        print("✓ Tous les tests ont réussi!")
        return 0
    else:
        print("✗ Certains tests ont échoué")
        return 1

if __name__ == '__main__':
    exit(main())