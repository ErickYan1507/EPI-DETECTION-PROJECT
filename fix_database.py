#!/usr/bin/env python
"""
Script pour vérifier et corriger les bases de données réelles
- Vérifier la connexion
- Nettoyer les données invalides
- Corriger les timestamps invalides
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from pathlib import Path

def check_sqlite_db():
    """Vérifier la base SQLite"""
    print("\n" + "="*70)
    print("🔍 Vérification SQLite")
    print("="*70)
    
    try:
        from config import config
        import sqlite3
        
        db_path = config.DATABASE_URI.replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print(f"❌ Base SQLite non trouvée: {db_path}")
            return False
        
        print(f"✅ Base trouvée: {db_path}")
        print(f"   Taille: {os.path.getsize(db_path) / 1024:.2f} KB")
        
        # Vérifier la structure
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lister les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n   Tables ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} lignes")
        
        # Vérifier les timestamps invalides
        print(f"\n   Vérification des timestamps...")
        cursor.execute("""
            SELECT COUNT(*) FROM detections 
            WHERE timestamp IS NULL OR timestamp = ''
        """)
        null_timestamps = cursor.fetchone()[0]
        if null_timestamps > 0:
            print(f"   ⚠️  {null_timestamps} détections avec timestamp invalide")
        
        cursor.execute("""
            SELECT COUNT(*) FROM training_results 
            WHERE timestamp IS NULL OR timestamp = ''
        """)
        null_training = cursor.fetchone()[0]
        if null_training > 0:
            print(f"   ⚠️  {null_training} entraînements avec timestamp invalide")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur SQLite: {e}")
        return False

def check_mysql_db():
    """Vérifier la base MySQL"""
    print("\n" + "="*70)
    print("🔍 Vérification MySQL")
    print("="*70)
    
    try:
        from config import config
        
        if config.DB_TYPE != 'mysql':
            print("⏭️  MySQL non configuré (DB_TYPE != 'mysql')")
            return True
        
        import pymysql
        
        connection = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        
        cursor = connection.cursor()
        
        print(f"✅ Connexion MySQL réussie")
        print(f"   Host: {config.DB_HOST}:{config.DB_PORT}")
        print(f"   Database: {config.DB_NAME}")
        
        # Lister les tables
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(f"\n   Tables ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} lignes")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"⚠️  Erreur MySQL: {e}")
        return False

def fix_timestamps():
    """Corriger les timestamps invalides"""
    print("\n" + "="*70)
    print("🔧 Correction des timestamps")
    print("="*70)
    
    try:
        from app.main import app, db
        from app.database_unified import Detection, TrainingResult
        
        with app.app_context():
            # Corriger les détections
            detections = Detection.query.filter(
                (Detection.timestamp == None) | (Detection.timestamp == '')
            ).all()
            
            if detections:
                print(f"⚠️  Correction de {len(detections)} détections sans timestamp...")
                now = datetime.utcnow()
                for det in detections:
                    det.timestamp = now
                db.session.commit()
                print(f"✅ {len(detections)} détections corrigées")
            
            # Corriger les entraînements
            trainings = TrainingResult.query.filter(
                (TrainingResult.timestamp == None) | (TrainingResult.timestamp == '')
            ).all()
            
            if trainings:
                print(f"⚠️  Correction de {len(trainings)} entraînements sans timestamp...")
                now = datetime.utcnow()
                for train in trainings:
                    train.timestamp = now
                db.session.commit()
                print(f"✅ {len(trainings)} entraînements corrigés")
            
            if not detections and not trainings:
                print("✅ Aucun timestamp invalide trouvé")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur correction timestamps: {e}")
        return False

def clean_database():
    """Nettoyer la base de données"""
    print("\n" + "="*70)
    print("🧹 Nettoyage de la base de données")
    print("="*70)
    
    try:
        from app.main import app, db
        from app.database_unified import Detection, Alert
        
        with app.app_context():
            # Supprimer les alertes résolues anciennes
            from datetime import timedelta
            old_date = datetime.utcnow() - timedelta(days=30)
            
            old_alerts = Alert.query.filter(
                Alert.resolved == True,
                Alert.timestamp < old_date
            ).count()
            
            if old_alerts > 0:
                print(f"⚠️  Suppression de {old_alerts} alertes résolues anciennes...")
                Alert.query.filter(
                    Alert.resolved == True,
                    Alert.timestamp < old_date
                ).delete()
                db.session.commit()
                print(f"✅ {old_alerts} alertes supprimées")
            
            # Afficher les statistiques
            total_detections = Detection.query.count()
            total_alerts = Alert.query.count()
            
            print(f"\n   Statistiques finales:")
            print(f"   - Détections: {total_detections}")
            print(f"   - Alertes: {total_alerts}")
            
            return True
            
    except Exception as e:
        print(f"⚠️  Erreur nettoyage: {e}")
        return False

if __name__ == '__main__':
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " " * 10 + "🔧 VÉRIFICATION ET CORRECTION DES BASES DE DONNÉES" + " " * 8 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {
        'SQLite': check_sqlite_db(),
        'MySQL': check_mysql_db(),
        'Fix Timestamps': fix_timestamps(),
        'Clean Database': clean_database(),
    }
    
    print("\n" + "="*70)
    print("📊 RÉSUMÉ")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status}  {test_name}")
    
    print("\n✅ Base de données vérifiée et corrigée!")
