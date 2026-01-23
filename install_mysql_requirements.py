#!/usr/bin/env python3
"""
Installation rapide des dépendances MySQL pour EPI Detection

Usage:
    python install_mysql_requirements.py
"""

import subprocess
import sys
from pathlib import Path

# Packages requis pour MySQL
MYSQL_PACKAGES = [
    'mysql-connector-python',
    'PyMySQL',
    'python-dotenv',
    'tabulate'
]

# Packages optionnels
OPTIONAL_PACKAGES = [
    'PyMySQL',  # Alternative MySQL driver
    'tabulate'  # Pour l'affichage formaté
]


def install_package(package_name):
    """Installer un package via pip"""
    print(f"📦 Installing {package_name}...", end=' ')
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', package_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✓")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def check_installation(package_name, import_name=None):
    """Vérifier qu'un package est installé"""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def main():
    print("\n" + "="*60)
    print("🚀 EPI DETECTION - MYSQL REQUIREMENTS INSTALLER")
    print("="*60 + "\n")
    
    # Vérifier les packages déjà installés
    print("🔍 Checking current installations...\n")
    installed = []
    missing = []
    
    for package in MYSQL_PACKAGES:
        if check_installation(package):
            print(f"  ✓ {package}")
            installed.append(package)
        else:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if not missing:
        print(f"\n✅ All required packages are already installed!")
        return
    
    # Installer les packages manquants
    print(f"\n📥 Installing {len(missing)} missing package(s)...\n")
    
    failed = []
    for package in missing:
        if not install_package(package):
            failed.append(package)
    
    # Résumé
    print(f"\n" + "="*60)
    print("📊 INSTALLATION SUMMARY")
    print("="*60)
    print(f"Already installed: {len(installed)}")
    print(f"Successfully installed: {len(missing) - len(failed)}")
    if failed:
        print(f"Failed: {len(failed)} - {', '.join(failed)}")
    else:
        print(f"\n✅ All packages installed successfully!")
    print("="*60 + "\n")
    
    if failed:
        print("Try installing manually:")
        for package in failed:
            print(f"  pip install {package}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
