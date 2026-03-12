#!/usr/bin/env python3
"""
Quick integration example for real-time bidirectional sync
Montre comment intégrer le dual-sync en 3 lignes pour une app existante

Run:
    python app/realtime_sync_example.py
"""

import os
import sys
from pathlib import Path

# Add parent to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def example_1_basic_setup():
    """Example 1: Minimal setup - add 3 lines to existing Flask app"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Minimal Setup")
    print("="*70 + "\n")
    
    from flask import Flask
    from app.database_unified import db, Detection, Alert, TrainingResult
    from app.realtime_sync import init_realtime_sync, register_sync_for_models
    
    # === YOUR EXISTING FLASK APP ===
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/epi_detection.db'
    db.init_app(app)
    
    # === ADD THESE 3 LINES FOR SYNC ===
    from app.dual_db_manager import create_dual_db_configs
    sqlite_uri, mysql_uri = create_dual_db_configs()
    sync_mgr = init_realtime_sync(db, db, app)  # Pass db twice for now
    register_sync_for_models([Detection, Alert, TrainingResult])
    
    print("✓ Basic sync setup complete")
    print(f"  SQLite: {sqlite_uri}")
    print(f"  MySQL:  {mysql_uri}")
    print(f"  Sync enabled: {sync_mgr.enabled}")


def example_2_test_sync():
    """Example 2: Test sync by creating objects"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Test Synchronization")
    print("="*70 + "\n")
    
    from flask import Flask
    from app.database_unified import db, Detection, Alert
    from app.realtime_sync import init_realtime_sync, register_sync_for_models, get_sync_manager
    from datetime import datetime
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_sync.db'
    db.init_app(app)
    
    # Initialize sync
    sync_mgr = init_realtime_sync(db, db, app)
    register_sync_for_models([Detection, Alert])
    
    with app.app_context():
        db.create_all()
        
        print("Creating test detection...")
        d = Detection(
            image_path="/test/image.jpg",
            total_persons=5,
            with_helmet=4,
            with_vest=3,
            compliance_rate=75.0,
            alert_type="warning"
        )
        db.session.add(d)
        db.session.commit()
        print(f"✓ Detection created: ID={d.id}")
        
        print("\nCreating test alert...")
        a = Alert(
            type="non-conformite",
            message="Unsafe helmet detection",
            severity="high"
        )
        db.session.add(a)
        db.session.commit()
        print(f"✓ Alert created: ID={a.id}")
        
        print("\nSync stats:")
        stats = sync_mgr.get_stats()
        print(f"  Inserts synced: {stats['inserts_synced']}")
        print(f"  Updates synced: {stats['updates_synced']}")
        print(f"  Errors: {len(stats['errors'])}")
        print(f"  Enabled: {stats['enabled']}")
        print(f"  Direction: {stats['direction']}")


def example_3_show_stats():
    """Example 3: Monitor sync statistics"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Monitor Sync Statistics")
    print("="*70 + "\n")
    
    from app.realtime_sync import get_sync_manager
    import json
    
    sync_mgr = get_sync_manager()
    if sync_mgr:
        stats = sync_mgr.get_stats()
        print(json.dumps(stats, indent=2, default=str))
    else:
        print("⚠️ Sync manager not initialized")


def example_4_health_check():
    """Example 4: Check database connectivity"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Database Health Check")
    print("="*70 + "\n")
    
    from app.dual_db_manager import get_dual_db_manager, create_dual_db_configs
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    import json
    
    # Create both DB instances
    sqlite_uri, mysql_uri = create_dual_db_configs()
    
    from app.database_unified import db
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
    
    print(f"SQLite URI:  {sqlite_uri}")
    print(f"MySQL URI:   {mysql_uri}")
    print()
    
    # Test SQLite
    print("Testing SQLite connectivity...")
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
    db.init_app(app)
    try:
        with app.app_context():
            db.engine.connect()
        print("  ✓ SQLite: OK")
    except Exception as e:
        print(f"  ✗ SQLite: {e}")
    
    # Test MySQL
    print("\nTesting MySQL connectivity...")
    try:
        from sqlalchemy import create_engine
        engine = create_engine(mysql_uri, connect_args={'timeout': 5})
        with engine.connect() as conn:
            conn.execute('SELECT 1')
        print("  ✓ MySQL: OK")
    except Exception as e:
        print(f"  ⚠️  MySQL: {e}")
        print("     (This is OK if MySQL/XAMPP is not running)")


def example_5_manual_sync_control():
    """Example 5: Manual sync control (disable/enable/flush)"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Manual Sync Control")
    print("="*70 + "\n")
    
    from app.realtime_sync import get_sync_manager
    
    sync_mgr = get_sync_manager()
    if not sync_mgr:
        print("⚠️ Sync manager not initialized")
        return
    
    print(f"Current sync state: {sync_mgr.enabled}")
    print()
    
    # Disable
    print("Disabling sync...")
    sync_mgr.disable()
    print(f"✓ Sync disabled: {not sync_mgr.enabled}")
    
    # Re-enable
    print("\nRe-enabling sync...")
    sync_mgr.enable()
    print(f"✓ Sync enabled: {sync_mgr.enabled}")
    
    # Flush
    print("\nFlushing pending syncs...")
    sync_mgr.flush_pending_syncs()
    print("✓ Pending syncs flushed")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time sync examples')
    parser.add_argument('--example', type=int, choices=[1, 2, 3, 4, 5], default=1,
                        help='Which example to run (1-5)')
    parser.add_argument('--all', action='store_true', help='Run all examples')
    
    args = parser.parse_args()
    
    examples = {
        1: example_1_basic_setup,
        2: example_2_test_sync,
        3: example_3_show_stats,
        4: example_4_health_check,
        5: example_5_manual_sync_control,
    }
    
    if args.all:
        for i in [1, 2, 4]:  # Skip 3, 5 if not initialized
            try:
                examples[i]()
            except Exception as e:
                print(f"\n⚠️  Example {i} error: {e}")
    else:
        examples[args.example]()
    
    print("\n" + "="*70 + "\n")
