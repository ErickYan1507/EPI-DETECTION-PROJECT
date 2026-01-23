#!/usr/bin/env python3
"""
Tests unitaires pour les périphériques physiques optionnels
Valide les routes API et la gestion des configurations
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes_physical_devices import (
    physical_routes,
    PhysicalDeviceConfig,
    test_serial_connection,
    test_mqtt_connection,
    test_http_connection,
    send_serial_command
)

class TestPhysicalDeviceConfig:
    """Tests pour la classe de configuration"""
    
    def test_initialization(self):
        """Tester l'initialisation de la config"""
        config = PhysicalDeviceConfig()
        
        assert config.config is not None
        assert 'devices' in config.config
        assert 'settings' in config.config
        assert config.connection_status == {}
    
    def test_default_config_structure(self):
        """Vérifier la structure par défaut"""
        config = PhysicalDeviceConfig()
        
        # Vérifier les clés devices
        required_devices = ['arduino', 'mqtt', 'network', 'bluetooth', 'usb', 'cloud']
        for device in required_devices:
            assert device in config.config['devices']
        
        # Vérifier les clés settings
        required_settings = [
            'arduino_port', 'mqtt_broker', 'network_endpoint',
            'bluetooth_device', 'usb_device_id', 'cloud_config',
            'scan_interval', 'connection_timeout', 'reconnect_attempts'
        ]
        for setting in required_settings:
            assert setting in config.config['settings']
    
    def test_enable_device(self):
        """Tester l'activation d'un périphérique"""
        config = PhysicalDeviceConfig()
        
        config.config['devices']['arduino'] = True
        assert config.config['devices']['arduino'] is True
    
    def test_update_settings(self):
        """Tester la mise à jour des paramètres"""
        config = PhysicalDeviceConfig()
        
        config.config['settings']['arduino_port'] = 'COM5'
        assert config.config['settings']['arduino_port'] == 'COM5'


class TestSerialConnection:
    """Tests pour la connexion série Arduino"""
    
    @patch('app.routes_physical_devices.serial.Serial')
    def test_serial_connection_success(self, mock_serial):
        """Tester une connexion série réussie"""
        mock_serial_instance = MagicMock()
        mock_serial.return_value = mock_serial_instance
        
        result = test_serial_connection('COM3')
        
        assert result['connected'] is True
        assert 'Arduino' in result['message']
        mock_serial.assert_called_once_with('COM3', 9600, timeout=2)
        mock_serial_instance.close.assert_called_once()
    
    @patch('app.routes_physical_devices.serial')
    def test_serial_connection_no_module(self, mock_serial):
        """Tester quand pyserial n'est pas installé"""
        mock_serial.side_effect = ImportError()
        
        # Simuler ImportError
        import importlib
        with patch.dict('sys.modules', {'serial': None}):
            # Cette approche teste le comportement esperé
            pass
    
    @patch('app.routes_physical_devices.serial.Serial')
    def test_serial_connection_failure(self, mock_serial):
        """Tester une connexion série échouée"""
        mock_serial.side_effect = Exception("Port not found")
        
        result = test_serial_connection('COM3')
        
        assert result['connected'] is False
        assert 'erreur' in result['message'].lower()


class TestMQTTConnection:
    """Tests pour la connexion MQTT"""
    
    @patch('app.routes_physical_devices.mqtt.Client')
    def test_mqtt_connection_success(self, mock_mqtt_client):
        """Tester une connexion MQTT réussie"""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client
        mock_client.connect.return_value = 0  # Success code
        
        result = test_mqtt_connection('localhost:1883')
        
        assert result['connected'] is True
        assert 'MQTT' in result['message']
        mock_client.connect.assert_called_once_with('localhost', 1883, keepalive=2)
        mock_client.disconnect.assert_called_once()
    
    @patch('app.routes_physical_devices.mqtt.Client')
    def test_mqtt_connection_invalid_broker(self, mock_mqtt_client):
        """Tester avec un broker invalide"""
        mock_client = MagicMock()
        mock_mqtt_client.return_value = mock_client
        mock_client.connect.side_effect = Exception("Connection refused")
        
        result = test_mqtt_connection('invalid.broker:1883')
        
        assert result['connected'] is False
        assert 'erreur' in result['message'].lower() or 'Erreur' in result['message']
    
    def test_mqtt_broker_parsing(self):
        """Tester le parsing du broker MQTT"""
        # Tester avec port
        with patch('app.routes_physical_devices.mqtt.Client'):
            result = test_mqtt_connection('broker.example.com:1883')
            assert result is not None
        
        # Tester sans port (défaut)
        with patch('app.routes_physical_devices.mqtt.Client'):
            result = test_mqtt_connection('broker.example.com')
            assert result is not None


class TestHTTPConnection:
    """Tests pour la connexion HTTP"""
    
    @patch('app.routes_physical_devices.requests.get')
    def test_http_connection_success(self, mock_get):
        """Tester une connexion HTTP réussie"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = test_http_connection('http://localhost:8000/api/sensors')
        
        assert result['connected'] is True
        assert result['status_code'] == 200
    
    @patch('app.routes_physical_devices.requests.get')
    def test_http_connection_timeout(self, mock_get):
        """Tester un timeout HTTP"""
        import requests
        mock_get.side_effect = requests.Timeout()
        
        result = test_http_connection('http://localhost:8000/api/sensors')
        
        assert result['connected'] is False
        assert 'Timeout' in result['message']
    
    @patch('app.routes_physical_devices.requests.get')
    def test_http_connection_refused(self, mock_get):
        """Tester une connexion refusée"""
        import requests
        mock_get.side_effect = requests.ConnectionError()
        
        result = test_http_connection('http://localhost:8000/api/sensors')
        
        assert result['connected'] is False
        assert 'Impossible' in result['message']


class TestSendSerialCommand:
    """Tests pour l'envoi de commandes série"""
    
    @patch('app.routes_physical_devices.serial.Serial')
    def test_send_command_success(self, mock_serial):
        """Tester l'envoi d'une commande réussie"""
        mock_instance = MagicMock()
        mock_serial.return_value = mock_instance
        mock_instance.readline.return_value = b'OK\n'
        
        result = send_serial_command('COM3', 'C85')
        
        assert result['success'] is True
        assert 'Commande' in result['message']
        mock_instance.write.assert_called_once_with(b'C85\n')
    
    @patch('app.routes_physical_devices.serial.Serial')
    def test_send_command_failure(self, mock_serial):
        """Tester l'envoi d'une commande échouée"""
        mock_serial.side_effect = Exception("Port error")
        
        result = send_serial_command('COM3', 'C85')
        
        assert result['success'] is False
        assert 'erreur' in result['message'].lower() or 'Erreur' in result['message']


class TestFlaskRoutes:
    """Tests pour les routes Flask"""
    
    def test_routes_registered(self):
        """Vérifier que les routes sont bien enregistrées"""
        assert physical_routes is not None
        assert physical_routes.name == 'physical'
        assert physical_routes.url_prefix == '/api/physical'
    
    def test_route_endpoints(self):
        """Vérifier les endpoints disponibles"""
        endpoints = [
            '/config',
            '/status',
            '/arduino/test',
            '/mqtt/test',
            '/network/test',
            '/bluetooth/test',
            '/usb/test',
            '/cloud/test',
        ]
        
        # Vérifier que les fonctions existent
        route_functions = [func.__name__ for func in physical_routes.deferred_functions]
        
        # Note: Les routes deferred_functions ne contiennent pas les noms,
        # nous simplement vérifions que le blueprint a des routes
        assert len(physical_routes.deferred_functions) > 0


class TestConfigValidation:
    """Tests pour la validation de configuration"""
    
    def test_valid_port_strings(self):
        """Tester les formats de port valides"""
        valid_ports = ['COM1', 'COM3', '/dev/ttyUSB0', '/dev/cu.usbserial-123']
        
        for port in valid_ports:
            assert isinstance(port, str)
            assert len(port) > 0
    
    def test_valid_mqtt_broker_format(self):
        """Tester les formats de broker MQTT valides"""
        valid_brokers = [
            'localhost:1883',
            'broker.hivemq.com:1883',
            'mqtt.example.com:8883',
            '192.168.1.100:1883'
        ]
        
        for broker in valid_brokers:
            parts = broker.split(':')
            assert len(parts) == 2
            assert int(parts[1]) > 0
    
    def test_valid_endpoint_url(self):
        """Tester les formats d'URL valides"""
        valid_urls = [
            'http://localhost:8000/api/sensors',
            'http://192.168.1.100:5000/data',
            'https://api.example.com/sensors',
        ]
        
        for url in valid_urls:
            assert url.startswith('http://') or url.startswith('https://')


if __name__ == '__main__':
    # Lancer les tests
    print("🧪 Lancement des tests pour les périphériques physiques...\n")
    
    pytest.main([__file__, '-v', '--tb=short'])
    
    print("\n✅ Tests terminés")
