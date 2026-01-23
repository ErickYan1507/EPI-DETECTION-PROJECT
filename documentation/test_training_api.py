#!/usr/bin/env python3
"""
Test des APIs training-results
Teste les 3 nouveaux endpoints pour afficher les résultats d'entraînement
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def test_training_apis():
    """Tester les 3 APIs"""
    
    print("="*70)
    print("🧪 TEST DES APIs TRAINING-RESULTS")
    print("="*70)
    
    # Test 1: Récupérer tous les résultats
    print("\n✅ TEST 1: GET /api/training-results (tous les résultats)")
    try:
        response = requests.get(f'{BASE_URL}/api/training-results?limit=10')
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Total résultats trouvés: {data.get('total', 0)}")
            
            if data.get('training_results'):
                for i, result in enumerate(data['training_results'][:3], 1):
                    print(f"\n   Résultat {i}:")
                    print(f"     - ID: {result.get('id')}")
                    print(f"     - Modèle: {result.get('model_name')} v{result.get('model_version')}")
                    print(f"     - Dataset: {result.get('dataset_name')}")
                    print(f"     - Val Accuracy: {result.get('validation', {}).get('accuracy', 'N/A')}")
                    print(f"     - Status: {result.get('status')}")
            else:
                print("   ⚠️  Aucun résultat trouvé (BD vide)")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Récupérer le résumé
    print("\n✅ TEST 2: GET /api/training-summary (résumé)")
    try:
        response = requests.get(f'{BASE_URL}/api/training-summary')
        if response.status_code == 200:
            data = response.json()
            summary = data.get('summary', {})
            print(f"   Status: {response.status_code}")
            print(f"   Total d'entraînements: {summary.get('total_trainings', 0)}")
            print(f"   Precision moyenne (Train): {summary.get('avg_train_accuracy', 0):.2%}")
            print(f"   Precision moyenne (Val): {summary.get('avg_val_accuracy', 0):.2%}")
            
            if summary.get('latest_training'):
                latest = summary['latest_training']
                print(f"\n   Dernier entraînement:")
                print(f"     - Modèle: {latest.get('model_name')} v{latest.get('model_version')}")
                print(f"     - Date: {latest.get('timestamp')}")
                print(f"     - Val Accuracy: {latest.get('val_accuracy'):.2%}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Récupérer un résultat spécifique (ID 1)
    print("\n✅ TEST 3: GET /api/training-results/1 (détail)")
    try:
        response = requests.get(f'{BASE_URL}/api/training-results/1')
        if response.status_code == 200:
            data = response.json()
            result = data.get('training_result', {})
            print(f"   Status: {response.status_code}")
            print(f"   Modèle: {result.get('model_name')} v{result.get('model_version')}")
            print(f"   Dataset: {result.get('dataset_name')}")
            print(f"   Epochs: {result.get('epochs')}")
            print(f"   Batch Size: {result.get('batch_size')}")
            print(f"   Image Size: {result.get('image_size')}")
            print(f"\n   Métriques d'entraînement:")
            train = result.get('training', {})
            print(f"     - Loss: {train.get('loss')}")
            print(f"     - Accuracy: {train.get('accuracy')}")
            print(f"     - Precision: {train.get('precision')}")
            print(f"     - Recall: {train.get('recall')}")
            print(f"     - F1-Score: {train.get('f1_score')}")
            print(f"\n   Métriques de validation:")
            val = result.get('validation', {})
            print(f"     - Loss: {val.get('loss')}")
            print(f"     - Accuracy: {val.get('accuracy')}")
            print(f"     - Precision: {val.get('precision')}")
            print(f"     - Recall: {val.get('recall')}")
            print(f"     - F1-Score: {val.get('f1_score')}")
        elif response.status_code == 404:
            print(f"   ⚠️  Résultat ID 1 non trouvé (BD vide)")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Vérifier que la route /training-results existe
    print("\n✅ TEST 4: GET /training-results (page HTML)")
    try:
        response = requests.get(f'{BASE_URL}/training-results')
        if response.status_code == 200:
            if 'training_results' in response.text.lower():
                print(f"   Status: {response.status_code}")
                print(f"   Page HTML trouvée (contient 'training_results')")
            else:
                print(f"   Status: {response.status_code}")
                print(f"   Page trouvée mais contenu incomplet")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "="*70)
    print("✅ TESTS TERMINÉS")
    print("="*70)

if __name__ == '__main__':
    import time
    
    print("\n⏳ Attente de 2 secondes pour que le serveur soit prêt...")
    time.sleep(2)
    
    test_training_apis()
