#!/usr/bin/env python3
"""
Quick Start Script pour Dual Database System
Fonctionne directement sans problèmes de subprocess
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Démarrage rapide"""
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        🚀 EPI DETECTION - DUAL DATABASE QUICK START 🚀        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

ÉTAPE 1: Installer les dépendances Python
═════════════════════════════════════════════════════════════════""")
    
    packages = [
        'mysql-connector-python',
        'PyMySQL',
        'python-dotenv',
        'tabulate'
    ]
    
    print("\n📦 Installation des packages...")
    for package in packages:
        print(f"  {package}...", end=' ')
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-q', package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✓")
        except Exception as e:
            print(f"⚠️  (continuer...)")
    
    print("""

ÉTAPE 2: Créer les répertoires
═════════════════════════════════════════════════════════════════""")
    
    dirs = ['database', 'logs', 'instance']
    for d in dirs:
        path = project_root / d
        path.mkdir(exist_ok=True)
        print(f"  ✓ {d}/")
    
    print("""

ÉTAPE 3: Créer .env (si nécessaire)
═════════════════════════════════════════════════════════════════""")
    
    env_file = project_root / '.env'
    env_example = project_root / '.env.example'
    
    if env_file.exists():
        print(f"  ✓ .env existe déjà")
    elif env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print(f"  ✓ .env créé depuis .env.example")
    else:
        print(f"  ⚠️  .env.example non trouvé")
    
    print("""

════════════════════════════════════════════════════════════════════
✅ SETUP RAPIDE TERMINÉ!

PROCHAINES ÉTAPES:
════════════════════════════════════════════════════════════════════

1️⃣  CONFIGURER MYSQL:
    python app\\mysql_config_setup.py --all

2️⃣  LANCER LA SYNC:
    python app\\sync_databases.py --watch

3️⃣  APP FLASK (autre PowerShell):
    python run_app.py run

DOCUMENTATION:
    START_HERE_DUAL_DB.txt
    GUIDE_DUAL_DATABASE.md
    INDEX_DUAL_DATABASE.txt

════════════════════════════════════════════════════════════════════
""")

if __name__ == '__main__':
    main()
