#!/usr/bin/env python3
"""
Script pour initialiser la BD de manière non-interactive
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from flask import Flask
from config import config
from app.database_unified import db

# Supprimer la BD SQLite si elle existe
if config.DB_TYPE == 'sqlite':
    db_path = Path(config.DATABASE_URI.replace('sqlite:///', ''))
    if db_path.exists():
        print(f"🗑️  Suppression de {db_path}...")
        try:
            db_path.unlink()
            print("✅ Ancienne BD supprimée")
        except Exception as e:
            print(f"⚠️  Impossible de supprimer: {e}")

# Créer l'app et initialiser la BD
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = getattr(config, 'SQLALCHEMY_ENGINE_OPTIONS', {})

print(f"\n📌 Initialisation BD: {config.DB_TYPE.upper()}")

try:
    db.init_app(app)
    
    with app.app_context():
        print("🔨 Création des tables...")
        db.create_all()
        
        # Vérifier les tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n✅ BD initialisée avec {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  ✓ {table}")
        
        print("\n✅ Succès!")
        
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
