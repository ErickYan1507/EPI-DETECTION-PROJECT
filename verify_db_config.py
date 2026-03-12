#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification que la configuration MySQL est correcte
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import config
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("\n" + "="*60)
print("✓ VÉRIFICATION CONFIGURATION BASE DE DONNÉES")
print("="*60 + "\n")

# Check DB_TYPE
db_type = config.DB_TYPE if hasattr(config, 'DB_TYPE') else 'sqlite'
print(f"📊 Type de base de données: {db_type.upper()}")

# Check DATABASE_URI
print(f"📍 DATABASE_URI: {config.DATABASE_URI[:50]}...")

# Test connection
try:
    engine = create_engine(config.DATABASE_URI, future=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Connexion réussie!")
        
        # Get database name
        if 'mysql' in config.DATABASE_URI.lower():
            result = conn.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"   Base de données: {db_name}")
            
            # Count tables
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE()
            """))
            table_count = result.fetchone()[0]
            print(f"   Tables: {table_count}")
            
            # List notification tables
            result = conn.execute(text("""
                SELECT TABLE_NAME FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME LIKE 'notification%' OR TABLE_NAME = 'report_schedule'
            """))
            notif_tables = [row[0] for row in result.fetchall()]
            if notif_tables:
                print(f"   Tables de notifications: {', '.join(notif_tables)}")
                for table in notif_tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"     - {table}: {count} lignes")
        else:
            print("   Type: SQLite")
    
except Exception as e:
    print(f"❌ Erreur connexion: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ Configuration valide!")
print("="*60 + "\n")
