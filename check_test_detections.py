#!/usr/bin/env python3
"""Vérifier les dernières détections générées"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app, db
from app.database_unified import Detection
from datetime import datetime

with app.app_context():
    print("=" * 80)
    print("VÉRIFICATION DES DÉTECTIONS DE TEST")
    print("=" * 80)
    
    # Afficher les 10 dernières
    detections = Detection.query.order_by(Detection.id.desc()).limit(10).all()
    
    for det in detections:
        print(f"\nID: {det.id} | Source: {det.source}")
        print(f"  Personnes: {det.total_persons} | Casques: {det.with_helmet} | Gilets: {det.with_vest} | Lunettes: {det.with_glasses} | Bottes: {det.with_boots}")
        print(f"  Conformité: {det.compliance_rate}%")
    
    print("\n" + "=" * 80)
