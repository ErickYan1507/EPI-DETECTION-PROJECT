"""
Script d'optimisation pour accélérer l'entraînement YOLOv5
Configure tous les paramètres pour maximiser la vitesse d'entraînement
"""

import os
import torch
from pathlib import Path

def optimize_training_speed():
    """Optimise tous les paramètres pour la vitesse d'entraînement maximale"""

    print("🚀 OPTIMISATION DE LA VITESSE D'ENTRAÎNEMENT")
    print("=" * 60)

    # 1. Vérifier le matériel disponible
    print("\n1. 📊 ANALYSE DU MATÉRIEL")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"   Device: {device}")

    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA: {torch.version.cuda}")
        print(f"   Mémoire GPU: {torch.cuda.get_device_properties(0).total_memory // 1024**3} GB")
        gpu_memory = torch.cuda.get_device_properties(0).total_memory // 1024**3
    else:
        print("   ⚠️  Aucun GPU détecté - l'entraînement sera lent")
        gpu_memory = 0

    # 2. Optimisations de configuration
    print("\n2. ⚙️  CONFIGURATIONS OPTIMISÉES")

    # Calculer la taille de batch optimale
    if gpu_memory >= 8:  # 8GB+ GPU
        batch_size = 32
        img_size = 640
    elif gpu_memory >= 4:  # 4-8GB GPU
        batch_size = 16
        img_size = 640
    else:  # CPU ou petit GPU
        batch_size = 8
        img_size = 416

    print(f"   Batch size recommandé: {batch_size}")
    print(f"   Taille d'image: {img_size}x{img_size}")
    print("   Précision: FP16 activée")
    print("   Workers DataLoader: 8")
    print("   Cache images: Activé")
    print("   Freeze backbone: Activé (couches 0-9)")
    print("   Sauvegarde checkpoints: Tous les 10 epochs")

    # 3. Créer le fichier d'optimisation pour YOLOv5
    create_optimized_train_script(batch_size, img_size)

    # 4. Recommandations supplémentaires
    print("\n3. 💡 RECOMMANDATIONS SUPPLÉMENTAIRES")
    print("   • Utilisez --cache ram si vous avez assez de RAM")
    print("   • Désactivez les augmentations lourdes si possible")
    print("   • Utilisez --rect pour des batches rectangulaires")
    print("   • Considérez --evolve pour optimiser les hyperparamètres")

    print("\n4. 🏃‍♂️ SCRIPT D'ENTRAÎNEMENT OPTIMISÉ CRÉÉ")
    print("   Exécutez: python train_ultra_fast.py")

def create_optimized_train_script(batch_size, img_size):
    """Crée un script d'entraînement ultra-optimisé"""

    script_content = f'''"""
Script d'entraînement YOLOv5 ultra-optimisé pour la vitesse maximale
"""

import torch
import os
from pathlib import Path

def main():
    # Configuration optimisée pour la vitesse
    batch_size = {batch_size}
    img_size = {img_size}
    epochs = 100

    print("🚀 LANCEMENT ENTRAÎNEMENT ULTRA-RAPIDE")
    print(f"   Batch size: {{batch_size}}")
    print(f"   Image size: {{img_size}}x{{img_size}}")
    print(f"   Epochs: {{epochs}}")
    print("   Cache: RAM activé")
    print("   Workers: 8")
    print("   Freeze: 10 couches")
    print("   Rect: Activé")

    # Vérifier GPU
    if torch.cuda.is_available():
        print(f"✅ GPU détecté: {{torch.cuda.get_device_name(0)}}")
        print(f"   Mémoire: {{torch.cuda.get_device_properties(0).total_memory // 1024**3}} GB")
    else:
        print("⚠️  Aucun GPU - entraînement sur CPU (sera lent)")

    print("\\n" + "="*60)
    print("💡 ASTUCES DE PERFORMANCE:")
    print("   • Fermez autres applications utilisant le GPU")
    print("   • Surveillez l'utilisation GPU avec nvidia-smi")
    print("   • Si OOM: réduisez batch_size ou img_size")
    print("="*60)

    # Commande d'entraînement optimisée
    cmd = f"""
    python yolov5/train.py \\
        --img {{img_size}} \\
        --batch {{batch_size}} \\
        --epochs {{epochs}} \\
        --data data/epi_data.yaml \\
        --weights yolov5s.pt \\
        --cache ram \\
        --device 0 \\
        --workers 8 \\
        --project runs/train \\
        --name epi_ultra_fast \\
        --hyp data/hyps/hyp.scratch-low.yaml \\
        --optimizer AdamW \\
        --freeze 10 \\
        --save-period 10 \\
        --patience 50 \\
        --rect
    """

    print("\\nCommande à exécuter:")
    print(cmd)

if __name__ == "__main__":
    main()
'''

    with open('train_ultra_fast.py', 'w', encoding='utf-8') as f:
        f.write(script_content)

    print("   ✅ Script train_ultra_fast.py créé")

def create_ultra_fast_config():
    """Crée une configuration ultra-optimisée"""

    config_content = '''# Configuration ultra-optimisée pour vitesse maximale

# Dataset
train: dataset/images/train
val: dataset/images/val
test: dataset/images/test

# Classes
nc: 5
names: ['helmet', 'glasses', 'person', 'vest', 'boots']

# Optimisations de vitesse
cache: ram  # Cache en RAM pour vitesse maximale
'''

    # Créer le dossier data s'il n'existe pas
    os.makedirs('data', exist_ok=True)

    with open('data/epi_ultra_fast.yaml', 'w', encoding='utf-8') as f:
        f.write(config_content)

    print("   ✅ Configuration epi_ultra_fast.yaml créée")

if __name__ == "__main__":
    optimize_training_speed()
    create_ultra_fast_config()