"""
Script pour reprendre l'entraînement YOLOv5 interrompu
"""

import os
import subprocess
import sys

def resume_training():
    print("🔄 REPRISE ENTRAÎNEMENT YOLOv5")
    print("=" * 50)

    # Vérifier si nous sommes dans le bon répertoire
    if not os.path.exists('yolov5'):
        print("❌ Dossier yolov5 non trouvé.")
        return

    # Chercher le dernier checkpoint
    runs_dir = 'runs/train'
    if os.path.exists(runs_dir):
        subdirs = [d for d in os.listdir(runs_dir) if d.startswith('epi_detection_session_003')]
        if subdirs:
            latest_run = max(subdirs, key=lambda x: os.path.getctime(os.path.join(runs_dir, x)))
            weights_path = f'{runs_dir}/{latest_run}/weights/last.pt'
            if os.path.exists(weights_path):
                print(f"✅ Checkpoint trouvé: {weights_path}")
            else:
                print("⚠️  Aucun checkpoint trouvé, recommencement depuis yolov5s.pt")
                weights_path = 'yolov5s.pt'
        else:
            print("⚠️  Aucun run précédent trouvé, recommencement depuis yolov5s.pt")
            weights_path = 'yolov5s.pt'
    else:
        print("⚠️  Aucun run précédent trouvé, recommencement depuis yolov5s.pt")
        weights_path = 'yolov5s.pt'

    # Commande de reprise optimisée pour CPU
    cmd = [
        sys.executable, 'yolov5/train.py',
        '--resume', weights_path,  # Reprendre depuis le checkpoint
        '--img', '416',
        '--batch', '4',
        '--epochs', '50',
        '--data', 'data/epi_data.yaml',
        '--device', 'cpu',
        '--workers', '2',
        '--project', 'runs/train',
        '--name', 'epi_detection_session_003_resume',  # DEPRECATED: ancien nom 'epi_cpu_optimized_resume'
        '--cache', 'disk',
        '--optimizer', 'Adam',
        '--freeze', '10',
        '--save-period', '10',
        '--patience', '20',
        '--rect',
        '--exist-ok'
    ]

    print("Configuration de reprise:")
    print(f"  • Reprise depuis: {weights_path}")
    print(f"  • Taille d'image: 416x416")
    print(f"  • Batch size: 4")
    print(f"  • Epochs restants: jusqu'à 50")
    print(f"  • Device: CPU")
    print(f"  • Workers: 2")
    print(f"  • Cache: Disk")
    print()

    print("Commande exécutée:")
    print(" ".join(cmd))
    print()

    # Lancer la reprise
    try:
        print("🔥 REPRISE DE L'ENTRAÎNEMENT...")
        print("=" * 50)
        subprocess.run(cmd, cwd='.')
    except KeyboardInterrupt:
        print("\n⏹️  Entraînement interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors de la reprise: {e}")

if __name__ == "__main__":
    resume_training()