"""
Script de vérification du système avant entraînement YOLOv5
"""

import os
import sys
import torch
import psutil
import platform

def check_system():
    print("🔍 VÉRIFICATION DU SYSTÈME")
    print("=" * 50)

    # Informations système
    print("Système d'exploitation:", platform.system(), platform.release())
    print("Architecture:", platform.machine())
    print("Python version:", sys.version.split()[0])
    print()

    # Mémoire RAM
    ram = psutil.virtual_memory()
    print(f"RAM totale: {ram.total / 1024**3:.1f} GB")
    print(f"RAM disponible: {ram.available / 1024**3:.1f} GB")
    print()

    # GPU
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        print(f"✅ GPU détecté(s): {gpu_count}")
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"  GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
    else:
        print("❌ Aucun GPU détecté - entraînement CPU uniquement")
    print()

    # Vérifier YOLOv5
    if os.path.exists('yolov5'):
        print("✅ Dossier yolov5 trouvé")
        if os.path.exists('yolov5/train.py'):
            print("✅ Script train.py trouvé")
        else:
            print("❌ Script train.py manquant")
    else:
        print("❌ Dossier yolov5 manquant")
    print()

    # Vérifier les données
    if os.path.exists('data/epi_data.yaml'):
        print("✅ Fichier de configuration data/epi_data.yaml trouvé")
    else:
        print("❌ Fichier de configuration data/epi_data.yaml manquant")
    print()

    # Vérifier les poids
    if os.path.exists('yolov5s.pt'):
        print("✅ Poids yolov5s.pt trouvés")
    else:
        print("⚠️  Poids yolov5s.pt manquants - téléchargement automatique lors du premier entraînement")
    print()

    # Recommandations
    print("📋 RECOMMANDATIONS:")
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        if gpu_memory >= 8:
            print("  • Utilisez quick_train_gpu.py pour un entraînement GPU optimisé")
            print("  • Batch size recommandé: 16-32")
        else:
            print("  • GPU avec mémoire limitée - utilisez batch size réduit")
            print("  • Utilisez quick_train_gpu.py avec ajustements")
    else:
        print("  • Utilisez quick_train_cpu.py pour un entraînement CPU optimisé")
        print("  • Batch size recommandé: 4-8")
        print("  • Envisagez d'augmenter les workers si plus de CPU disponibles")

    if ram.available / 1024**3 < 4:
        print("  • Mémoire RAM faible - utilisez --cache disk au lieu de --cache ram")

    print()
    print("✅ Vérification terminée!")

def main():
    try:
        check_system()
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    main()