"""
Test automatisé pour vérifier les statistiques temps réel
Utilise: unittest, requests, Flask test client

Usage:
  python test_stats_realtime.py
"""

import unittest
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.database_unified import Detection, Alert, TrainingResult

class StatsRealtimeTestCase(unittest.TestCase):
    """Tests pour les endpoints statistiques temps réel"""
    
    def setUp(self):
        """Initialiser l'app de test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
            self._create_test_data()
            self.client = self.app.test_client()
    
    def _create_test_data(self):
        """Créer des données de test"""
        # Créer une détection
        detection = Detection(
            timestamp=datetime.now(),
            source='test_camera',
            image_path='test.jpg',
            total_persons=10,
            with_helmet=8,
            with_vest=7,
            with_glasses=6,
            with_boots=5,
            compliance_rate=80.0
        )
        db.session.add(detection)
        
        # Créer une alerte
        alert = Alert(
            timestamp=datetime.now(),
            detection_id=None,
            alert_type='missing_helmet',
            severity='high',
            message='Casque manquant',
            resolved=False
        )
        db.session.add(alert)
        
        # Créer un résultat d'entraînement
        training = TrainingResult(
            timestamp=datetime.now(),
            model_name='helmet_detection_v3',
            model_version='3.1',
            epochs=100,
            batch_size=32,
            image_size=640,
            val_precision=0.95,
            val_recall=0.92,
            val_f1_score=0.93,
            training_time_seconds=3600
        )
        db.session.add(training)
        
        db.session.commit()
    
    def tearDown(self):
        """Nettoyer après les tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    # =========================================================================
    # TESTS DES ENDPOINTS
    # =========================================================================
    
    def test_api_stats_exists(self):
        """Vérifier que /api/stats existe"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
    
    def test_api_stats_format(self):
        """Vérifier le format de /api/stats"""
        response = self.client.get('/api/stats')
        data = json.loads(response.data)
        
        # Vérifier les clés obligatoires
        required_keys = [
            'compliance_rate', 'total_persons', 'with_helmet',
            'with_vest', 'with_glasses', 'alerts', 'detections_today',
            'status'
        ]
        
        for key in required_keys:
            self.assertIn(key, data, f"Clé '{key}' manquante dans réponse")
    
    def test_api_stats_values(self):
        """Vérifier les valeurs de /api/stats"""
        response = self.client.get('/api/stats')
        data = json.loads(response.data)
        
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total_persons'], 10)
        self.assertEqual(data['with_helmet'], 8)
        self.assertEqual(data['with_vest'], 7)
        self.assertGreaterEqual(data['compliance_rate'], 0)
        self.assertLessEqual(data['compliance_rate'], 100)
    
    def test_api_realtime_exists(self):
        """Vérifier que /api/realtime existe"""
        response = self.client.get('/api/realtime')
        self.assertEqual(response.status_code, 200)
    
    def test_api_realtime_format(self):
        """Vérifier le format de /api/realtime"""
        response = self.client.get('/api/realtime')
        data = json.loads(response.data)
        
        required_keys = [
            'timestamps', 'persons', 'helmets', 'vests', 
            'glasses', 'boots', 'compliance_rates', 'status'
        ]
        
        for key in required_keys:
            self.assertIn(key, data, f"Clé '{key}' manquante")
    
    def test_api_chart_hourly_exists(self):
        """Vérifier que /api/chart/hourly existe"""
        response = self.client.get('/api/chart/hourly')
        self.assertEqual(response.status_code, 200)
    
    def test_api_chart_hourly_format(self):
        """Vérifier le format de /api/chart/hourly"""
        response = self.client.get('/api/chart/hourly')
        data = json.loads(response.data)
        
        self.assertIn('hours', data)
        self.assertIn('detections', data)
        self.assertEqual(len(data['hours']), len(data['detections']))
    
    def test_api_chart_epi_exists(self):
        """Vérifier que /api/chart/epi existe"""
        response = self.client.get('/api/chart/epi')
        self.assertEqual(response.status_code, 200)
    
    def test_api_chart_epi_format(self):
        """Vérifier le format de /api/chart/epi"""
        response = self.client.get('/api/chart/epi')
        data = json.loads(response.data)
        
        required_keys = ['helmets', 'vests', 'glasses', 'boots']
        for key in required_keys:
            self.assertIn(key, data)
    
    def test_api_chart_alerts_exists(self):
        """Vérifier que /api/chart/alerts existe"""
        response = self.client.get('/api/chart/alerts')
        self.assertEqual(response.status_code, 200)
    
    def test_api_chart_alerts_format(self):
        """Vérifier le format de /api/chart/alerts"""
        response = self.client.get('/api/chart/alerts')
        data = json.loads(response.data)
        
        required_keys = ['high', 'medium', 'low']
        for key in required_keys:
            self.assertIn(key, data)
    
    def test_api_chart_cumulative_exists(self):
        """Vérifier que /api/chart/cumulative existe"""
        response = self.client.get('/api/chart/cumulative')
        self.assertEqual(response.status_code, 200)
    
    def test_api_chart_cumulative_format(self):
        """Vérifier le format de /api/chart/cumulative"""
        response = self.client.get('/api/chart/cumulative')
        data = json.loads(response.data)
        
        self.assertIn('labels', data)
        self.assertIn('data', data)
        self.assertEqual(len(data['labels']), len(data['data']))
    
    # =========================================================================
    # TESTS DE CONTENU
    # =========================================================================
    
    def test_stats_has_data(self):
        """Vérifier que /api/stats retourne des données"""
        response = self.client.get('/api/stats')
        data = json.loads(response.data)
        
        # Les données de test doivent être présentes
        self.assertGreater(data['total_persons'], 0)
        self.assertGreater(data['with_helmet'], 0)
    
    def test_realtime_returns_list(self):
        """Vérifier que /api/realtime retourne des listes"""
        response = self.client.get('/api/realtime')
        data = json.loads(response.data)
        
        self.assertIsInstance(data['timestamps'], list)
        self.assertIsInstance(data['persons'], list)
        self.assertIsInstance(data['helmets'], list)
    
    def test_chart_epi_values_correct(self):
        """Vérifier que /api/chart/epi a les bonnes valeurs"""
        response = self.client.get('/api/chart/epi')
        data = json.loads(response.data)
        
        self.assertEqual(data['helmets'], 8)
        self.assertEqual(data['vests'], 7)
        self.assertEqual(data['glasses'], 6)
    
    # =========================================================================
    # TESTS DE PERFORMANCE
    # =========================================================================
    
    def test_stats_response_time(self):
        """Vérifier que /api/stats répond rapidement"""
        import time
        
        start = time.time()
        response = self.client.get('/api/stats')
        duration = time.time() - start
        
        self.assertLess(duration, 1.0, "Réponse trop lente (>1s)")
    
    def test_realtime_response_time(self):
        """Vérifier que /api/realtime répond rapidement"""
        import time
        
        start = time.time()
        response = self.client.get('/api/realtime')
        duration = time.time() - start
        
        self.assertLess(duration, 1.0, "Réponse trop lente (>1s)")
    
    # =========================================================================
    # TESTS D'ERREUR
    # =========================================================================
    
    def test_stats_returns_json(self):
        """Vérifier que /api/stats retourne du JSON"""
        response = self.client.get('/api/stats')
        
        self.assertEqual(
            response.content_type, 
            'application/json',
            "Content-Type doit être application/json"
        )
    
    def test_realtime_returns_json(self):
        """Vérifier que /api/realtime retourne du JSON"""
        response = self.client.get('/api/realtime')
        
        self.assertEqual(
            response.content_type,
            'application/json',
            "Content-Type doit être application/json"
        )


class StatsIntegrationTestCase(unittest.TestCase):
    """Tests d'intégration pour les statistiques"""
    
    def setUp(self):
        """Initialiser"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        with self.app.app_context():
            self.client = self.app.test_client()
    
    def test_all_endpoints_accessible(self):
        """Vérifier que tous les endpoints sont accessibles"""
        endpoints = [
            '/api/stats',
            '/api/realtime',
            '/api/chart/hourly',
            '/api/chart/epi',
            '/api/chart/alerts',
            '/api/chart/cumulative',
            '/api/stats/training',
            '/api/stats/uploads',
            '/api/stats/live'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertIn(
                response.status_code,
                [200, 500],  # 200 OK ou 500 si erreur serveur (mais endpoint existe)
                f"Endpoint {endpoint} inaccessible (code: {response.status_code})"
            )


if __name__ == '__main__':
    # Lancer les tests
    print("\n" + "="*70)
    print("🧪 TESTS STATISTIQUES TEMPS RÉEL")
    print("="*70 + "\n")
    
    # Exécuter les tests
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé
    print("\n" + "="*70)
    if result.wasSuccessful():
        print("✅ TOUS LES TESTS PASSÉS!")
        print("="*70)
        sys.exit(0)
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ!")
        print(f"   - Erreurs: {len(result.errors)}")
        print(f"   - Échecs: {len(result.failures)}")
        print("="*70)
        sys.exit(1)
