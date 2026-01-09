import random
import time
import threading
import logging
from datetime import datetime
import requests
import json

# Importer la configuration globale et les constantes
from config import config
from app import constants as const

class TinkerCadSimulator:
    def __init__(self, db_session=None):
        self.api_url = config.TINKERCAD_API_URL
        self.db_session = db_session
        self.is_running = False
        self.simulation_thread = None
        self.sensor_id = None
        self.sensor_db_id = None
        self.current_state = {
            'motion_detected': False,
            'compliance_level': 100,
            'led_green': True,
            'led_red': False,
            'buzzer_active': False,
            'worker_present': False
        }
        self.logger = logging.getLogger(__name__)
    
    def set_db_session(self, db_session):
        """Définir la session de base de données"""
        self.db_session = db_session
    
    def register_sensor(self, sensor_name="TinkerCad Simulation", location="Lab"):
        """Enregistrer le capteur de simulation dans la base de données"""
        if not self.db_session:
            self.logger.warning("DB session non définie")
            return False
        
        try:
            from app.database_new import IoTSensor
            
            self.sensor_id = const.SIMULATOR_SENSOR_ID
            
            # Vérifier si le capteur existe déjà
            existing_sensor = self.db_session.query(IoTSensor).filter_by(
                sensor_id=self.sensor_id
            ).first()
            
            if existing_sensor:
                self.sensor_db_id = existing_sensor.id
                self.logger.info(f"Capteur existant trouvé: {existing_sensor.sensor_name}")
                return True
            
            # Créer un nouveau capteur
            sensor = IoTSensor(
                sensor_id=self.sensor_id,
                sensor_name=sensor_name,
                sensor_type='tinkercad_sim',
                location=location,
                status='active',
                last_data=json.dumps(self.current_state)
            )
            
            self.db_session.add(sensor)
            self.db_session.commit()
            
            self.sensor_db_id = sensor.id
            self.logger.info(f"Capteur enregistré avec succès: {sensor_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement du capteur: {e}")
            return False
    
    def start_simulation(self):
        """Démarrer la simulation TinkerCad"""
        if self.is_running:
            self.logger.warning("Simulation déjà en cours")
            return
        
        self.is_running = True
        self.simulation_thread = threading.Thread(target=self._simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        self.logger.info("Simulation TinkerCad démarrée")
    
    def stop_simulation(self):
        """Arrêter la simulation"""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=2)
        self.logger.info("Simulation TinkerCad arrêtée")
    
    def _simulation_loop(self):
        """Boucle principale de simulation"""
        simulation_count = 0
        
        while self.is_running:
            try:
                # Simuler l'entrée/sortie d'un travailleur
                if simulation_count % const.WORKER_PRESENCE_CHECK_INTERVAL == 0:
                    self._simulate_worker_presence()
                
                # Simuler la détection EPI si un travailleur est présent
                if self.current_state['worker_present']:
                    self._simulate_epi_detection()
                
                # Envoyer les données à l'API
                self._send_to_api()
                
                # Attendre avant la prochaine itération
                time.sleep(const.SIMULATION_SLEEP_TIME)
                simulation_count += 1
                
            except Exception as e:
                self.logger.error(f"Erreur dans la simulation: {e}")
                time.sleep(5) # Garder une pause de sécurité en cas d'erreur répétée
    
    def _simulate_worker_presence(self):
        """Simuler l'entrée et la sortie d'un travailleur."""
        # Utilise la probabilité définie dans les constantes
        worker_enters = random.random() < const.WORKER_ENTRY_PROBABILITY
        
        if worker_enters and not self.current_state['worker_present']:
            self.current_state.update({
                'worker_present': True,
                'motion_detected': True,
                'compliance_level': random.randint(
                    const.INITIAL_COMPLIANCE_MIN, 
                    const.INITIAL_COMPLIANCE_MAX
                )
            })
            self.logger.info("Travailleur détecté - Début vérification EPI")
        
        elif not worker_enters and self.current_state['worker_present']:
            self.current_state.update({
                'worker_present': False,
                'motion_detected': False,
                'led_green': True,
                'led_red': False,
                'buzzer_active': False
            })
            self.logger.info("Zone vide - Travailleur sorti")
    
    def _simulate_epi_detection(self):
        """Simuler la détection des EPI et mettre à jour l'état."""
        compliance = self.current_state['compliance_level']
        
        # Mettre à jour les LEDs et buzzer selon les seuils de conformité
        if compliance >= const.HIGH_COMPLIANCE_THRESHOLD:
            self.current_state.update({
                'led_green': True, 'led_red': False, 'buzzer_active': False
            })
        elif compliance >= const.MEDIUM_COMPLIANCE_THRESHOLD:
            self.current_state.update({
                'led_green': False, 'led_red': True, 'buzzer_active': False # Alerte visuelle seule
            })
        else:
            self.current_state.update({
                'led_green': False, 'led_red': True, 'buzzer_active': True # Alerte visuelle et sonore
            })
        
        # Simuler une variation du niveau de conformité pour le prochain cycle
        change = random.randint(const.COMPLIANCE_FLUCTUATION_MIN, const.COMPLIANCE_FLUCTUATION_MAX)
        new_compliance = max(0, min(100, compliance + change))
        self.current_state['compliance_level'] = new_compliance
    
    def _save_to_db(self):
        """Sauvegarder l'état actuel dans la base de données"""
        if not self.db_session or not self.sensor_db_id:
            return
        
        try:
            from app.database_new import IoTDataLog, IoTSensor
            
            # Créer un log
            log_entry = IoTDataLog(
                sensor_id=self.sensor_db_id,
                timestamp=datetime.utcnow(),
                motion_detected=self.current_state.get('motion_detected', False),
                compliance_level=self.current_state.get('compliance_level', 0),
                led_green=self.current_state.get('led_green', False),
                led_red=self.current_state.get('led_red', False),
                buzzer_active=self.current_state.get('buzzer_active', False),
                worker_present=self.current_state.get('worker_present', False),
                raw_data=json.dumps(self.current_state)
            )
            
            self.db_session.add(log_entry)
            
            # Mettre à jour le capteur
            sensor = self.db_session.query(IoTSensor).get(self.sensor_db_id)
            if sensor:
                sensor.last_data = json.dumps(self.current_state)
                sensor.last_update = datetime.utcnow()
            
            self.db_session.commit()
            self.logger.debug("Données sauvegardées en base de données")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde en BD: {e}")
            self.db_session.rollback()
    
    def _send_to_api(self):
        """Envoyer l'état actuel à l'API Flask et sauvegarder en BD."""
        # Sauvegarder en base de données
        self._save_to_db()
        
        try:
            payload = {
                'sensor_id': const.SIMULATOR_SENSOR_ID,
                'timestamp': datetime.now().isoformat(),
                'data': self.current_state.copy()
            }
            
            # Envoyer la requête POST
            response = requests.post(
                f"{self.api_url}/update",
                json=payload,
                timeout=const.API_TIMEOUT
            )
            
            if response.status_code == 200:
                self.logger.debug("Données de simulation envoyées avec succès à l'API.")
            else:
                self.logger.warning(
                    f"Échec de l'envoi à l'API. Statut: {response.status_code}, Réponse: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur de connexion à l'API: {e}")
    
    def get_state(self):
        """Obtenir l'état actuel de la simulation."""
        return self.current_state.copy()
    
    def force_compliance_level(self, level):
        """Forcer un niveau de conformité pour les tests."""
        level = max(0, min(100, int(level)))
        self.current_state['compliance_level'] = level
        self._simulate_epi_detection() # Mettre à jour l'état immédiatement
        self.logger.info(f"Niveau de conformité forcé à {level}%")
        return self.get_state()