# app/constants.py
from enum import Enum

# Dictionnaire mappant les indices de classe aux noms de classe
# IMPORTANT: L'ordre DOIT correspondre à data.yaml (0-4)
CLASS_MAP = {
    0: 'helmet',
    1: 'glasses',
    2: 'person',
    3: 'vest',
    4: 'boots'
}

# Couleurs pour la visualisation (par défaut)
CLASS_COLORS = {
    'helmet': (0, 255, 0),     # Vert
    'glasses': (0, 0, 255),    # Bleu
    'person': (255, 255, 0),   # Jaune
    'vest': (255, 0, 0),       # Rouge
    'boots': (255, 165, 0)     # Orange
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


def calculate_compliance_score(
    total_persons: int,
    with_helmet: int,
    with_vest: int,
    with_glasses: int,
    with_boots: int
) -> float:
    """
    Calcule le score de conformité selon l'algorithme personnalisé:
    - 100% si TOUS les EPI sont détectés (pour au moins 1 personne)
    - 90% si 1 ou 2 classes manquent
    - 60% si 3 classes manquent
    - 10% si 4 classes manquent
    - 0% si aucun EPI ou pas de personne détectée
    
    RÈGLE CRITIQUE: La classe 'personne' doit être obligatoirement détectée.
    Si 'personne' n'est pas détectée, le score est 0%.
    
    Les autres classes (EPI) détectées seules ne comptent PAS comme une personne présente.
    """
    # RÈGLE: Si aucune personne n'est détectée, retourner 0%
    if total_persons == 0:
        return 0.0
    
    # Classes requises pour la conformité
    required_classes = ['helmet', 'vest', 'glasses', 'boots']
    required_epi_counts = [with_helmet, with_vest, with_glasses, with_boots]
    
    # Compter combien de classes EPI ont au moins une détection
    # (Pour chaque personne, on doit avoir tous les EPI)
    detected_epi = sum(1 for count in required_epi_counts if count > 0)
    missing_epi = 4 - detected_epi  # Nombre de classes EPI manquantes
    
    # Appliquer la règle de score selon le nombre de classes manquantes
    if missing_epi == 0:
        # Tous les EPI sont détectés
        return 100.0
    elif missing_epi <= 2:
        # 1 ou 2 classes manquent
        return 90.0
    elif missing_epi == 3:
        # 3 classes manquent
        return 60.0
    else:  # missing_epi == 4
        # 4 classes manquent (aucun EPI)
        return 10.0