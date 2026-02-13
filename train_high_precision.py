"""
Script d'entraînement YOLOv5 optimisé pour PRÉCISION MAXIMALE
Utilise yolov5m.pt, epochs=100, img_size=640, optimisations avancées
"""

import sys
import os
import subprocess
import time
from pathlib import Path
import torch

def train_high_precision():
    """Entraînement haute précision pour EPI Detection (100 epochs, 640px)"""

    # Configuration pour précision maximale
    config = {
        'weights': 'yolov5m.pt',  # Modèle medium pour meilleur équilibre précision/vitesse
        'data': 'data/data.yaml',
        'epochs': 100,  # 100 epochs pour bon équilibre temps/précision
        'batch_size': 8,  # Batch plus petit pour stabilité
        'img_size': 640,  # Taille d'image standard optimisée
        'device': 'cuda:0' if torch.cuda.is_available() else 'cpu',
        'project': 'runs/train',
        'name': 'epi_detection_session_003',  # DEPRECATED: ancien nom 'epi_high_precision'
        'hyp': 'yolov5/data/hyps/hyp.scratch-high.yaml',  # Hyperparamètres pour haute précision
    }

    yolov5_dir = Path('yolov5')
    if not yolov5_dir.exists():
        print("❌ YOLOv5 non trouvé. Exécutez d'abord train.py pour l'installer.")
        return False

    print("🚀 DÉMARRAGE ENTRAÎNEMENT HAUTE PRÉCISION")
    print("="*60)
    for k, v in config.items():
        print(f"  {k}: {v}")

    # Commande d'entraînement optimisée pour précision
    cmd = [
        sys.executable, str(yolov5_dir / 'train.py'),
        '--weights', config['weights'],
        '--data', config['data'],
        '--epochs', str(config['epochs']),
        '--batch-size', str(config['batch_size']),
        '--imgsz', str(config['img_size']),
        '--device', config['device'],
        '--project', config['project'],
        '--name', config['name'],
        '--exist-ok',

        # Optimisations pour précision maximale
        '--optimizer', 'AdamW',
        '--rect',
        '--cos-lr',
        '--cache', 'ram',
        '--workers', '8',
        '--patience', '100',  # Patience élevée
        '--label-smoothing', '0.1',
        '--multi-scale',
        '--freeze', '10',  # Fine-tuning
        '--hyp', config['hyp'],
    ]

    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=True)
        training_time = time.time() - start_time
        print(f"✅ Entraînement terminé en {training_time:.1f}s")
        return True
    except subprocess.CalledProcessError as e:
        training_time = time.time() - start_time
        print(f"❌ Entraînement échoué: {e}")
        return False
    except Exception as e:
        training_time = time.time() - start_time
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = train_high_precision()
    if success:
        print("\n✅ Entraînement haute précision terminé avec succès!")
        print("📁 Résultats dans: runs/train/epi_detection_session_003/")
        print("🏆 Modèle sauvegardé dans: models/best.pt")
    else:
        print("\n❌ Échec de l'entraînement haute précision")
        sys.exit(1)