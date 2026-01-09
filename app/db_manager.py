#!/usr/bin/env python
"""
Database Manager - Gestion des bases de donnees SQLite et MySQL
Utilisation: python -m app.db_manager [commande]
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from config import config
from app.db_init import init_db, get_db_info, create_app_context
from flask_sqlalchemy import SQLAlchemy


def print_banner():
    """Affiche une bannière de bienvenue"""
    print("\n" + "="*70)
    print("  EPI Detection - Database Manager")
    print("="*70 + "\n")


def print_db_info():
    """Affiche les informations de la base de données actuelle"""
    info = get_db_info()
    print("Configuration actuelle:")
    print(f"  Type de BD: {info['type'].upper()}")
    print(f"  URI: {info['uri']}")
    if info['host']:
        print(f"  Host: {info['host']}")
        print(f"  Port: {info['port']}")
    print(f"  Database: {info['database']}\n")


def cmd_init(args):
    """Initialise la base de données"""
    print("Initialisation de la base de donnees...")
    try:
        app = create_app_context()
        init_db(app)
        print_db_info()
        print("[OK] Base de donnees initialisee avec succes!")
        return 0
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'initialisation: {e}")
        return 1


def cmd_info(args):
    """Affiche les informations de la base de données"""
    print_db_info()
    return 0


def cmd_status(args):
    """Verifie le statut de la base de données"""
    print("Verification du statut de la base de donnees...")
    print_db_info()
    
    try:
        if config.DB_TYPE == 'mysql':
            _check_mysql_connection()
        else:
            _check_sqlite_status()
        return 0
    except Exception as e:
        print(f"[ERROR] Erreur lors de la verification: {e}")
        return 1


def _check_sqlite_status():
    """Verifie le statut de SQLite"""
    if hasattr(config, 'DB_PATH'):
        if os.path.exists(config.DB_PATH):
            size = os.path.getsize(config.DB_PATH)
            print(f"[OK] Base de donnees SQLite existante")
            print(f"  Chemin: {config.DB_PATH}")
            print(f"  Taille: {size} octets")
        else:
            print("[WARN] Base de donnees SQLite non trouvee")
            print(f"  Chemin attendu: {config.DB_PATH}")
    else:
        print("[ERROR] Configuration SQLite invalide")


def _check_mysql_connection():
    """Verifie la connexion MySQL"""
    import mysql.connector
    from mysql.connector import Error
    
    print(f"Test de connexion a MySQL {config.DB_HOST}:{config.DB_PORT}...")
    try:
        connection = mysql.connector.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        if connection.is_connected():
            print("[OK] Connexion MySQL reussie")
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            db = cursor.fetchone()[0]
            print(f"  Base active: {db or 'aucune'}")
            cursor.close()
            connection.close()
    except Error as err:
        if err.errno == 2003:
            print(f"[ERROR] Impossible de se connecter a MySQL")
            print(f"  Serveur non accessible: {config.DB_HOST}:{config.DB_PORT}")
        elif err.errno == 1045:
            print(f"[ERROR] Authentification echouee")
            print(f"  Utilisateur: {config.DB_USER}")
        else:
            raise


def cmd_reset(args):
    """Remet la base de données à zéro"""
    print("WARNING: Cette action va supprimer toutes les donnees!")
    if not args.yes:
        response = input("Confirmer? (oui/non): ").strip().lower()
        if response not in ['oui', 'yes', 'o', 'y']:
            print("Annule.")
            return 1
    
    try:
        app = create_app_context()
        with app.app_context():
            from app.db_init import db
            print("Suppression de toutes les tables...")
            db.drop_all()
            print("[OK] Toutes les tables supprimees")
            
            print("Recreation des tables...")
            db.create_all()
            print("[OK] Tables recreees")
        print_db_info()
        return 0
    except Exception as e:
        print(f"[ERROR] Erreur lors de la reinitialisation: {e}")
        return 1


def cmd_backup(args):
    """Cree une sauvegarde de la base de données"""
    if config.DB_TYPE == 'mysql':
        print("[ERROR] Sauvegarde MySQL non implementee")
        print("Utilisez mysqldump pour sauvegarder votre base MySQL")
        return 1
    
    import shutil
    from datetime import datetime
    
    db_path = config.DB_PATH
    if not os.path.exists(db_path):
        print(f"[ERROR] Base de donnees non trouvee: {db_path}")
        return 1
    
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"epi_detection_{timestamp}.db")
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"[OK] Sauvegarde cree avec succes")
        print(f"  Chemin: {backup_path}")
        return 0
    except Exception as e:
        print(f"[ERROR] Erreur lors de la sauvegarde: {e}")
        return 1


def cmd_restore(args):
    """Restaure une base de données depuis une sauvegarde"""
    if config.DB_TYPE == 'mysql':
        print("[ERROR] Restauration MySQL non implementee")
        return 1
    
    if not args.backup_file:
        print("[ERROR] Specifiez le fichier de sauvegarde")
        return 1
    
    if not os.path.exists(args.backup_file):
        print(f"[ERROR] Fichier non trouve: {args.backup_file}")
        return 1
    
    import shutil
    db_path = config.DB_PATH
    
    print(f"Restauration depuis: {args.backup_file}")
    if not args.yes:
        response = input("Confirmer? (oui/non): ").strip().lower()
        if response not in ['oui', 'yes', 'o', 'y']:
            print("Annule.")
            return 1
    
    try:
        shutil.copy2(args.backup_file, db_path)
        print(f"[OK] Restauration reussie")
        print(f"  Base de donnees: {db_path}")
        return 0
    except Exception as e:
        print(f"[ERROR] Erreur lors de la restauration: {e}")
        return 1


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Gestionnaire de base de donnees pour EPI Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python -m app.db_manager init        Initialiser la base de donnees
  python -m app.db_manager status      Verifier le statut
  python -m app.db_manager backup      Creer une sauvegarde
  python -m app.db_manager reset --yes Reinitialiser sans confirmation
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    init_parser = subparsers.add_parser('init', help='Initialiser la base de donnees')
    init_parser.set_defaults(func=cmd_init)
    
    info_parser = subparsers.add_parser('info', help='Afficher les informations')
    info_parser.set_defaults(func=cmd_info)
    
    status_parser = subparsers.add_parser('status', help='Verifier le statut')
    status_parser.set_defaults(func=cmd_status)
    
    reset_parser = subparsers.add_parser('reset', help='Reinitialiser la base')
    reset_parser.add_argument('--yes', '-y', action='store_true', help='Confirmer sans demander')
    reset_parser.set_defaults(func=cmd_reset)
    
    backup_parser = subparsers.add_parser('backup', help='Creer une sauvegarde (SQLite)')
    backup_parser.set_defaults(func=cmd_backup)
    
    restore_parser = subparsers.add_parser('restore', help='Restaurer une sauvegarde (SQLite)')
    restore_parser.add_argument('backup_file', help='Chemin du fichier de sauvegarde')
    restore_parser.add_argument('--yes', '-y', action='store_true', help='Confirmer sans demander')
    restore_parser.set_defaults(func=cmd_restore)
    
    args = parser.parse_args()
    print_banner()
    
    if not args.command:
        parser.print_help()
        print("\nUtilisez 'python -m app.db_manager [commande] -h' pour plus d'aide")
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
