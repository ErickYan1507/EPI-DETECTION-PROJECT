#!/usr/bin/env python3
"""
Forcer la réinitialisation complète de la BD
Supprime TOUTES les tables et les recrée
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from flask import Flask
from config import config
from app.database_unified import db

print("=" * 70)
print("⚠️  RÉINITIALISATION COMPLÈTE DE LA BASE DE DONNÉES")
print("=" * 70)
print("\n🔴 ATTENTION: Cela supprimera TOUTES les données!")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = getattr(config, 'SQLALCHEMY_ENGINE_OPTIONS', {})

db.init_app(app)

with app.app_context():
    print(f"\n📌 BD: {config.DB_TYPE.upper()}")
    print(f"📌 URI: {config.DATABASE_URI}")
    
    try:
        # Supprimer TOUTES les tables
        print("\n🗑️  Suppression de TOUTES les tables...")
        db.drop_all()
        print("✅ Tables supprimées")
        
        # Recréer les tables avec le nouveau schéma
        print("\n🔨 Création des nouvelles tables...")
        db.create_all()
        
        # Vérifier
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n✅ BD réinitialisée avec {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  ✓ {table}")
        
        # Vérifier les colonnes de training_results
        columns = [col['name'] for col in inspector.get_columns('training_results')]
        print(f"\n📊 Colonnes de training_results:")
        for col in sorted(columns):
            print(f"  ✓ {col}")
        
        print("\n✅ Réinitialisation réussie!")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
