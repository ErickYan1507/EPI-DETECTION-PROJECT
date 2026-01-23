#!/usr/bin/env python3
"""
Installation des dépendances optionnelles pour les périphériques physiques
Permet l'intégration optionnelle d'Arduino, MQTT, Bluetooth, etc.
"""

import subprocess
import sys
import os

# Couleurs pour le terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def install_package(package_name, import_name=None):
    """Installer un package pip"""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        __import__(import_name)
        print_success(f"{package_name} est déjà installé")
        return True
    except ImportError:
        print_info(f"Installation de {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print_success(f"{package_name} a été installé avec succès")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Erreur lors de l'installation de {package_name}: {e}")
            return False

def main():
    print_header("🔌 Installation des Dépendances Périphériques Physiques")
    
    print("""
Choisissez les dépendances à installer:

1. ✅ TOUS les périphériques (Arduino + MQTT + USB + Cloud)
2. 🔌 Arduino / TinkerCAD (pyserial)
3. 🌐 MQTT (paho-mqtt)
4. 📡 Réseau (requests - probablement déjà installé)
5. ☁️  Cloud (azure-iot-device, boto3, google-cloud-iot)
6. 🧬 Utilitaires (pyusb, bleak pour Bluetooth)
7. ❌ Quitter

Votre choix: """)
    
    choice = input().strip()
    
    success_count = 0
    failed_count = 0
    
    if choice == '1':
        print_header("Installation de TOUTES les dépendances")
        
        packages = [
            ('pyserial', 'serial'),           # Arduino
            ('paho-mqtt', 'paho'),            # MQTT
            ('requests', 'requests'),         # HTTP
            ('azure-iot-device', 'azure'),    # Azure IoT
            ('boto3', 'boto3'),               # AWS IoT
            ('google-cloud-iot', 'google'),   # Google Cloud IoT
            ('pyusb', 'usb'),                 # USB
            ('bleak', 'bleak'),               # Bluetooth
        ]
        
        for package, import_name in packages:
            if install_package(package, import_name):
                success_count += 1
            else:
                failed_count += 1
    
    elif choice == '2':
        print_header("Installation d'Arduino / TinkerCAD")
        
        packages = [
            ('pyserial', 'serial'),
        ]
        
        for package, import_name in packages:
            if install_package(package, import_name):
                success_count += 1
            else:
                failed_count += 1
        
        print_info("Configuration Arduino:")
        print("  Port par défaut: COM3 (Windows)")
        print("  Port par défaut: /dev/ttyUSB0 (Linux)")
        print("  Port par défaut: /dev/cu.usbserial-* (macOS)")
    
    elif choice == '3':
        print_header("Installation de MQTT")
        
        packages = [
            ('paho-mqtt', 'paho'),
        ]
        
        for package, import_name in packages:
            if install_package(package, import_name):
                success_count += 1
            else:
                failed_count += 1
        
        print_info("Brokers MQTT publics (pour tester):")
        print("  • broker.hivemq.com:1883")
        print("  • test.mosquitto.org:1883")
        print("  • iot.eclipse.org:1883")
    
    elif choice == '4':
        print_header("Installation HTTP/Réseau")
        
        packages = [
            ('requests', 'requests'),
        ]
        
        for package, import_name in packages:
            if install_package(package, import_name):
                success_count += 1
            else:
                failed_count += 1
    
    elif choice == '5':
        print_header("Installation Cloud / Edge")
        
        print("""
Choisissez votre plateforme Cloud:

a) ☁️  Azure IoT
b) ☁️  AWS IoT
c) ☁️  Google Cloud IoT
d) 🟣 Tous

Votre choix: """)
        
        cloud_choice = input().strip().lower()
        
        packages = []
        
        if cloud_choice in ['a', 'd']:
            packages.append(('azure-iot-device', 'azure'))
        
        if cloud_choice in ['b', 'd']:
            packages.append(('boto3', 'boto3'))
        
        if cloud_choice in ['c', 'd']:
            packages.append(('google-cloud-iot', 'google'))
        
        for package, import_name in packages:
            if install_package(package, import_name):
                success_count += 1
            else:
                failed_count += 1
    
    elif choice == '6':
        print_header("Installation Utilitaires")
        
        packages = [
            ('pyusb', 'usb'),
            ('bleak', 'bleak'),
        ]
        
        for package, import_name in packages:
            if install_package(package, import_name):
                success_count += 1
            else:
                failed_count += 1
    
    elif choice == '7':
        print_info("Annulation")
        return
    
    else:
        print_error("Choix invalide")
        return
    
    # Résumé
    print_header("📊 Résumé de l'Installation")
    print_success(f"Packages installés avec succès: {success_count}")
    
    if failed_count > 0:
        print_error(f"Packages échoués: {failed_count}")
    
    # Vérifier le statut complet
    print("\n" + "="*60)
    print("Vérification des dépendances disponibles:")
    print("="*60 + "\n")
    
    modules_to_check = [
        ('pyserial', '🔌 Arduino/TinkerCAD'),
        ('paho', '🌐 MQTT'),
        ('requests', '📡 HTTP/Réseau'),
        ('azure', '☁️  Azure IoT'),
        ('boto3', '☁️  AWS IoT'),
        ('google', '☁️  Google Cloud'),
        ('usb', '🔌 USB'),
        ('bleak', '🔵 Bluetooth'),
    ]
    
    for module, label in modules_to_check:
        try:
            __import__(module)
            print_success(f"{label} - Disponible")
        except ImportError:
            print_warning(f"{label} - Non installé")
    
    print("\n" + "="*60)
    print("✅ Installation terminée!")
    print("="*60 + "\n")
    
    print(f"""
📚 Documentation:
  • Guide complet: PHYSICAL_DEVICES_GUIDE.md
  • Config exemples: PHYSICAL_DEVICES_CONFIG.example.ini
  • Code Arduino: scripts/tinkercad_arduino.ino

🚀 Prochaines étapes:
  1. Accédez à unified_monitoring.html
  2. Ouvrez "Configuration Périphériques Physiques"
  3. Cochez les périphériques à utiliser
  4. Entrez les paramètres
  5. Cliquez "Appliquer Configuration"
  6. Cliquez "Tester Périphériques"

🔧 Dépannage:
  • Arduino: Vérifiez le port COM dans Gestionnaire de périphériques
  • MQTT: Testez avec: mosquitto_sub -h broker -t "sensors/#"
  • HTTP: Testez avec: curl http://endpoint/api/sensors

💬 Support:
  Consultez CONTRIBUTING.md pour l'aide
    """)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + Colors.WARNING + "⚠️  Installation annulée par l'utilisateur" + Colors.ENDC)
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Erreur: {e}{Colors.ENDC}")
        sys.exit(1)
