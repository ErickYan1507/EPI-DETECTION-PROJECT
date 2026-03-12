#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour migrer les données de notifications de SQLite vers MySQL
Demande les infos de connexion MySQL de manière interactive
"""

import os
import sys
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

# Obtenir SQLite URI
sqlite_uri = config.DATABASE_URI
logging.info(f"✓ Base SQLite trouvée: {sqlite_uri}")

# Chercher config MySQL
mysql_uri = getattr(config, 'MYSQL_DATABASE_URI', None)

# Si pas de MySQL_DATABASE_URI, demander interactivement
if not mysql_uri:
    print("\n" + "="*60)
    print("📊 MIGRATION SQLite → MySQL")
    print("="*60)
    print("\n⚠️  Configuration MySQL non trouvée.")
    print("Veuillez entrer les informations de connexion MySQL:\n")
    
    db_host = input("🔹 Host MySQL [localhost]: ").strip() or "localhost"
    db_port = input("🔹 Port MySQL [3306]: ").strip() or "3306"
    db_user = input("🔹 Utilisateur MySQL [epi_user]: ").strip() or "epi_user"
    db_password = input("🔹 Mot de passe MySQL: ").strip()
    db_name = input("🔹 Nom base de données [epi_detection_db]: ").strip() or "epi_detection_db"
    
    # Construire l'URI MySQL
    db_password_encoded = quote_plus(db_password) if db_password else ""
    if db_password_encoded:
        mysql_uri = f'mysql+pymysql://{db_user}:{db_password_encoded}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
    else:
        mysql_uri = f'mysql+pymysql://{db_user}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
    
    logging.info(f"\n✓ URI MySQL construit: {mysql_uri.replace(db_password_encoded or '', '***')}\n")

sqlite_eng = create_engine(sqlite_uri, future=True)
mysql_eng = create_engine(mysql_uri, future=True)

try:
    logging.info("📌 Création des tables dans MySQL...")
    db.metadata.create_all(mysql_eng)
    logging.info("✓ Tables créées dans MySQL (si manquantes)")
    
    SqliteSession = sessionmaker(bind=sqlite_eng)
    MysqlSession = sessionmaker(bind=mysql_eng)
    
    sqlite_s = SqliteSession()
    mysql_s = MysqlSession()
    
    models = [NotificationRecipient, NotificationHistory, NotificationConfig, ReportSchedule]
    total_pushed = 0
    
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
    
    print("\n" + "="*60)
    print(f"✅ MIGRATION RÉUSSIE")
    print(f"   Total lignes importées: {total_pushed}")
    print("="*60 + "\n")
    logging.info("✓ Migration terminée avec succès!")
    
except Exception as e:
    logging.error(f"❌ Erreur lors de la migration: {e}")
    logging.error("   Vérifiez:")
    logging.error("   - Les informations de connexion MySQL")
    logging.error("   - Que le serveur MySQL est en cours d'exécution")
    logging.error("   - Que l'utilisateur MySQL a les permissions")
    sys.exit(1)

