#!/usr/bin/env python3
"""
Database Manager - Basculer entre SQLite et MySQL facilement

Usage:
    python database_manager.py --status          # État actuel
    python database_manager.py --switch mysql    # Basculer vers MySQL
    python database_manager.py --switch sqlite   # Basculer vers SQLite
    python database_manager.py --export          # Exporter les données
    python database_manager.py --info            # Infos détaillées
"""

import os
import sys
import json
import argparse
import sqlite3
import mysql.connector
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

# Configuration
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / 'config.py'
ENV_FILE = PROJECT_ROOT / '.env'


class DatabaseManager:
    """Gestionnaire de base de données"""
    
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'sqlite').lower()
        self.config = self.load_config()
    
    def load_config(self):
        """Charger la configuration"""
        return {
            'current': self.db_type,
            'sqlite': {
                'path': os.getenv('SQLITE_DB_PATH', str(PROJECT_ROOT / 'instance/epi_detection.db')),
                'exists': False
            },
            'mysql': {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 3306)),
                'user': os.getenv('DB_USER', 'epi_user'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'epi_detection_db'),
                'connected': False
            }
        }
    
    def get_status(self):
        """Récupérer le statut des bases de données"""
        status = {
            'current_db': self.db_type.upper(),
            'timestamp': datetime.now().isoformat(),
            'sqlite': {},
            'mysql': {}
        }
        
        # SQLite
        sqlite_path = self.config['sqlite']['path']
        if Path(sqlite_path).exists():
            size = Path(sqlite_path).stat().st_size / (1024 * 1024)  # En MB
            try:
                conn = sqlite3.connect(sqlite_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                rows = {}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    rows[table] = cursor.fetchone()[0]
                
                conn.close()
                
                status['sqlite']['exists'] = True
                status['sqlite']['path'] = sqlite_path
                status['sqlite']['size_mb'] = round(size, 2)
                status['sqlite']['tables'] = len(tables)
                status['sqlite']['total_rows'] = sum(rows.values())
                status['sqlite']['details'] = rows
            except Exception as e:
                status['sqlite']['error'] = str(e)
        else:
            status['sqlite']['exists'] = False
        
        # MySQL
        try:
            conn = mysql.connector.connect(
                host=self.config['mysql']['host'],
                port=self.config['mysql']['port'],
                user=self.config['mysql']['user'],
                password=self.config['mysql']['password'] or None
            )
            cursor = conn.cursor()
            
            # Vérifier si la base existe
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            status['mysql']['exists'] = self.config['mysql']['database'] in databases
            
            if status['mysql']['exists']:
                cursor.execute(f"USE {self.config['mysql']['database']}")
                cursor.execute("""
                    SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = %s
                """, (self.config['mysql']['database'],))
                tables = [row[0] for row in cursor.fetchall()]
                
                rows = {}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    rows[table] = cursor.fetchone()[0]
                
                # Taille de la base
                cursor.execute("""
                    SELECT 
                        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = %s
                """, (self.config['mysql']['database'],))
                size = cursor.fetchone()[0] or 0
                
                status['mysql']['host'] = self.config['mysql']['host']
                status['mysql']['port'] = self.config['mysql']['port']
                status['mysql']['user'] = self.config['mysql']['user']
                status['mysql']['size_mb'] = size
                status['mysql']['tables'] = len(tables)
                status['mysql']['total_rows'] = sum(rows.values())
                status['mysql']['details'] = rows
            
            status['mysql']['connected'] = True
            cursor.close()
            conn.close()
        
        except Exception as e:
            status['mysql']['connected'] = False
            status['mysql']['error'] = str(e)
        
        return status
    
    def get_info(self):
        """Infos détaillées"""
        status = self.get_status()
        
        print("\n" + "="*70)
        print("📊 DATABASE MANAGER - STATE")
        print("="*70 + "\n")
        
        # Base actuelle
        print(f"🎯 Current Database: {status['current_db']}")
        print()
        
        # SQLite
        print("📁 SQLite:")
        if status['sqlite']['exists']:
            print(f"  ✓ Status: Active")
            print(f"  Path: {status['sqlite']['path']}")
            print(f"  Size: {status['sqlite']['size_mb']} MB")
            print(f"  Tables: {status['sqlite']['tables']}")
            print(f"  Total Rows: {status['sqlite']['total_rows']}")
            
            if status['sqlite']['details']:
                print("\n  Tables detail:")
                data = [[table, count] for table, count in status['sqlite']['details'].items()]
                print("  " + tabulate(data, headers=['Table', 'Rows'], tablefmt='simple'))
        else:
            print(f"  ✗ Status: Not found")
            print(f"  Path: {status['sqlite']['path']}")
        print()
        
        # MySQL
        print("🐬 MySQL:")
        if status['mysql']['connected']:
            if status['mysql']['exists']:
                print(f"  ✓ Status: Connected")
                print(f"  Host: {status['mysql']['host']}:{status['mysql']['port']}")
                print(f"  User: {status['mysql']['user']}")
                print(f"  Database: {self.config['mysql']['database']}")
                print(f"  Size: {status['mysql']['size_mb']} MB")
                print(f"  Tables: {status['mysql']['tables']}")
                print(f"  Total Rows: {status['mysql']['total_rows']}")
                
                if status['mysql']['details']:
                    print("\n  Tables detail:")
                    data = [[table, count] for table, count in status['mysql']['details'].items()]
                    print("  " + tabulate(data, headers=['Table', 'Rows'], tablefmt='simple'))
            else:
                print(f"  ⚠️  Status: Connected but database doesn't exist")
                print(f"  Host: {status['mysql']['host']}:{status['mysql']['port']}")
        else:
            print(f"  ✗ Status: Disconnected")
            if 'error' in status['mysql']:
                print(f"  Error: {status['mysql']['error']}")
        
        print("\n" + "="*70 + "\n")
        
        return status
    
    def compare_databases(self):
        """Comparer les deux bases"""
        status = self.get_status()
        
        print("\n" + "="*70)
        print("🔄 DATABASE COMPARISON")
        print("="*70 + "\n")
        
        if not status['sqlite']['exists']:
            print("❌ SQLite database not found")
            return
        
        if not status['mysql']['connected']:
            print("❌ MySQL not connected")
            return
        
        sqlite_tables = set(status['sqlite']['details'].keys())
        mysql_tables = set(status['mysql']['details'].keys())
        
        common = sqlite_tables & mysql_tables
        only_sqlite = sqlite_tables - mysql_tables
        only_mysql = mysql_tables - sqlite_tables
        
        print(f"Common tables: {len(common)}")
        if common:
            print("\n  Rows comparison:")
            data = []
            for table in sorted(common):
                sqlite_count = status['sqlite']['details'][table]
                mysql_count = status['mysql']['details'][table]
                match = "✓" if sqlite_count == mysql_count else "❌"
                data.append([table, sqlite_count, mysql_count, match])
            
            print(tabulate(data, headers=['Table', 'SQLite', 'MySQL', 'Match'], tablefmt='simple'))
        
        if only_sqlite:
            print(f"\n⚠️  Only in SQLite: {', '.join(only_sqlite)}")
        
        if only_mysql:
            print(f"\n⚠️  Only in MySQL: {', '.join(only_mysql)}")
        
        print("\n" + "="*70 + "\n")
    
    def check_health(self):
        """Vérifier la santé des bases"""
        print("\n" + "="*70)
        print("🏥 DATABASE HEALTH CHECK")
        print("="*70 + "\n")
        
        status = self.get_status()
        issues = []
        
        # SQLite checks
        if self.db_type == 'sqlite' and not status['sqlite']['exists']:
            issues.append("❌ Current DB is SQLite but file not found")
        
        # MySQL checks
        if self.db_type == 'mysql' and not status['mysql']['connected']:
            issues.append("❌ Current DB is MySQL but connection failed")
        elif self.db_type == 'mysql' and not status['mysql']['exists']:
            issues.append("❌ Current DB is MySQL but database doesn't exist")
        
        # Data consistency
        if status['sqlite']['exists'] and status['mysql']['exists']:
            sqlite_rows = status['sqlite']['total_rows']
            mysql_rows = status['mysql']['total_rows']
            if sqlite_rows != mysql_rows:
                issues.append(f"⚠️  Data mismatch: SQLite={sqlite_rows}, MySQL={mysql_rows}")
        
        if not issues:
            print("✅ All checks passed!\n")
        else:
            print("Found issues:\n")
            for issue in issues:
                print(f"  {issue}")
            print()
        
        print("="*70 + "\n")
        
        return len(issues) == 0
    
    def export_status(self, filename='db_status.json'):
        """Exporter le statut en JSON"""
        status = self.get_status()
        
        with open(filename, 'w') as f:
            json.dump(status, f, indent=2, default=str)
        
        print(f"✓ Status exported to {filename}")
    
    def print_status_simple(self):
        """Afficher un statut simple"""
        status = self.get_status()
        
        print(f"\n📊 Current Database: {status['current_db']}")
        
        if self.db_type == 'sqlite':
            if status['sqlite']['exists']:
                print(f"   ✓ SQLite: {status['sqlite']['size_mb']} MB, {status['sqlite']['total_rows']} rows")
            else:
                print(f"   ✗ SQLite: Not found")
        else:
            if status['mysql']['connected'] and status['mysql']['exists']:
                print(f"   ✓ MySQL: {status['mysql']['size_mb']} MB, {status['mysql']['total_rows']} rows")
            else:
                print(f"   ✗ MySQL: Disconnected or not found")
        
        print()


def main():
    parser = argparse.ArgumentParser(description='Database Manager')
    parser.add_argument('--status', action='store_true',
                       help='Afficher le statut')
    parser.add_argument('--info', action='store_true',
                       help='Infos détaillées')
    parser.add_argument('--compare', action='store_true',
                       help='Comparer SQLite et MySQL')
    parser.add_argument('--health', action='store_true',
                       help='Vérification de santé')
    parser.add_argument('--export', metavar='FILE',
                       help='Exporter le statut en JSON')
    
    args = parser.parse_args()
    
    manager = DatabaseManager()
    
    try:
        if args.status:
            manager.print_status_simple()
        elif args.info:
            manager.get_info()
        elif args.compare:
            manager.compare_databases()
        elif args.health:
            manager.check_health()
        elif args.export:
            manager.export_status(args.export)
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
