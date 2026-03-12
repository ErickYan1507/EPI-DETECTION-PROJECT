#!/usr/bin/env python3
"""
🔧 DIAGNOSTIC ARDUINO - Guide de résolution

Ce script aide à diagnostiquer les problèmes de connexion Arduino
"""

import sys
import os
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))

from app.logger import logger, setup_logging
from config import config

setup_logging()

def check_serial_availability():
    """Vérifier si PySerial est installé"""
    logger.info("\n📦 Vérification des dépendances...")
    try:
        import serial
        from serial.tools import list_ports
        logger.info("✅ PySerial disponible")
        return True
    except ImportError as e:
        logger.error(f"❌ PySerial non installé: {e}")
        logger.info("   Solution: pip install pyserial")
        return False

def list_available_ports():
    """Lister les ports série disponibles"""
    logger.info("\n🔌 Ports série disponibles:")
    try:
        from serial.tools import list_ports
        ports = list(list_ports.comports())
        
        if not ports:
            logger.warning("❌ Aucun port série détecté!")
            logger.info("   - Vérifier que Arduino est branché")
            logger.info("   - Vérifier les drivers USB")
            return []
        
        for i, port in enumerate(ports, 1):
            logger.info(f"  [{i}] {port.device}: {port.description}")
            if port.hwid:
                logger.info(f"      Hardware: {port.hwid}")
        
        return ports
    except Exception as e:
        logger.error(f"❌ Erreur énumération ports: {e}")
        return []

def test_port_connection(port_name):
    """Tester la connexion sur un port spécifique"""
    logger.info(f"\n🧪 Test connexion sur {port_name}...")
    try:
        import serial
        import time
        
        logger.info(f"  Ouverture du port avec baudrate=9600...")
        ser = serial.Serial(port=port_name, baudrate=9600, timeout=1)
        
        logger.info(f"  ✅ Port ouvert avec succès")
        logger.info(f"  Variables: is_open={ser.is_open}, timeout={ser.timeout}")
        
        # Tenter d'envoyer une commande simple
        test_cmd = "C100\n"  # Commande compliance niveau 100
        logger.info(f"  📤 Envoi test: {repr(test_cmd)}")
        ser.write(test_cmd.encode())
        
        # Essayer de lire la réponse
        logger.info(f"  📥 Attente réponse (1 sec)...")
        response = ser.readline()
        
        if response:
            logger.info(f"  ✅ Réponse reçue: {repr(response)}")
        else:
            logger.warning(f"  ⚠️ Pas de réponse (normal si Arduino n'attend pas)")
        
        ser.close()
        logger.info(f"  ✅ Port fermé")
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Erreur connexion: {type(e).__name__}: {e}")
        return False

def test_arduino_manager():
    """Tester l'ArduinoSessionManager"""
    logger.info(f"\n🚀 Test ArduinoSessionManager...")
    try:
        from app.arduino_integration import ArduinoSessionManager
        
        logger.info(f"  Création session sur port 'COM3'...")
        session = ArduinoSessionManager(port='COM3')
        
        logger.info(f"  Port configuré: {session.controller.port}")
        logger.info(f"  Baudrate: {session.controller.baudrate}")
        logger.info(f"  État initial: connected={session.connected}")
        
        logger.info(f"  Tentative de connexion...")
        ok = session.connect()
        
        if ok:
            logger.info(f"  ✅ Connecté avec succès!")
            logger.info(f"  État actuel: connected={session.connected}")
            
            # Tester send_command
            logger.info(f"  📤 Test send_command...")
            success = session.send_command("C99")
            logger.info(f"  Résultat: {success}")
            
            session.disconnect()
        else:
            logger.warning(f"  ⚠️ Connexion échouée (normal si Arduino pas connecté)")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Erreur: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Diagnostic principal"""
    logger.info("=" * 60)
    logger.info("🔧 DIAGNOSTIC ARDUINO")
    logger.info("=" * 60)
    
    logger.info(f"\nConfiguration:")
    logger.info(f"  ARDUINO_PORT env var: {os.getenv('ARDUINO_PORT', 'Non défini')}")
    logger.info(f"  ARDUINO_BAUD env var: {os.getenv('ARDUINO_BAUD', '9600')}")
    
    # Étapes de diagnostic
    if not check_serial_availability():
        return 1
    
    ports = list_available_ports()
    
    if ports:
        # Tester le premier port disponible
        logger.info(f"\n🧪 Essai du port: {ports[0].device}")
        test_port_connection(ports[0].device)
    
    # Tester l'intégration
    test_arduino_manager()
    
    logger.info("\n" + "=" * 60)
    logger.info("📋 RÉSUMÉ DIAGNOSTIC:")
    logger.info("=" * 60)
    logger.info("""
Si la connexion échoue :

1. ❌ "Aucun port série détecté"
   → Arduino débranché ou mauvais driver USB
   → Installer les drivers CH340/FTDI
   → Vérifier le câble USB

2. ❌ "Erreur connexion: [Errno XX]"
   → Port série en utilisation par autre app
   → Arduino occupé par l'IDE
   → Fermer tous les autres programmes

3. ⚠️ "Pas de réponse" lors du test
   → Normal, l'Arduino MCP envoie pas de réponse
   → La connexion fonctionne
   
4. Si application Flask ne voit pas Arduino:
   → Vérifier que app.arduino est assigné (logs "✅ ArduinoSession")
   → Si "Arduino non connecté immédiatement", l'auto-reconnect tente
   → Voir les logs "Arduino non initialisé" ou "Arduino déconnecté"

🔗 Pour configurer le port manuellement:
   SET ARDUINO_PORT=COM3 (Windows)
   export ARDUINO_PORT=COM3 (Linux/Mac)

📊 Logs à vérifier:
   - Startup: "🔌 Initialisation Arduino"
   - Connexion: "🔄 Tentative Arduino X/5"
   - Envoi: "📤 Commande envoyée: DETECT:..."
""")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
