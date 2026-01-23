#!/usr/bin/env python3
"""
Dual Database Configuration - SQLite + MySQL en parallèle
SQLite: Cache local + développement
MySQL: Stockage central + production

Usage:
    from app.dual_database import DualDB
    dual_db = DualDB(app)
    dual_db.sync_all()  # Synchroniser SQLite → MySQL
"""

import os
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

# Configuration des deux bases
SQLITE_DB_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'instance', 'epi_detection.db'
)

MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'epi_user'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'epi_detection_db')
}

# Activer le dual-database par défaut
DUAL_DATABASE_ENABLED = os.getenv('DUAL_DATABASE', 'true').lower() == 'true'

# Mode de synchronisation:
# 'sqlite_primary': Les données vont d'abord dans SQLite, puis sync vers MySQL
# 'mysql_primary': Les données vont d'abord dans MySQL, puis sync vers SQLite
# 'both': Les deux en même temps (plus lent mais garantit la cohérence)
SYNC_MODE = os.getenv('SYNC_MODE', 'sqlite_primary').lower()


class DualDatabase:
    """Gestionnaire de base de données double (SQLite + MySQL)"""
    
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.sqlite_engine = None
        self.mysql_engine = None
        self.sync_stats = {
            'last_sync': None,
            'synced_tables': {},
            'errors': []
        }
    
    def init_app(self, app, db):
        """Initialiser avec une app Flask et SQLAlchemy"""
        self.app = app
        self.db = db
        
        # Créer les engines
        self._create_engines()
    
    def _create_engines(self):
        """Créer les moteurs de base de données"""
        # SQLite
        self.sqlite_engine = create_engine(
            f'sqlite:///{SQLITE_DB_PATH}',
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=os.getenv('SQLALCHEMY_ECHO', 'false').lower() == 'true'
        )
        
        # MySQL
        if MYSQL_CONFIG['password']:
            mysql_uri = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
        else:
            mysql_uri = f"mysql+pymysql://{MYSQL_CONFIG['user']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
        
        self.mysql_engine = create_engine(
            mysql_uri,
            pool_size=10,
            pool_recycle=3600,
            echo=os.getenv('SQLALCHEMY_ECHO', 'false').lower() == 'true'
        )
    
    def check_connectivity(self):
        """Vérifier la connectivité des deux bases"""
        status = {
            'sqlite': {'available': False, 'error': None},
            'mysql': {'available': False, 'error': None}
        }
        
        # SQLite
        try:
            with self.sqlite_engine.connect() as conn:
                conn.execute('SELECT 1')
            status['sqlite']['available'] = True
        except Exception as e:
            status['sqlite']['error'] = str(e)
        
        # MySQL
        try:
            with self.mysql_engine.connect() as conn:
                conn.execute('SELECT 1')
            status['mysql']['available'] = True
        except Exception as e:
            status['mysql']['error'] = str(e)
        
        return status
    
    def get_table_names(self, engine):
        """Récupérer les noms des tables"""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        return inspector.get_table_names()
    
    def sync_table_sqlite_to_mysql(self, table_name, batch_size=1000):
        """Synchroniser une table de SQLite vers MySQL"""
        try:
            from sqlalchemy import MetaData, Table, select
            
            # Lire les données de SQLite
            sqlite_metadata = MetaData()
            sqlite_table = Table(table_name, sqlite_metadata, autoload_with=self.sqlite_engine)
            
            with self.sqlite_engine.connect() as sqlite_conn:
                sqlite_data = sqlite_conn.execute(select(sqlite_table)).fetchall()
            
            if not sqlite_data:
                self.sync_stats['synced_tables'][table_name] = {'status': 'empty', 'rows': 0}
                return
            
            # Préparer les données pour MySQL
            mysql_metadata = MetaData()
            mysql_table = Table(table_name, mysql_metadata, autoload_with=self.mysql_engine)
            
            # Insérer par batch
            rows_synced = 0
            with self.mysql_engine.begin() as mysql_conn:
                # Effacer les anciennes données
                mysql_conn.execute(mysql_table.delete())
                
                # Insérer les nouvelles
                for i in range(0, len(sqlite_data), batch_size):
                    batch = sqlite_data[i:i+batch_size]
                    values_list = []
                    for row in batch:
                        values_list.append(dict(row._mapping))
                    
                    if values_list:
                        mysql_conn.execute(mysql_table.insert(), values_list)
                    rows_synced += len(batch)
            
            self.sync_stats['synced_tables'][table_name] = {
                'status': 'synced',
                'rows': rows_synced
            }
            return rows_synced
        
        except Exception as e:
            self.sync_stats['synced_tables'][table_name] = {
                'status': 'error',
                'error': str(e)
            }
            self.sync_stats['errors'].append(f"{table_name}: {str(e)}")
    
    def sync_table_mysql_to_sqlite(self, table_name, batch_size=1000):
        """Synchroniser une table de MySQL vers SQLite"""
        try:
            from sqlalchemy import MetaData, Table, select
            
            # Lire les données de MySQL
            mysql_metadata = MetaData()
            mysql_table = Table(table_name, mysql_metadata, autoload_with=self.mysql_engine)
            
            with self.mysql_engine.connect() as mysql_conn:
                mysql_data = mysql_conn.execute(select(mysql_table)).fetchall()
            
            if not mysql_data:
                self.sync_stats['synced_tables'][table_name] = {'status': 'empty', 'rows': 0}
                return
            
            # Préparer les données pour SQLite
            sqlite_metadata = MetaData()
            sqlite_table = Table(table_name, sqlite_metadata, autoload_with=self.sqlite_engine)
            
            # Insérer par batch
            rows_synced = 0
            with self.sqlite_engine.begin() as sqlite_conn:
                # Effacer les anciennes données
                sqlite_conn.execute(sqlite_table.delete())
                
                # Insérer les nouvelles
                for i in range(0, len(mysql_data), batch_size):
                    batch = mysql_data[i:i+batch_size]
                    values_list = []
                    for row in batch:
                        values_list.append(dict(row._mapping))
                    
                    if values_list:
                        sqlite_conn.execute(sqlite_table.insert(), values_list)
                    rows_synced += len(batch)
            
            self.sync_stats['synced_tables'][table_name] = {
                'status': 'synced',
                'rows': rows_synced
            }
            return rows_synced
        
        except Exception as e:
            self.sync_stats['synced_tables'][table_name] = {
                'status': 'error',
                'error': str(e)
            }
            self.sync_stats['errors'].append(f"{table_name}: {str(e)}")
    
    def sync_all(self, direction='sqlite_to_mysql'):
        """Synchroniser toutes les tables"""
        connectivity = self.check_connectivity()
        
        if not connectivity['sqlite']['available']:
            raise Exception(f"SQLite not available: {connectivity['sqlite']['error']}")
        
        if not connectivity['mysql']['available']:
            raise Exception(f"MySQL not available: {connectivity['mysql']['error']}")
        
        print("\n" + "="*60)
        print(f"🔄 SYNCHRONIZATION: {direction.upper()}")
        print("="*60 + "\n")
        
        # Récupérer les tables
        if direction == 'sqlite_to_mysql':
            tables = self.get_table_names(self.sqlite_engine)
            sync_func = self.sync_table_sqlite_to_mysql
        else:
            tables = self.get_table_names(self.mysql_engine)
            sync_func = self.sync_table_mysql_to_sqlite
        
        # Synchroniser chaque table
        total_rows = 0
        for table in tables:
            if table.startswith('sqlite_'):
                continue
            
            print(f"  📋 {table}...", end=' ')
            rows = sync_func(table)
            if rows is not None:
                total_rows += rows
                print(f"✓ ({rows} rows)")
            else:
                print("✓ (0 rows)")
        
        self.sync_stats['last_sync'] = datetime.now()
        
        print(f"\n✅ Sync completed: {total_rows} rows synced")
        print("="*60 + "\n")
    
    def get_stats(self):
        """Obtenir les statistiques de synchronisation"""
        return {
            'connectivity': self.check_connectivity(),
            'last_sync': self.sync_stats['last_sync'],
            'synced_tables': self.sync_stats['synced_tables'],
            'errors': self.sync_stats['errors']
        }


# Instance globale
dual_db = DualDatabase()


def create_dual_database_app(app, db):
    """Factory pour créer et initialiser le dual-database"""
    global dual_db
    dual_db.init_app(app, db)
    return dual_db


# Decorateur pour enregistrer les listeners
def setup_dual_database_sync(app, db):
    """Configurer la synchronisation automatique"""
    if not DUAL_DATABASE_ENABLED:
        return
    
    from sqlalchemy import event
    
    # Après chaque commit, synchroniser
    @event.listens_for(db.session, 'after_commit')
    def after_commit():
        if SYNC_MODE == 'sqlite_primary':
            # SQLite write → MySQL sync
            try:
                dual_db.sync_all('sqlite_to_mysql')
            except Exception as e:
                app.logger.warning(f"Sync SQLite→MySQL failed: {e}")
        elif SYNC_MODE == 'mysql_primary':
            # MySQL write → SQLite sync
            try:
                dual_db.sync_all('mysql_to_sqlite')
            except Exception as e:
                app.logger.warning(f"Sync MySQL→SQLite failed: {e}")
