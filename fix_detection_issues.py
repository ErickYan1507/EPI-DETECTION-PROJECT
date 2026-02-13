#!/usr/bin/env python
"""
Script de diagnostic et correction des problèmes de détection
- Double-clic sur uploads
- Dates invalides
- Aucune détection sur unified_monitoring
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from config import config
from app.logger import logger
import cv2
import numpy as np

def test_model_loading():
    """Tester le chargement du modèle"""
    print("\n" + "="*70)
    print("🔍 TEST 1: Chargement du modèle best.pt")
    print("="*70)
    
    model_path = os.path.join(config.MODELS_FOLDER, 'best.pt')
    
    if not os.path.exists(model_path):
        print(f"❌ ERREUR: Modèle non trouvé à {model_path}")
        return False
    
    print(f"✅ Modèle trouvé: {model_path}")
    print(f"   Taille: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
    
    # Test de chargement
    try:
        from app.detection import EPIDetector
        logger.info("Initialisation de EPIDetector...")
        detector = EPIDetector(model_path=model_path)
        print("✅ EPIDetector initialisé avec succès")
        
        # Test inference sur une image de test
        test_image = np.zeros((640, 640, 3), dtype=np.uint8)
        test_image[100:200, 100:200] = [255, 100, 0]  # Orange (pour tester)
        
        detections, stats = detector.detect(test_image)
        print(f"✅ Inférence testée: {len(detections)} détections")
        print(f"   Stats: compliance={stats.get('compliance_rate', 0):.1f}%")
        print(f"   Timing: {stats.get('total_ms', 0):.1f}ms")
        
        return True
    except Exception as e:
        print(f"❌ ERREUR lors du test: {e}")
        logger.error(f"Erreur test détection: {e}", exc_info=True)
        return False

def test_database():
    """Tester la connexion à la base de données"""
    print("\n" + "="*70)
    print("🔍 TEST 2: Base de données")
    print("="*70)
    
    try:
        from app.main import app, db
        from app.database_unified import Detection, TrainingResult, Alert
        
        with app.app_context():
            # Test requête simple
            total_detections = Detection.query.count()
            total_trainings = TrainingResult.query.count()
            total_alerts = Alert.query.count()
            
            print(f"✅ Connexion BD réussie")
            print(f"   Détections: {total_detections}")
            print(f"   Entraînements: {total_trainings}")
            print(f"   Alertes: {total_alerts}")
            
            # Vérifier les timestamps récents
            if total_detections > 0:
                recent = Detection.query.order_by(Detection.timestamp.desc()).first()
                print(f"   Dernière détection: {recent.timestamp}")
            
            if total_trainings > 0:
                recent_train = TrainingResult.query.order_by(TrainingResult.timestamp.desc()).first()
                print(f"   Dernier entraînement: {recent_train.timestamp}")
            
            return True
    except Exception as e:
        print(f"❌ ERREUR BDD: {e}")
        logger.error(f"Erreur test BDD: {e}", exc_info=True)
        return False

def test_multi_detector():
    """Tester le MultiModelDetector"""
    print("\n" + "="*70)
    print("🔍 TEST 3: MultiModelDetector")
    print("="*70)
    
    try:
        from app.multi_model_detector import MultiModelDetector
        
        logger.info("Initialisation MultiModelDetector...")
        detector = MultiModelDetector(use_ensemble=False)
        
        print(f"✅ MultiModelDetector initialisé")
        print(f"   Modèles chargés: {list(detector.models.keys())}")
        
        for model_name, model_info in detector.models.items():
            print(f"   - {model_name}: weight={model_info['weight']}")
        
        # Test détection
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        detections, stats = detector.detect(test_image, use_ensemble=False)
        
        print(f"✅ Détection testée: {len(detections)} détections")
        print(f"   Compliance: {stats.get('compliance_rate', 0):.1f}%")
        
        return True
    except Exception as e:
        print(f"❌ ERREUR MultiDetector: {e}")
        logger.error(f"Erreur MultiDetector: {e}", exc_info=True)
        return False

def test_upload_endpoint():
    """Tester l'endpoint upload"""
    print("\n" + "="*70)
    print("🔍 TEST 4: Endpoint /upload")
    print("="*70)
    
    try:
        from app.main import app
        
        with app.test_client() as client:
            # Créer une image test
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            _, buffer = cv2.imencode('.jpg', test_image)
            
            # Envoyer POST request
            response = client.post(
                '/upload',
                data={'file': (buffer.tobytes(), 'test.jpg'), 'type': 'image'},
                content_type='multipart/form-data'
            )
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Upload endpoint fonctionnel")
                print(f"   Response: success={data.get('success')}")
                print(f"   Détections: {data.get('detections_count', 0)}")
                return True
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                print(f"   Response: {response.get_data(as_text=True)}")
                return False
    except Exception as e:
        print(f"❌ ERREUR upload test: {e}")
        logger.error(f"Erreur upload test: {e}", exc_info=True)
        return False

def test_unified_monitoring():
    """Tester unified monitoring"""
    print("\n" + "="*70)
    print("🔍 TEST 5: Endpoint /api/detect (Unified Monitoring)")
    print("="*70)
    
    try:
        from app.main import app
        import base64
        
        with app.test_client() as client:
            # Créer une image test
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            _, buffer = cv2.imencode('.jpg', test_image)
            image_base64 = base64.b64encode(buffer.tobytes()).decode()
            
            # Envoyer POST request
            response = client.post(
                '/api/detect',
                json={'image_base64': image_base64},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ /api/detect endpoint fonctionnel")
                print(f"   Response: success={data.get('success')}")
                print(f"   Détections: {len(data.get('detections', []))}")
                return True
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                return False
    except Exception as e:
        print(f"⚠️  AVERTISSEMENT: {e}")
        return False

def check_config():
    """Vérifier la configuration"""
    print("\n" + "="*70)
    print("📋 Configuration")
    print("="*70)
    
    print(f"DB_TYPE: {config.DB_TYPE}")
    print(f"DATABASE_URI: {config.DATABASE_URI[:50]}...")
    print(f"MODELS_FOLDER: {config.MODELS_FOLDER}")
    print(f"UPLOAD_FOLDER: {config.UPLOAD_FOLDER}")
    print(f"CONFIDENCE_THRESHOLD: {config.CONFIDENCE_THRESHOLD}")
    print(f"IOU_THRESHOLD: {config.IOU_THRESHOLD}")
    print(f"DEFAULT_USE_ENSEMBLE: {config.DEFAULT_USE_ENSEMBLE}")
    print(f"MULTI_MODEL_ENABLED: {config.MULTI_MODEL_ENABLED}")

if __name__ == '__main__':
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " " * 15 + "🔧 DIAGNOSTIC DES PROBLÈMES DE DÉTECTION" + " " * 13 + "║")
    print("╚" + "="*68 + "╝")
    
    check_config()
    
    results = {
        'Model Loading': test_model_loading(),
        'Database': test_database(),
        'MultiDetector': test_multi_detector(),
        'Upload Endpoint': test_upload_endpoint(),
        'Unified Monitoring': test_unified_monitoring(),
    }
    
    print("\n" + "="*70)
    print("📊 RÉSUMÉ")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅ OK" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    if all(results.values()):
        print("\n✅ Tous les tests sont passés!")
        sys.exit(0)
    else:
        print("\n❌ Certains tests ont échoué, voir les détails ci-dessus")
        sys.exit(1)
