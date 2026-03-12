#!/usr/bin/env python3
"""
Diagnostic complet de la base de données MySQL
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au PATH
sys.path.insert(0, str(Path(__file__).parent))

from app.logger import logger
from config import config
from app.database_unified import db
from app.main_new import create_app

def diagnose_database():
    """Diagnostiquer l'état de la base de données"""
    
    print("\n" + "="*80)
    print("🔍 DIAGNOSTIC BASE DE DONNÉES EPI DETECTION")
    print("="*80)
    
    # 1. Configuration
    print("\n📋 CONFIGURATION DE LA BASE DE DONNÉES:")
    print(f"  DB_TYPE: {config.DB_TYPE}")
    print(f"  DATABASE_URI: {config.DATABASE_URI}")
    
    if config.DB_TYPE == 'mysql':
        print(f"  Hôte: {config.DB_HOST}:{config.DB_PORT}")
        print(f"  Utilisateur: {config.DB_USER}")
        print(f"  Base de données: {config.DB_NAME}")
    else:
        print(f"  Fichier SQLite: {config.DB_PATH}")
    
    # 2. Vérifier la connexion
    print("\n🔗 VÉRIFICATION DE LA CONNEXION:")
    try:
        app = create_app('development')
        with app.app_context():
            # Tester la connexion
            from sqlalchemy import text
            result = db.session.execute(text("SELECT 1"))
            print("  ✅ Connexion à la base de données: OK")
            
            # 3. Vérifier les tables
            print("\n📊 VÉRIFICATION DES TABLES:")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"  Total de tables: {len(tables)}")
            for table in sorted(tables):
                print(f"    - {table}")
            
            # 4. Compter les enregistrements
            print("\n📈 NOMBRE D'ENREGISTREMENTS:")
            
            from app.database_unified import Detection, Alert, TrainingResult
            
            detections_count = Detection.query.count()
            alerts_count = Alert.query.count()
            training_count = TrainingResult.query.count()
            
            print(f"  Détections: {detections_count}")
            print(f"  Alertes: {alerts_count}")
            print(f"  Résultats d'entraînement: {training_count}")
            
            # 5. Détections récentes
            if detections_count > 0:
                print("\n🕐 DÉTECTIONS RÉCENTES:")
                recent = Detection.query.order_by(Detection.timestamp.desc()).limit(5).all()
                for det in recent:
                    print(f"  - {det.timestamp}: {det.total_persons} personnes (conformité: {det.compliance_rate}%)")
            else:
                print("\n⚠️  AUCUNE DÉTECTION TROUVÉE!")
                print("  💡 Solution: Uploader une image ou renseigner des données de test")
            
            print("\n✅ Diagnostic terminé!")
            
    except Exception as e:
        print(f"  ❌ Erreur de connexion: {e}")
        print("\n💡 SOLUTIONS:")
        if config.DB_TYPE == 'mysql':
            print("  1. Vérifier que MySQL est démarré")
            print("     Windows: MySQL doit être dans les services Windows")
            print("     Commande: services.msc → MySQL80")
            print("")
            print("  2. Vérifier les identifiants MySQL:")
            print(f"     Hôte: {config.DB_HOST}")
            print(f"     Port: {config.DB_PORT}")
            print(f"     Utilisateur: {config.DB_USER}")
            print(f"     Base de données: {config.DB_NAME}")
        print("")
        return False
    
    return True

if __name__ == '__main__':
    success = diagnose_database()
    sys.exit(0 if success else 1)
