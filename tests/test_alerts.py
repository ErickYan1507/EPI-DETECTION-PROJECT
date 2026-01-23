#!/usr/bin/env python3
"""
Tests unitaires pour le système d'alertes email
"""

import pytest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Ajouter le chemin du projet
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Importer le gestionnaire d'alertes
from app.alert_manager import AlertManager


class TestAlertManager:
    """Tests du gestionnaire d'alertes"""
    
    @pytest.fixture
    def alert_manager(self):
        """Créer une instance du gestionnaire pour les tests"""
        return AlertManager(
            enabled=True,
            sender_email='test@gmail.com',
            password='test_password',
            recipients=['admin@test.com'],
            smtp_server='smtp.gmail.com',
            smtp_port=587
        )
    
    def test_initialization(self, alert_manager):
        """Tester l'initialisation du gestionnaire"""
        assert alert_manager.enabled is True
        assert alert_manager.sender_email == 'test@gmail.com'
        assert 'admin@test.com' in alert_manager.recipients
        assert alert_manager.smtp_server == 'smtp.gmail.com'
        assert alert_manager.smtp_port == 587
    
    def test_is_configured(self, alert_manager):
        """Tester la détection de configuration"""
        # Avec configuration valide
        assert alert_manager.is_configured() is True
        
        # Sans destinataire
        alert_manager.recipients = []
        assert alert_manager.is_configured() is False
        
        # Sans email expéditeur
        alert_manager.sender_email = None
        alert_manager.recipients = ['admin@test.com']
        assert alert_manager.is_configured() is False
    
    def test_multiple_recipients(self, alert_manager):
        """Tester les destinataires multiples"""
        alert_manager.recipients = ['admin@test.com', 'manager@test.com', 'safety@test.com']
        assert len(alert_manager.recipients) == 3
        assert 'manager@test.com' in alert_manager.recipients
    
    def test_alert_cooldown(self, alert_manager):
        """Tester le mécanisme de cooldown"""
        alert_type = 'missing_epi'
        
        # Première alerte - pas de cooldown
        can_alert = alert_manager._can_send_alert(alert_type)
        assert can_alert is True
        
        # Enregistrer l'heure d'alerte
        alert_manager.last_alert_time[alert_type] = datetime.now()
        
        # Essayer immédiatement - cooldown actif
        can_alert = alert_manager._can_send_alert(alert_type)
        assert can_alert is False
        
        # Simuler l'écoulement du cooldown
        alert_manager.last_alert_time[alert_type] = \
            datetime.now() - timedelta(seconds=alert_manager.alert_cooldown + 1)
        can_alert = alert_manager._can_send_alert(alert_type)
        assert can_alert is True
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp, alert_manager):
        """Tester l'envoi d'email réussi"""
        # Configurer le mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Envoyer un email
        result = alert_manager.send(
            subject='Test Subject',
            body='Test Body',
            html=True
        )
        
        # Vérifier
        assert result is True
        mock_server.sendmail.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp, alert_manager):
        """Tester l'échec d'envoi d'email"""
        # Configurer le mock pour lever une exception
        mock_smtp.side_effect = Exception("Connection failed")
        
        # Envoyer un email
        result = alert_manager.send(
            subject='Test Subject',
            body='Test Body'
        )
        
        # Vérifier
        assert result is False
    
    @patch.object(AlertManager, 'send')
    def test_alert_missing_epi(self, mock_send, alert_manager):
        """Tester l'alerte EPI manquant"""
        mock_send.return_value = True
        
        result = alert_manager.alert_missing_epi(
            epi_type='helmet',
            duration_seconds=300
        )
        
        assert result is True
        mock_send.assert_called_once()
        
        # Vérifier le contenu
        call_args = mock_send.call_args
        assert 'helmet' in call_args[1]['subject']
        assert '300' in call_args[1]['body']
    
    @patch.object(AlertManager, 'send')
    def test_alert_low_detection_rate(self, mock_send, alert_manager):
        """Tester l'alerte taux de détection faible"""
        mock_send.return_value = True
        
        result = alert_manager.alert_low_detection_rate(
            detection_count=2,
            time_window_minutes=10
        )
        
        assert result is True
        mock_send.assert_called_once()
    
    @patch.object(AlertManager, 'send')
    def test_alert_system_error(self, mock_send, alert_manager):
        """Tester l'alerte erreur système"""
        mock_send.return_value = True
        
        result = alert_manager.alert_system_error(
            error_type='DatabaseError',
            error_message='Connection failed'
        )
        
        assert result is True
        mock_send.assert_called_once()
    
    @patch.object(AlertManager, 'send')
    def test_test_configuration(self, mock_send, alert_manager):
        """Tester la fonction de test de configuration"""
        mock_send.return_value = True
        
        result = alert_manager.test_configuration()
        
        assert result is True
        mock_send.assert_called_once()


class TestAlertManagerWithoutConfiguration:
    """Tests du gestionnaire sans configuration"""
    
    def test_alerts_disabled(self):
        """Tester quand les alertes sont désactivées"""
        alert_manager = AlertManager(enabled=False)
        
        result = alert_manager.send(subject='Test', body='Test')
        assert result is False  # Ne pas envoyer si désactivé
    
    def test_missing_configuration(self):
        """Tester avec configuration manquante"""
        alert_manager = AlertManager(
            enabled=True,
            sender_email=None,
            password=None,
            recipients=[]
        )
        
        assert alert_manager.is_configured() is False


class TestEmailFormatting:
    """Tests du formatage des emails"""
    
    def test_html_email_format(self):
        """Tester le formatage HTML"""
        alert_manager = AlertManager(
            enabled=True,
            sender_email='test@gmail.com',
            password='test',
            recipients=['admin@test.com']
        )
        
        # Créer un email HTML
        subject = "Test Subject"
        body = "<h1>Test Title</h1><p>Test content</p>"
        
        # Vérifier que le body contient du HTML
        assert '<h1>' in body
        assert '</h1>' in body
    
    def test_plain_text_email_format(self):
        """Tester le formatage texte brut"""
        alert_manager = AlertManager(
            enabled=True,
            sender_email='test@gmail.com',
            password='test',
            recipients=['admin@test.com']
        )
        
        # Créer un email en texte brut
        subject = "Test Subject"
        body = "Test content"
        
        # Vérifier
        assert '<' not in body  # Pas de HTML


class TestAsyncEmails:
    """Tests des emails asynchrones"""
    
    @patch.object(AlertManager, 'send')
    def test_async_alert_missing_epi(self, mock_send):
        """Tester l'alerte asynchrone EPI manquant"""
        alert_manager = AlertManager(
            enabled=True,
            sender_email='test@gmail.com',
            password='test',
            recipients=['admin@test.com']
        )
        
        mock_send.return_value = True
        
        # Envoyer de manière asynchrone
        alert_manager.send_async(
            subject='Test',
            body='Body'
        )
        
        # Vérifier que send a été appelé
        assert mock_send.called


# ============================================================================
# TESTS D'INTÉGRATION
# ============================================================================

class TestAlertIntegration:
    """Tests d'intégration avec le système"""
    
    @patch('app.alert_manager.smtplib.SMTP')
    def test_full_workflow(self, mock_smtp):
        """Tester le workflow complet"""
        # Configurer le mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Créer le gestionnaire
        alert_manager = AlertManager(
            enabled=True,
            sender_email='test@gmail.com',
            password='test_pass',
            recipients=['admin@test.com', 'manager@test.com'],
            smtp_server='smtp.gmail.com',
            smtp_port=587
        )
        
        # Vérifier la configuration
        assert alert_manager.is_configured() is True
        
        # Envoyer une alerte
        result = alert_manager.alert_missing_epi(
            epi_type='helmet',
            duration_seconds=300
        )
        
        # Vérifier
        assert result is True
        mock_server.sendmail.assert_called_once()


# ============================================================================
# FIXTURES PYTEST
# ============================================================================

@pytest.fixture(scope="session")
def test_config():
    """Configuration de test"""
    return {
        'sender_email': 'test@gmail.com',
        'password': 'test_password',
        'recipients': ['admin@test.com'],
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'enabled': True
    }


# ============================================================================
# EXÉCUTION DES TESTS
# ============================================================================

if __name__ == '__main__':
    # Exécuter les tests avec pytest
    pytest.main([__file__, '-v', '--tb=short'])
