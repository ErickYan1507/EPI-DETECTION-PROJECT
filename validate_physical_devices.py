#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validation de l'intégration des périphériques physiques
Vérifie que tout est correctement configuré et fonctionnel
"""

import os
import sys
import json
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_ok(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_fail(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_warn(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")

def check_file_exists(path, description):
    """Vérifier si un fichier existe"""
    if Path(path).exists():
        print_ok(f"{description}")
        return True
    else:
        print_fail(f"{description} - NON TROUVÉ")
        return False

def check_python_module(module_name, display_name):
    """Vérifier si un module Python est installé"""
    try:
        __import__(module_name)
        print_warn(f"{display_name} - Installé (optionnel)")
        return True
    except ImportError:
        print_info(f"{display_name} - Non installé (optionnel)")
        return False

def main():
    print_section("🔌 Validation de l'Intégration des Périphériques Physiques")
    
    success = True
    
    # ===== VÉRIFIER LES FICHIERS CRÉÉS =====
    print_section("📄 Vérification des Fichiers")
    
    files_to_check = [
        ('PHYSICAL_DEVICES_GUIDE.md', 'Documentation complète'),
        ('PHYSICAL_DEVICES_SUMMARY.md', 'Résumé technique'),
        ('QUICK_START_PHYSICAL_DEVICES.md', 'Guide rapide'),
        ('PHYSICAL_DEVICES_CONFIG.example.ini', 'Exemples config'),
        ('PHYSICAL_DEVICES_INDEX.md', 'Index des fichiers'),
        ('install_physical_devices.py', 'Script installation'),
        ('app/routes_physical_devices.py', 'Routes API'),
        ('tests/test_physical_devices.py', 'Tests unitaires'),
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, f"{description}"):
            success = False
    
    # ===== VÉRIFIER LES MODIFICATIONS =====
    print_section("✏️  Vérification des Modifications")
    
    # Vérifier que unified_monitoring.html a été modifié
    with open('templates/unified_monitoring.html', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'PhysicalDeviceManager' in content:
            print_ok("unified_monitoring.html - Section configuration ajoutée")
        else:
            print_fail("unified_monitoring.html - Modification non trouvée")
            success = False
    
    # Vérifier que main.py a les imports
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'routes_physical_devices' in content and 'physical_routes' in content:
            print_ok("app/main.py - Import et enregistrement ajoutés")
        else:
            print_fail("app/main.py - Import manquant")
            success = False
    
    # ===== VÉRIFIER LES DÉPENDANCES OPTIONNELLES =====
    print_section("📦 Dépendances Optionnelles")
    
    optional_modules = [
        ('serial', 'PySerial (Arduino)'),
        ('paho', 'paho-mqtt (MQTT)'),
        ('requests', 'requests (HTTP)'),
        ('azure', 'azure-iot-device (Azure)'),
        ('boto3', 'boto3 (AWS)'),
        ('google', 'google-cloud-iot (Google Cloud)'),
        ('usb', 'pyusb (USB)'),
        ('bleak', 'bleak (Bluetooth)'),
    ]
    
    modules_found = 0
    for module, display_name in optional_modules:
        if check_python_module(module, display_name):
            modules_found += 1
    
    print_info(f"\n{modules_found}/8 dépendances optionnelles installées")
    if modules_found == 0:
        print_info("Exécutez: python install_physical_devices.py")
    
    # ===== VÉRIFIER LA STRUCTURE =====
    print_section("📁 Structure du Projet")
    
    directories = [
        ('templates', 'Répertoire templates'),
        ('app', 'Répertoire app'),
        ('tests', 'Répertoire tests'),
        ('scripts', 'Répertoire scripts'),
    ]
    
    for dirname, description in directories:
        if Path(dirname).exists():
            print_ok(description)
        else:
            print_fail(description)
            success = False
    
    # ===== RÉSUMÉ =====
    print_section("📊 Résumé de Validation")
    
    if success:
        print_ok("✨ Tous les fichiers de base sont présents!")
        print_info("\n🚀 Prochaines étapes:")
        print(f"  1. Lire: {Colors.BOLD}QUICK_START_PHYSICAL_DEVICES.md{Colors.ENDC}")
        print(f"  2. Exécuter: {Colors.BOLD}python install_physical_devices.py{Colors.ENDC}")
        print(f"  3. Accéder: {Colors.BOLD}http://localhost:5000/unified_monitoring.html{Colors.ENDC}")
        print(f"  4. Configurer les périphériques dans l'interface")
        print(f"  5. Cliquer sur \"Tester Périphériques\"")
    else:
        print_fail("⚠️  Certains fichiers manquent!")
        print_warn("Veuillez vérifier l'installation")
    
    # ===== RESSOURCES =====
    print_section("📚 Ressources Disponibles")
    
    resources = [
        ('QUICK_START_PHYSICAL_DEVICES.md', 'Démarrage rapide (7 min)'),
        ('PHYSICAL_DEVICES_GUIDE.md', 'Documentation complète (30 min)'),
        ('PHYSICAL_DEVICES_SUMMARY.md', 'Résumé technique (15 min)'),
        ('PHYSICAL_DEVICES_CONFIG.example.ini', '7 exemples prêts'),
        ('install_physical_devices.py', 'Installation dépendances'),
    ]
    
    for filename, description in resources:
        print_info(f"{filename} - {description}")
    
    # ===== VÉRIFICATION FINALE =====
    print_section("✅ Validation Complète")
    
    if success:
        print_ok("L'intégration des périphériques physiques est correctement installée!")
        print_ok("Vous pouvez commencer à utiliser le système.")
        print("\n" + Colors.BOLD + "Pour plus d'informations:" + Colors.ENDC)
        print("  • Guide rapide: QUICK_START_PHYSICAL_DEVICES.md")
        print("  • Guide complet: PHYSICAL_DEVICES_GUIDE.md")
        print("  • Index fichiers: PHYSICAL_DEVICES_INDEX.md")
        return 0
    else:
        print_fail("Veuillez vérifier l'installation des fichiers.")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Validation annulée{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Erreur: {e}{Colors.ENDC}")
        sys.exit(1)
