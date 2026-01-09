#!/usr/bin/env python3
"""
Script d'initialisation du projet EPI Detection
À exécuter une seule fois après le clonage
"""
import os
import sys
from pathlib import Path
import subprocess

def print_header(msg):
    print("\n" + "="*60)
    print(f"  {msg}")
    print("="*60)

def init_project():
    """Initialiser le projet"""
    root = Path(__file__).parent
    
    print_header("🚀 INITIALISATION EPI DETECTION")
    
    # 1. Créer .env
    print("\n1️⃣  Configuration de l'environnement...")
    env_file = root / '.env'
    env_example = root / '.env.example'
    
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("   ✓ Fichier .env créé (copié depuis .env.example)")
    else:
        print("   ✓ Fichier .env déjà existant")
    
    # 2. Créer les dossiers
    print("\n2️⃣  Création des dossiers...")
    folders = [
        'data',
        'logs',
        'models',
        'models/custom_weights',
        'static/uploads',
        'static/uploads/images',
        'static/uploads/videos'
    ]
    
    for folder in folders:
        folder_path = root / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {folder}")
    
    # 3. Vérifier les dépendances
    print("\n3️⃣  Vérification des dépendances...")
    try:
        import flask
        import torch
        import cv2
        print("   ✓ Dépendances principales installées")
    except ImportError as e:
        print(f"   ⚠️  Dépendances manquantes: {e}")
        print("   Installer avec: pip install -r requirements.txt")
    
    # 4. Initialiser la base de données
    print("\n4️⃣  Initialisation de la base de données...")
    try:
        sys.path.insert(0, str(root))
        from app.main_new import app, db
        with app.app_context():
            db.create_all()
        print("   ✓ Tables de base de données créées")
    except Exception as e:
        print(f"   ⚠️  Erreur: {e}")
    
    # 5. Vérifier le modèle
    print("\n5️⃣  Vérification du modèle...")
    models_dir = root / 'models'
    best_model = models_dir / 'best.pt'
    
    if best_model.exists():
        print(f"   ✓ Modèle trouvé: {best_model.name}")
    else:
        print("   ⚠️  Aucun modèle entraîné trouvé")
        print("   À faire: python train.py --epochs 100")
    
    # 6. Tester la configuration
    print("\n6️⃣  Test de la configuration...")
    try:
        from config import config
        print(f"   ✓ Mode: {os.getenv('ENV', 'development')}")
        print(f"   ✓ Debug: {config.DEBUG}")
        print(f"   ✓ DB: {config.DATABASE_URI[:50]}...")
    except Exception as e:
        print(f"   ⚠️  Erreur config: {e}")
    
    print_header("✅ INITIALISATION COMPLÈTE")
    
    print("\nÉtapes suivantes:")
    print("1. Éditer .env pour votre configuration")
    print("2. Entraîner le modèle: python train.py")
    print("3. Lancer l'app: python run_app.py dev")
    print("\nPour l'aide: python cli.py --help")

if __name__ == '__main__':
    try:
        init_project()
    except KeyboardInterrupt:
        print("\n⚠️  Initialisation annulée")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)
