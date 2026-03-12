#!/usr/bin/env python3
"""
Test détections avec les nouveaux seuils (0.1 conf, 0.45 IOU)
Pour vérifier que helmet et glasses sont maintenant détectés
"""
import sys
from pathlib import Path
import logging

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from app.logger import logger, setup_logging
from app.detection import EPIDetector
import cv2
import numpy as np

setup_logging()

logger.info(f"CONFIDENCE_THRESHOLD: {config.CONFIDENCE_THRESHOLD}")
logger.info(f"IOU_THRESHOLD: {config.IOU_THRESHOLD}")

# Initialiser le détecteur
logger.info("Initialisation du modèle...")
detector = EPIDetector()

# Créer une image de test simple (à adapter selon vos besoins)
# Pour un test rapide, utilisons une image de test existante
test_image_path = Path(__file__).parent / 'test_image.jpg'

if not test_image_path.exists():
    logger.warning("test_image.jpg non trouvé dans le répertoire racine")
    logger.info("Créons une image de test vide pour tester le pipeline...")
    
    # Créer une image blanche de test
    img = np.ones((640, 640, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(test_image_path), img)

# Charger l'image
logger.info(f"Chargement de l'image: {test_image_path}")
image = cv2.imread(str(test_image_path))

if image is None:
    logger.error(f"Impossible de charger l'image: {test_image_path}")
    sys.exit(1)

logger.info(f"Image shape: {image.shape}")

# Lancer la détection
logger.info("\n🔍 Lancement de la détection...")
results = detector.detect(image)

if results:
    logger.info(f"\n✅ Détection complète!")
    
    stats = results.get('stats', {})
    logger.info(f"\nStatistiques:")
    logger.info(f"  - Total persons detected: {stats.get('total_persons', 0)}")
    logger.info(f"  - With helmet: {stats.get('with_helmet', 0)}")
    logger.info(f"  - With glasses: {stats.get('with_glasses', 0)}")
    logger.info(f"  - With vest: {stats.get('with_vest', 0)}")
    logger.info(f"  - With boots: {stats.get('with_boots', 0)}")
    logger.info(f"  - Compliance rate: {stats.get('compliance_rate', 0)}%")
    logger.info(f"  - Compliance level: {stats.get('compliance_level', 'N/A')}")
    
    # Afficher les détections brutes
    detections = results.get('detections', [])
    if detections:
        logger.info(f"\nDétections brutes ({len(detections)} objets):")
        for i, det in enumerate(detections):
            logger.info(f"  [{i}] {det.get('class_name', 'Unknown')} - conf: {det.get('confidence', 0):.2f}")
    else:
        logger.warning("Aucune détection brute trouvée")
else:
    logger.warning("Aucun résultat de détection")

logger.info("\n✅ Test terminé!")
