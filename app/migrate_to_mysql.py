#!/usr/bin/env python3
"""
Script de migration SQLite → MySQL
Permet d'exporter les données SQLite et les importer dans MySQL

Usage:
    python migrate_to_mysql.py --export-sql    # Exporte les données en SQL
    python migrate_to_mysql.py --migrate       # Migre directement vers MySQL
    python migrate_to_mysql.py --verify        # Vérifie la migration
"""

import os
import sys
import json
import argparse
import sqlite3
import mysql.connector
from datetime import datetime
from pathlib import Path

# Configuration
SQLITE_DB = os.getenv('SQLITE_DB_PATH', 'instance/epi_detection.db')
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'epi_user'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'epi_detection_db')
}

class SQLiteMigrator:
    """Classe pour migrer SQLite vers MySQL"""
    
    def __init__(self, sqlite_path=SQLITE_DB, mysql_config=MYSQL_CONFIG):
        self.sqlite_path = sqlite_path
        self.mysql_config = mysql_config.copy()
        self.stats = {
            'tables': {},
            'total_rows': 0,
            'start_time': None,
            'end_time': None
        }
    
    def connect_sqlite(self):
        """Connexion à SQLite"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"❌ Erreur connexion SQLite: {e}")
            sys.exit(1)
    
    def connect_mysql(self):
        """Connexion à MySQL"""
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            return conn
        except Exception as e:
            print(f"❌ Erreur connexion MySQL: {e}")
            sys.exit(1)
    
    def export_to_sql(self, output_file='epi_detection_backup.sql'):
        """Exporte les données SQLite en format SQL"""
        print(f"\n📤 Exportation des données SQLite vers {output_file}")
        
        sqlite_conn = self.connect_sqlite()
        cursor = sqlite_conn.cursor()
        
        # Récupérer les tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- EPI Detection - Export SQLite vers MySQL\n")
            f.write(f"-- Créé le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for table in tables:
                print(f"  📋 Table: {table}...", end=' ')
                
                # Récupérer les données
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                col_names = [description[0] for description in cursor.description]
                
                if not rows:
                    print("(vide)")
                    continue
                
                # Générer INSERT statements
                f.write(f"\n-- Données pour la table {table}\n")
                f.write(f"INSERT INTO {table} ({', '.join(col_names)}) VALUES\n")
                
                insert_values = []
                for row in rows:
                    values = []
                    for val in row:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, str):
                            # Échapper les caractères spéciaux
                            escaped = val.replace("'", "''")
                            values.append(f"'{escaped}'")
                        elif isinstance(val, bool):
                            values.append('1' if val else '0')
                        else:
                            values.append(str(val))
                    insert_values.append(f"({', '.join(values)})")
                
                f.write(',\n'.join(insert_values))
                f.write(';\n')
                
                self.stats['tables'][table] = len(rows)
                self.stats['total_rows'] += len(rows)
                print(f"✓ {len(rows)} lignes")
        
        sqlite_conn.close()
        print(f"\n✅ Export terminé: {output_file}")
        return output_file
    
    def migrate_to_mysql(self, confirm=True):
        """Migre les données de SQLite vers MySQL"""
        print(f"\n🔄 Migration SQLite → MySQL")
        print(f"   SQLite: {self.sqlite_path}")
        print(f"   MySQL: {self.mysql_config['user']}@{self.mysql_config['host']}")
        
        if confirm:
            response = input("\n⚠️  Cette action va copier les données. Continuer? (o/n): ")
            if response.lower() != 'o':
                print("❌ Migration annulée")
                return False
        
        self.stats['start_time'] = datetime.now()
        
        sqlite_conn = self.connect_sqlite()
        mysql_conn = self.connect_mysql()
        
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()
        
        try:
            # Récupérer les tables SQLite
            sqlite_cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in sqlite_cursor.fetchall()]
            
            for table in tables:
                print(f"\n  📋 Migration table: {table}...", end=' ')
                
                # Récupérer les données
                sqlite_cursor.execute(f"SELECT * FROM {table}")
                rows = sqlite_cursor.fetchall()
                col_names = [description[0] for description in sqlite_cursor.description]
                
                if not rows:
                    print("(vide)")
                    continue
                
                # Préparer l'INSERT
                placeholders = ', '.join(['%s'] * len(col_names))
                insert_sql = f"INSERT INTO {table} ({', '.join(col_names)}) VALUES ({placeholders})"
                
                # Convertir les données
                data = []
                for row in rows:
                    converted_row = []
                    for val in row:
                        if isinstance(val, bool):
                            converted_row.append(1 if val else 0)
                        else:
                            converted_row.append(val)
                    data.append(converted_row)
                
                # Exécuter l'insertion
                mysql_cursor.executemany(insert_sql, data)
                mysql_conn.commit()
                
                self.stats['tables'][table] = len(rows)
                self.stats['total_rows'] += len(rows)
                print(f"✓ {len(rows)} lignes")
            
        except Exception as e:
            print(f"\n❌ Erreur migration: {e}")
            mysql_conn.rollback()
            return False
        
        finally:
            mysql_cursor.close()
            mysql_conn.close()
            sqlite_conn.close()
        
        self.stats['end_time'] = datetime.now()
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        print(f"\n✅ Migration terminée en {duration:.2f}s")
        print(f"   Total: {self.stats['total_rows']} lignes")
        return True
    
    def verify_migration(self):
        """Vérifie que la migration s'est bien déroulée"""
        print(f"\n✔️  Vérification de la migration")
        
        sqlite_conn = self.connect_sqlite()
        mysql_conn = self.connect_mysql()
        
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()
        
        try:
            # Comparer les tables
            sqlite_cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            sqlite_tables = set([row[0] for row in sqlite_cursor.fetchall()])
            
            mysql_cursor.execute("""
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = %s
            """, (self.mysql_config['database'],))
            mysql_tables = set([row[0] for row in mysql_cursor.fetchall()])
            
            # Tables présentes dans les deux
            common_tables = sqlite_tables & mysql_tables
            only_sqlite = sqlite_tables - mysql_tables
            only_mysql = mysql_tables - sqlite_tables
            
            print(f"\n  📊 Tables communes: {len(common_tables)}")
            if only_sqlite:
                print(f"  ⚠️  Tables SQLite seulement: {only_sqlite}")
            if only_mysql:
                print(f"  ℹ️  Tables MySQL supplémentaires: {only_mysql}")
            
            # Comparer les lignes
            print(f"\n  📈 Nombre de lignes par table:")
            all_match = True
            for table in common_tables:
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                mysql_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                mysql_count = mysql_cursor.fetchone()[0]
                
                match = "✓" if sqlite_count == mysql_count else "❌"
                print(f"    {match} {table}: SQLite={sqlite_count}, MySQL={mysql_count}")
                
                if sqlite_count != mysql_count:
                    all_match = False
            
            if all_match:
                print(f"\n✅ Vérification réussie: tous les compte correspondent!")
            else:
                print(f"\n⚠️  Certains comptes ne correspondent pas")
            
            return all_match
        
        finally:
            mysql_cursor.close()
            mysql_conn.close()
            sqlite_conn.close()
    
    def print_stats(self):
        """Affiche les statistiques"""
        print("\n" + "="*60)
        print("📊 STATISTIQUES DE MIGRATION")
        print("="*60)
        print(f"Base SQLite: {self.sqlite_path}")
        print(f"Base MySQL: {self.mysql_config['user']}@{self.mysql_config['host']}")
        print(f"\nRésumé par table:")
        for table, count in self.stats['tables'].items():
            print(f"  • {table}: {count} lignes")
        print(f"\nTotal: {self.stats['total_rows']} lignes")
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            print(f"Durée: {duration:.2f}s")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Migrer SQLite vers MySQL')
    parser.add_argument('--export-sql', action='store_true', 
                       help='Exporter les données en fichier SQL')
    parser.add_argument('--migrate', action='store_true',
                       help='Migrer directement vers MySQL')
    parser.add_argument('--verify', action='store_true',
                       help='Vérifier la migration')
    parser.add_argument('--all', action='store_true',
                       help='Exporter, migrer et vérifier')
    parser.add_argument('--output', default='epi_detection_backup.sql',
                       help='Fichier de sortie SQL')
    parser.add_argument('--skip-confirm', action='store_true',
                       help='Ne pas demander confirmation')
    
    args = parser.parse_args()
    
    migrator = SQLiteMigrator()
    
    try:
        if args.export_sql or args.all:
            migrator.export_to_sql(args.output)
        
        if args.migrate or args.all:
            migrator.migrate_to_mysql(confirm=not args.skip_confirm)
        
        if args.verify or args.all:
            migrator.verify_migration()
        
        if args.export_sql or args.migrate or args.verify or args.all:
            migrator.print_stats()
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n❌ Migration interrompue")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
