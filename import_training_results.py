#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour importer les résultats d'entraînement existants dans la base de données
"""

import sys
import os
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from config import config
from flask import Flask
from app.database import db, TrainingResult


def import_training_results():
    """Importer les résultats d'entraînement depuis results.csv"""
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    results_csv = Path('runs/train/epi_detection_v1/results.csv')
    
    if not results_csv.exists():
        print(f"❌ Fichier non trouvé: {results_csv}")
        return False
    
    print(f"📖 Lecture du fichier: {results_csv}")
    
    with app.app_context():
        try:
            import csv
            
            with open(results_csv, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if not rows:
                print("❌ Aucune donnée trouvée")
                return False
            
            last_row = rows[-1]
            
            cleaned_row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in last_row.items()}
            
            print("\n📊 Données extraites (dernière epoch):")
            for key, value in cleaned_row.items():
                print(f"  {key}: {value}")
            
            try:
                train_loss = float(cleaned_row.get('train/box_loss', 0)) if cleaned_row.get('train/box_loss') else None
                train_accuracy = float(cleaned_row.get('metrics/mAP_0.5', 0)) if cleaned_row.get('metrics/mAP_0.5') else None
                train_precision = float(cleaned_row.get('metrics/precision', 0)) if cleaned_row.get('metrics/precision') else None
                train_recall = float(cleaned_row.get('metrics/recall', 0)) if cleaned_row.get('metrics/recall') else None
                
                val_loss = float(cleaned_row.get('val/box_loss', 0)) if cleaned_row.get('val/box_loss') else None
                val_accuracy = float(cleaned_row.get('metrics/mAP_0.5:0.95', 0)) if cleaned_row.get('metrics/mAP_0.5:0.95') else None
                val_precision = float(cleaned_row.get('metrics/precision', 0)) if cleaned_row.get('metrics/precision') else None
                val_recall = float(cleaned_row.get('metrics/recall', 0)) if cleaned_row.get('metrics/recall') else None
                
                result = TrainingResult(
                    model_name='YOLOv5s-EPI',
                    model_version='1.0',
                    dataset_name='dataset',
                    epochs=int(cleaned_row.get('epoch', 100)) + 1 if cleaned_row.get('epoch') else 100,
                    batch_size=16,
                    train_loss=train_loss,
                    train_accuracy=train_accuracy,
                    train_precision=train_precision,
                    train_recall=train_recall,
                    train_f1_score=None,
                    val_loss=val_loss,
                    val_accuracy=val_accuracy,
                    val_precision=val_precision,
                    val_recall=val_recall,
                    val_f1_score=None,
                    training_time_seconds=0,
                    status='completed',
                    weights_path='models/best.pt',
                    timestamp=datetime.utcnow()
                )
                
                db.session.add(result)
                db.session.commit()
                
                print(f"\n✅ Résultat d'entraînement importé (ID: {result.id})")
                return True
                
            except ValueError as e:
                print(f"❌ Erreur conversion de valeurs: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur import: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    print("="*70)
    print("📥 IMPORTATION DES RÉSULTATS D'ENTRAÎNEMENT")
    print("="*70)
    
    if import_training_results():
        print("\n✓ Import réussi!")
    else:
        print("\n✗ Import échoué")
