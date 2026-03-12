#!/usr/bin/env python3
"""
QUICK START: Lancer le système EPI Detection avec Arduino
Auteur: AI Assistant
Date: 2026-02-18
"""

import os
import sys
import subprocess
import time
from pathlib import Path

print("\n" + "="*70)
print("🚀 LANCEMENT SYSTÈME EPI DETECTION + ARDUINO")
print("="*70 + "\n")

# Set Arduino port
os.environ['ARDUINO_PORT'] = 'COM3'
os.environ['FLASK_ENV'] = 'development'

print("📋 Configuration:")
print(f"  Arduino Port: {os.environ.get('ARDUINO_PORT')}")
print(f"  Flask Env:   {os.environ.get('FLASK_ENV')}")
print(f"  Working Dir: {Path.cwd()}\n")

# Check if Flask is already running
print("🔍 Vérification des processus existants...")
result = subprocess.run(
    ['powershell', '-Command', 'Get-Process python -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count'],
    capture_output=True,
    text=True
)

python_count = int(result.stdout.strip() or 0)
if python_count > 0:
    print(f"   ⚠️  {python_count} processus Python détectés")
    print("   Tuant les processus existants...")
    subprocess.run(
        ['powershell', '-Command', 'Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue'],
        capture_output=True
    )
    time.sleep(2)
    print("   ✅ Processus arrêtés\n")

# Launch Flask
print("🚀 Lancement Flask...\n")
print("-" * 70)
print("Pour tester, ouvrez dans un navigateur:")
print("   http://localhost:5000/unified_monitoring.html")
print("-" * 70 + "\n")

try:
    # Run Flask
    subprocess.run([
        str(Path('.venv/Scripts/python.exe')),
        'run_app.py',
        'dev'
    ], env=os.environ)
    
except KeyboardInterrupt:
    print("\n\n⛔ Arrêt du système par l'utilisateur")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    sys.exit(1)
