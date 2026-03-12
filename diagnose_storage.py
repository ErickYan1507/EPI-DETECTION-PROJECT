#!/usr/bin/env python3
"""Diagnostic du stockage des données"""

import sqlite3
from pathlib import Path
import json

db_path = Path('database/notifications.db')
config_path = Path('.notification_config.json')

print("\n" + "="*60)
print("🔍 DIAGNOSTIC STOCKAGE DES DONNÉES")
print("="*60 + "\n")

# 1. Vérifier SQLite
print("1️⃣  BASE DE DONNÉES SQLITE")
print(f"   Chemin: {db_path}")
print(f"   Existe: {'✅ OUI' if db_path.exists() else '❌ NON'}")

if db_path.exists():
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   Tables créées: {len(tables)} - {tables}")
        
        # Recipients
        try:
            cursor.execute("SELECT COUNT(*) FROM recipients")
            count = cursor.fetchone()[0]
            print(f"   📧 Recipients: {count}")
            if count > 0:
                cursor.execute("SELECT email FROM recipients")
                for row in cursor.fetchall():
                    print(f"      - {row[0]}")
        except Exception as e:
            print(f"   ❌ Erreur recipients: {e}")
        
        # Email config
        try:
            cursor.execute("SELECT sender_email FROM email_config")
            result = cursor.fetchone()
            if result:
                print(f"   📧 Config email: {result[0]}")
            else:
                print(f"   📧 Config email: Aucune")
        except Exception as e:
            print(f"   ❌ Erreur config: {e}")
        
        # Historique
        try:
            cursor.execute("SELECT COUNT(*) FROM notification_history")
            count = cursor.fetchone()[0]
            print(f"   📝 Historique: {count} enregistrements")
        except Exception as e:
            print(f"   ❌ Erreur historique: {e}")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

# 2. Vérifier fichier config
print(f"\n2️⃣  FICHIER CONFIGURATION")
print(f"   Chemin: {config_path}")
print(f"   Existe: {'✅ OUI' if config_path.exists() else '❌ NON'}")

if config_path.exists():
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            print(f"   📧 Email: {config.get('sender_email', 'N/A')}")
            print(f"   🔒 Password: {'***' if config.get('sender_password') else 'N/A'}")
            print(f"   ⏰ Daily enabled: {config.get('daily_enabled', False)}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

print("\n" + "="*60 + "\n")
