"""
Test l'API de détection pour diagnostiquer les problèmes
"""
import requests
import base64
import json
import cv2
import sys
from pathlib import Path

def test_api_with_image(image_path, use_ensemble=True):
    """Tester l'API de détection avec une image"""
    
    print(f"\n{'='*60}")
    print(f"Test API /api/detect avec {image_path}")
    print(f"Mode: {'Ensemble' if use_ensemble else 'Single'}")
    print(f"{'='*60}\n")
    
    # Lire l'image
    if not Path(image_path).exists():
        print(f"❌ Image non trouvée: {image_path}")
        return False
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Impossible de charger l'image")
        return False
    
    print(f"✓ Image chargée: {image.shape}")
    
    # Encoder en base64
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Format data URL
    image_data_url = f"data:image/jpeg;base64,{image_base64}"
    
    print(f"✓ Image encodée: {len(image_base64)} chars")
    
    # Préparer la requête
    url = f"http://localhost:5000/api/detect?use_ensemble={str(use_ensemble).lower()}"
    payload = {
        "image": image_data_url,
        "use_ensemble": use_ensemble
    }
    
    try:
        print(f"\n📤 Envoi requête à {url}...")
        response = requests.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
        
        # Parser la réponse
        result = response.json()
        
        print(f"\n{'='*60}")
        print("RÉPONSE API")
        print(f"{'='*60}")
        print(json.dumps(result, indent=2))
        
        if not result.get('success'):
            print(f"\n❌ Échec: {result.get('error', 'Unknown error')}")
            return False
        
        # Afficher les résultats
        stats = result.get('statistics', {})
        detections = result.get('detections', [])
        
        print(f"\n{'='*60}")
        print("STATISTIQUES")
        print(f"{'='*60}")
        print(f"  Modèle utilisé: {stats.get('model_used', 'N/A')}")
        print(f"  Mode ensemble: {stats.get('ensemble_mode', False)}")
        print(f"  Total personnes: {stats.get('total_persons', 0)}")
        print(f"  Avec casque: {stats.get('with_helmet', 0)}")
        print(f"  Avec gilet: {stats.get('with_vest', 0)}")
        print(f"  Avec lunettes: {stats.get('with_glasses', 0)}")
        print(f"  Avec bottes: {stats.get('with_boots', 0)}")
        print(f"  Taux conformité: {stats.get('compliance_rate', 0)}%")
        print(f"  Niveau conformité: {stats.get('compliance_level', 'N/A')}")
        print(f"  Type alerte: {stats.get('alert_type', 'N/A')}")
        print(f"  Temps inférence: {stats.get('inference_ms', 0)}ms")
        print(f"  Temps total: {stats.get('total_ms', 0)}ms")
        
        print(f"\n{'='*60}")
        print(f"DÉTECTIONS ({len(detections)})")
        print(f"{'='*60}")
        
        if detections:
            for i, det in enumerate(detections, 1):
                class_name = det.get('class_name') or det.get('class', 'unknown')
                confidence = det.get('confidence', 0) * 100
                bbox = det.get('bbox', [])
                print(f"  {i}. {class_name} - {confidence:.1f}% - bbox: {bbox}")
        else:
            print("  Aucune détection")
        
        print(f"\n✓ Test réussi!")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Erreur: Impossible de se connecter au serveur")
        print(f"   Assurez-vous que le serveur Flask est démarré (python run_app.py)")
        return False
    except requests.exceptions.Timeout:
        print(f"\n❌ Erreur: Timeout (>30s)")
        return False
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_health():
    """Tester l'endpoint de santé"""
    print(f"\n{'='*60}")
    print("Test API /api/health")
    print(f"{'='*60}\n")
    
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Serveur en ligne")
            print(f"  Status: {data.get('status')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Multi-model: {data.get('multi_model_enabled')}")
            print(f"  Models loaded: {data.get('models_loaded')}")
            print(f"  Ensemble mode: {data.get('ensemble_mode')}")
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Point d'entrée"""
    print("\n" + "="*60)
    print("TEST API DE DÉTECTION EPI")
    print("="*60)
    
    # Test 1: Health check
    health_ok = test_api_health()
    
    if not health_ok:
        print("\n❌ Le serveur n'est pas disponible. Démarrez-le avec:")
        print("   python run_app.py")
        return 1
    
    # Test 2: Détection avec image
    test_images = [
        'images/aa.jpg',
        'aa.jpg',
        'a.jpg'
    ]
    
    image_path = None
    for path in test_images:
        if Path(path).exists():
            image_path = path
            break
    
    if not image_path:
        print(f"\n❌ Aucune image de test trouvée dans: {test_images}")
        return 1
    
    # Test mode ensemble
    print(f"\n{'='*60}")
    print("TEST MODE ENSEMBLE")
    print(f"{'='*60}")
    ensemble_ok = test_api_with_image(image_path, use_ensemble=True)
    
    # Test mode single
    print(f"\n{'='*60}")
    print("TEST MODE SINGLE")
    print(f"{'='*60}")
    single_ok = test_api_with_image(image_path, use_ensemble=False)
    
    # Résumé
    print(f"\n{'='*60}")
    print("RÉSUMÉ")
    print(f"{'='*60}")
    print(f"  Health Check: {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"  Mode Ensemble: {'✓ PASS' if ensemble_ok else '✗ FAIL'}")
    print(f"  Mode Single: {'✓ PASS' if single_ok else '✗ FAIL'}")
    
    if health_ok and ensemble_ok and single_ok:
        print(f"\n✓ Tous les tests ont réussi!")
        print(f"\nL'API fonctionne correctement. Si unified_monitoring.html ne détecte pas,")
        print(f"vérifiez la console du navigateur (F12) pour les erreurs JavaScript.")
        return 0
    else:
        print(f"\n✗ Certains tests ont échoué")
        return 1

if __name__ == '__main__':
    exit(main())