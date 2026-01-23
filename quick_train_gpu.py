"""
Script de lancement rapide pour GPU (si disponible)
"""

import os
import subprocess
import sys
import torch

def main():
    print("🚀 LANCEMENT ENTRAÎNEMENT YOLOv5 GPU OPTIMISÉ")
    print("=" * 50)

    # Vérifier si nous sommes dans le bon répertoire
    if not os.path.exists('yolov5'):
        print("❌ Dossier yolov5 non trouvé. Assurez-vous d'avoir cloné YOLOv5.")
        return

    # Vérifier le fichier de données
    if not os.path.exists('data/epi_data.yaml'):
        print("❌ Fichier data/epi_data.yaml non trouvé.")
        return

    # Détecter GPU
    if torch.cuda.is_available():
        device = '0'  # Premier GPU
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        batch_size = min(16, max(4, int(gpu_memory / 2)))  # Ajuster selon la mémoire
        workers = 8
        cache = 'ram'
        print(f"✅ GPU détecté: {torch.cuda.get_device_name(0)} ({gpu_memory:.1f}GB)")
    else:
        print("❌ Aucun GPU détecté. Utilisez quick_train_cpu.py à la place.")
        return

    # Commande optimisée pour GPU
    cmd = [
        sys.executable, 'yolov5/train.py',
        '--img', '640',
        '--batch', str(batch_size),
        '--epochs', '100',
        '--data', 'data/epi_data.yaml',
        '--weights', 'yolov5s.pt',
        '--device', device,
        '--workers', str(workers),
        '--project', 'runs/train',
        '--name', 'epi_gpu_optimized',
        '--cache', cache,
        '--optimizer', 'AdamW',
        '--freeze', '10',
        '--save-period', '10',
        '--patience', '50',
        '--rect',
        '--exist-ok'
    ]

    print("Configuration d'entraînement:")
    print(f"  • Taille d'image: 640x640")
    print(f"  • Batch size: {batch_size}")
    print(f"  • Epochs: 100")
    print(f"  • Device: GPU ({device})")
    print(f"  • Workers: {workers}")
    print(f"  • Cache: {cache}")
    print(f"  • Freeze: 10 couches")
    print()

    print("Commande exécutée:")
    print(" ".join(cmd))
    print()

    # Lancer l'entraînement
    try:
        print("🔥 DÉMARRAGE DE L'ENTRAÎNEMENT...")
        print("=" * 50)
        subprocess.run(cmd, cwd='.')
    except KeyboardInterrupt:
        print("\n⏹️  Entraînement interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors de l'entraînement: {e}")

if __name__ == "__main__":
    main()