#!/usr/bin/env python3
"""
SQLite ↔ MySQL Real-time Synchronizer
Synchronise les données en temps réel entre les deux bases

Usage:
    python sync_databases.py --watch            # Écouter les changements
    python sync_databases.py --sync-sqlite      # SQLite → MySQL
    python sync_databases.py --sync-mysql       # MySQL → SQLite
    python sync_databases.py --status           # État de sync
    python sync_databases.py --daemon           # Mode daemon (background)
"""

import os
import sys
import time
import json
import argparse
import threading
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire parent au chemin
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.dual_database import DualDatabase, DUAL_DATABASE_ENABLED


class DatabaseSynchronizer:
    """Synchroniseur de bases de données"""
    
    def __init__(self, check_interval=30):
        self.dual_db = DualDatabase()
        self.check_interval = check_interval
        self.running = False
        self.last_check = None
        self.sync_count = 0
        self.errors = []
    
    def sync_sqlite_to_mysql(self, verbose=True):
        """Synchroniser SQLite → MySQL"""
        if verbose:
            print(f"\n🔄 Synchronizing SQLite → MySQL ({datetime.now().strftime('%H:%M:%S')})")
        
        try:
            self.dual_db.sync_all(direction='sqlite_to_mysql')
            self.sync_count += 1
            self.last_check = datetime.now()
            return True
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            self.errors.append(error_msg)
            if verbose:
                print(f"❌ {error_msg}")
            return False
    
    def sync_mysql_to_sqlite(self, verbose=True):
        """Synchroniser MySQL → SQLite"""
        if verbose:
            print(f"\n🔄 Synchronizing MySQL → SQLite ({datetime.now().strftime('%H:%M:%S')})")
        
        try:
            self.dual_db.sync_all(direction='mysql_to_sqlite')
            self.sync_count += 1
            self.last_check = datetime.now()
            return True
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            self.errors.append(error_msg)
            if verbose:
                print(f"❌ {error_msg}")
            return False
    
    def check_status(self):
        """Vérifier le statut"""
        connectivity = self.dual_db.check_connectivity()
        
        print("\n" + "="*70)
        print("📊 SYNCHRONIZATION STATUS")
        print("="*70 + "\n")
        
        print("🔗 Connectivity:")
        print(f"  SQLite: {'✓' if connectivity['sqlite']['available'] else '✗'}")
        if connectivity['sqlite']['error']:
            print(f"    Error: {connectivity['sqlite']['error']}")
        
        print(f"  MySQL:  {'✓' if connectivity['mysql']['available'] else '✗'}")
        if connectivity['mysql']['error']:
            print(f"    Error: {connectivity['mysql']['error']}")
        
        print(f"\n📈 Statistics:")
        print(f"  Total syncs: {self.sync_count}")
        print(f"  Last sync: {self.last_check or 'Never'}")
        print(f"  Errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\n❌ Recent errors:")
            for error in self.errors[-5:]:
                print(f"    • {error}")
        
        stats = self.dual_db.get_stats()
        if stats['synced_tables']:
            print(f"\n📋 Last synced tables:")
            for table, info in list(stats['synced_tables'].items())[-5:]:
                status = info.get('status', '?')
                rows = info.get('rows', 0)
                print(f"    {table}: {status} ({rows} rows)")
        
        print("\n" + "="*70 + "\n")
    
    def watch_mode(self):
        """Mode d'écoute: synchroniser en continu"""
        print("\n" + "="*70)
        print("👁️  WATCH MODE - Continuous synchronization")
        print(f"     Check interval: {self.check_interval}s")
        print("     Press Ctrl+C to stop")
        print("="*70 + "\n")
        
        self.running = True
        sync_direction = 'sqlite_to_mysql'  # Défaut
        
        try:
            iteration = 0
            while self.running:
                iteration += 1
                
                # Alterne entre les deux directions
                if iteration % 2 == 1:
                    sync_direction = 'sqlite_to_mysql'
                else:
                    sync_direction = 'mysql_to_sqlite'
                
                print(f"\n[{iteration}] ", end='')
                
                try:
                    if sync_direction == 'sqlite_to_mysql':
                        self.sync_sqlite_to_mysql(verbose=False)
                        print("✓ SQLite→MySQL synced")
                    else:
                        self.sync_mysql_to_sqlite(verbose=False)
                        print("✓ MySQL→SQLite synced")
                except Exception as e:
                    print(f"⚠️  Error: {e}")
                
                # Attendre avant le prochain check
                try:
                    time.sleep(self.check_interval)
                except KeyboardInterrupt:
                    break
        
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            print("\n\n✅ Watch mode stopped\n")
    
    def daemon_mode(self, daemon=True):
        """Mode daemon: tourner en arrière-plan"""
        print(f"\n🚀 Starting synchronizer daemon...")
        print(f"   Check interval: {self.check_interval}s")
        print(f"   Daemon mode: {daemon}")
        
        # Créer et démarrer le thread
        sync_thread = threading.Thread(target=self.watch_mode, daemon=daemon)
        sync_thread.start()
        
        # Afficher le statut toutes les minutes
        try:
            while self.running:
                time.sleep(60)
                print(f"\n📊 Daemon running... (syncs: {self.sync_count})")
        except KeyboardInterrupt:
            self.running = False
            sync_thread.join(timeout=5)
            print("\n✅ Daemon stopped")
    
    def export_config(self, filename='sync_config.json'):
        """Exporter la configuration de sync"""
        config = {
            'enabled': DUAL_DATABASE_ENABLED,
            'check_interval': self.check_interval,
            'sync_mode': os.getenv('SYNC_MODE', 'sqlite_primary'),
            'databases': {
                'sqlite': {
                    'path': os.getenv('SQLITE_DB_PATH', 'instance/epi_detection.db')
                },
                'mysql': {
                    'host': os.getenv('DB_HOST', 'localhost'),
                    'port': int(os.getenv('DB_PORT', 3306)),
                    'user': os.getenv('DB_USER', 'epi_user'),
                    'database': os.getenv('DB_NAME', 'epi_detection_db')
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Configuration exported to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='SQLite ↔ MySQL Real-time Synchronizer'
    )
    parser.add_argument('--sync-sqlite', action='store_true',
                       help='Synchronize SQLite → MySQL')
    parser.add_argument('--sync-mysql', action='store_true',
                       help='Synchronize MySQL → SQLite')
    parser.add_argument('--watch', action='store_true',
                       help='Watch mode: continuous sync')
    parser.add_argument('--daemon', action='store_true',
                       help='Daemon mode: background service')
    parser.add_argument('--status', action='store_true',
                       help='Check synchronization status')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in seconds (default: 30)')
    parser.add_argument('--export-config', metavar='FILE',
                       help='Export configuration to JSON')
    
    args = parser.parse_args()
    
    if not DUAL_DATABASE_ENABLED:
        print("⚠️  Dual database is disabled (DUAL_DATABASE=false)")
        print("   Set DUAL_DATABASE=true in .env to enable")
        sys.exit(1)
    
    syncer = DatabaseSynchronizer(check_interval=args.interval)
    
    try:
        if args.sync_sqlite:
            syncer.sync_sqlite_to_mysql()
        elif args.sync_mysql:
            syncer.sync_mysql_to_sqlite()
        elif args.watch:
            syncer.watch_mode()
        elif args.daemon:
            syncer.daemon_mode()
        elif args.status:
            syncer.check_status()
        elif args.export_config:
            syncer.export_config(args.export_config)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n✅ Synchronizer stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
