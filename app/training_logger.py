"""Module pour enregistrer les résultats d'entraînement/validation/test dans la base de données"""

import json
import os
from pathlib import Path
from datetime import datetime
import csv
from typing import Dict, Optional, Any

def extract_yolov5_metrics(training_dir: str) -> Dict[str, Any]:
    """
    Extraire les métriques d'entraînement YOLOv5 depuis le répertoire results.csv
    
    Args:
        training_dir: Chemin du répertoire d'entraînement YOLOv5
        
    Returns:
        Dictionnaire contenant les métriques extraites
    """
    metrics = {}
    results_csv = Path(training_dir) / 'results.csv'
    
    if not results_csv.exists():
        return metrics
    
    try:
        with open(results_csv, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if not rows:
            return metrics
        
        last_epoch = rows[-1]
        
        # Nettoyer les clés (supprimer les espaces)
        cleaned_row = {k.strip(): v for k, v in last_epoch.items()}
        
        # Mapper les colonnes YOLOv5 aux métriques
        metrics.update({
            'train_loss': float(cleaned_row.get('train/box_loss', 0)) if cleaned_row.get('train/box_loss') else None,
            'train_accuracy': float(cleaned_row.get('metrics/accuracy', 0)) if cleaned_row.get('metrics/accuracy') else None,
            'train_precision': float(cleaned_row.get('metrics/precision', 0)) if cleaned_row.get('metrics/precision') else None,
            'train_recall': float(cleaned_row.get('metrics/recall', 0)) if cleaned_row.get('metrics/recall') else None,
            'val_loss': float(cleaned_row.get('val/box_loss', 0)) if cleaned_row.get('val/box_loss') else None,
            'val_accuracy': float(cleaned_row.get('metrics/mAP_0.5', 0)) if cleaned_row.get('metrics/mAP_0.5') else None,
            'val_precision': float(cleaned_row.get('metrics/precision', 0)) if cleaned_row.get('metrics/precision') else None,
            'val_recall': float(cleaned_row.get('metrics/recall', 0)) if cleaned_row.get('metrics/recall') else None,
        })
        
    except Exception as e:
        print(f"Erreur lors de la lecture de results.csv: {e}")
    
    return metrics

def extract_yolov5_confusion_matrix(training_dir: str) -> Optional[str]:
    """
    Extraire la matrice de confusion depuis le répertoire d'entraînement
    
    Args:
        training_dir: Chemin du répertoire d'entraînement
        
    Returns:
        Matrice de confusion en JSON ou None
    """
    confusion_path = Path(training_dir) / 'confusion_matrix.png'
    # YOLOv5 génère une image, pas un JSON. On pourrait le faire si nécessaire
    # Pour l'instant, on retourne None
    return None

def extract_class_metrics(training_dir: str) -> Optional[str]:
    """
    Extraire les métriques par classe depuis les résultats
    
    Args:
        training_dir: Chemin du répertoire d'entraînement
        
    Returns:
        Métriques par classe en JSON ou None
    """
    try:
        # Chercher le fichier de résultats
        results_csv = Path(training_dir) / 'results.csv'
        
        if not results_csv.exists():
            return None
        
        class_metrics = {}
        
        # YOLOv5 ne sauvegarde pas les métriques par classe dans results.csv
        # mais génère des fichiers dans le répertoire
        # On pourrait les extraire si nécessaire
        
        return json.dumps(class_metrics) if class_metrics else None
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des métriques par classe: {e}")
        return None

def save_training_results(training_data: Dict[str, Any], db_session) -> bool:
    """
    Sauvegarder les résultats d'entraînement dans la base de données
    
    Args:
        training_data: Dictionnaire contenant les données d'entraînement
        db_session: Session SQLAlchemy
        
    Returns:
        True si succès, False sinon
    """
    try:
        from app.database_unified import TrainingResult
        
        result = TrainingResult()
        
        for key, value in training_data.items():
            if hasattr(result, key) and value is not None:
                setattr(result, key, value)
        
        db_session.add(result)
        db_session.commit()
        
        print(f"✓ Résultats d'entraînement sauvegardés (ID: {result.id})")
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors de la sauvegarde: {e}")
        db_session.rollback()
        return False

def get_all_training_results(db_session) -> list:
    """Récupérer tous les résultats d'entraînement"""
    try:
        from app.database_unified import TrainingResult
        results = db_session.query(TrainingResult).order_by(TrainingResult.timestamp.desc()).all()
        return [r.to_dict() for r in results]
    except Exception as e:
        print(f"Erreur lors de la récupération: {e}")
        return []

def get_training_result_by_id(result_id: int, db_session):
    """Récupérer un résultat d'entraînement par ID"""
    try:
        from app.database_unified import TrainingResult
        result = db_session.query(TrainingResult).filter_by(id=result_id).first()
        return result.to_dict() if result else None
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def get_latest_training_result(db_session):
    """Récupérer le résultat d'entraînement le plus récent"""
    try:
        from app.database_unified import TrainingResult
        result = db_session.query(TrainingResult).order_by(
            TrainingResult.timestamp.desc()
        ).first()
        return result.to_dict() if result else None
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def calculate_f1_scores(precision: float, recall: float) -> float:
    """Calculer le score F1"""
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

def log_training_metrics(
    model_name: str,
    model_version: str,
    dataset_name: str,
    epochs: int,
    batch_size: int,
    training_dir: str,
    db_session,
    **kwargs
) -> bool:
    """
    Fonction principale pour enregistrer les métriques d'entraînement
    
    Args:
        model_name: Nom du modèle
        model_version: Version du modèle
        dataset_name: Nom du dataset
        epochs: Nombre d'epochs
        batch_size: Taille du batch
        training_dir: Répertoire d'entraînement
        db_session: Session DB
        **kwargs: Paramètres supplémentaires
        
    Returns:
        True si succès, False sinon
    """
    
    # Extraire les métriques
    metrics = extract_yolov5_metrics(training_dir)
    
    # Calculer F1 scores si possible
    if metrics.get('train_precision') and metrics.get('train_recall'):
        metrics['train_f1_score'] = calculate_f1_scores(
            metrics['train_precision'],
            metrics['train_recall']
        )
    
    if metrics.get('val_precision') and metrics.get('val_recall'):
        metrics['val_f1_score'] = calculate_f1_scores(
            metrics['val_precision'],
            metrics['val_recall']
        )
    
    # Préparer les données
    training_data = {
        'model_name': model_name,
        'model_version': model_version,
        'dataset_name': dataset_name,
        'epochs': epochs,
        'batch_size': batch_size,
        'status': 'completed',
        'timestamp': datetime.utcnow(),
        **metrics,
        **kwargs
    }
    
    # Sauvegarder
    return save_training_results(training_data, db_session)
