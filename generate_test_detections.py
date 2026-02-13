#!/usr/bin/env python3
"""Générer des détections de test avec des données EPI réalistes"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app, db
from app.database_unified import Detection
from datetime import datetime, timedelta
import random

with app.app_context():
    print("=" * 80)
    print("GÉNÉRATION DE DÉTECTIONS DE TEST AVEC EPI")
    print("=" * 80)
    
    # Générer 50 détections avec données EPI réalistes
    base_time = datetime.now() - timedelta(hours=12)
    
    for i in range(50):
        total_persons = random.randint(1, 5)
        
        # Générer des comptes EPI réalistes (80-100% de conformité)
        helmet_count = int(total_persons * random.uniform(0.7, 1.0))
        vest_count = int(total_persons * random.uniform(0.6, 0.95))
        glasses_count = int(total_persons * random.uniform(0.3, 0.8))
        boots_count = int(total_persons * random.uniform(0.5, 0.95))
        
        # Calculer le taux de conformité (tous les EPI obligatoires)
        epi_counts = [helmet_count, vest_count, boots_count]
        min_epi = min(epi_counts) if epi_counts else 0
        compliance_rate = (min_epi / total_persons * 100) if total_persons > 0 else 0
        
        detection = Detection(
            timestamp=base_time + timedelta(minutes=i*5),
            source='test',
            image_path='test_image.jpg',
            total_persons=total_persons,
            with_helmet=helmet_count,
            with_vest=vest_count,
            with_glasses=glasses_count,
            with_boots=boots_count,
            compliance_rate=round(compliance_rate, 2),
            compliance_level='good' if compliance_rate >= 80 else 'warning',
            alert_type='safe' if compliance_rate >= 80 else 'warning',
            model_used='best.pt'
        )
        db.session.add(detection)
        
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/50 détections créées...")
    
    db.session.commit()
    print(f"\n✅ {50} détections de test créées!")
    
    # Vérifier
    total = Detection.query.count()
    print(f"✓ Nombre total de détections: {total}")
    
    # Afficher un exemple
    latest = Detection.query.order_by(Detection.timestamp.desc()).first()
    if latest:
        print(f"\nDernière détection:")
        print(f"  Total personnes: {latest.total_persons}")
        print(f"  Casques: {latest.with_helmet}")
        print(f"  Gilets: {latest.with_vest}")
        print(f"  Lunettes: {latest.with_glasses}")
        print(f"  Bottes: {latest.with_boots}")
        print(f"  Taux conformité: {latest.compliance_rate}%")
    
    print("\n" + "=" * 80)
