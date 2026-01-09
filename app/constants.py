# app/constants.py
from enum import Enum

# Dictionnaire mappant les indices de classe aux noms de classe
CLASS_MAP = {
    0: 'helmet',
    1: 'vest',
    2: 'glasses',
    3: 'person'
}

# Couleurs pour la visualisation (par défaut)
CLASS_COLORS = {
    'helmet': (0, 255, 0),    # Vert
    'vest': (255, 0, 0),      # Rouge
    'glasses': (0, 0, 255),   # Bleu
    'person': (255, 255, 0)   # Jaune
}

# --- Niveaux de conformité et alertes ---

class ComplianceLevel(Enum):
    """Niveaux de conformité EPI."""
    EXCELLENT = "Excellent"  # 100%
    BON = "Bon"              # >= 80%
    MOYEN = "Moyen"          # >= 50%
    FAIBLE = "Faible"        # < 50%
    INCONNU = "Inconnu"

class AlertType(Enum):
    """Types d'alerte déclenchées."""
    AUCUNE = "Aucune"        # Conformité élevée
    AVERTISSEMENT = "Avertissement" # Conformité moyenne
    CRITIQUE = "Critique"    # Conformité faible

# --- TinkerCad Simulator Constants ---

# Durée de la pause entre chaque itération de la simulation (en secondes)
SIMULATION_SLEEP_TIME = 2

# Intervalle (en nombre d'itérations) pour vérifier l'entrée/sortie d'un travailleur
WORKER_PRESENCE_CHECK_INTERVAL = 10

# Probabilité (0.0 à 1.0) qu'un travailleur entre dans la zone à chaque vérification
WORKER_ENTRY_PROBABILITY = 0.33  # 33% de chance

# Plage de conformité initiale lors de l'entrée d'un travailleur
INITIAL_COMPLIANCE_MIN = 30
INITIAL_COMPLIANCE_MAX = 100

# Seuils de conformité pour les alertes
HIGH_COMPLIANCE_THRESHOLD = 80  # En dessous, la LED verte s'éteint
MEDIUM_COMPLIANCE_THRESHOLD = 50 # En dessous, le buzzer s'active (déjà en alerte rouge)

# Fluctuation aléatoire du niveau de conformité à chaque itération
COMPLIANCE_FLUCTUATION_MIN = -10
COMPLIANCE_FLUCTUATION_MAX = 10

# Délai d'attente pour les requêtes API (en secondes)
API_TIMEOUT = 3

# ID du capteur simulé
SIMULATOR_SENSOR_ID = "tinkercad_sim_01"

def get_compliance_level(compliance_rate: float) -> ComplianceLevel:
    """Retourne le niveau de conformité basé sur le taux."""
    if compliance_rate is None:
        return ComplianceLevel.INCONNU
    if compliance_rate >= HIGH_COMPLIANCE_THRESHOLD:
        return ComplianceLevel.BON
    if compliance_rate >= MEDIUM_COMPLIANCE_THRESHOLD:
        return ComplianceLevel.MOYEN
    return ComplianceLevel.FAIBLE

def get_alert_type(compliance_rate: float) -> AlertType:
    """Retourne le type d'alerte basé sur le taux de conformité."""
    if compliance_rate is None or compliance_rate >= HIGH_COMPLIANCE_THRESHOLD:
        return AlertType.AUCUNE
    if compliance_rate >= MEDIUM_COMPLIANCE_THRESHOLD:
        return AlertType.AVERTISSEMENT
    return AlertType.CRITIQUE