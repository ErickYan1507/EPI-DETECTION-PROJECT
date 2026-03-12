#!/usr/bin/env python3
"""
Realtime Bidirectional Database Synchronization
SQLite ↔ MySQL synchronization with automatic hooks and event listeners

Automatically syncs changes between SQLite and MySQL in real-time.
"""

import os
import json
import logging
from datetime import datetime
from threading import Thread, Lock
from collections import defaultdict
from typing import Optional, Dict, List, Any

from sqlalchemy import event, inspect, engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class RealtimeSyncManager:
    """Manager for real-time bi-directional sync between SQLite and MySQL"""
    
    def __init__(self, sqlite_db, mysql_db, app=None):
        """
        Initialize the sync manager
        
        Args:
            sqlite_db: Flask-SQLAlchemy instance for SQLite
            mysql_db: Flask-SQLAlchemy instance for MySQL  
            app: Flask app instance (optional, for async tasks)
        """
        self.sqlite_db = sqlite_db
        self.mysql_db = mysql_db
        self.app = app
        
        self.enabled = os.getenv('REALTIME_SYNC', 'true').lower() == 'true'
        self.sync_direction = os.getenv('SYNC_DIRECTION', 'sqlite_to_mysql').lower()
        
        # Track pending syncs to batch operations
        self.pending_syncs = defaultdict(list)
        self.sync_lock = Lock()
        
        # Stats
        self.stats = {
            'inserts_synced': 0,
            'updates_synced': 0,
            'deletes_synced': 0,
            'errors': [],
            'last_sync': None
        }
        
        self.interceptors_registered = False
    
    def register_model_interceptors(self, models: List[type]):
        """
        Register automatic sync interceptors on model classes
        
        Usage:
            from app.database import Detection, Alert, TrainingResult
            sync_manager = RealtimeSyncManager(sqlite_db, mysql_db)
            sync_manager.register_model_interceptors([Detection, Alert, TrainingResult])
        """
        if not self.enabled or self.interceptors_registered:
            return
        
        logger.info(f"Registering sync interceptors for {len(models)} models...")
        
        for model in models:
            self._register_model_hooks(model)
        
        self.interceptors_registered = True
        logger.info("✓ Sync interceptors registered")
    
    def _register_model_hooks(self, model: type):
        """Register after_insert, after_update, after_delete hooks on a model"""
        
        @event.listens_for(model, 'after_insert', propagate=True)
        def after_insert_listener(mapper, connection, target):
            if not self.enabled:
                return
            self._queue_sync('insert', model, target)
        
        @event.listens_for(model, 'after_update', propagate=True)
        def after_update_listener(mapper, connection, target):
            if not self.enabled:
                return
            self._queue_sync('update', model, target)
        
        @event.listens_for(model, 'after_delete', propagate=True)
        def after_delete_listener(mapper, connection, target):
            if not self.enabled:
                return
            self._queue_sync('delete', model, target)
    
    def _queue_sync(self, operation: str, model: type, obj: Any):
        """Queue a sync operation"""
        with self.sync_lock:
            self.pending_syncs[model.__tablename__].append({
                'operation': operation,
                'model': model,
                'object': obj,
                'timestamp': datetime.utcnow()
            })
            
            # Auto-flush if queue gets large
            if len(self.pending_syncs[model.__tablename__]) >= 50:
                self.flush_pending_syncs()
    
    def flush_pending_syncs(self):
        """Execute all pending sync operations"""
        if not self.pending_syncs or not self.enabled:
            return
        
        with self.sync_lock:
            syncs_to_execute = dict(self.pending_syncs)
            self.pending_syncs.clear()
        
        for table_name, operations in syncs_to_execute.items():
            for sync_op in operations:
                try:
                    self._execute_sync(sync_op)
                except Exception as e:
                    logger.error(f"Sync error for {table_name}: {e}")
                    self.stats['errors'].append(str(e))
    
    def _execute_sync(self, sync_op: Dict):
        """Execute a single sync operation"""
        operation = sync_op['operation']
        model = sync_op['model']
        obj = sync_op['object']
        
        try:
            if self.sync_direction == 'sqlite_to_mysql':
                self._sync_to_mysql(operation, model, obj)
            elif self.sync_direction == 'mysql_to_sqlite':
                self._sync_to_sqlite(operation, model, obj)
            else:  # both
                self._sync_to_mysql(operation, model, obj)
                self._sync_to_sqlite(operation, model, obj)
            
            # Update stats
            if operation == 'insert':
                self.stats['inserts_synced'] += 1
            elif operation == 'update':
                self.stats['updates_synced'] += 1
            elif operation == 'delete':
                self.stats['deletes_synced'] += 1
            
            self.stats['last_sync'] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to sync {operation} on {model.__tablename__}: {e}")
            self.stats['errors'].append({
                'operation': operation,
                'table': model.__tablename__,
                'error': str(e),
                'timestamp': datetime.utcnow()
            })
    
    def _sync_to_mysql(self, operation: str, model: type, obj: Any):
        """Sync an operation to MySQL"""
        session = self.mysql_db.session
        
        try:
            if operation == 'insert':
                # Get primary key value from object
                pk_value = self._get_pk_value(obj)
                # Check if already exists
                existing = session.query(model).filter_by(id=pk_value).first()
                if not existing:
                    mysql_obj = self._clone_object(obj, model)
                    session.add(mysql_obj)
                    
            elif operation == 'update':
                pk_value = self._get_pk_value(obj)
                mysql_obj = session.query(model).filter_by(id=pk_value).first()
                if mysql_obj:
                    self._update_object(mysql_obj, obj)
                else:
                    mysql_obj = self._clone_object(obj, model)
                    session.add(mysql_obj)
                    
            elif operation == 'delete':
                pk_value = self._get_pk_value(obj)
                mysql_obj = session.query(model).filter_by(id=pk_value).first()
                if mysql_obj:
                    session.delete(mysql_obj)
            
            session.commit()
            logger.debug(f"Synced {operation} to MySQL: {model.__tablename__}")
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"MySQL sync error: {e}")
            raise
    
    def _sync_to_sqlite(self, operation: str, model: type, obj: Any):
        """Sync an operation to SQLite"""
        session = self.sqlite_db.session
        
        try:
            if operation == 'insert':
                pk_value = self._get_pk_value(obj)
                existing = session.query(model).filter_by(id=pk_value).first()
                if not existing:
                    sqlite_obj = self._clone_object(obj, model)
                    session.add(sqlite_obj)
                    
            elif operation == 'update':
                pk_value = self._get_pk_value(obj)
                sqlite_obj = session.query(model).filter_by(id=pk_value).first()
                if sqlite_obj:
                    self._update_object(sqlite_obj, obj)
                else:
                    sqlite_obj = self._clone_object(obj, model)
                    session.add(sqlite_obj)
                    
            elif operation == 'delete':
                pk_value = self._get_pk_value(obj)
                sqlite_obj = session.query(model).filter_by(id=pk_value).first()
                if sqlite_obj:
                    session.delete(sqlite_obj)
            
            session.commit()
            logger.debug(f"Synced {operation} to SQLite: {model.__tablename__}")
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"SQLite sync error: {e}")
            raise
    
    def _get_pk_value(self, obj: Any) -> Any:
        """Get primary key value from object"""
        mapper = inspect(obj.__class__)
        pk = mapper.primary_key[0]
        return getattr(obj, pk.name)
    
    def _clone_object(self, source: Any, target_model: type) -> Any:
        """Clone object from source to target model, copying all columns"""
        target_obj = target_model()
        
        source_mapper = inspect(source.__class__)
        for col in source_mapper.columns:
            col_name = col.name
            if hasattr(source, col_name):
                value = getattr(source, col_name)
                if hasattr(target_obj, col_name):
                    setattr(target_obj, col_name, value)
        
        return target_obj
    
    def _update_object(self, target: Any, source: Any):
        """Update target object with values from source"""
        source_mapper = inspect(source.__class__)
        for col in source_mapper.columns:
            col_name = col.name
            if hasattr(source, col_name) and hasattr(target, col_name):
                value = getattr(source, col_name)
                setattr(target, col_name, value)
    
    def get_stats(self) -> Dict:
        """Get synchronization statistics"""
        return {
            **self.stats,
            'enabled': self.enabled,
            'direction': self.sync_direction,
            'interceptors_active': self.interceptors_registered,
            'pending_syncs_count': sum(len(v) for v in self.pending_syncs.values())
        }
    
    def enable(self):
        """Enable synchronization"""
        self.enabled = True
        logger.info("✓ Real-time sync enabled")
    
    def disable(self):
        """Disable synchronization"""
        self.flush_pending_syncs()  # Flush before disabling
        self.enabled = False
        logger.info("✓ Real-time sync disabled")
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'inserts_synced': 0,
            'updates_synced': 0,
            'deletes_synced': 0,
            'errors': [],
            'last_sync': None
        }


# Global instance
_sync_manager: Optional[RealtimeSyncManager] = None


def init_realtime_sync(sqlite_db, mysql_db, app=None) -> RealtimeSyncManager:
    """Initialize the real-time sync manager globally"""
    global _sync_manager
    _sync_manager = RealtimeSyncManager(sqlite_db, mysql_db, app)
    return _sync_manager


def get_sync_manager() -> Optional[RealtimeSyncManager]:
    """Get the global sync manager instance"""
    return _sync_manager


def register_sync_for_models(models: List[type]):
    """Register sync interceptors for a list of models"""
    if _sync_manager:
        _sync_manager.register_model_interceptors(models)
