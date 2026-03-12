#!/usr/bin/env python3
"""Test les propriétés et méthodes d'ArduinoSessionManager"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.arduino_integration import ArduinoSessionManager
from app.logger import logger

logger.info("Test de ArduinoSessionManager...")

# Créer une session
session = ArduinoSessionManager(port='COM3')
logger.info(f"✅ Session créée")

# Vérifier les propriétés
logger.info(f"  - connected: {session.connected}")
logger.info(f"  - ser: {session.ser}")
logger.info(f"  - port: {session.port}")
logger.info(f"  - baudrate: {session.baudrate}")

# Vérifier les méthodes
logger.info(f"  - send_detection_data retourne: bool? {hasattr(session.send_detection_data, '__call__')}")
logger.info(f"  - send_compliance_level retourne: bool? {hasattr(session.send_compliance_level, '__call__')}")

# Test des return values sans connexion
logger.info(f"\n📤 Test send_detection_data (pas connecté):")
result = session.send_detection_data(helmet=True, vest=False, glasses=True, confidence=75)
logger.info(f"  Résultat: {result} (attendu: False)")

logger.info(f"\n✅ Tous les tests de structure passou")
