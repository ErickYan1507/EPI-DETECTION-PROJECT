import sys
import os
import subprocess
import argparse
import shutil
import time
import json
import sqlite3
from pathlib import Path
from datetime import datetime

import torch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Import BD unifiée
try:
    from app.database_unified import db, TrainingResult
except ImportError:
    TrainingResult = None
    db = None

def count_images(dataset_path, split='train'):
    """Compter les images d'un split"""
    img_path = Path(dataset_path) / 'images' / split
    if not img_path.exists():
        return 0
    return len(list(img_path.glob('*.[jp][pn][g]*'))) + len(list(img_path.glob('*.jpeg')))

def count_labels(dataset_path, split='train'):
    """Compter les labels d'un split"""
    lbl_path = Path(dataset_path) / 'labels' / split
    return len(list(lbl_path.glob('*.txt'))) if lbl_path.exists() else 0

def check_dataset_structure(dataset_path):
    """Vérifier la structure du dataset et compter les fichiers"""
    print("Vérification de la structure du dataset...")
    
    # Créer les répertoires manquants
    required_dirs = ['images/train', 'images/val', 'images/test', 'labels/train', 'labels/val', 'labels/test']
    for dir_path in required_dirs:
        (Path(dataset_path) / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Compter les images et labels
    stats = {}
    for split in ['train', 'val']:
        stats[split] = {
            'images': count_images(dataset_path, split),
            'labels': count_labels(dataset_path, split)
        }
    
    train_imgs, train_lbls = stats['train']['images'], stats['train']['labels']
    val_imgs, val_lbls = stats['val']['images'], stats['val']['labels']
    
    print(f"\n📊 Statistiques du dataset:")
    print(f"  - Images d'entraînement: {train_imgs}")
    print(f"  - Images de validation: {val_imgs}")
    print(f"  - Labels d'entraînement: {train_lbls}")
    print(f"  - Labels de validation: {val_lbls}")
    
    if train_imgs == 0:
        print("❌ ERREUR: Aucune image d'entraînement trouvée!")
        return False
    
    if train_imgs != train_lbls or val_imgs != val_lbls:
        print(f"⚠️  Attention: mismatch images/labels")
    
    return True

def detect_num_classes(dataset_path):
    """Détecter le nombre de classes à partir des labels"""
    max_label = -1
    labels_dir = Path(dataset_path) / 'labels'
    
    if not labels_dir.exists():
        return 0
    
    for f in labels_dir.rglob('*.txt'):
        for line in f.read_text(encoding='utf-8').splitlines():
            try:
                cls = int(float(line.split()[0]))
                max_label = max(max_label, cls)
            except (ValueError, IndexError):
                continue
    
    return max_label + 1

def create_data_yaml(dataset_path, class_names):
    """Créer le fichier data.yaml pour YOLOv5"""
    # Utiliser seulement les classes spécifiées
    nc = len(class_names)
    names = list(class_names)
    
    yaml_content = f"""# Dataset EPI Detection
path: {os.path.abspath(dataset_path)}
train: images/train
val: images/val
test: images/test

# Number of classes
nc: {nc}

# Class names
names: {names}
"""
    
    yaml_path = Path(dataset_path) / 'data.yaml'
    yaml_path.write_text(yaml_content, encoding='utf-8')
    
    print(f"✓ Fichier data.yaml créé: {yaml_path}")
    print("\n📄 Contenu de data.yaml:")
    print("-" * 40)
    print(yaml_content)
    print("-" * 40)
    
    return yaml_path

def install_yolov5_local():
    """Vérifier ou installer YOLOv5 localement"""
    yolov5_dir = Path('yolov5')
    
    if yolov5_dir.exists():
        print("✓ YOLOv5 trouvé localement")
        return True
    
    print("📥 Installation de YOLOv5...")
    
    # Essayer git clone
    try:
        subprocess.run(['git', 'clone', 'https://github.com/ultralytics/yolov5.git'],
                      check=True, capture_output=True, text=True, timeout=60)
        print("✓ YOLOv5 cloné depuis GitHub")
        return True
    except Exception:
        print("⚠️  Git clone échoué, tentative de téléchargement...")
    
    # Téléchargement direct
    try:
        import urllib.request, zipfile
        url = "https://github.com/ultralytics/yolov5/archive/refs/tags/v7.0.zip"
        zip_path = "yolov5.zip"
        
        print(f"Téléchargement de {url}...")
        urllib.request.urlretrieve(url, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as f:
            f.extractall()
        os.rename("yolov5-7.0", "yolov5")
        os.remove(zip_path)
        print("✓ YOLOv5 téléchargé et extrait")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def init_sqlite(results_dir='training_results'):
    """Initialiser la base de données SQLite locale"""
    results_path = Path(results_dir)
    results_path.mkdir(exist_ok=True)
    
    sqlite_db = results_path / 'training_results.db'
    conn = sqlite3.connect(str(sqlite_db))
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_number INTEGER NOT NULL UNIQUE,
            model_name TEXT,
            model_version TEXT,
            dataset_name TEXT,
            dataset_size INTEGER,
            epochs INTEGER,
            batch_size INTEGER,
            train_loss REAL,
            val_loss REAL,
            training_time_seconds REAL,
            status TEXT DEFAULT 'completed',
            model_path TEXT,
            weights_path TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    return str(sqlite_db)

def get_next_session_number(sqlite_db):
    """Obtenir le numéro de session suivant"""
    try:
        conn = sqlite3.connect(sqlite_db)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(session_number) FROM training_sessions")
        result = cursor.fetchone()
        conn.close()
        
        return 1 if result[0] is None else result[0] + 1
    except Exception:
        return 1

def save_to_sqlite(sqlite_db, session_number, session_data):
    """Sauvegarder les résultats dans SQLite"""
    try:
        conn = sqlite3.connect(sqlite_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO training_sessions (
                session_number, model_name, model_version, dataset_name, dataset_size,
                epochs, batch_size, training_time_seconds, status, model_path, 
                weights_path, started_at, completed_at, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_number,
            session_data.get('model_name', 'YOLOv5s-EPI'),
            session_data.get('model_version', '1.0'),
            session_data.get('dataset_name', ''),
            session_data.get('dataset_size', 0),
            session_data.get('epochs', 0),
            session_data.get('batch_size', 0),
            session_data.get('training_time', 0),
            'completed',
            session_data.get('training_dir', ''),
            session_data.get('weights_path', ''),
            session_data.get('started_at', ''),
            session_data.get('completed_at', ''),
            session_data.get('notes', '')
        ))
        
        conn.commit()
        conn.close()
        print(f"✓ Résultats sauvegardés SQLite: Session #{session_number:03d}")
        return True
    except Exception as e:
        print(f"⚠️ Erreur SQLite: {e}")
        return False

def save_to_json(results_dir, session_number, session_data):
    """Exporter les résultats en JSON"""
    try:
        results_path = Path(results_dir)
        results_path.mkdir(exist_ok=True)
        
        session_file = results_path / f'session_{session_number:03d}_results.json'
        export_data = {
            'session_number': session_number,
            'timestamp': datetime.now().isoformat(),
            'data': session_data
        }
        
        session_file.write_text(json.dumps(export_data, indent=2))
        print(f"✓ Résultats exportés JSON: {session_file}")
        return True
    except Exception as e:
        print(f"⚠️ Erreur JSON: {e}")
        return False

def save_to_unified_db(session_number, session_data):
    """Sauvegarder les résultats dans la BD unifiée"""
    try:
        if not TrainingResult or not db:
            print("⚠️  BD unifiée non disponible (app.database_unified non importé)")
            return False
            
        from config import config
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        
        with app.app_context():
            # Préparer les données
            class_names = session_data.get('class_names', ['helmet', 'glasses', 'person', 'vest', 'boots'])
            
            # Créer le résultat d'entraînement
            result = TrainingResult(
                model_name=session_data.get('model_name', 'YOLOv5s-EPI'),
                model_version=session_data.get('model_version', '1.0'),
                model_family='YOLOv5',
                dataset_name=session_data.get('dataset_name', 'EPI Dataset'),
                dataset_path=session_data.get('dataset_path', 'dataset'),
                dataset_size=session_data.get('dataset_size', 0),
                num_classes=len(class_names),
                class_names=json.dumps(class_names),
                
                # Configuration d'entraînement
                epochs=session_data.get('epochs', 0),
                batch_size=session_data.get('batch_size', 0),
                image_size=session_data.get('img_size', 640),
                learning_rate=session_data.get('learning_rate', 0.001),
                optimizer=session_data.get('optimizer', 'SGD'),
                loss_function='YOLOv5Loss',
                patience=session_data.get('patience', 30),
                
                # Métriques d'entraînement
                train_loss=session_data.get('train_loss'),
                train_accuracy=session_data.get('train_accuracy'),
                train_precision=session_data.get('train_precision'),
                train_recall=session_data.get('train_recall'),
                train_f1_score=session_data.get('train_f1_score'),
                
                # Métriques de validation
                val_loss=session_data.get('val_loss'),
                val_accuracy=session_data.get('val_accuracy'),
                val_precision=session_data.get('val_precision'),
                val_recall=session_data.get('val_recall'),
                val_f1_score=session_data.get('val_f1_score'),
                
                # Métriques de test (optionnel)
                test_loss=session_data.get('test_loss'),
                test_accuracy=session_data.get('test_accuracy'),
                test_precision=session_data.get('test_precision'),
                test_recall=session_data.get('test_recall'),
                test_f1_score=session_data.get('test_f1_score'),
                
                # Données détaillées
                class_metrics=json.dumps(session_data.get('class_metrics', {})),
                confusion_matrix=json.dumps(session_data.get('confusion_matrix', [])),
                epoch_losses=json.dumps(session_data.get('epoch_losses', [])),
                
                # Performance
                training_time_seconds=session_data.get('training_time', 0),
                inference_time_ms=session_data.get('inference_time_ms'),
                fps=session_data.get('fps'),
                gpu_memory_mb=session_data.get('gpu_memory_mb'),
                
                # Artifacts
                model_path=session_data.get('training_dir'),
                weights_path=session_data.get('weights_path'),
                metrics_plot_path=session_data.get('metrics_plot_path'),
                confusion_matrix_plot_path=session_data.get('confusion_matrix_plot_path'),
                training_log_path=session_data.get('training_log_path'),
                
                # Status
                status='completed',
                notes=f"Training Session #{session_number:03d} - {session_data.get('notes', '')}"
            )
            
            db.session.add(result)
            db.session.commit()
            print(f"✅ Résultats sauvegardés BD Unifiée: Session #{session_number:03d} (ID: {result.id})")
            return True
    except Exception as e:
        print(f"⚠️  Erreur sauvegarde BD unifiée: {e}")
        import traceback
        traceback.print_exc()
        return False

def save_to_mysql(session_number, session_data):
    """Sauvegarder dans MySQL (via Flask) - LEGACY"""
    # Utiliser la BD unifiée à la place
    return save_to_unified_db(session_number, session_data)

def train_model(data_yaml, epochs=10, batch_size=8, img_size=640, weights='yolov5s.pt', retry_with_reduced_batch=True, session_name='epi_detection_v1'):
    """Lancer l'entraînement avec YOLOv5"""
    yolov5_dir = Path('yolov5')
    
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    gpu_info = f"\n  - GPU: {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else ""
    
    import psutil
    mem = psutil.virtual_memory()
    available_gb = mem.available / (1024**3)
    
    if available_gb < batch_size * 0.5 and device == 'cpu':
        print(f"⚠️  Mémoire disponible: {available_gb:.1f}GB, batch_size={batch_size} peut causer un crash")
        if retry_with_reduced_batch and batch_size > 4:
            new_batch_size = max(4, batch_size // 2)
            print(f"🔄 Réduction du batch_size: {batch_size} -> {new_batch_size}")
            return train_model(data_yaml, epochs, new_batch_size, img_size, weights=weights, retry_with_reduced_batch=False, session_name=session_name)
    
    print("\n" + "="*60)
    print("🚀 DÉMARRAGE DE L'ENTRAÎNEMENT YOLOv5")
    print("="*60)
    print(f"📋 Configuration:")
    print(f"  - Modèle: {weights}")
    print(f"  - Dataset: {data_yaml}")
    print(f"  - Epochs: {epochs}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Image size: {img_size}")
    print(f"  - Device: {device}{gpu_info}")
    print(f"\n⏳ Entraînement en cours (voir runs/train/)")
    
    if not yolov5_dir.exists():
        print("⚠️  YOLOv5 non trouvé, installation...")
        if not install_yolov5_local():
            print("❌ Installation YOLOv5 échouée")
            return False, 0
    
    cmd = [
        sys.executable, str(yolov5_dir / 'train.py'),
        '--weights', weights,
        '--data', str(data_yaml),
        '--epochs', str(epochs),
        '--batch-size', str(batch_size),
        '--img', str(img_size),
        '--device', device,
        '--project', 'runs/train',
        '--name', session_name,
        '--exist-ok'
    ]
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=False)
        training_time = time.time() - start_time
        if result.returncode != 0:
            print(f"❌ Entraînement échoué (code: {result.returncode})")
            return False, training_time
    except Exception as e:
        training_time = time.time() - start_time
        print(f"❌ Erreur: {e}")
        return False, training_time
    
    best_model = Path(f'runs/train/{session_name}/weights/best.pt')
    if best_model.exists():
        models_dir = Path('models')
        models_dir.mkdir(exist_ok=True)
        #MODIFICATION ICI
        print(f"\n✅ Modèle disponible: {best_model}")
        return True, training_time
    
    return False, training_time

def main():
    """Pipeline complet d'entraînement"""
    parser = argparse.ArgumentParser(description='Entraînement YOLOv5 pour détection EPI')
    parser.add_argument('--dataset', default='dataset', help='Chemin du dataset')
    parser.add_argument('--epochs', type=int, default=100, help='Nombre d\'epochs')
    parser.add_argument('--batch-size', type=int, default=16, help='Taille du batch')
    parser.add_argument('--img-size', type=int, default=640, help='Taille des images')
    parser.add_argument('--weights', type=str, default='yolov5s.pt', help='Chemin des poids initiaux')
    parser.add_argument('--run-name', type=str, default=None, help='Nom de l\'exécution pour sauvegarder le modèle')
    parser.add_argument('--classes', nargs='+', default=['helmet', 'glasses', 'person', 'vest', 'boots'],
                       help='Noms des classes')
    parser.add_argument('--num-trainings', type=int, default=1, help='Nombre d\'entraînements successifs')
    parser.add_argument('--results-dir', default='training_results', help='Répertoire des résultats')
    parser.add_argument('--model-name', default='YOLOv5s-EPI', help='Nom du modèle')
    parser.add_argument('--model-version', default='1.0', help='Version du modèle')
    
    args = parser.parse_args()
    
    sqlite_db = init_sqlite(args.results_dir)
    
    print("="*70)
    if args.num_trainings == 1:
        print("🧠 ENTRAÎNEMENT MODÈLE DE DÉTECTION EPI")
    else:
        print(f"🧠 ENTRAÎNEMENTS MULTIPLES - {args.num_trainings} sessions")
    print("="*70)
    
    # Étape 1: Vérifier le dataset
    if not check_dataset_structure(args.dataset):
        print("\n❌ Structure du dataset incorrecte")
        print("\n📁 Structure attendue:")
        print("  dataset/")
        print("  ├── images/train/   # Images d'entraînement")
        print("  ├── images/val/     # Images de validation")
        print("  └── labels/train/   # Labels YOLO (.txt)")
        return
    
    # Étape 2: Créer data.yaml
    data_yaml = create_data_yaml(args.dataset, args.classes)
    
    # Étape 3: Installer YOLOv5
    if not install_yolov5_local():
        print("❌ Installation YOLOv5 échouée")
        return
    
    # Boucle des entraînements multiples
    results_summary = []
    
    for train_idx in range(1, args.num_trainings + 1):
        session_number = get_next_session_number(sqlite_db)
        
        if args.run_name:
            session_name = args.run_name
            if args.num_trainings > 1:
                session_name += f"_{train_idx}"
        else:
            session_name = f"epi_detection_session_{session_number:03d}"
        
        if args.num_trainings > 1:
            print(f"\n📍 Session {train_idx}/{args.num_trainings} (nom: {session_name})")
        
        session_start = datetime.now()
        success, training_time = train_model(
            data_yaml, 
            args.epochs, 
            args.batch_size, 
            args.img_size, 
            weights=args.weights,
            session_name=session_name
        )
        
        if success:
            print("\n" + "="*70)
            print(f"✅ ENTRAÎNEMENT SESSION '{session_name}' RÉUSSI !")
            print("="*70)
            
            # Copier le modèle
            training_dir = Path(f'runs/train/{session_name}')
            best_model = training_dir / 'weights' / 'best.pt'
            
            #MODIFICATION
            # model_save_path = Path(args.results_dir) / 'models' / f'{session_name}.pt'

            if best_model.exists():
                session_models_dir = Path(args.results_dir) / 'models' / f'session_{session_number:03d}'
                session_models_dir.mkdir(parents=True, exist_ok=True)
                
                dest_model = session_models_dir / 'best.pt'
                shutil.copy(best_model, dest_model)
                print(f"✓ Modèle copié: {dest_model}")

                #MODIFICATION
                # shutil.copy(best_model, model_save_path)
                # print(f"✓ Modèle sauvegardé dans models/: {model_save_path}")
            
            # Préparer les données de session
            session_data = {
                'session_number': session_number,
                'model_name': args.model_name,
                'model_version': args.model_version,
                'dataset_name': args.dataset,
                'dataset_size': 0,
                'epochs': args.epochs,
                'batch_size': args.batch_size,
                'training_time': training_time,
                'training_dir': str(training_dir),
                'weights_path': str(dest_model if best_model.exists() else ''),
                'started_at': session_start.isoformat(),
                'completed_at': datetime.now().isoformat()
            }
            
            # Sauvegarder dans SQLite
            save_to_sqlite(sqlite_db, session_number, session_data)
            
            # Sauvegarder dans MySQL
            save_to_mysql(session_number, session_data)
            
            # Exporter en JSON
            save_to_json(args.results_dir, session_number, session_data)
            
            results_summary.append({
                'session': session_name,
                'status': 'completed',
                'time': training_time
            })
        else:
            print(f"\n❌ SESSION '{session_name}' ÉCHOUÉE")
            results_summary.append({
                'session': session_name,
                'status': 'failed',
                'time': training_time
            })
    
    # Résumé final
    if args.num_trainings > 1:
        print(f"\n{'='*70}")
        print("📊 RÉSUMÉ DES ENTRAÎNEMENTS")
        print(f"{'='*70}")
        
        completed = sum(1 for r in results_summary if r['status'] == 'completed')
        failed = sum(1 for r in results_summary if r['status'] == 'failed')
        total_time = sum(r['time'] for r in results_summary)
        
        for result in results_summary:
            status_icon = "✅" if result['status'] == 'completed' else "❌"
            print(f"  {status_icon} Session '{result['session']}': {result['status']} ({result['time']:.2f}s)")
        
        print(f"\n  Résumé:")
        print(f"  - Complétées: {completed}")
        print(f"  - Échouées: {failed}")
        print(f"  - Temps total: {total_time:.2f}s ({total_time/3600:.2f}h)")
    
    print(f"\n💾 Résultats sauvegardés dans:")
    print(f"  - SQLite: {sqlite_db}")
    print(f"  - Modèles: {Path(args.results_dir) / 'models'}")
    print(f"  - JSON: {Path(args.results_dir) / 'session_*_results.json'}")

if __name__ == '__main__':
    main()