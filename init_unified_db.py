#!/usr/bin/env python3
"""
Script d'initialisation de la base de données unifiée
Crée les tables, import les résultats d'entraînement existants
Supporte SQLite et MySQL
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Ajouter le chemin racine
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from flask import Flask
from config import config
from app.database_unified import db, init_db

def setup_database():
    """Initialiser la base de données"""
    
    print("=" * 70)
    print("🗄️  INITIALISATION BASE DE DONNÉES UNIFIÉE")
    print("=" * 70)
    
    # Créer l'app Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = getattr(config, 'SQLALCHEMY_ENGINE_OPTIONS', {})
    
    print(f"\n📌 Type de base de données: {config.DB_TYPE.upper()}")
    print(f"📌 URI: {config.DATABASE_URI}")
    
    # Pour SQLite, optionner de supprimer l'ancienne BD
    if config.DB_TYPE == 'sqlite':
        db_path = Path(config.DATABASE_URI.replace('sqlite:///', ''))
        if db_path.exists():
            response = input(f"\n⚠️  Fichier BD existant: {db_path}\n   Supprimer et recréer? (o/n): ").strip().lower()
            if response == 'o':
                try:
                    db_path.unlink()
                    print("✅ Ancienne BD supprimée")
                except Exception as e:
                    print(f"⚠️  Impossible de supprimer: {e}")
    
    try:
        # Initialiser la BD
        db.init_app(app)
        
        with app.app_context():
            # Créer les tables
            print("\n🔨 Création des tables...")
            db.create_all()
            print("✅ Tables créées/vérifiées avec succès")
            
            # Afficher les tables créées
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n📊 Tables dans la base de données ({len(tables)}):")
            for table in sorted(tables):
                print(f"  ✓ {table}")
            
            # Afficher les comptes
            from app.database_unified import TrainingResult, Detection, Alert, Worker, IoTSensor, IoTDataLog, SystemLog
            
            print(f"\n📈 Statistiques actuelles:")
            print(f"  - TrainingResult: {TrainingResult.query.count()}")
            print(f"  - Detection: {Detection.query.count()}")
            print(f"  - Alert: {Alert.query.count()}")
            print(f"  - Worker: {Worker.query.count()}")
            print(f"  - IoTSensor: {IoTSensor.query.count()}")
            print(f"  - IoTDataLog: {IoTDataLog.query.count()}")
            print(f"  - SystemLog: {SystemLog.query.count()}")
            
        print("\n✅ Base de données initialisée avec succès!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_training_results():
    """Importer les résultats d'entraînement existants"""
    
    print("\n" + "=" * 70)
    print("📥 IMPORT DES RÉSULTATS D'ENTRAÎNEMENT")
    print("=" * 70)
    
    from app.db_training_integration import import_all_training_results_to_db
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = getattr(config, 'SQLALCHEMY_ENGINE_OPTIONS', {})
    
    db.init_app(app)
    
    with app.app_context():
        try:
            count = import_all_training_results_to_db(app)
            print(f"\n✅ {count} résultats d'entraînement importés avec succès!")
            return count > 0
        except Exception as e:
            print(f"\n⚠️  Erreur lors de l'import: {e}")
            return False


def main():
    """Fonction principale"""
    
    # Vérifier les dépendances
    print("\n🔍 Vérification des dépendances...")
    
    try:
        import flask
        import flask_sqlalchemy
        import sqlalchemy
        print("✓ Flask, Flask-SQLAlchemy, SQLAlchemy OK")
    except ImportError as e:
        print(f"❌ Erreur: {e}")
        return False
    
    if config.DB_TYPE == 'mysql':
        try:
            import pymysql
            print("✓ PyMySQL OK")
        except ImportError:
            print("⚠️  PyMySQL non installé - essai de mysqlconnector...")
            try:
                import mysql.connector
                print("✓ mysql-connector-python OK")
            except ImportError:
                print("❌ Aucun driver MySQL disponible!")
                print("   Installez: pip install pymysql")
                return False
    
    # Initialiser la BD
    if not setup_database():
        return False
    
    # Import optionnel des résultats d'entraînement
    print("\n" + "=" * 70)
    response = input("🤔 Importer les résultats d'entraînement existants? (o/n): ").strip().lower()
    
    if response == 'o':
        import_training_results()
    
    print("\n" + "=" * 70)
    print("✅ INITIALISATION COMPLÈTE!")
    print("=" * 70)
    print("\n📝 Prochaines étapes:")
    print("  1. Vérifier la connexion à la BD:")
    print("     python -c \"from app.database_unified import db; print('BD OK')\"")
    print("  2. Lancer l'application:")
    print("     python run_app.py")
    print("  3. Accéder à http://localhost:5000")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
