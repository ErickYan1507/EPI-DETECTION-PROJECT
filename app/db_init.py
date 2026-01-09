import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from config import config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()


def create_app_context():
    """Crée un contexte Flask pour l'initialisation de la base de données"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


def init_db(app=None):
    """
    Initialise la base de données avec les tables.
    Supporte SQLite et MySQL.
    """
    if app is None:
        app = create_app_context()
    
    with app.app_context():
        print(f"Initialisation de la base de données...")
        print(f"Type de base de données: {config.DB_TYPE}")
        print(f"URI: {config.DATABASE_URI}")
        
        if config.DB_TYPE == 'mysql':
            _init_mysql_db()
        else:
            _init_sqlite_db()
        
        db.create_all()
        print("[OK] Base de donnees initialisee avec succes!")


def _init_sqlite_db():
    """Initialise la base SQLite en créant le répertoire si nécessaire"""
    db_path = config.DB_PATH
    db_dir = os.path.dirname(db_path)
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"[OK] Repertoire cree: {db_dir}")


def _init_mysql_db():
    """
    Initialise MySQL en créant la base de données si elle n'existe pas.
    """
    import mysql.connector
    from mysql.connector import Error
    
    try:
        connection = mysql.connector.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            charset='utf8mb4'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            create_db_query = f"""
            CREATE DATABASE IF NOT EXISTS {config.DB_NAME}
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
            """
            cursor.execute(create_db_query)
            connection.commit()
            print(f"[OK] Base de donnees MySQL '{config.DB_NAME}' prete")
            
            cursor.close()
            connection.close()
    
    except Error as err:
        if err.errno == 2003:
            print(f"[ERROR] Impossible de se connecter a MySQL sur {config.DB_HOST}:{config.DB_PORT}")
            print("  Assurez-vous que MySQL est en cours d'execution et accessible.")
        elif err.errno == 1045:
            print(f"[ERROR] Identifiants MySQL invalides pour l'utilisateur '{config.DB_USER}'")
        else:
            print(f"[ERROR] MySQL: {err}")
        raise


def get_db_info():
    """Retourne les informations de la base de données actuelle"""
    return {
        'type': config.DB_TYPE,
        'uri': config.DATABASE_URI,
        'host': getattr(config, 'DB_HOST', None) if config.DB_TYPE == 'mysql' else None,
        'port': getattr(config, 'DB_PORT', None) if config.DB_TYPE == 'mysql' else None,
        'database': getattr(config, 'DB_NAME', None) if config.DB_TYPE == 'mysql' else os.path.basename(config.DB_PATH)
    }


if __name__ == '__main__':
    init_db()
    info = get_db_info()
    print("\n--- Informations de la base de données ---")
    for key, value in info.items():
        if value:
            print(f"{key}: {value}")
