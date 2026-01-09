"""Script d'entraînement pour des modèles indépendants"""

import sys
import os
import subprocess
import argparse
import shutil
import time
from pathlib import Path
from datetime import datetime
import json

import torch
from flask import Flask

def setup_flask_app():
    """Initialiser l'application Flask et la base de données"""
    try:
        from config import config
    except ModuleNotFoundError:
        project_root = Path(__file__).resolve().parents[0]
        sys.path.insert(0, str(project_root))
        from config import config
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    return app

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
    """Vérifier la structure du dataset"""
    print("Vérification de la structure du dataset...")
    
    required_dirs = ['images/train', 'images/val', 'images/test', 'labels/train', 'labels/val', 'labels/test']
    for dir_path in required_dirs:
        (Path(dataset_path) / dir_path).mkdir(parents=True, exist_ok=True)
    
    stats = {}
    for split in ['train', 'val']:
        stats[split] = {
            'images': count_images(dataset_path, split),
            'labels': count_labels(dataset_path, split)
        }
    
    train_imgs = stats['train']['images']
    val_imgs = stats['val']['images']
    dataset_size = train_imgs + val_imgs
    
    print(f"\n📊 Statistiques du dataset:")
    print(f"  - Images d'entraînement: {train_imgs}")
    print(f"  - Images de validation: {val_imgs}")
    print(f"  - Total: {dataset_size}")
    
    if train_imgs == 0:
        print("❌ ERREUR: Aucune image d'entraînement trouvée!")
        return False, dataset_size
    
    return True, dataset_size

def detect_num_classes(dataset_path):
    """Détecter le nombre de classes"""
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
    """Créer le fichier data.yaml"""
    detected_nc = detect_num_classes(dataset_path)
    nc = max(len(class_names), detected_nc)
    names = list(class_names) + [f'class_{i}' for i in range(len(class_names), nc)]
    
    yaml_content = f"""path: {os.path.abspath(dataset_path)}
train: images/train
val: images/val
test: images/test

nc: {nc}

names: {names}
"""
    
    yaml_path = Path(dataset_path) / 'data.yaml'
    yaml_path.write_text(yaml_content, encoding='utf-8')
    
    print(f"✓ Fichier data.yaml créé: {yaml_path}")
    return yaml_path

def train_model(data_yaml, session_name, epochs=10, batch_size=8, img_size=640):
    """Lancer l'entraînement YOLOv5"""
    yolov5_dir = Path('yolov5')
    
    if not yolov5_dir.exists():
        print("❌ Dossier yolov5 non trouvé. Veuillez exécuter train.py d'abord pour l'installer.")
        return False, 0

    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    gpu_info = f"\n  - GPU: {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else ""
    
    print("\n" + "="*60)
    print(f"🚀 DÉMARRAGE DE L'ENTRAÎNEMENT INDÉPENDANT: {session_name}")
    print("="*60)
    print(f"📋 Configuration:")
    print(f"  - Modèle base: yolov5s.pt")
    print(f"  - Dataset: {data_yaml}")
    print(f"  - Session: {session_name}")
    print(f"  - Epochs: {epochs}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Image size: {img_size}")
    print(f"  - Device: {device}{gpu_info}")
    
    # Commande d'entraînement YOLOv5
    cmd = [
        sys.executable, str(yolov5_dir / 'train.py'),
        '--weights', 'yolov5s.pt',  # Toujours partir de zéro (ou presque)
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
        # Lancer le processus et afficher la sortie en temps réel
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Afficher la sortie
        for line in process.stdout:
            print(line, end='')
            
        process.wait()
        result = process.returncode
        training_time = time.time() - start_time
        
        if result != 0:
            print(f"❌ Entraînement échoué (code: {result})")
            return False, training_time
    except Exception as e:
        training_time = time.time() - start_time
        print(f"❌ Erreur: {e}")
        return False, training_time
    
    # Sauvegarder le modèle indépendamment
    run_dir = Path(f'runs/train/{session_name}')
    best_model_src = run_dir / 'weights' / 'best.pt'
    
    if best_model_src.exists():
        custom_weights_dir = Path('models/custom_weights')
        custom_weights_dir.mkdir(parents=True, exist_ok=True)
        
        target_name = f"{session_name}.pt"
        target_path = custom_weights_dir / target_name
        
        shutil.copy(best_model_src, target_path)
        print(f"\n✅ Modèle indépendant sauvegardé: {target_path}")
        return True, training_time
    
    return False, training_time

def save_training_results_to_db(
    model_name,
    model_version,
    dataset_name,
    dataset_size,
    epochs,
    batch_size,
    training_dir,
    training_time,
    app,
    db
):
    """Sauvegarder les résultats d'entraînement dans la base de données"""
    try:
        from app.training_logger import log_training_metrics
        
        # Le nom du fichier de poids sauvegardé
        weights_filename = f"{model_name}.pt" if model_name != 'best' else 'best.pt'
        weights_path_final = f"models/custom_weights/{weights_filename}"
        
        with app.app_context():
            success = log_training_metrics(
                model_name=model_name,
                model_version=model_version,
                dataset_name=dataset_name,
                dataset_size=dataset_size,
                epochs=epochs,
                batch_size=batch_size,
                training_dir=training_dir,
                db_session=db.session,
                training_time_seconds=training_time,
                weights_path=weights_path_final,
                model_path=training_dir
            )
            
            if success:
                print("✓ Résultats sauvegardés dans la base de données")
                return True
            else:
                print("✗ Erreur lors de la sauvegarde des résultats")
                return False
                
    except Exception as e:
        print(f"✗ Erreur lors de l'intégration DB: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Entraînement de modèles indépendants')
    parser.add_argument('--name', default=None, help='Nom unique pour ce modèle (défaut: timestamp)')
    parser.add_argument('--dataset', default='dataset', help='Chemin du dataset')
    parser.add_argument('--epochs', type=int, default=50, help='Nombre d\'epochs')
    parser.add_argument('--batch-size', type=int, default=16, help='Taille du batch')
    parser.add_argument('--img-size', type=int, default=640, help='Taille des images')
    
    args = parser.parse_args()
    
    # Générer un nom si non fourni
    if args.name:
        session_name = args.name
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = f"model_{timestamp}"
    
    print("="*70)
    print(f"🧠 ENTRAÎNEMENT MODÈLE INDÉPENDANT: {session_name}")
    print("="*70)
    
    # Étape 1: Vérifier le dataset
    valid, dataset_size = check_dataset_structure(args.dataset)
    if not valid:
        print("\n❌ Structure du dataset incorrecte")
        return
    
    # Étape 2: Créer data.yaml
    data_yaml = create_data_yaml(
        args.dataset,
        ['helmet', 'vest', 'glasses', 'person', 'boots']
    )
    
    # Étape 3: Lancer l'entraînement
    success, training_time = train_model(
        data_yaml,
        session_name,
        args.epochs,
        args.batch_size,
        args.img_size
    )
    
    if success:
        print("\n" + "="*70)
        print("🎉 ENTRAÎNEMENT RÉUSSI !")
        print("="*70)
        
        print("\n💾 Sauvegarde des résultats dans la base de données...")
        app = setup_flask_app()
        
        from app.database import db
        db.init_app(app)
        
        training_dir = f'runs/train/{session_name}'
        
        save_training_results_to_db(
            model_name=session_name,
            model_version='1.0',
            dataset_name=args.dataset,
            dataset_size=dataset_size,
            epochs=args.epochs,
            batch_size=args.batch_size,
            training_dir=training_dir,
            training_time=training_time,
            app=app,
            db=db
        )
        
        print("\n📊 Résultats sauvegardés avec succès!")
        
        print("\n📁 Fichiers générés:")
        print(f"  - models/custom_weights/{session_name}.pt  # Votre modèle indépendant")
        print(f"  - {training_dir}/                           # Logs complets")
        
    else:
        print("\n❌ L'entraînement a échoué.")

if __name__ == '__main__':
    main()
