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

    # Commande d'entraînement optimisée
    cmd = f"""
    python train.py \\
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

    print("🚀 LANCEMENT ENTRAÎNEMENT ULTRA-RAPIDE")
    print(f"   Batch size: {{batch_size}}")
    print(f"   Image size: {{img_size}}x{{img_size}}")
    print(f"   Epochs: {{epochs}}")
    print("   Cache: RAM activé")
    print("   Workers: 8")
    print("   Freeze: 10 couches")
    print("   Rect: Activé")
    print()
    print("Commande à exécuter:")
    print(cmd)

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
    yaml_path.write_text(content)
    print(f"✅ data.yaml mis à jour")

def print_optimization_guide():
    """Afficher les paramètres optimisés recommandés"""
    print("\n" + "="*70)
    print("⚡ PARAMÈTRES D'ENTRAÎNEMENT OPTIMISÉS")
    print("="*70)
    print("""
📊 COMPARAISON: Avant vs Après
┌─────────────────┬──────────┬───────────┐
│ Paramètre       │ Avant    │ Après     │
├─────────────────┼──────────┼───────────┤
│ Image size      │ 640×640  │ 416×416   │ -57% images
│ Batch size      │ 8-16     │ 32-48     │ Mieux GPU util
│ Workers         │ 8        │ 12-16     │ Chargement + rapide
│ Cache           │ disk     │ ram       │ Lecture directe
│ Epochs/epoch    │ 1554     │ ~600      │ -62% itérations
│ Temps/epoch     │ 3:00h    │ 20-30min  │ -85% gain
└─────────────────┴──────────┴───────────┘

🔧 COMMANDE OPTIMISÉE:
python train.py \\
    --epochs 50 \\
    --batch-size 48 \\
    --img 416 \\
    --optimizer Adam \\
    --workers 16 \\
    --cache ram \\
    --rect \\
    --quad \\
    --cos-lr \\
    --patience 10 \\
    --label-smoothing 0.1

⚠️  NOTES IMPORTANTES:
1. Réduire resolution: 640 → 416 = -62% itérations/epoch
2. Augmenter batch: 8-16 → 32-48 = 2-3x plus rapide
3. Cache RAM: 5-10x plus rapide que disk
4. Patience réduite: 30 → 10 (early stopping)
5. Après optimization: relancer avec resolution 640 si précision insuffisante
""")

def create_optimized_train_script():
    """Créer un script d'entraînement optimisé"""
    script_content = '''#!/usr/bin/env python3
"""Entraînement YOLOv5 OPTIMISÉ pour vitesse maximale"""

import subprocess
import sys
import torch

def main():
    # Paramètres optimisés
    params = {
        'epochs': 50,
        'batch_size': 48,
        'img_size': 416,
        'weights': 'yolov5s.pt',
        'device': 'cuda:0' if torch.cuda.is_available() else 'cpu',
    }
    
    device = params['device']
    if device != 'cpu':
        # Vérifier VRAM disponible
        props = torch.cuda.get_device_properties(0)
        total_memory = props.total_memory / 1e9
        print(f"✅ GPU trouvé: {props.name} ({total_memory:.1f}GB VRAM)")
        
        # Ajuster batch size selon VRAM
        if total_memory < 4:
            params['batch_size'] = 16
            print(f"⚠️  VRAM limitée, batch_size réduit à {params['batch_size']}")
        elif total_memory < 8:
            params['batch_size'] = 32
    
    cmd = [
        sys.executable, 'yolov5/train.py',
        '--weights', params['weights'],
        '--data', 'dataset/data.yaml',
        '--epochs', str(params['epochs']),
        '--batch-size', str(params['batch_size']),
        '--img', str(params['img_size']),
        '--device', device,
        '--project', 'runs/train',
        '--name', 'optimized_training',
        '--exist-ok',
        # OPTIMISATIONS CRITIQUES
        '--optimizer', 'Adam',
        '--rect',
        '--quad',
        '--cos-lr',
        '--cache', 'ram',  # CRUCIAL: mettre en RAM si possible
        '--workers', '16',
        '--patience', '10',
        '--label-smoothing', '0.1',
        '--save-period', '10',  # Sauvegarder tous les 10 epochs
    ]
    
    print(f"\\n🚀 Lancement avec: {' '.join(cmd[2:])}\\n")
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
'''
    
    script_path = Path('quick_train_optimized.py')
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    print(f"✅ Script créé: {script_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Optimisation agressive du temps d\'entraînement')
    parser.add_argument('--resize', action='store_true', help='Redimensionner le dataset')
    parser.add_argument('--size', type=int, default=416, help='Taille cible (default: 416)')
    parser.add_argument('--dataset', default='dataset', help='Chemin du dataset')
    parser.add_argument('--guide', action='store_true', help='Afficher le guide d\'optimisation')
    parser.add_argument('--create-script', action='store_true', help='Créer script d\'entraînement optimisé')
    
    args = parser.parse_args()
    
    if args.guide or (not args.resize and not args.create_script):
        print_optimization_guide()
    
    if args.resize:
        resize_dataset(args.dataset, args.size)
        adjust_yaml_resolution(args.dataset + '/data.yaml', args.size)
    
    if args.create_script:
        create_optimized_train_script()
