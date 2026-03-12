#!/usr/bin/env python3
"""
Test Arduino simulation - Tester sans hardware Arduino physique
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.arduino_integration import ArduinoController

def test_simulation():
    """Tester avec le port spécial 'SIMULATION'"""
    print("\n" + "="*60)
    print("  🧪 TEST SIMULATION ARDUINO (Sans Hardware)")
    print("="*60 + "\n")
    
    # Mode simulation - pas besoin de hardware
    controller = ArduinoController(port='SIMULATION', baudrate=9600)
    
    # Force connected pour simulation
    controller.connected = True
    controller.ser = None  # Pas de port série réel
    
    print("✅ MODE SIMULATION ACTIVÉ (Arduino simulé)")
    
    # Test 1: Envoyer une conformité
    print("\n📝 Test 1: Envoi compliance 85% (LED Verte attendue)")
    msg1 = controller.send_compliance_level(85)
    print(f"  Résultat: {msg1}")
    
    print("\n📝 Test 2: Envoi compliance 70% (LED Jaune attendue)")
    msg2 = controller.send_compliance_level(70)
    print(f"  Résultat: {msg2}")
    
    print("\n📝 Test 3: Envoi compliance 30% (LED Rouge + Buzzer attendue)")
    msg3 = controller.send_compliance_level(30)
    print(f"  Résultat: {msg3}")
    
    # Test 2: Envoyer des données de détection
    print("\n📝 Test 4: Envoi données détection (EPI Complet)")
    msg4 = controller.send_detection_data(helmet=True, vest=True, glasses=True, confidence=95)
    print(f"  Résultat: {msg4}")
    
    print("\n📝 Test 5: Envoi données détection (EPI Partiel)")
    msg5 = controller.send_detection_data(helmet=True, vest=False, glasses=True, confidence=60)
    print(f"  Résultat: {msg5}")
    
    print("\n📝 Test 6: Envoi données détection (Pas d'EPI)")
    msg6 = controller.send_detection_data(helmet=False, vest=False, glasses=False, confidence=0)
    print(f"  Résultat: {msg6}")
    
    print("\n✅ SIMULATION TERMINÉE")
    print("\n💡 Pour utiliser avec Arduino réel:")
    print("  1. Brancher l'Arduino au port USB")
    print("  2. Définir la variable d'environnement:")
    print("     $env:ARDUINO_PORT = 'COM3'  (ou le port réel)")
    print("  3. Redémarrer l'application")
    
if __name__ == '__main__':
    test_simulation()
