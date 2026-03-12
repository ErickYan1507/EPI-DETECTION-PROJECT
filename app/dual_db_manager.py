#!/usr/bin/env python3
"""
Dual Database Manager - Unified interface for SQLite + MySQL with real-time sync

Provides:
- Dual database connections (SQLite + MySQL)
- Transparent model access
- Real-time bidirectional synchronization
- Fallback handling (if MySQL fails, app continues with SQLite)

Usage:
    from app.dual_db_manager import create_dual_db_app
    app = create_dual_db_app(app)
    
    # Now use db and models as usual - they auto-sync!
    detection = Detection(...)
    db.session.add(detection)
    db.session.commit()  # Automatically synced to both SQLite and MySQL
"""

import os
import logging
from typing import Optional, Type
from flask import Flask
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from urllib.parse import quote_plus

from app.realtime_sync import RealtimeSyncManager, init_realtime_sync, register_sync_for_models

logger = logging.getLogger(__name__)


class DualDatabaseManager:
    """Manages dual SQLite + MySQL database setup with real-time sync"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.sqlite_db = None
        self.mysql_db = None
        self.sync_manager: Optional[RealtimeSyncManager] = None
        self.primary_db = None
        self.dual_enabled = True
        
    def init_app(self, app: Flask, db_sqlite, db_mysql):
        """
        Initialize dual database with Flask app
        
        Args:
            app: Flask application
            db_sqlite: Flask-SQLAlchemy instance for SQLite
            db_mysql: Flask-SQLAlchemy instance for MySQL
        """
        self.app = app
        self.sqlite_db = db_sqlite
        self.mysql_db = db_mysql
        
        # Determine primary database from config
        db_type = os.getenv('DB_TYPE', 'sqlite').lower()
        self.primary_db = self.mysql_db if db_type == 'mysql' else self.sqlite_db
        
        logger.info(f"Primary DB: {db_type}")
        
        # Initialize sync manager
        sync_enabled = os.getenv('REALTIME_SYNC', 'true').lower() == 'true'
        if sync_enabled:
            self.sync_manager = init_realtime_sync(
                self.sqlite_db, 
                self.mysql_db, 
                app
            )
            logger.info("✓ Realtime sync manager initialized")
        else:
            logger.info("⊘ Realtime sync disabled (REALTIME_SYNC=false)")
    
    def register_models_for_sync(self, *models):
        """Register models for automatic real-time synchronization"""
        if self.sync_manager and self.sync_manager.enabled:
            register_sync_for_models(list(models))
            logger.info(f"✓ Registered {len(models)} model(s) for sync")
    
    def get_active_session(self):
        """Get session from primary database"""
        return self.primary_db.session
    
    def get_sync_stats(self):
        """Get synchronization statistics"""
        if self.sync_manager:
            return self.sync_manager.get_stats()
        return {'enabled': False}
    
    def flush_pending_syncs(self):
        """Manually flush all pending sync operations"""
        if self.sync_manager:
            self.sync_manager.flush_pending_syncs()
            logger.info("✓ Pending syncs flushed")
    
    def health_check(self):
        """Check connectivity of both databases"""
        health = {
            'sqlite': {'status': 'unknown', 'error': None},
            'mysql': {'status': 'unknown', 'error': None},
            'sync': 'disabled'
        }
        
        # Check SQLite
        try:
            with self.sqlite_db.engine.connect() as conn:
                conn.execute('SELECT 1')
            health['sqlite']['status'] = 'ok'
        except Exception as e:
            health['sqlite']['status'] = 'error'
            health['sqlite']['error'] = str(e)
        
        # Check MySQL
        try:
            with self.mysql_db.engine.connect() as conn:
                conn.execute('SELECT 1')
            health['mysql']['status'] = 'ok'
        except Exception as e:
            health['mysql']['status'] = 'error'
            health['mysql']['error'] = str(e)
        
        # Sync status
        if self.sync_manager:
            health['sync'] = 'active' if self.sync_manager.enabled else 'disabled'
            health['sync_stats'] = {
                'inserts': self.sync_manager.stats['inserts_synced'],
                'updates': self.sync_manager.stats['updates_synced'],
                'deletes': self.sync_manager.stats['deletes_synced'],
                'errors': len(self.sync_manager.stats['errors'])
            }
        
        return health


# Global instance
_dual_db_manager: Optional[DualDatabaseManager] = None


def get_dual_db_manager() -> Optional[DualDatabaseManager]:
    """Get the global dual database manager instance"""
    return _dual_db_manager


def create_dual_db_configs(base_dir: str = None) -> tuple:
    """
    Create configurations for both SQLite and MySQL databases
    
    Returns:
        Tuple of (sqlite_uri, mysql_uri)
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # SQLite URI
    sqlite_path = os.path.join(base_dir, 'database', 'epi_detection.db')
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    sqlite_uri = f'sqlite:///{sqlite_path}'
    
    # MySQL URI
    mysql_host = os.getenv('MYSQL_HOST', os.getenv('DB_HOST', 'localhost'))
    mysql_port = int(os.getenv('MYSQL_PORT', os.getenv('DB_PORT', 3306)))
    mysql_user = os.getenv('MYSQL_USER', os.getenv('DB_USER', 'epi_user'))
    mysql_pass = os.getenv('MYSQL_PASSWORD', os.getenv('DB_PASSWORD', ''))
    mysql_db = os.getenv('MYSQL_DB', os.getenv('DB_NAME', 'epi_detection_db'))
    
    if mysql_pass:
        mysql_uri = f'mysql+pymysql://{mysql_user}:{quote_plus(mysql_pass)}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4'
    else:
        mysql_uri = f'mysql+pymysql://{mysql_user}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4'
    
    return sqlite_uri, mysql_uri


def init_dual_databases(app: Flask, db_primary):
    """
    Initialize both SQLite and MySQL databases
    
    Args:
        app: Flask application
        db_primary: Primary Flask-SQLAlchemy instance (will be cloned)
    
    Returns:
        DualDatabaseManager instance
    """
    global _dual_db_manager
    
    # Get URIs
    sqlite_uri, mysql_uri = create_dual_db_configs()
    
    # Create SQLite instance
    from flask_sqlalchemy import SQLAlchemy
    db_sqlite = SQLAlchemy()
    app.config['SQLALCHEMY_BINDS'] = {
        'sqlite': sqlite_uri,
        'mysql': mysql_uri
    }
    
    # Initialize primary DB
    db_primary.init_app(app)
    db_sqlite.init_app(app)
    
    # Create MySQL instance separately
    app_mysql = Flask(__name__)
    app_mysql.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
    app_mysql.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app_mysql.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    db_mysql = SQLAlchemy()
    db_mysql.init_app(app_mysql)
    
    # Create manager
    _dual_db_manager = DualDatabaseManager(app)
    _dual_db_manager.init_app(app, db_sqlite, db_mysql)
    
    logger.info("✓ Dual database manager initialized")
    return _dual_db_manager


def setup_realtime_sync_for_app(app: Flask, db, models: list):
    """
    Setup real-time synchronization for a Flask app
    
    Usage:
        from app.database_unified import db, Detection, Alert, TrainingResult
        from app.dual_db_manager import setup_realtime_sync_for_app
        
        app = Flask(__name__)
        setup_realtime_sync_for_app(app, db, [Detection, Alert, TrainingResult])
    
    Args:
        app: Flask application
        db: Flask-SQLAlchemy instance
        models: List of model classes to sync
    """
    # Create both DB instances
    sqlite_uri, mysql_uri = create_dual_db_configs()
    
    # SQLite DB
    from flask_sqlalchemy import SQLAlchemy
    db_sqlite = SQLAlchemy()
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
    db_sqlite.init_app(app)
    
    # MySQL DB
    app_mysql_ctx = app.app_context()
    app_mysql_ctx.push()
    
    # Create sync manager
    sync_manager = init_realtime_sync(db, db_sqlite, app)
    
    # Register models
    register_sync_for_models(models)
    
    logger.info(f"✓ Real-time sync initialized for {len(models)} model(s)")
    logger.info(f"  SQLite: {sqlite_uri}")
    logger.info(f"  MySQL:  {mysql_uri}")
    logger.info(f"  Sync enabled: {sync_manager.enabled}")
    
    return sync_manager
