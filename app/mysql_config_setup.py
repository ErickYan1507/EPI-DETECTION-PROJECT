#!/usr/bin/env python3
"""
Configuration MySQL pour EPI Detection
Aide à configurer la connexion MySQL avec les bonnes variables d'environnement

Usage:
    python mysql_config_setup.py --interactive  # Configuration interactive
    python mysql_config_setup.py --verify       # Vérifier la connexion
    python mysql_config_setup.py --create-env   # Créer fichier .env
"""

import os
import sys
import argparse
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv, dotenv_values


class MySQLConfigSetup:
    """Classe pour configurer MySQL"""
    
    def __init__(self):
        self.config = {
            'DB_TYPE': 'mysql',
            'DB_HOST': 'localhost',
            'DB_PORT': 3306,
            'DB_USER': 'epi_user',
            'DB_PASSWORD': '',
            'DB_NAME': 'epi_detection_db'
        }
    
    def test_connection(self, config=None):
        """Teste la connexion MySQL"""
        if config is None:
            config = self.config
        
        try:
            conn = mysql.connector.connect(
                host=config['DB_HOST'],
                port=config['DB_PORT'],
                user=config['DB_USER'],
                password=config['DB_PASSWORD'] or None,
                database=config['DB_NAME']
            )
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return True, version
        except Exception as e:
            return False, str(e)
    
    def test_base_exists(self, config=None):
        """Teste si la base de données existe"""
        if config is None:
            config = self.config
        
        try:
            conn = mysql.connector.connect(
                host=config['DB_HOST'],
                port=config['DB_PORT'],
                user=config['DB_USER'],
                password=config['DB_PASSWORD'] or None
            )
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            return config['DB_NAME'] in databases
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def create_database(self, config=None):
        """Crée la base de données"""
        if config is None:
            config = self.config
        
        try:
            conn = mysql.connector.connect(
                host=config['DB_HOST'],
                port=config['DB_PORT'],
                user=config['DB_USER'],
                password=config['DB_PASSWORD'] or None
            )
            cursor = conn.cursor()
            
            # Créer la base de données
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {config['DB_NAME']}
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
            """)
            
            # Sélectionner la base
            cursor.execute(f"USE {config['DB_NAME']}")
            
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Erreur création base: {e}")
            return False
    
    def create_user(self, config=None):
        """Crée l'utilisateur MySQL"""
        if config is None:
            config = self.config
        
        try:
            # Se connecter en tant qu'admin (root)
            root_password = input("Mot de passe MySQL root: ") or None
            conn = mysql.connector.connect(
                host=config['DB_HOST'],
                port=config['DB_PORT'],
                user='root',
                password=root_password
            )
            cursor = conn.cursor()
            
            # Créer l'utilisateur
            cursor.execute(f"""
                CREATE USER IF NOT EXISTS '{config['DB_USER']}'@'{config['DB_HOST']}'
                IDENTIFIED BY '{config['DB_PASSWORD']}'
            """)
            
            # Donner les permissions
            cursor.execute(f"""
                GRANT ALL PRIVILEGES ON {config['DB_NAME']}.* 
                TO '{config['DB_USER']}'@'{config['DB_HOST']}'
            """)
            
            cursor.execute("FLUSH PRIVILEGES")
            
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Erreur création utilisateur: {e}")
            return False
    
    def import_schema(self, schema_file, config=None):
        """Importe le schéma SQL"""
        if config is None:
            config = self.config
        
        try:
            conn = mysql.connector.connect(
                host=config['DB_HOST'],
                port=config['DB_PORT'],
                user=config['DB_USER'],
                password=config['DB_PASSWORD'] or None,
                database=config['DB_NAME']
            )
            cursor = conn.cursor()
            
            # Lire et exécuter le fichier SQL
            with open(schema_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Diviser par les points-virgules et exécuter
            statements = sql_content.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Erreur import schéma: {e}")
            return False
    
    def interactive_setup(self):
        """Configuration interactive"""
        print("\n" + "="*60)
        print("⚙️  CONFIGURATION MYSQL - EPI DETECTION")
        print("="*60 + "\n")
        
        self.config['DB_HOST'] = input(f"Hôte MySQL [{self.config['DB_HOST']}]: ") or self.config['DB_HOST']
        self.config['DB_PORT'] = int(input(f"Port [{self.config['DB_PORT']}]: ") or self.config['DB_PORT'])
        self.config['DB_USER'] = input(f"Utilisateur [{self.config['DB_USER']}]: ") or self.config['DB_USER']
        self.config['DB_PASSWORD'] = input(f"Mot de passe: ") or ''
        self.config['DB_NAME'] = input(f"Base de données [{self.config['DB_NAME']}]: ") or self.config['DB_NAME']
        
        print(f"\n🔍 Configuration:")
        print(f"  Host: {self.config['DB_HOST']}")
        print(f"  Port: {self.config['DB_PORT']}")
        print(f"  User: {self.config['DB_USER']}")
        print(f"  Database: {self.config['DB_NAME']}")
        
        return self.config
    
    def verify_setup(self):
        """Vérifie la configuration"""
        print("\n" + "="*60)
        print("✔️  VÉRIFICATION SETUP")
        print("="*60 + "\n")
        
        # Test connexion
        print("🔗 Test de connexion MySQL...", end=' ')
        success, result = self.test_connection()
        if success:
            print(f"✓ OK (Version: {result})")
        else:
            print(f"❌ Échec: {result}")
            return False
        
        # Test base de données
        print(f"📦 Test base de données '{self.config['DB_NAME']}'...", end=' ')
        if self.test_base_exists():
            print("✓ Existe")
        else:
            print("❌ N'existe pas")
            response = input("Créer la base de données? (o/n): ")
            if response.lower() == 'o':
                if self.create_database():
                    print("  ✓ Base de données créée")
                else:
                    return False
            else:
                return False
        
        # Test schéma
        print(f"📋 Vérification schéma...", end=' ')
        try:
            conn = mysql.connector.connect(
                host=self.config['DB_HOST'],
                port=self.config['DB_PORT'],
                user=self.config['DB_USER'],
                password=self.config['DB_PASSWORD'] or None,
                database=self.config['DB_NAME']
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = %s
            """, (self.config['DB_NAME'],))
            tables = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if tables:
                print(f"✓ {len(tables)} tables trouvées")
            else:
                print("⚠️  Aucune table trouvée")
                schema_file = 'database/epi_detection_mysql_schema.sql'
                if Path(schema_file).exists():
                    response = input(f"Importer le schéma depuis {schema_file}? (o/n): ")
                    if response.lower() == 'o':
                        if self.import_schema(schema_file):
                            print("  ✓ Schéma importé")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
        
        print("\n✅ Configuration vérifiée avec succès!\n")
        return True
    
    def create_env_file(self, filename='.env'):
        """Crée un fichier .env"""
        print(f"\n💾 Création {filename}...")
        
        content = f"""# EPI Detection - Configuration MySQL
DB_TYPE=mysql
DB_HOST={self.config['DB_HOST']}
DB_PORT={self.config['DB_PORT']}
DB_USER={self.config['DB_USER']}
DB_PASSWORD={self.config['DB_PASSWORD']}
DB_NAME={self.config['DB_NAME']}

# Options SQLAlchemy
SQLALCHEMY_ECHO=False
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Autres configurations
FLASK_ENV=production
DEBUG=False
"""
        
        try:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✓ Fichier {filename} créé")
            return True
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def print_config(self):
        """Affiche la configuration"""
        print("\n" + "="*60)
        print("📋 CONFIGURATION MYSQL")
        print("="*60)
        print(f"Base de données: {self.config['DB_NAME']}")
        print(f"Hôte: {self.config['DB_HOST']}")
        print(f"Port: {self.config['DB_PORT']}")
        print(f"Utilisateur: {self.config['DB_USER']}")
        print(f"Type: {self.config['DB_TYPE']}")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Configuration MySQL pour EPI Detection')
    parser.add_argument('--interactive', action='store_true',
                       help='Configuration interactive')
    parser.add_argument('--verify', action='store_true',
                       help='Vérifier la configuration')
    parser.add_argument('--create-env', action='store_true',
                       help='Créer fichier .env')
    parser.add_argument('--import-schema', metavar='FILE',
                       help='Importer le schéma SQL')
    parser.add_argument('--all', action='store_true',
                       help='Configuration complète (interactive + verify + env)')
    
    args = parser.parse_args()
    
    setup = MySQLConfigSetup()
    
    try:
        if args.interactive or args.all:
            setup.interactive_setup()
        
        if args.verify or args.all:
            if not setup.verify_setup():
                sys.exit(1)
        
        if args.create_env or args.all:
            setup.create_env_file()
        
        if args.import_schema:
            if setup.import_schema(args.import_schema):
                print("✅ Schéma importé avec succès")
        
        setup.print_config()
    
    except KeyboardInterrupt:
        print("\n\n❌ Configuration interrompue")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
