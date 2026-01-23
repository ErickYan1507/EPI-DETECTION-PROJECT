"""
Script de lancement rapide pour l'entraînement YOLOv5 optimisé
"""

import os
import subprocess
import sys

def main():
    print("🚀 LANCEMENT ENTRAÎNEMENT YOLOv5 OPTIMISÉ")
    print("=" * 50)

    # Vérifier si nous sommes dans le bon répertoire
    if not os.path.exists('yolov5'):
        print("❌ Dossier yolov5 non trouvé. Assurez-vous d'avoir cloné YOLOv5.")
        return

    # Vérifier le fichier de données
    if not os.path.exists('data/epi_data.yaml'):
        print("❌ Fichier data/epi_data.yaml non trouvé.")
        return

    # Commande optimisée pour CPU
    cmd = [
        sys.executable, 'yolov5/train.py',
        '--img', '416',
        '--batch', '4',  # Réduit pour mémoire limitée
        '--epochs', '50',  # Réduit pour test rapide
        '--data', 'data/epi_data.yaml',
        '--weights', 'yolov5s.pt',
        '--device', 'cpu',
        '--workers', '2',  # Réduit pour CPU limité
        '--project', 'runs/train',
        '--name', 'epi_cpu_optimized',
        '--cache', 'disk',  # Disk au lieu de RAM pour mémoire limitée
        '--optimizer', 'Adam',
        '--freeze', '10',
        '--save-period', '10',
        '--patience', '20',
        '--rect',
        '--exist-ok'
    ]

    print("Configuration d'entraînement:")
    print(f"  • Taille d'image: 416x416")
    print(f"  • Batch size: 4")
    print(f"  • Epochs: 50")
    print(f"  • Device: CPU")
    print(f"  • Workers: 2")
    print(f"  • Cache: Disk")
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