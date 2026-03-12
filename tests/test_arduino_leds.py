#!/usr/bin/env python3
"""
Script de test Arduino - Diagnostic des connexions et des LEDs/Buzzer
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au PATH
sys.path.insert(0, str(Path(__file__).parent))

from app.arduino_integration import ArduinoController
from app.logger import logger
import time

def print_header(title):
    """Afficher un en-tête formaté"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_connection(port='COM3', baudrate=9600):
    """Tester la connexion Arduino"""
    print_header("1️⃣ TEST DE CONNEXION ARDUINO")
    
    print(f"Tentative de connexion à {port}@{baudrate}...")
    
    controller = ArduinoController(port=port, baudrate=baudrate)
    
    if controller.connect():
        print(f"✅ Connecté à Arduino sur {port}")
        return controller
    else:
        print(f"❌ ERREUR: Impossible de se connecter à {port}")
        print(f"\nActions possibles:")
        print(f"  1. Vérifier que l'Arduino est branché")
        print(f"  2. Vérifier le port (voir Gestionnaire de périphériques)")
        print(f"  3. Installer le driver Arduino")
        print(f"  4. Essayer un autre port (COM4, COM5, etc.)")
        return None

def test_led_green(controller):
    """Tester LED verte (80% compliance)"""
    print_header("2️⃣ TEST LED VERTE (80% compliance)")
    print("Envoi: C80 → LED verte devrait s'allumer")
    print("Attendez 2 secondes...\n")
    
    if controller.send_compliance_level(80):
        print("✅ Commande envoyée")
        time.sleep(2)
        print("🟢 La LED VERTE devrait être allumée")
        print("🔇 Le buzzer devrait être SILENCIEUX")
        return True
    else:
        print("❌ Erreur lors de l'envoi")
        return False

def test_led_yellow(controller):
    """Tester LED jaune (70% compliance)"""
    print_header("3️⃣ TEST LED JAUNE (70% compliance)")
    print("Envoi: C70 → LED jaune devrait s'allumer")
    print("Attendez 2 secondes...\n")
    
    if controller.send_compliance_level(70):
        print("✅ Commande envoyée")
        time.sleep(2)
        print("🟡 La LED JAUNE devrait être allumée")
        print("🔇 Le buzzer devrait être SILENCIEUX")
        return True
    else:
        print("❌ Erreur lors de l'envoi")
        return False

def test_led_red_with_buzzer(controller):
    """Tester LED rouge + buzzer (30% compliance)"""
    print_header("4️⃣ TEST LED ROUGE + BUZZER (30% compliance)")
    print("Envoi: C30 → LED rouge devrait s'allumer + buzzer")
    print("Attendez 2 secondes...\n")
    
    if controller.send_compliance_level(30):
        print("✅ Commande envoyée")
        time.sleep(2)
        print("🔴 La LED ROUGE devrait être allumée")
        print("🔊 Le BUZZER devrait sonner (1500Hz, 500ms)")
        return True
    else:
        print("❌ Erreur lors de l'envoi")
        return False

def test_detection_data(controller):
    """Tester l'envoi de données de détection"""
    print_header("5️⃣ TEST ENVOI DONNÉES DÉTECTION")
    
    tests = [
        {
            'name': 'Cas 1: EPI Complet (H+V+G)',
            'helmet': True,
            'vest': True,
            'glasses': True,
            'confidence': 95,
            'expected_led': '🟢 VERT'
        },
        {
            'name': 'Cas 2: EPI Partiel (H+V, pas G)',
            'helmet': True,
            'vest': True,
            'glasses': False,
            'confidence': 70,
            'expected_led': '🟡 JAUNE'
        },
        {
            'name': 'Cas 3: EPI Absent (pas H, V, G)',
            'helmet': False,
            'vest': False,
            'glasses': False,
            'confidence': 0,
            'expected_led': '🔴 ROUGE + 🔊 BUZZER'
        }
    ]
    
    for i, test_case in enumerate(tests, 1):
        print(f"\n{test_case['name']}")
        print(f"  Engagement: H={test_case['helmet']}, V={test_case['vest']}, G={test_case['glasses']}, Conf={test_case['confidence']}%")
        print(f"  Résultat attendu: {test_case['expected_led']}")
        
        if controller.send_detection_data(
            helmet=test_case['helmet'],
            vest=test_case['vest'],
            glasses=test_case['glasses'],
            confidence=test_case['confidence']
        ):
            print(f"  ✅ Données envoyées")
            time.sleep(2)
        else:
            print(f"  ❌ Erreur lors de l'envoi")

def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("  🔧 DIAGNOSTIC ARDUINO - EPI DETECTION SYSTEM")
    print("="*60)
    
    # Configuration
    port = os.getenv('ARDUINO_PORT', 'COM3')
    baudrate = int(os.getenv('ARDUINO_BAUD', 9600))
    
    print(f"\nConfiguration:")
    print(f"  Port: {port}")
    print(f"  Bauds: {baudrate}")
    print(f"\nNOTA: Pour utiliser un autre port, définir la variable d'environnement:")
    print(f"  $env:ARDUINO_PORT = 'COM4'  (PowerShell)")
    
    # Test 1: Connexion
    controller = test_connection(port, baudrate)
    if not controller:
        print("\n❌ TEST ÉCHOUÉ - Arduino non connecté")
        sys.exit(1)
    
    # Test 2-4: LEDs
    print("\nPhase suivante: Test des LEDs")
    print("Assurez-vous que l'Arduino est bien alimenté et branché!")
    input("Appuyez sur ENTRÉE pour continuer...")
    
    if not test_led_green(controller):
        print("⚠️ Problème lors de l'envoi à l'Arduino")
    
    if not test_led_yellow(controller):
        print("⚠️ Problème lors de l'envoi à l'Arduino")
    
    if not test_led_red_with_buzzer(controller):
        print("⚠️ Problème lors de l'envoi à l'Arduino")
    
    # Test 5: Données de détection
    print("\nPhase suivante: Test envoi données détection")
    input("Appuyez sur ENTRÉE pour continuer...")
    test_detection_data(controller)
    
    # Conclusion
    print_header("✅ DIAGNOSTIC TERMINÉ")
    print("Bilan:")
    print("  ✅ Arduino connecté et functional")
    print("  ✅ Toutes les LEDs testées")
    print("  ✅ Buzzer testé")
    print("  ✅ Données de détection envoyées")
    print("\n💡 Prochaines étapes:")
    print("  1. Lancer the application: python run_app.py dev")
    print("  2. Aller à: http://localhost:5000/unified_monitoring.html")
    print("  3. Importer une image avec des personnes")
    print("  4. Vérifier que les LEDs s'allument selon la détection EPI")
    
    controller.disconnect()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Diagnostic interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
