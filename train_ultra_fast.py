"""
Script d'entraînement YOLOv5 ultra-optimisé pour la vitesse maximale
"""

import torch
import os
from pathlib import Path

def main():
    # Configuration optimisée pour la vitesse
    batch_size = 8
    img_size = 416
    epochs = 100

    print("🚀 LANCEMENT ENTRAÎNEMENT ULTRA-RAPIDE")
    print(f"   Batch size: {batch_size}")
    print(f"   Image size: {img_size}x{img_size}")
    print(f"   Epochs: {epochs}")
    print("   Cache: RAM activé")
    print("   Workers: 8")
    print("   Freeze: 10 couches")
    print("   Rect: Activé")

    # Vérifier GPU
    if torch.cuda.is_available():
        print(f"✅ GPU détecté: {torch.cuda.get_device_name(0)}")
        print(f"   Mémoire: {torch.cuda.get_device_properties(0).total_memory // 1024**3} GB")
    else:
        print("⚠️  Aucun GPU - entraînement sur CPU (sera lent)")

    print("\n" + "="*60)
    print("💡 ASTUCES DE PERFORMANCE:")
    print("   • Fermez autres applications utilisant le GPU")
    print("   • Surveillez l'utilisation GPU avec nvidia-smi")
    print("   • Si OOM: réduisez batch_size ou img_size")
    print("="*60)

    # Commande d'entraînement optimisée
    cmd = f"""
    python yolov5/train.py \
        --img {img_size} \
        --batch {batch_size} \
        --epochs {epochs} \
        --data data/epi_data.yaml \
        --weights yolov5s.pt \
        --cache ram \
        --device 0 \
        --workers 8 \
        --project runs/train \
        --name epi_ultra_fast \
        --hyp data/hyps/hyp.scratch-low.yaml \
        --optimizer AdamW \
        --freeze 10 \
        --save-period 10 \
        --patience 50 \
        --rect
    """

    print("\nCommande à exécuter:")
    print(cmd)

if __name__ == "__main__":
    main()
