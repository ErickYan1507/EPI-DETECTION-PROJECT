"""
Tests unitaires pour le système de notifications
Exécutez avec: python -m pytest test_notification_system.py
"""

import unittest
import json
from pathlib import Path
import tempfile
import sys
import os

# Ajouter le répertoire parent au sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.notification_service import NotificationService


class TestNotificationService(unittest.TestCase):
    """Tests pour le service de notifications"""
    
    def setUp(self):
        """Initialiser avant chaque test"""
        # Créer une instance de service avec des fichiers temporaires
        self.temp_dir = tempfile.mkdtemp()
        self.service = NotificationService()
    
    def test_get_default_config(self):
        """Tester la récupération de la configuration par défaut"""
        config = self.service.get_config()
        
        self.assertIsInstance(config, dict)
        self.assertIn('sender_email', config)
        self.assertIn('daily_enabled', config)
        self.assertIn('daily_hour', config)
    
    def test_save_config(self):
        """Tester la sauvegarde de la configuration"""
        new_config = {
            'sender_email': 'test@example.com',
            'sender_password': 'testpass123',
            'daily_hour': 10
        }
        
        result = self.service.save_config(new_config)
        self.assertTrue(result)
        
        # Vérifier que la config a été sauvegardée
        saved_config = self.service.get_config()
        self.assertEqual(saved_config.get('sender_email'), 'test@example.com')
        self.assertEqual(saved_config.get('daily_hour'), 10)
    
    def test_add_recipient(self):
        """Tester l'ajout d'un destinataire"""
        email = "admin@example.com"
        result = self.service.add_recipient(email)
        
        self.assertTrue(result)
        
        # Vérifier que le destinataire a été ajouté
        recipients = self.service.get_recipients()
        self.assertIn(email, recipients)
    
    def test_duplicate_recipient(self):
        """Tester qu'on ne peut pas ajouter deux fois le même destinataire"""
        email = "admin@example.com"
        
        # Ajouter une première fois
        result1 = self.service.add_recipient(email)
        self.assertTrue(result1)
        
        # Tenter d'ajouter une deuxième fois
        result2 = self.service.add_recipient(email)
        self.assertFalse(result2)
    
    def test_invalid_email(self):
        """Tester l'ajout d'un email invalide"""
        result = self.service.add_recipient("notanemail")
        self.assertFalse(result)
    
    def test_remove_recipient(self):
        """Tester la suppression d'un destinataire"""
        email = "admin@example.com"
        
        # Ajouter
        self.service.add_recipient(email)
        
        # Supprimer
        result = self.service.remove_recipient(email)
        self.assertTrue(result)
        
        # Vérifier que le destinataire a été supprimé
        recipients = self.service.get_recipients()
        self.assertNotIn(email, recipients)
    
    def test_remove_nonexistent_recipient(self):
        """Tester la suppression d'un destinataire inexistant"""
        result = self.service.remove_recipient("nonexistent@example.com")
        self.assertFalse(result)
    
    def test_get_history(self):
        """Tester la récupération de l'historique"""
        history = self.service.get_history()
        self.assertIsInstance(history, list)
    
    def test_record_notification(self):
        """Tester l'enregistrement d'une notification"""
        self.service._record_notification(
            'test@example.com',
            'manual',
            'Test Subject',
            'success'
        )
        
        history = self.service.get_history()
        self.assertGreater(len(history), 0)
        
        # Vérifier la dernière notification
        latest = history[0]
        self.assertEqual(latest['recipient'], 'test@example.com')
        self.assertEqual(latest['type'], 'manual')
        self.assertEqual(latest['status'], 'success')
    
    def test_generate_daily_report_html(self):
        """Tester la génération du rapport quotidien"""
        # Cela va nécessiter une base de données
        # Pour ce test, on vérifie juste la structure
        html = self.service.generate_daily_report()
        
        self.assertIsInstance(html, str)
        self.assertIn('Rapport Quotidien', html)
        self.assertIn('</html>', html)
        self.assertIn('EPI Detection', html)
    
    def test_generate_weekly_report_html(self):
        """Tester la génération du rapport hebdomadaire"""
        html = self.service.generate_weekly_report()
        
        self.assertIsInstance(html, str)
        self.assertIn('Rapport Hebdomadaire', html)
        self.assertIn('</html>', html)
    
    def test_generate_monthly_report_html(self):
        """Tester la génération du rapport mensuel"""
        html = self.service.generate_monthly_report()
        
        self.assertIsInstance(html, str)
        self.assertIn('Rapport Mensuel', html)
        self.assertIn('</html>', html)


class TestNotificationServiceWithAPI(unittest.TestCase):
    """Tests d'intégration avec Flask"""
    
    @classmethod
    def setUpClass(cls):
        """Configurer l'application Flask pour les tests"""
        from app.main import app
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
    
    def test_api_get_config(self):
        """Tester l'endpoint GET /api/notifications/config"""
        response = self.client.get('/api/notifications/config')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('config', data)
    
    def test_api_add_recipient(self):
        """Tester l'endpoint POST /api/notifications/recipients"""
        email = "testapi@example.com"
        
        response = self.client.post(
            '/api/notifications/recipients',
            data=json.dumps({'email': email}),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [200, 201])
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_api_get_recipients(self):
        """Tester l'endpoint GET /api/notifications/recipients"""
        response = self.client.get('/api/notifications/recipients')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('recipients', data)
        self.assertIsInstance(data['recipients'], list)
    
    def test_api_get_history(self):
        """Tester l'endpoint GET /api/notifications/history"""
        response = self.client.get('/api/notifications/history')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('history', data)
        self.assertIsInstance(data['history'], list)
    
    def test_api_test_connection_no_config(self):
        """Tester l'endpoint POST /api/notifications/test-connection sans config"""
        response = self.client.post('/api/notifications/test-connection')
        
        # Devrait échouer si pas de configuration
        data = json.loads(response.data)
        # Soit success=false, soit une erreur
        self.assertIn('success', data)


if __name__ == '__main__':
    unittest.main()
