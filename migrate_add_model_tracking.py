"""
Script de migration pour ajouter les colonnes de traçabilité multi-modèles
à la table Detection
"""
import sys
from pathlib import Path
import sqlite3
from datetime import datetime

# Ajouter le répertoire parent au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from config import config
from app.logger import logger

def migrate_sqlite():
    """Migration pour SQLite"""
    db_path = Path(config.BASE_DIR) / 'database' / 'epi_detection.db'
    
    if not db_path.exists():
        logger.error(f"Base de données SQLite non trouvée: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Vérifier si les colonnes existent déjà
        cursor.execute("PRAGMA table_info(detection)")
        columns = [col[1] for col in cursor.fetchall()]
        
        migrations_needed = []
        
        if 'model_used' not in columns:
            migrations_needed.append(
                "ALTER TABLE detection ADD COLUMN model_used VARCHAR(255) DEFAULT 'best.pt'"
            )
        
        if 'ensemble_mode' not in columns:
            migrations_needed.append(
                "ALTER TABLE detection ADD COLUMN ensemble_mode BOOLEAN DEFAULT 0"
            )
        
        if 'model_votes' not in columns:
            migrations_needed.append(
                "ALTER TABLE detection ADD COLUMN model_votes TEXT"
            )
        
        if 'aggregation_method' not in columns:
            migrations_needed.append(
                "ALTER TABLE detection ADD COLUMN aggregation_method VARCHAR(50)"
            )
        
        if not migrations_needed:
            logger.info("✓ Toutes les colonnes de traçabilité existent déjà")
            conn.close()
            return True
        
        # Exécuter les migrations
        logger.info(f"Exécution de {len(migrations_needed)} migrations...")
        for migration in migrations_needed:
            logger.info(f"  - {migration}")
            cursor.execute(migration)
        
        conn.commit()
        conn.close()
        
        logger.info("✓ Migration SQLite terminée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur migration SQLite: {e}")
        return False

def migrate_mysql():
    """Migration pour MySQL"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        
        cursor = connection.cursor()
        
        # Vérifier les colonnes existantes
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'detection'
        """, (config.DB_NAME,))
        
        columns = [row[0] for row in cursor.fetchall()]
        
        migrations_needed = []
        
        if 'model_used' not in columns:
            migrations_needed.append(
                "ALTER TABLE detection ADD COLUMN model_used VARCHAR(255) DEFAULT 'best.pt'"
            )
        
        if 'ensemble_mode' not in columns:
            migrations_needed.append(
                "ALTER TABLE detection ADD COLUMN ensemble_mode BOOLEAN DEFAULT FALSE"
            )
        
        if 'model_votes' not in columns:
            migrations_needed.append(
                "ALTER TABLE detection ADD COLUMN model_votes TEXT"
            )
        
        if 'aggregation_method' not in columns:
            migrations_needed.append(
                "ALTER TABLE detection ADD COLUMN aggregation_method VARCHAR(50)"
            )
        
        if not migrations_needed:
            logger.info("✓ Toutes les colonnes de traçabilité existent déjà")
            connection.close()
            return True
        
        # Exécuter les migrations
        logger.info(f"Exécution de {len(migrations_needed)} migrations...")
        for migration in migrations_needed:
            logger.info(f"  - {migration}")
            cursor.execute(migration)
        
        connection.commit()
        connection.close()
        
        logger.info("✓ Migration MySQL terminée avec succès")
        return True
        
    except ImportError:
        logger.error("pymysql non installé. Exécutez: pip install pymysql")
        return False
    except Exception as e:
        logger.error(f"Erreur migration MySQL: {e}")
        return False

def main():
    """Point d'entrée principal"""
    logger.info("=" * 60)
    logger.info("Migration: Ajout colonnes traçabilité multi-modèles")
    logger.info("=" * 60)
    
    if config.DB_TYPE == 'mysql':
        logger.info("Type de BD: MySQL")
        success = migrate_mysql()
    else:
        logger.info("Type de BD: SQLite")
        success = migrate_sqlite()
    
    if success:
        logger.info("\n✓ Migration réussie!")
        logger.info("\nNouvelles colonnes ajoutées:")
        logger.info("  - model_used: Modèle(s) utilisé(s) pour la détection")
        logger.info("  - ensemble_mode: Mode ensemble activé (True/False)")
        logger.info("  - model_votes: Votes JSON des différents modèles")
        logger.info("  - aggregation_method: Méthode d'agrégation utilisée")
    else:
        logger.error("\n✗ Migration échouée")
        sys.exit(1)

if __name__ == '__main__':
    main()