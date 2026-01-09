"""
Module pour intégrer les résultats d'entraînement YOLOv5 dans la BD unifiée
Réutilisé par train.py pour sauvegarder directement les résultats
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import csv

from flask import Flask
from app.database_unified import db, TrainingResult

def parse_yolo_results_csv(results_csv_path, class_names=None):
    """
    Parser le fichier results.csv de YOLOv5
    Retourne un dict avec les métriques extraites
    """
    if not Path(results_csv_path).exists():
        return None
    
    try:
        with open(results_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            return None
        
        # Prendre la dernière epoch (complète)
        last_row = rows[-1]
        
        # Nettoyage des espaces
        cleaned = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in last_row.items()}
        
        # Extraction des métriques
        metrics = {
            'epochs': len(rows),
            'train_loss': safe_float(cleaned.get('train/box_loss')),
            'train_accuracy': safe_float(cleaned.get('metrics/mAP_0.5')),
            'train_precision': safe_float(cleaned.get('metrics/precision')),
            'train_recall': safe_float(cleaned.get('metrics/recall')),
            'train_f1_score': None,
            
            'val_loss': safe_float(cleaned.get('val/box_loss')),
            'val_accuracy': safe_float(cleaned.get('metrics/mAP_0.5:0.95')),
            'val_precision': safe_float(cleaned.get('metrics/precision')),
            'val_recall': safe_float(cleaned.get('metrics/recall')),
            'val_f1_score': None,
            
            'class_names': class_names or ['helmet', 'vest', 'glasses', 'person'],
            'num_classes': len(class_names) if class_names else 4
        }
        
        return metrics
    except Exception as e:
        print(f"❌ Erreur parsing CSV: {e}")
        return None


def safe_float(value):
    """Convertir une valeur en float de manière sûre"""
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def save_training_to_db(
    model_name='YOLOv5s-EPI',
    model_version='1.0',
    dataset_name='dataset',
    dataset_path='dataset',
    training_dir='runs/train/epi_detection_v1',
    weights_path='models/best.pt',
    epochs=100,
    batch_size=16,
    image_size=320,
    learning_rate=0.001,
    optimizer='SGD',
    training_time_seconds=0,
    inference_time_ms=0,
    fps=None,
    class_names=None,
    notes='',
    app_context=None
):
    """
    Sauvegarder un résultat d'entraînement dans la BD unifiée
    
    Args:
        model_name: nom du modèle
        model_version: version du modèle
        dataset_name: nom du dataset
        dataset_path: chemin du dataset
        training_dir: répertoire d'entraînement (pour chercher results.csv)
        weights_path: chemin du fichier de poids
        epochs: nombre d'epochs
        batch_size: taille du batch
        image_size: taille des images
        learning_rate: taux d'apprentissage
        optimizer: optimiseur utilisé
        training_time_seconds: temps d'entraînement
        inference_time_ms: temps d'inférence moyen
        fps: FPS (images/sec)
        class_names: noms des classes
        notes: notes additionnelles
        app_context: contexte Flask (si None, crée un nouveau)
    """
    
    # Parser les résultats
    results_csv = Path(training_dir) / 'results.csv'
    metrics = parse_yolo_results_csv(str(results_csv), class_names)
    
    if metrics is None:
        print(f"⚠️  Pas de résultats trouvés dans {results_csv}")
        metrics = {}
    
    # Créer le contexte Flask s'il n'existe pas
    if app_context is None:
        from config import config
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = getattr(config, 'SQLALCHEMY_ENGINE_OPTIONS', {})
        db.init_app(app)
        app_context = app
        use_context = True
    else:
        use_context = False
    
    try:
        with app_context.app_context():
            # Créer le résultat d'entraînement
            result = TrainingResult(
                model_name=model_name,
                model_version=model_version,
                model_family='YOLOv5',
                dataset_name=dataset_name,
                dataset_path=dataset_path,
                dataset_size=0,  # À remplir manuellement si disponible
                
                epochs=epochs or metrics.get('epochs'),
                batch_size=batch_size,
                image_size=image_size,
                learning_rate=learning_rate,
                optimizer=optimizer,
                loss_function='BCE+Smooth L1',
                
                train_loss=metrics.get('train_loss'),
                train_accuracy=metrics.get('train_accuracy'),
                train_precision=metrics.get('train_precision'),
                train_recall=metrics.get('train_recall'),
                train_f1_score=metrics.get('train_f1_score'),
                
                val_loss=metrics.get('val_loss'),
                val_accuracy=metrics.get('val_accuracy'),
                val_precision=metrics.get('val_precision'),
                val_recall=metrics.get('val_recall'),
                val_f1_score=metrics.get('val_f1_score'),
                
                class_names=json.dumps(metrics.get('class_names', class_names or [])),
                num_classes=metrics.get('num_classes', len(class_names) if class_names else 4),
                
                training_time_seconds=training_time_seconds,
                inference_time_ms=inference_time_ms,
                fps=fps,
                
                weights_path=weights_path,
                model_path=str(Path(training_dir) / 'weights' / 'best.pt'),
                training_log_path=str(results_csv),
                
                status='completed',
                notes=notes,
                
                timestamp=datetime.utcnow()
            )
            
            db.session.add(result)
            db.session.commit()
            
            print(f"✅ Résultat d'entraînement sauvegardé (ID: {result.id})")
            return result.id
            
    except Exception as e:
        print(f"❌ Erreur sauvegarde BD: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if use_context and app_context:
            with app_context.app_context():
                db.session.close()


def import_all_training_results_to_db(app_context=None):
    """
    Importer TOUS les résultats d'entraînement existants depuis le dossier runs/train
    vers la BD unifiée
    """
    from pathlib import Path
    
    training_dir = Path('runs/train')
    
    if not training_dir.exists():
        print(f"❌ Dossier {training_dir} non trouvé")
        return 0
    
    imported_count = 0
    
    # Parcourir tous les sous-dossiers
    for session_dir in sorted(training_dir.iterdir()):
        if not session_dir.is_dir():
            continue
        
        results_csv = session_dir / 'results.csv'
        weights_file = session_dir / 'weights' / 'best.pt'
        
        if not results_csv.exists():
            print(f"⚠️  Pas de results.csv dans {session_dir}")
            continue
        
        print(f"\n📥 Import: {session_dir.name}")
        
        training_id = save_training_to_db(
            model_name=f'YOLOv5-{session_dir.name}',
            model_version='1.0',
            dataset_name='dataset',
            dataset_path='dataset',
            training_dir=str(session_dir),
            weights_path=str(weights_file) if weights_file.exists() else '',
            notes=f'Imported from {session_dir.name}'
        )
        
        if training_id:
            imported_count += 1
    
    print(f"\n✅ {imported_count} résultats d'entraînement importés")
    return imported_count


if __name__ == '__main__':
    # Test/exemple
    import_all_training_results_to_db()
