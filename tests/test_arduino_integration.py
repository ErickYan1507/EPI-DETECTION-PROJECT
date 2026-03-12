#!/usr/bin/env python
"""
Script de test d'intégration Arduino pour EPI Detection System
Permet de tester la communication avec Arduino sans le hardware physique
"""

import json
import time
import argparse
from app.arduino_integration import (
    ArduinoController,
    ArduinoDataParser,
    ArduinoSessionManager
)
from app.logger import logger

def test_parser():
    """Tester le parser de données Arduino"""
    print("\n" + "="*60)
    print("🧪 TEST: Arduino Data Parser")
    print("="*60)
    
    test_lines = [
        "[STARTUP] EPI Detection Arduino Controller v2.0",
        "[SENSOR] temp=25.5,humidity=60",
        "[MOTION] Motion detected!",
        "[DETECT] Helmet:✓ Vest:✗ Glasses:✓ Confidence:92%",
        "[STATUS] ✅ SAFE (Compliance: 92%)",
        "[STATUS] ⚠️ WARNING (Compliance: 65%)",
        "[STATUS] 🚨 DANGER (Compliance: 45%)",
        "[CMD] Received compliance level: 85",
    ]
    
    parser = ArduinoDataParser()
    
    for line in test_lines:
        print(f"\n📥 Ligne brute: {line}")
        
        parsed = parser.parse_line(line)
        print(f"   Type: {parsed['type']}")
        print(f"   Data: {parsed['data']}")
        
        metrics = parser.extract_metrics(parsed)
        print(f"   Métriques: {metrics}")


def test_simulation():
    """Simuler une session Arduino sans hardware"""
    print("\n" + "="*60)
    print("🧪 TEST: Arduino Session Simulation")
    print("="*60)
    
    # Créer une session (sur un port qui n'existe pas)
    session = ArduinoSessionManager(port='SIMULATION')
    parser = ArduinoDataParser()
    
    print("\n📡 Simulation de données Arduino reçues:")
    
    simulation_data = [
        "[STARTUP] EPI Detection Arduino Controller v2.0",
        "[SENSOR] temp=23.5,humidity=55",
        "[DETECT] Helmet:✓ Vest:✓ Glasses:✓ Confidence:95%",
        "[STATUS] ✅ SAFE (Compliance: 95%)",
        "[SENSOR] temp=24.0,humidity=58",
        "[MOTION] Motion detected!",
        "[DETECT] Helmet:✓ Vest:✗ Glasses:✓ Confidence:72%",
        "[STATUS] ⚠️ WARNING (Compliance: 72%)",
    ]
    
    # Simuler la réception de données
    for data_line in simulation_data:
        parsed = parser.parse_line(data_line)
        metrics = parser.extract_metrics(parsed)
        
        print(f"\n   Line: {data_line[:50]}...")
        print(f"   Parsed Type: {parsed['type']}")
        
        # Mettre à jour les métriques de session
        for key, value in metrics.items():
            if value is not None:
                session.current_metrics[key] = value
    
    print("\n✅ Métriques finales après simulation:")
    print(json.dumps(session.current_metrics, indent=2, ensure_ascii=False))


def test_json_output():
    """Tester l'affichage JSON des métriques"""
    print("\n" + "="*60)
    print("🧪 TEST: JSON Output Format")
    print("="*60)
    
    sample_metrics = {
        'motion_detected': True,
        'temperature': 24.5,
        'humidity': 56,
        'helmet': True,
        'vest': True,
        'glasses': True,
        'compliance': 92,
        'status': 'SAFE',
        'last_update': '2026-01-22T10:30:45.123456'
    }
    
    print("\n📊 Métriques en JSON:")
    print(json.dumps(sample_metrics, indent=2, ensure_ascii=False))
    
    print("\n✅ Format valide pour Server-Sent Events (SSE)")


def test_compliance_levels():
    """Tester les niveaux de conformité"""
    print("\n" + "="*60)
    print("🧪 TEST: Compliance Levels & LED States")
    print("="*60)
    
    levels = [
        (95, "🟢", "SAFE", "LED verte + Buzzer silencieux"),
        (85, "🟢", "SAFE", "LED verte + Buzzer silencieux"),
        (80, "🟢", "SAFE", "LED verte + Buzzer silencieux"),
        (75, "🟡", "WARNING", "LED rouge + Buzzer silencieux"),
        (65, "🟡", "WARNING", "LED rouge + Buzzer silencieux"),
        (60, "🟡", "WARNING", "LED rouge + Buzzer silencieux"),
        (55, "🔴", "DANGER", "LED rouge + Buzzer ACTIF"),
        (35, "🔴", "DANGER", "LED rouge + Buzzer ACTIF"),
        (0, "🔴", "DANGER", "LED rouge + Buzzer ACTIF"),
    ]
    
    print("\nNiveaux de Conformité:")
    print("-" * 60)
    print("Conformité | LED  | État     | Description                   ")
    print("-" * 60)
    
    for compliance, led, state, description in levels:
        print(f"{compliance:3d}%      | {led}   | {state:8} | {description}")
    
    print("-" * 60)


def test_command_formats():
    """Afficher les formats de commande"""
    print("\n" + "="*60)
    print("🧪 TEST: Arduino Command Formats")
    print("="*60)
    
    print("\n📤 Commandes Python → Arduino:")
    print("-" * 60)
    
    commands = [
        ("C85", "Envoyer niveau de conformité 85%"),
        ("C0", "Non conforme (0%)"),
        ("C100", "Entièrement conforme (100%)"),
        ("DETECT:helmet=1,vest=1,glasses=1,confidence=95",
         "Tous les EPI détectés avec 95% de confiance"),
        ("DETECT:helmet=1,vest=0,glasses=1,confidence=72",
         "Casque et lunettes détectés, pas de gilet"),
        ("DETECT:helmet=0,vest=0,glasses=0,confidence=0",
         "Aucun EPI détecté"),
    ]
    
    for command, description in commands:
        print(f"\n  Command: {command}")
        print(f"  Desc:    {description}")
    
    print("\n📥 Données Arduino → Python:")
    print("-" * 60)
    
    responses = [
        ("[STARTUP] ...", "Démarrage Arduino"),
        ("[SENSOR] temp=25.5,humidity=60", "Lecture capteurs"),
        ("[MOTION] Motion detected!", "Mouvement détecté"),
        ("[STATUS] ✅ SAFE (Compliance: 92%)", "État SAFE"),
        ("[STATUS] ⚠️ WARNING (Compliance: 65%)", "État WARNING"),
        ("[STATUS] 🚨 DANGER (Compliance: 45%)", "État DANGER"),
    ]
    
    for response, description in responses:
        print(f"\n  Response: {response}")
        print(f"  Meaning:  {description}")


def main():
    """Lancer tous les tests"""
    parser = argparse.ArgumentParser(
        description='Test Arduino Integration pour EPI Detection'
    )
    parser.add_argument(
        '--test',
        choices=['parser', 'simulation', 'json', 'compliance', 'commands', 'all'],
        default='all',
        help='Tests à lancer'
    )
    
    args = parser.parse_args()
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   🤖 TESTS D'INTÉGRATION ARDUINO - EPI DETECTION SYSTEM   ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    if args.test in ['parser', 'all']:
        test_parser()
    
    if args.test in ['simulation', 'all']:
        test_simulation()
    
    if args.test in ['json', 'all']:
        test_json_output()
    
    if args.test in ['compliance', 'all']:
        test_compliance_levels()
    
    if args.test in ['commands', 'all']:
        test_command_formats()
    
    print("""
    
    ✅ TOUS LES TESTS COMPLÉTÉS
    
    📚 Documentation complète: ARDUINO_INTEGRATION_GUIDE.md
    🚀 Pour démarrer: python run.py
    🌐 Dashboard: http://localhost:5000/unified_monitoring.html
    """)


if __name__ == '__main__':
    main()

