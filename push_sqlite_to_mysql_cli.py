#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script CLI pour migrer les données de notifications de SQLite vers MySQL
Accepte les paramètres en ligne de commande
Usage: python push_sqlite_to_mysql_cli.py [--host HOST] [--port PORT] [--user USER] [--password PASS] [--db DB]
"""

import sys
import argparse
from pathlib import Path
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Ajouter le répertoire parent au chemin
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from app.database_unified import db, NotificationRecipient, NotificationHistory, NotificationConfig, ReportSchedule

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    parser = argparse.ArgumentParser(description='Migrer les notifications de SQLite vers MySQL')
    parser.add_argument('--host', default='localhost', help='Host MySQL (défaut: localhost)')
    parser.add_argument('--port', default='3306', help='Port MySQL (défaut: 3306)')
    parser.add_argument('--user', default='root', help='Utilisateur MySQL (défaut: root)')
    parser.add_argument('--password', default='', help='Mot de passe MySQL (défaut: vide)')
    parser.add_argument('--db', default='epi_detection_db', help='Nom base de données (défaut: epi_detection_db)')
    
    args = parser.parse_args()
    
    # Obtenir SQLite URI
    sqlite_uri = config.DATABASE_URI
    logging.info(f"✓ Base SQLite trouvée: {sqlite_uri}")
    
    # Construire l'URI MySQL
    db_password_encoded = quote_plus(args.password) if args.password else ""
    if db_password_encoded:
        mysql_uri = f'mysql+pymysql://{args.user}:{db_password_encoded}@{args.host}:{args.port}/{args.db}?charset=utf8mb4'
    else:
        mysql_uri = f'mysql+pymysql://{args.user}@{args.host}:{args.port}/{args.db}?charset=utf8mb4'
    
    logging.info(f"✓ URI MySQL: {mysql_uri.replace(db_password_encoded or '', '***')}")
    
    try:
        logging.info("\n📌 Création des tables dans MySQL...")
        
        sqlite_eng = create_engine(sqlite_uri, future=True)
        mysql_eng = create_engine(mysql_uri, future=True)
        
        # Tester la connexion MySQL
        with mysql_eng.connect() as conn:
            logging.info("✓ Connexion MySQL établie")
        
        # Créer les tables
        db.metadata.create_all(mysql_eng)
        logging.info("✓ Tables créées dans MySQL (si manquantes)")
        
        SqliteSession = sessionmaker(bind=sqlite_eng)
        MysqlSession = sessionmaker(bind=mysql_eng)
        
        sqlite_s = SqliteSession()
        mysql_s = MysqlSession()
        
        models = [NotificationRecipient, NotificationHistory, NotificationConfig, ReportSchedule]
        total_pushed = 0
        
        print("\n" + "="*60)
        print("📊 MIGRATION SQLite → MySQL")
        print("="*60 + "\n")
        
        for model in models:
            rows = sqlite_s.query(model).all()
            count = 0
            for row in rows:
                # Construire un dictionnaire de données
                data = {}
                for col in row.__table__.columns:
                    name = col.name
                    data[name] = getattr(row, name)
                # Insérer dans MySQL (ignorer les conflits de clé primaire)
                ins = model.__table__.insert().prefix_with("IGNORE")
                mysql_s.execute(ins.values(**data))
                count += 1
            mysql_s.commit()
            logging.info(f"  ✓ {count} lignes importées pour {model.__tablename__}")
            total_pushed += count
        
        sqlite_s.close()
        mysql_s.close()
        
        print("="*60)
        print(f"✅ MIGRATION RÉUSSIE")
        print(f"   Total lignes importées: {total_pushed}")
        print("="*60 + "\n")
        logging.info("✓ Migration terminée avec succès!")
        
        print("Vérification dans phpMyAdmin:")
        print(f"  Host: {args.host}:{args.port}")
        print(f"  User: {args.user}")
        print(f"  Database: {args.db}")
        print(f"  Tables créées: notification_recipients, notification_history, notification_config, report_schedule\n")
        
        return 0
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de la migration: {e}")
        logging.error("\n📋 Vérifications à faire:")
        logging.error("   ✓ Le serveur MySQL est-il en cours d'exécution?")
        logging.error(f"   ✓ Pouvez-vous vous connecter à {args.host}:{args.port}?")
        logging.error(f"   ✓ L'utilisateur '{args.user}' existe-t-il avec les bonnes permissions?")
        logging.error(f"   ✓ La base de données '{args.db}' existe-t-elle?")
        return 1

if __name__ == '__main__':
    sys.exit(main())
