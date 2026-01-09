#!/usr/bin/env python3
"""
Script de test de la base de données unifiée
Teste SQLite et MySQL
"""

import sys
import os
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from flask import Flask
from config import config

def test_database_connection():
    """Tester la connexion à la BD"""
    
    print("=" * 70)
    print("🧪 TEST DE LA BASE DE DONNÉES")
    print("=" * 70)
    
    print(f"\n📌 Type BD: {config.DB_TYPE.upper()}")
    print(f"📌 URI: {config.DATABASE_URI}")
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = getattr(config, 'SQLALCHEMY_ENGINE_OPTIONS', {})
    
    from app.database_unified import db
    db.init_app(app)
    
    try:
        with app.app_context():
            # Test de connexion
            connection = db.engine.connect()
            connection.close()
            print("\n✅ Connexion BD réussie!")
            
            # Lister les tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n📊 Tables ({len(tables)}):")
            for table in sorted(tables):
                print(f"  ✓ {table}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Erreur connexion: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_operations():
    """Tester les opérations CRUD sur les modèles"""
    
    print("\n" + "=" * 70)
    print("🧪 TEST DES MODÈLES")
    print("=" * 70)
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = getattr(config, 'SQLALCHEMY_ENGINE_OPTIONS', {})
    
    from app.database_unified import (
        db, TrainingResult, Detection, Alert, 
        Worker, IoTSensor, IoTDataLog, SystemLog
    )
    db.init_app(app)
    
    try:
        with app.app_context():
            # Test 1: TrainingResult
            print("\n1️⃣  Test TrainingResult...")
            result = TrainingResult(
                model_name='YOLOv5s-Test',
                model_version='1.0',
                dataset_name='dataset',
                epochs=100,
                batch_size=16,
                image_size=320,
                train_loss=0.5,
                val_accuracy=0.92,
                status='completed',
                weights_path='models/best.pt'
            )
            db.session.add(result)
            db.session.commit()
            print(f"   ✓ Créé: ID={result.id}")
            
            # Vérifier
            fetched = TrainingResult.query.get(result.id)
            assert fetched is not None
            print(f"   ✓ Récupéré: {fetched.model_name}")
            
            # Supprimer pour nettoyer
            db.session.delete(fetched)
            db.session.commit()
            print(f"   ✓ Supprimé")
            
            # Test 2: Detection
            print("\n2️⃣  Test Detection...")
            detection = Detection(
                source='test',
                total_persons=5,
                with_helmet=4,
                with_vest=3,
                with_glasses=2,
                compliance_rate=80.0,
                compliance_level='good',
                alert_type='safe'
            )
            db.session.add(detection)
            db.session.commit()
            print(f"   ✓ Créé: ID={detection.id}")
            
            db.session.delete(detection)
            db.session.commit()
            print(f"   ✓ Supprimé")
            
            # Test 3: IoTSensor
            print("\n3️⃣  Test IoTSensor...")
            sensor = IoTSensor(
                sensor_id='test_sensor_001',
                sensor_name='Test Sensor',
                sensor_type='test',
                location='Lab',
                status='active'
            )
            db.session.add(sensor)
            db.session.commit()
            print(f"   ✓ Créé: ID={sensor.id}")
            
            # Test 4: IoTDataLog
            print("\n4️⃣  Test IoTDataLog...")
            log = IoTDataLog(
                sensor_id=sensor.id,
                motion_detected=True,
                compliance_level=85.5,
                led_green=True,
                led_red=False,
                buzzer_active=False
            )
            db.session.add(log)
            db.session.commit()
            print(f"   ✓ Créé: ID={log.id}")
            
            # Vérifier la relation
            assert len(sensor.data_logs) == 1
            print(f"   ✓ Relation OK (1 log pour ce capteur)")
            
            # Nettoyer
            db.session.delete(log)
            db.session.delete(sensor)
            db.session.commit()
            print(f"   ✓ Supprimé")
            
            # Test 5: Worker
            print("\n5️⃣  Test Worker...")
            worker = Worker(
                name='John Doe',
                badge_id='BADGE001',
                department='Engineering',
                role='Senior Engineer',
                compliance_score=95.0
            )
            db.session.add(worker)
            db.session.commit()
            print(f"   ✓ Créé: ID={worker.id}")
            
            db.session.delete(worker)
            db.session.commit()
            print(f"   ✓ Supprimé")
            
            # Test 6: Alert
            print("\n6️⃣  Test Alert...")
            alert = Alert(
                type='test_alert',
                message='Test alert message',
                severity='low'
            )
            db.session.add(alert)
            db.session.commit()
            print(f"   ✓ Créé: ID={alert.id}")
            
            db.session.delete(alert)
            db.session.commit()
            print(f"   ✓ Supprimé")
            
            # Test 7: SystemLog
            print("\n7️⃣  Test SystemLog...")
            slog = SystemLog(
                level='info',
                message='Test log message',
                source='test_script'
            )
            db.session.add(slog)
            db.session.commit()
            print(f"   ✓ Créé: ID={slog.id}")
            
            db.session.delete(slog)
            db.session.commit()
            print(f"   ✓ Supprimé")
            
            print("\n✅ Tous les tests des modèles réussis!")
            return True
            
    except Exception as e:
        print(f"\n❌ Erreur test modèles: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    
    success1 = test_database_connection()
    success2 = test_model_operations() if success1 else False
    
    print("\n" + "=" * 70)
    if success1 and success2:
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("=" * 70)
        print("\nVotre base de données est prête à être utilisée!")
        print("Type de BD:", config.DB_TYPE.upper())
        print("\nCommandes suivantes:")
        print("  1. python init_unified_db.py  (pour importer les résultats d'entraînement)")
        print("  2. python run_app.py           (pour démarrer l'application)")
        return 0
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("=" * 70)
        print("\nVérifiez:")
        print("  - La BD est accessible")
        print("  - Les crédentiels MySQL sont corrects")
        print("  - Les drivers sont installés (pymysql pour MySQL)")
        return 1


if __name__ == '__main__':
    sys.exit(main())
