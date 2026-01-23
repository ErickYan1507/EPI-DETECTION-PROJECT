"""Routes API pour la gestion optionnelle des périphériques physiques (Arduino, MQTT, Bluetooth, USB, etc.)"""

from flask import Blueprint, request, jsonify, Response
from app.logger import logger
import json
import asyncio
from datetime import datetime
from app.arduino_integration import ArduinoSessionManager

physical_routes = Blueprint('physical', __name__, url_prefix='/api/physical')

# ===== GESTION CONFIGURATION =====
class PhysicalDeviceConfig:
    """Gestionnaire de configuration des périphériques physiques"""
    
    def __init__(self):
        self.config = {
            'devices': {
                'arduino': False,
                'mqtt': False,
                'network': False,
                'bluetooth': False,
                'usb': False,
                'cloud': False
            },
            'settings': {
                'arduino_port': 'COM3',
                'mqtt_broker': 'localhost:1883',
                'network_endpoint': 'http://localhost:8000/api/sensors',
                'bluetooth_device': '',
                'usb_device_id': '',
                'cloud_config': '',
                'scan_interval': 5000,
                'connection_timeout': 10,
                'reconnect_attempts': 5
            }
        }
        self.device_handlers = {}
        self.connection_status = {}

config_manager = PhysicalDeviceConfig()

# ===== ROUTES API =====

@physical_routes.route('/config', methods=['GET'])
def get_config():
    """Récupérer la configuration actuelle des périphériques"""
    try:
        return jsonify({
            'status': 'ok',
            'config': config_manager.config,
            'connection_status': config_manager.connection_status
        }), 200
    except Exception as e:
        logger.error(f"Erreur récupération config: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/config', methods=['POST'])
def set_config():
    """Définir la configuration des périphériques"""
    try:
        data = request.json
        
        if 'devices' in data:
            config_manager.config['devices'].update(data.get('devices', {}))
        
        if 'settings' in data:
            config_manager.config['settings'].update(data.get('settings', {}))
        
        logger.info(f"Configuration mise à jour: {config_manager.config}")
        
        return jsonify({
            'status': 'ok',
            'message': 'Configuration appliquée',
            'config': config_manager.config
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur config: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/status', methods=['GET'])
def get_device_status():
    """Récupérer le statut de tous les périphériques"""
    try:
        return jsonify({
            'status': 'ok',
            'devices': config_manager.connection_status,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Erreur statut: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===== TESTS PÉRIPHÉRIQUES =====

@physical_routes.route('/arduino/test', methods=['POST'])
def test_arduino():
    """Tester la connexion Arduino"""
    try:
        data = request.json
        port = data.get('port', 'COM3')
        
        logger.info(f"Test Arduino sur port: {port}")
        
        # Tentative de connexion
        status = test_serial_connection(port)
        
        config_manager.connection_status['arduino'] = {
            'connected': status['connected'],
            'port': port,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'ok' if status['connected'] else 'error',
            'message': status['message'],
            'port': port
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur test Arduino: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/mqtt/test', methods=['POST'])
def test_mqtt():
    """Tester la connexion MQTT"""
    try:
        data = request.json
        broker = data.get('broker', 'localhost:1883')
        
        logger.info(f"Test MQTT sur: {broker}")
        
        # Tentative de connexion MQTT
        status = test_mqtt_connection(broker)
        
        config_manager.connection_status['mqtt'] = {
            'connected': status['connected'],
            'broker': broker,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'ok' if status['connected'] else 'error',
            'message': status['message'],
            'broker': broker
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur test MQTT: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/network/test', methods=['POST'])
def test_network():
    """Tester la connexion réseau (HTTP)"""
    try:
        data = request.json
        endpoint = data.get('endpoint', 'http://localhost:8000/api/sensors')
        
        logger.info(f"Test réseau: {endpoint}")
        
        # Tentative de connexion HTTP
        status = test_http_connection(endpoint)
        
        config_manager.connection_status['network'] = {
            'connected': status['connected'],
            'endpoint': endpoint,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'ok' if status['connected'] else 'error',
            'message': status['message'],
            'endpoint': endpoint
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur test réseau: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/bluetooth/test', methods=['POST'])
def test_bluetooth():
    """Tester la connexion Bluetooth (Web Bluetooth API)"""
    try:
        data = request.json
        device_uuid = data.get('device', '')
        
        logger.info(f"Test Bluetooth: {device_uuid}")
        
        return jsonify({
            'status': 'pending',
            'message': 'Bluetooth testing requires client-side Web Bluetooth API',
            'note': 'Use navigator.bluetooth.requestDevice() in JavaScript'
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur test Bluetooth: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/usb/test', methods=['POST'])
def test_usb():
    """Tester la connexion USB (WebUSB API)"""
    try:
        data = request.json
        device_id = data.get('device_id', '')
        
        logger.info(f"Test USB: {device_id}")
        
        return jsonify({
            'status': 'pending',
            'message': 'USB testing requires client-side WebUSB API',
            'note': 'Use navigator.usb.requestDevice() in JavaScript'
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur test USB: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/cloud/test', methods=['POST'])
def test_cloud():
    """Tester la connexion Cloud (Azure, AWS, Google Cloud)"""
    try:
        data = request.json
        cloud_config = data.get('cloud_config', '')
        
        logger.info(f"Test Cloud connection")
        
        return jsonify({
            'status': 'pending',
            'message': 'Cloud connection test pending'
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur test Cloud: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===== FONCTIONS DE TEST AUXILIAIRES =====

def test_serial_connection(port):
    """Tester la connexion série (Arduino)"""
    try:
        import serial
        
        ser = serial.Serial(port, 9600, timeout=2)
        ser.close()
        
        return {
            'connected': True,
            'message': f'Arduino connecté sur {port}'
        }
    except ImportError:
        return {
            'connected': False,
            'message': 'Librairie pyserial non installée. Installez avec: pip install pyserial'
        }
    except Exception as e:
        return {
            'connected': False,
            'message': f'Erreur connexion serie: {str(e)}'
        }


def test_mqtt_connection(broker):
    """Tester la connexion MQTT"""
    try:
        import paho.mqtt.client as mqtt
        
        client = mqtt.Client()
        
        host, port = broker.split(':') if ':' in broker else (broker, 1883)
        port = int(port)
        
        result = client.connect(host, port, keepalive=2)
        client.disconnect()
        
        if result == 0:
            return {
                'connected': True,
                'message': f'MQTT connecté à {broker}'
            }
        else:
            return {
                'connected': False,
                'message': f'Erreur connexion MQTT: code {result}'
            }
            
    except ImportError:
        return {
            'connected': False,
            'message': 'Librairie paho-mqtt non installée. Installez avec: pip install paho-mqtt'
        }
    except Exception as e:
        return {
            'connected': False,
            'message': f'Erreur MQTT: {str(e)}'
        }


def test_http_connection(endpoint):
    """Tester la connexion HTTP"""
    try:
        import requests
        
        response = requests.get(endpoint, timeout=5)
        
        return {
            'connected': response.status_code < 500,
            'message': f'Réponse HTTP {response.status_code}',
            'status_code': response.status_code
        }
        
    except ImportError:
        return {
            'connected': False,
            'message': 'Librairie requests non installée'
        }
    except requests.ConnectionError:
        return {
            'connected': False,
            'message': f'Impossible de se connecter à {endpoint}'
        }
    except requests.Timeout:
        return {
            'connected': False,
            'message': f'Timeout lors de la connexion à {endpoint}'
        }
    except Exception as e:
        return {
            'connected': False,
            'message': f'Erreur HTTP: {str(e)}'
        }


# ===== STREAMING DE DONNÉES =====

@physical_routes.route('/stream/<device_type>', methods=['GET'])
def stream_device_data(device_type):
    """Flux continu des données du périphérique (Server-Sent Events)"""
    try:
        def generate():
            while True:
                # Générer des données fictives ou réelles
                data = {
                    'device': device_type,
                    'timestamp': datetime.now().isoformat(),
                    'data': {}
                }
                
                if device_type == 'arduino':
                    data['data'] = {
                        'motion': False,
                        'temperature': 23.5,
                        'humidity': 55,
                        'compliance': 85
                    }
                elif device_type == 'mqtt':
                    data['data'] = {
                        'topic': 'sensors/temperature',
                        'value': 22.8
                    }
                
                yield f"data: {json.dumps(data)}\n\n"
                
                import time
                time.sleep(5)
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"Erreur streaming: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===== COMMANDES DIRECTES AUX PÉRIPHÉRIQUES =====

@physical_routes.route('/arduino/command', methods=['POST'])
def send_arduino_command():
    """Envoyer une commande directe à Arduino"""
    try:
        data = request.json
        command = data.get('command')
        port = data.get('port', 'COM3')
        
        logger.info(f"Commande Arduino: {command} sur {port}")
        
        # Envoyer commande
        result = send_serial_command(port, command)
        
        return jsonify({
            'status': 'ok' if result['success'] else 'error',
            'message': result['message'],
            'response': result.get('response', '')
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur commande Arduino: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def send_serial_command(port, command):
    """Envoyer une commande via port série"""
    try:
        import serial
        
        ser = serial.Serial(port, 9600, timeout=2)
        
        # Envoyer commande
        ser.write((command + '\n').encode())
        
        # Lire réponse
        response = ser.readline().decode('utf-8', errors='ignore').strip()
        
        ser.close()
        
        return {
            'success': True,
            'message': f'Commande envoyée',
            'response': response
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Erreur envoi commande: {str(e)}'
        }


@physical_routes.route('/led/control', methods=['POST'])
def control_led():
    """Contrôler les LEDs (via Arduino)"""
    try:
        data = request.json
        led = data.get('led', 'red')  # 'red' ou 'green'
        state = data.get('state', 'on')  # 'on' ou 'off'
        port = data.get('port', 'COM3')
        
        # Construire commande Arduino
        command = f"LED:{led.upper()}:{state.upper()}"
        
        result = send_serial_command(port, command)
        
        return jsonify({
            'status': 'ok' if result['success'] else 'error',
            'message': result['message']
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur contrôle LED: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/buzzer/control', methods=['POST'])
def control_buzzer():
    """Contrôler le buzzer (via Arduino)"""
    try:
        data = request.json
        state = data.get('state', 'on')  # 'on' ou 'off'
        duration = data.get('duration', 1000)  # en ms
        port = data.get('port', 'COM3')
        
        # Construire commande Arduino
        command = f"BUZZER:{state.upper()}:{duration}"
        
        result = send_serial_command(port, command)
        
        return jsonify({
            'status': 'ok' if result['success'] else 'error',
            'message': result['message']
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur contrôle buzzer: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===== ROUTES ARDUINO AVANCÉES =====

# Gestionnaires Arduino par port
arduino_sessions = {}

@physical_routes.route('/arduino/connect', methods=['POST'])
def arduino_connect():
    """Établir une connexion Arduino persistent"""
    try:
        data = request.json
        port = data.get('port', 'COM3')
        
        logger.info(f"Connexion Arduino: {port}")
        
        # Créer ou réutiliser la session
        if port not in arduino_sessions:
            arduino_sessions[port] = ArduinoSessionManager(port=port)
        
        session = arduino_sessions[port]
        if session.connect():
            return jsonify({
                'status': 'ok',
                'message': f'Arduino connecté sur {port}',
                'port': port
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'Impossible de se connecter à {port}'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur connexion Arduino: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/arduino/disconnect', methods=['POST'])
def arduino_disconnect():
    """Fermer la connexion Arduino"""
    try:
        data = request.json
        port = data.get('port', 'COM3')
        
        if port in arduino_sessions:
            arduino_sessions[port].disconnect()
            del arduino_sessions[port]
        
        return jsonify({
            'status': 'ok',
            'message': f'Arduino déconnecté'
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur déconnexion Arduino: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/arduino/metrics', methods=['GET'])
def arduino_get_metrics():
    """Récupérer les métriques actuelles d'Arduino"""
    try:
        port = request.args.get('port', 'COM3')
        
        if port not in arduino_sessions:
            return jsonify({'status': 'error', 'message': 'Arduino non connecté'}), 400
        
        metrics = arduino_sessions[port].get_current_metrics()
        
        return jsonify({
            'status': 'ok',
            'port': port,
            'metrics': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lecture métriques: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/arduino/history', methods=['GET'])
def arduino_get_history():
    """Récupérer l'historique des données Arduino"""
    try:
        port = request.args.get('port', 'COM3')
        limit = request.args.get('limit', 50, type=int)
        
        if port not in arduino_sessions:
            return jsonify({'status': 'error', 'message': 'Arduino non connecté'}), 400
        
        history = arduino_sessions[port].get_history(limit=limit)
        
        return jsonify({
            'status': 'ok',
            'port': port,
            'count': len(history),
            'data': history
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lecture historique: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/arduino/send-compliance', methods=['POST'])
def arduino_send_compliance():
    """Envoyer le niveau de conformité à Arduino (0-100)"""
    try:
        data = request.json
        port = data.get('port', 'COM3')
        compliance = data.get('compliance', 0)
        
        if port not in arduino_sessions:
            return jsonify({'status': 'error', 'message': 'Arduino non connecté'}), 400
        
        compliance = max(0, min(100, compliance))
        arduino_sessions[port].send_compliance(compliance)
        
        return jsonify({
            'status': 'ok',
            'message': f'Niveau de conformité envoyé: {compliance}%',
            'port': port
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur envoi conformité: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/arduino/send-detection', methods=['POST'])
def arduino_send_detection():
    """Envoyer les données de détection EPI à Arduino"""
    try:
        data = request.json
        port = data.get('port', 'COM3')
        helmet = data.get('helmet', False)
        vest = data.get('vest', False)
        glasses = data.get('glasses', False)
        confidence = data.get('confidence', 0)
        
        if port not in arduino_sessions:
            return jsonify({'status': 'error', 'message': 'Arduino non connecté'}), 400
        
        arduino_sessions[port].send_detection(helmet, vest, glasses, confidence)
        
        return jsonify({
            'status': 'ok',
            'message': 'Données de détection envoyées',
            'port': port,
            'data': {
                'helmet': helmet,
                'vest': vest,
                'glasses': glasses,
                'confidence': confidence
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur envoi détection: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@physical_routes.route('/arduino/metrics-stream', methods=['GET'])
def arduino_stream_metrics():
    """Flux continu des métriques Arduino (Server-Sent Events)"""
    try:
        port = request.args.get('port', 'COM3')
        
        if port not in arduino_sessions:
            return jsonify({'status': 'error', 'message': 'Arduino non connecté'}), 400
        
        def generate():
            import time
            while True:
                try:
                    metrics = arduino_sessions[port].get_current_metrics()
                    yield f"data: {json.dumps(metrics)}\n\n"
                    time.sleep(1)
                except GeneratorExit:
                    break
                except Exception as e:
                    logger.error(f"Erreur streaming: {e}")
                    break
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"Erreur stream Arduino: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500