#!/usr/bin/env python3
"""
🤖 Script de Test et Control Arduino MEGA
Pour alertes en temps réel - LEDs (Rouge/Jaune/Vert) + Buzzer

Configuration:
- Buzzer: Port 9
- LED Rouge: Port 30
- LED Jaune: Port 26
- LED Vert: Port 36
"""

import time
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le projet au path
sys.path.insert(0, str(Path.cwd()))

try:
    from app.arduino_integration import ArduinoController, ArduinoDataParser
    from app.logger import logger
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("   Assurez-vous d'être dans le répertoire du projet")
    sys.exit(1)


class ArduinoMegaController:
    """Contrôleur dédié pour Arduino MEGA avec LEDs et Buzzer"""
    
    def __init__(self, port='COM3', baudrate=9600):
        self.arduino = ArduinoController(port=port, baudrate=baudrate)
        self.parser = ArduinoDataParser()
        self.arduino.register_callback(self._on_data_received)
        
    def _on_data_received(self, line: str):
        """Callback quand données reçues"""
        parsed = self.parser.parse_line(line)
        print(f"   📥 {line}")
        
    def connect(self):
        """Établir la connexion"""
        print(f"🔌 Connexion à Arduino sur {self.arduino.port}...")
        if self.arduino.connect():
            print("✅ Arduino connecté avec succès!")
            time.sleep(1)  # Attendre le startup
            return True
        else:
            print("❌ Erreur de connexion")
            return False
    
    def disconnect(self):
        """Fermer la connexion"""
        print("🔌 Fermeture de la connexion...")
        self.arduino.disconnect()
    
    def test_startup_sequence(self):
        """Tester la séquence de démarrage"""
        print("\n" + "="*60)
        print("🧪 TEST 1: Séquence de Démarrage")
        print("="*60)
        print("Vérifiez la séquence LED: Vert → Jaune → Rouge\n")
        
        # La séquence de startup est envoyée automatiquement
        # Attendre un peu pour la voir
        time.sleep(2)
        print("✅ Séquence de démarrage envoyée (attendez 1-2 secondes)")
    
    def test_compliance_levels(self):
        """Tester différents niveaux de conformité"""
        print("\n" + "="*60)
        print("🧪 TEST 2: Niveaux de Conformité")
        print("="*60)
        
        test_levels = [
            (85, "✅ SAFE (LED Vert)"),
            (70, "⚠️ WARNING (LED Jaune)"),
            (45, "🚨 DANGER (LED Rouge + Buzzer)"),
        ]
        
        for level, description in test_levels:
            print(f"\n📤 Envoi: Compliance Level = {level}%")
            print(f"   {description}")
            self.arduino.send_compliance_level(level)
            time.sleep(2)  # Attendre 2 secondes
    
    def test_epi_detection(self):
        """Tester les données de détection EPI"""
        print("\n" + "="*60)
        print("🧪 TEST 3: Détection EPI")
        print("="*60)
        
        test_scenarios = [
            {
                'name': 'Tous EPI détectés',
                'helmet': True,
                'vest': True,
                'glasses': True,
                'confidence': 95,
                'expected': '✅ SAFE (LED Vert)'
            },
            {
                'name': 'EPI partiels (Casque + Lunettes)',
                'helmet': True,
                'vest': False,
                'glasses': True,
                'confidence': 85,
                'expected': '⚠️ WARNING (LED Jaune)'
            },
            {
                'name': 'Pas d\'EPI',
                'helmet': False,
                'vest': False,
                'glasses': False,
                'confidence': 0,
                'expected': '🚨 DANGER (LED Rouge + Buzzer)'
            },
        ]
        
        for scenario in test_scenarios:
            print(f"\n📦 Scénario: {scenario['name']}")
            print(f"   Helmet: {'✓' if scenario['helmet'] else '✗'}")
            print(f"   Vest: {'✓' if scenario['vest'] else '✗'}")
            print(f"   Glasses: {'✓' if scenario['glasses'] else '✗'}")
            print(f"   Confidence: {scenario['confidence']}%")
            print(f"   Résultat attendu: {scenario['expected']}")
            
            self.arduino.send_detection_data(
                helmet=scenario['helmet'],
                vest=scenario['vest'],
                glasses=scenario['glasses'],
                confidence=scenario['confidence']
            )
            time.sleep(2)
    
    def interactive_control(self):
        """Mode contrôle interactif"""
        print("\n" + "="*60)
        print("🎮 MODE CONTRÔLE INTERACTIF")
        print("="*60)
        print("\nCommandes disponibles:")
        print("  1. Envoyer niveau de conformité (0-100)")
        print("  2. Tester détection EPI")
        print("  3. Sequence startup")
        print("  4. Quitter\n")
        
        while True:
            try:
                choice = input("Choisissez une option (1-4): ").strip()
                
                if choice == '1':
                    level = int(input("Niveau de conformité (0-100): "))
                    level = max(0, min(100, level))
                    print(f"📤 Envoi: C{level}")
                    self.arduino.send_compliance_level(level)
                    time.sleep(1)
                
                elif choice == '2':
                    helmet = input("Casque détecté? (y/n): ").lower() == 'y'
                    vest = input("Gilet détecté? (y/n): ").lower() == 'y'
                    glasses = input("Lunettes détectées? (y/n): ").lower() == 'y'
                    confidence = int(input("Confiance (0-100): "))
                    
                    cmd = f"DETECT:helmet={int(helmet)},vest={int(vest)},glasses={int(glasses)},confidence={confidence}"
                    print(f"📤 Envoi: {cmd}")
                    self.arduino.send_detection_data(helmet, vest, glasses, confidence)
                    time.sleep(1)
                
                elif choice == '3':
                    print("Envoi de la séquence startup...")
                    time.sleep(2)
                
                elif choice == '4':
                    print("Au revoir!")
                    break
                
                else:
                    print("❌ Option invalide")
                    
            except ValueError:
                print("❌ Entrée invalide")
            except KeyboardInterrupt:
                print("\n⏹️ Interruption utilisateur")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")


def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print("🤖 Arduino MEGA - Contrôle Alertes Temps Réel")
    print("="*70)
    print("\nConfiguration:")
    print("  • Buzzer: Port 9")
    print("  • LED Rouge (Danger): Port 30")
    print("  • LED Jaune (Warning): Port 26")
    print("  • LED Vert (Safe): Port 36")
    print("="*70)
    
    # Demander le port COM
    port = input("\nPort COM par défaut? (appuyez sur Entrée pour COM3): ").strip() or 'COM3'
    
    try:
        controller = ArduinoMegaController(port=port)
        
        # Connecter
        if not controller.connect():
            sys.exit(1)
        
        # Menu
        print("\n" + "="*60)
        print("📋 TESTS DISPONIBLES")
        print("="*60)
        print("\n1. Séquence de démarrage")
        print("2. Niveaux de conformité")
        print("3. Détection EPI")
        print("4. Tous les tests")
        print("5. Contrôle interactif")
        print("6. Quitter\n")
        
        choice = input("Choisissez une option (1-6): ").strip()
        
        if choice == '1':
            controller.test_startup_sequence()
        elif choice == '2':
            controller.test_compliance_levels()
        elif choice == '3':
            controller.test_epi_detection()
        elif choice == '4':
            controller.test_startup_sequence()
            time.sleep(1)
            controller.test_compliance_levels()
            time.sleep(1)
            controller.test_epi_detection()
        elif choice == '5':
            controller.interactive_control()
        elif choice == '6':
            print("Au revoir!")
            return
        else:
            print("❌ Option invalide")
        
        controller.disconnect()
        print("\n✅ Tests terminés avec succès!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Interruption utilisateur")
        if 'controller' in locals():
            controller.disconnect()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
