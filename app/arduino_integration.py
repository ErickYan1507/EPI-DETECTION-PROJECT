"""
Module d'intégration Arduino avancé pour EPI Detection
Gère la communication série, parsing de données, et contrôle des périphériques
"""

import threading
import queue
from datetime import datetime
from app.logger import logger
from typing import Optional, Dict, Any, Callable

# Importer serial avec gestion gracieuse de l'absence
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logger.warning("⚠️ PySerial non installé - Arduino communication désactivée")
    logger.warning("   Installez avec: pip install pyserial")

class ArduinoController:
    """Contrôleur Arduino avec support de lecture/écriture asynchrone"""
    
    def __init__(self, port: str = 'COM3', baudrate: int = 9600, timeout: int = 2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.connected = False
        self.read_queue = queue.Queue()
        self.read_thread = None
        self.stop_reading = False
        self.callbacks = []
        
    def connect(self) -> bool:
        """Établir connexion avec Arduino"""
        try:
            if not SERIAL_AVAILABLE:
                logger.error("❌ PySerial non disponible - installez avec: pip install pyserial")
                return False
            
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.connected = True
            
            # Démarrer thread de lecture
            self.stop_reading = False
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            logger.info(f"✅ Arduino connecté sur {self.port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion Arduino: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Fermer connexion Arduino"""
        try:
            self.stop_reading = True
            if self.read_thread:
                self.read_thread.join(timeout=2)
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.connected = False
            logger.info("🔌 Arduino déconnecté")
        except Exception as e:
            logger.error(f"Erreur déconnexion Arduino: {e}")
    
    def send_command(self, command: str) -> bool:
        """Envoyer une commande à Arduino"""
        try:
            if not self.connected or not self.ser:
                logger.warning("Arduino non connecté")
                return False
            
            self.ser.write((command + '\n').encode())
            logger.debug(f"📤 Commande envoyée: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi commande: {e}")
            return False
    
    def send_compliance_level(self, level: int) -> bool:
        """Envoyer le niveau de conformité à Arduino (0-100)"""
        level = max(0, min(100, level))
        return self.send_command(f"C{level}")
    
    def send_detection_data(self, helmet: bool, vest: bool, glasses: bool, confidence: int) -> bool:
        """Envoyer les données de détection EPI à Arduino"""
        helmet_val = 1 if helmet else 0
        vest_val = 1 if vest else 0
        glasses_val = 1 if glasses else 0
        command = f"DETECT:helmet={helmet_val},vest={vest_val},glasses={glasses_val},confidence={confidence}"
        return self.send_command(command)
    
    def get_data(self, timeout: float = 1.0) -> Optional[str]:
        """Récupérer une ligne de données Arduino"""
        try:
            return self.read_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def register_callback(self, callback: Callable):
        """Enregistrer un callback pour chaque ligne reçue"""
        self.callbacks.append(callback)
    
    def _read_loop(self):
        """Boucle de lecture des données Arduino"""
        while not self.stop_reading and self.connected:
            try:
                if self.ser and self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if line:
                        self.read_queue.put(line)
                        
                        # Appeler les callbacks
                        for callback in self.callbacks:
                            try:
                                callback(line)
                            except Exception as e:
                                logger.error(f"Erreur callback: {e}")
                        
                        logger.debug(f"📥 Arduino: {line}")
                        
            except Exception as e:
                if not self.stop_reading:
                    logger.error(f"Erreur lecture Arduino: {e}")
            
            # Petit délai pour éviter surcharge CPU
            import time
            time.sleep(0.05)


class ArduinoDataParser:
    """Parse et traite les données reçues de l'Arduino"""
    
    @staticmethod
    def parse_line(line: str) -> Dict[str, Any]:
        """Parser une ligne Arduino"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'raw': line,
            'type': None,
            'data': {}
        }
        
        # Motion detection
        if 'MOTION' in line.upper():
            result['type'] = 'motion'
            result['data']['detected'] = True
        
        # Sensor data: [SENSOR] temp=25.5,humidity=60
        elif '[SENSOR]' in line:
            result['type'] = 'sensor'
            parts = line.split('temp=')
            if len(parts) > 1:
                try:
                    temp_str = parts[1].split(',')[0]
                    humidity_str = line.split('humidity=')[1].strip()
                    result['data']['temperature'] = float(temp_str)
                    result['data']['humidity'] = float(humidity_str)
                except:
                    pass
        
        # Status: [STATUS] ✅ SAFE (Compliance: 85%)
        elif '[STATUS]' in line:
            result['type'] = 'status'
            if '✅' in line:
                result['data']['status'] = 'SAFE'
            elif '⚠️' in line:
                result['data']['status'] = 'WARNING'
            elif '🚨' in line:
                result['data']['status'] = 'DANGER'
            
            # Extract compliance percentage
            try:
                comp_str = line.split('Compliance: ')[1].split('%')[0]
                result['data']['compliance'] = int(comp_str)
            except:
                pass
        
        # Detection: [DETECT] Helmet:✓ Vest:✗ Glasses:✓ Confidence:92%
        elif '[DETECT]' in line:
            result['type'] = 'detection'
            result['data']['helmet'] = '✓' in line.split('Helmet:')[1].split()[0] if 'Helmet:' in line else False
            result['data']['vest'] = '✓' in line.split('Vest:')[1].split()[0] if 'Vest:' in line else False
            result['data']['glasses'] = '✓' in line.split('Glasses:')[1].split()[0] if 'Glasses:' in line else False
            try:
                conf_str = line.split('Confidence:')[1].split('%')[0].strip()
                result['data']['confidence'] = int(conf_str)
            except:
                pass
        
        # Command received: [CMD] Received compliance level: 85
        elif '[CMD]' in line:
            result['type'] = 'command'
            try:
                val = int(line.split(': ')[-1])
                result['data']['value'] = val
            except:
                pass
        
        return result
    
    @staticmethod
    def extract_metrics(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extraire les métriques clés pour l'UI"""
        metrics = {
            'motion_detected': False,
            'temperature': None,
            'humidity': None,
            'helmet': False,
            'vest': False,
            'glasses': False,
            'compliance': 0,
            'status': 'UNKNOWN'
        }
        
        data_type = parsed_data.get('type')
        data = parsed_data.get('data', {})
        
        if data_type == 'motion':
            metrics['motion_detected'] = data.get('detected', False)
        elif data_type == 'sensor':
            metrics['temperature'] = data.get('temperature')
            metrics['humidity'] = data.get('humidity')
        elif data_type == 'detection':
            metrics['helmet'] = data.get('helmet', False)
            metrics['vest'] = data.get('vest', False)
            metrics['glasses'] = data.get('glasses', False)
            metrics['compliance'] = data.get('confidence', 0)
        elif data_type == 'status':
            metrics['status'] = data.get('status', 'UNKNOWN')
            metrics['compliance'] = data.get('compliance', 0)
        
        return metrics


class ArduinoSessionManager:
    """Gestionnaire de session Arduino avec persistance d'état"""
    
    def __init__(self, port: str = 'COM3'):
        self.controller = ArduinoController(port=port)
        self.parser = ArduinoDataParser()
        self.current_metrics = {
            'motion_detected': False,
            'temperature': None,
            'humidity': None,
            'helmet': False,
            'vest': False,
            'glasses': False,
            'compliance': 0,
            'status': 'DISCONNECTED',
            'last_update': None
        }
        self.data_history = []
        self.max_history = 100
        
    def connect(self) -> bool:
        """Établir connexion et démarrer le monitoring"""
        if self.controller.connect():
            self.controller.register_callback(self._on_data_received)
            self.current_metrics['status'] = 'CONNECTED'
            return True
        return False
    
    def disconnect(self):
        """Fermer la connexion"""
        self.controller.disconnect()
        self.current_metrics['status'] = 'DISCONNECTED'
    
    def send_compliance(self, level: int):
        """Envoyer le niveau de conformité"""
        if self.controller.connected:
            self.controller.send_compliance_level(level)
    
    def send_detection(self, helmet: bool, vest: bool, glasses: bool, confidence: int):
        """Envoyer les données de détection"""
        if self.controller.connected:
            self.controller.send_detection_data(helmet, vest, glasses, confidence)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Obtenir les métriques actuelles"""
        return self.current_metrics.copy()
    
    def get_history(self, limit: int = 50) -> list:
        """Obtenir l'historique des données"""
        return self.data_history[-limit:]
    
    def _on_data_received(self, line: str):
        """Callback appelé quand Arduino envoie des données"""
        try:
            parsed = self.parser.parse_line(line)
            metrics = self.parser.extract_metrics(parsed)
            
            # Mettre à jour les métriques actuelles
            for key, value in metrics.items():
                if value is not None:
                    self.current_metrics[key] = value
            
            self.current_metrics['last_update'] = datetime.now().isoformat()
            
            # Ajouter à l'historique
            self.data_history.append({
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics.copy()
            })
            
            # Limiter l'historique
            if len(self.data_history) > self.max_history:
                self.data_history = self.data_history[-self.max_history:]
                
        except Exception as e:
            logger.error(f"Erreur processing Arduino data: {e}")

