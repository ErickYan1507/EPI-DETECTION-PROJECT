#!/usr/bin/env python3
"""Vérifier les détections en base de données"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app, db
from app.database_unified import Detection
from datetime import datetime, timedelta

with app.app_context():
    print("=" * 80)
    print("VÉRIFICATION DES DÉTECTIONS")
    print("=" * 80)
    
    # Compter les détections totales
    total = Detection.query.count()
    print(f"\n✓ Nombre total de détections: {total}")
    
    # Dernières détections
    last_detections = Detection.query.order_by(Detection.timestamp.desc()).limit(5).all()
    
    if last_detections:
        print(f"\n✓ Dernières détections:")
        for det in last_detections:
            print(f"\n  ID: {det.id}")
            print(f"  Timestamp: {det.timestamp}")
            print(f"  Total personnes: {det.total_persons}")
            print(f"  Casques: {det.with_helmet}")
            print(f"  Gilets: {det.with_vest}")
            print(f"  Lunettes: {det.with_glasses}")
            print(f"  Bottes: {det.with_boots}")
            print(f"  Taux conformité: {det.compliance_rate}%")
    else:
        print(f"\n⚠️ Aucune détection en base de données!")
    
    # Détections dernières 24h
    last_24h = datetime.now() - timedelta(hours=24)
    detections_24h = Detection.query.filter(Detection.timestamp >= last_24h).count()
    print(f"\n✓ Détections dernières 24h: {detections_24h}")
    
    print("\n" + "=" * 80)
