#!/usr/bin/env python3
"""
Script de test pour la détection en temps réel avec l'API /api/detect
Teste le pipeline complet: webcam -> base64 -> Flask API -> YOLOv5 inference
"""

import cv2
import base64
import json
import requests
import numpy as np
from datetime import datetime

def test_detection_api(image_path=None):
    """Tester l'endpoint /api/detect"""
    
    # URL de l'API
    api_url = "http://localhost:5000/api/detect"
    
    print("=" * 60)
    print("Test de détection en temps réel - API /api/detect")
    print("=" * 60)
    
    # Si pas d'image spécifiée, utiliser une image de test du projet
    if image_path is None:
        image_path = "data/annotated/test_image.jpg"
        if not os.path.exists(image_path):
            # Générer une image de test simple
            image = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
            cv2.imwrite("test_image_generated.jpg", image)
            image_path = "test_image_generated.jpg"
    
    print(f"\n1. Chargement de l'image: {image_path}")
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"❌ Erreur: Impossible de charger l'image {image_path}")
        return False
    
    print(f"   ✓ Image chargée: {image.shape}")
    
    # Convertir en base64
    print("\n2. Conversion en base64...")
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    print(f"   ✓ Taille: {len(image_base64)} caractères")
    
    # Préparer le payload
    payload = {
        'image': f'data:image/jpeg;base64,{image_base64}'
    }
    
    # Envoyer la requête
    print(f"\n3. Envoi de la requête à {api_url}")
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        print(f"   ✓ Réponse reçue (status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter à l'API")
        print("   Assurez-vous que le serveur Flask est en cours d'exécution:")
        print("   python app/main.py")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Vérifier la réponse
    print("\n4. Analyse de la réponse...")
    try:
        result = response.json()
        
        if result.get('success'):
            print("   ✓ Détection réussie!")
            
            detections = result.get('detections', [])
            stats = result.get('statistics', {})
            
            print(f"\n5. Résultats de détection:")
            print(f"   Nombre de détections: {len(detections)}")
            
            if detections:
                print(f"   Détections trouvées:")
                for det in detections:
                    print(f"     - {det['class_name']}: {det['confidence']:.1%} confiance")
            else:
                print(f"   Aucune détection trouvée")
            
            print(f"\n6. Statistiques:")
            print(f"   Personnes détectées: {stats.get('total_persons', 0)}")
            print(f"   Avec casque: {stats.get('with_helmet', 0)}")
            print(f"   Avec gilet: {stats.get('with_vest', 0)}")
            print(f"   Avec lunettes: {stats.get('with_glasses', 0)}")
            print(f"   Avec bottes: {stats.get('with_boots', 0)}")
            print(f"   Taux de conformité: {stats.get('compliance_rate', 0):.1%}")
            print(f"   Niveau de conformité: {stats.get('compliance_level', 'N/A')}")
            print(f"   Type d'alerte: {stats.get('alert_type', 'none')}")
            print(f"   Temps d'inférence: {stats.get('inference_ms', 0):.1f}ms")
            print(f"   Temps total: {stats.get('total_ms', 0):.1f}ms")
            
            return True
        else:
            print(f"   ❌ Erreur dans la réponse: {result.get('error', 'Unknown')}")
            return False
    
    except json.JSONDecodeError:
        print(f"❌ Erreur: Réponse non-JSON")
        print(f"   Contenu: {response.text}")
        return False

def test_training_results_api():
    """Tester l'endpoint /api/training-results"""
    
    api_url = "http://localhost:5000/api/training-results"
    
    print("\n" + "=" * 60)
    print("Test de données d'entraînement - API /api/training-results")
    print("=" * 60)
    
    print(f"\n1. Envoi de la requête à {api_url}")
    try:
        response = requests.get(api_url, timeout=10)
        print(f"   ✓ Réponse reçue (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    try:
        result = response.json()
        
        if result.get('success'):
            print("   ✓ Données d'entraînement récupérées!")
            
            results = result.get('results', [])
            total = result.get('total', 0)
            
            print(f"\n2. Résultats:")
            print(f"   Total d'entraînements: {total}")
            
            if results:
                latest = results[0]
                print(f"\n3. Dernier entraînement:")
                print(f"   Modèle: {latest.get('model_name')} v{latest.get('model_version')}")
                print(f"   Épochs: {latest.get('epochs')}")
                print(f"   Batch size: {latest.get('batch_size')}")
                print(f"   Train Accuracy: {latest.get('training', {}).get('accuracy', 'N/A')}")
                print(f"   Val Accuracy: {latest.get('validation', {}).get('accuracy', 'N/A')}")
                print(f"   FPS: {latest.get('fps', 'N/A')}")
                print(f"   Inference Time: {latest.get('inference_time_ms', 'N/A')}ms")
                
                return True
            else:
                print("   ⚠️  Aucun résultat d'entraînement trouvé")
                return False
        else:
            print(f"   ❌ Erreur: {result.get('error', 'Unknown')}")
            return False
    
    except json.JSONDecodeError:
        print(f"❌ Erreur: Réponse non-JSON")
        print(f"   Contenu: {response.text}")
        return False

if __name__ == "__main__":
    import os
    
    print("\n🎯 TEST DE DÉTECTION EN TEMPS RÉEL AVEC BEST.PT\n")
    
    # Test 1: API de détection
    success_detect = test_detection_api()
    
    # Test 2: API d'entraînement
    success_training = test_training_results_api()
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Détection temps réel: {'✓ SUCCÈS' if success_detect else '✗ ÉCHEC'}")
    print(f"Données d'entraînement: {'✓ SUCCÈS' if success_training else '✗ ÉCHEC'}")
    print("=" * 60)
    
    if success_detect and success_training:
        print("\n✅ Tous les tests sont passés! Système prêt pour utilisation.")
    else:
        print("\n❌ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
