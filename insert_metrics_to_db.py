#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insertion des métriques du modèle dans la base de données
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
try:
    from config import config
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[0]
    sys.path.insert(0, str(project_root))
    from config import config

from app.database_unified import db, TrainingResult
from flask import Flask

def insert_metrics_to_db():
    """Insère les métriques du modèle dans la base de données"""
    
    print("\n" + "="*70)
    print("INSERTION DES MÉTRIQUES DANS LA BASE DE DONNÉES")
    print("="*70)
    
    # Charger les métriques depuis le fichier JSON
    if not os.path.exists("model_metrics.json"):
        print("✗ Fichier model_metrics.json non trouvé")
        return False
    
    with open("model_metrics.json", 'r', encoding='utf-8') as f:
        metrics = json.load(f)
    
    # Créer l'application Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        try:
            # Préparer les données des classes
            class_metrics = {}
            for class_name, class_data in metrics['class_metrics'].items():
                class_metrics[class_name] = {
                    'precision': class_data['precision'],
                    'recall': class_data['recall'],
                    'ap': class_data['mAP_0_5'],  # mAP@0.5 comme AP
                    'avg_confidence': class_data.get('avg_confidence', 0)
                }
            
            # Créer une nouvelle entrée d'entraînement
            training_result = TrainingResult(
                model_name="best.pt",
                model_version="1.0",
                model_family="YOLOv5",
                
                dataset_name="EPI Dataset (Validation)",
                num_classes=5,
                class_names='["Casque", "Lunettes", "Personne", "Gilet", "Bottes"]',
                
                epochs=100,
                batch_size=16,
                image_size=640,
                learning_rate=0.001,
                optimizer="SGD",
                patience=20,
                
                # Métriques globales dans val_* (car ce sont des métriques de validation/test)
                val_precision=metrics['global_metrics']['precision'],
                val_recall=metrics['global_metrics']['recall'],
                val_f1_score=metrics['global_metrics']['f1_score'],
                val_accuracy=metrics['global_metrics']['mAP_0_5'],
                
                # Données détaillées par classe en JSON
                class_metrics=json.dumps(class_metrics, ensure_ascii=False),
                
                # Métadonnées
                training_time_seconds=0,
                inference_time_ms=0,
                model_path="models/best.pt",
            )
            
            db.session.add(training_result)
            db.session.commit()
            
            print(f"✓ Métriques insérées dans la base de données")
            print(f"  ID: {training_result.id}")
            print(f"  Timestamp: {training_result.timestamp}")
            
            return True
            
        except Exception as e:
            print(f"✗ Erreur lors de l'insertion: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

def display_metrics():
    """Affiche les métriques insérées"""
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        # Récupérer le dernier entraînement
        training = TrainingResult.query.filter_by(
            model_name="best.pt"
        ).order_by(TrainingResult.id.desc()).first()
        
        if not training:
            print("✗ Aucun entraînement trouvé")
            return
        
        print("\n" + "="*70)
        print("MÉTRIQUES INSÉRÉES DANS LA BASE DE DONNÉES")
        print("="*70)
        
        print(f"\nID: {training.id}")
        print(f"Modèle: {training.model_name}")
        print(f"Dataset: {training.dataset_name}")
        print(f"Date: {training.timestamp}")
        
        print("\n--- PERFORMANCE GLOBALE ---")
        print(f"Précision:  {training.val_precision:.4f}")
        print(f"Rappel:     {training.val_recall:.4f}")
        print(f"F1-Score:   {training.val_f1_score:.4f}")
        print(f"mAP@0.5:    {training.val_accuracy:.4f}")
        
        print("\n--- PERFORMANCE PAR CLASSE ---")
        print(f"{'Classe':<15} {'Précision':<12} {'Rappel':<12} {'mAP@0.5':<12}")
        print("-" * 51)
        
        if training.class_metrics:
            try:
                class_data = json.loads(training.class_metrics)
                for class_name, metrics_item in class_data.items():
                    print(f"{class_name:<15} {metrics_item['precision']:.4f}       "
                          f"{metrics_item['recall']:.4f}       "
                          f"{metrics_item['ap']:.4f}")
            except Exception as e:
                print(f"Erreur lors du parsing des métriques: {e}")

if __name__ == "__main__":
    success = insert_metrics_to_db()
    if success:
        display_metrics()
        print("\n✓ Insertion réussie!")
