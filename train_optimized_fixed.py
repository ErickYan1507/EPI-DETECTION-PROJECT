#!/usr/bin/env python3
"""
Entraînement optimisé avec hyperparamètres corrigés
- Taux d'apprentissage plus agressif
- Patience réduite
- Data augmentation améliorée
- Monitoring de mAP
"""

import sys
import subprocess
from pathlib import Path
import torch
import json
from datetime import datetime

def train_optimized():
    """Entraînement avec hyperparamètres optimisés"""
    
    print("\n" + "="*70)
    print("🚀 ENTRAÎNEMENT OPTIMISÉ - mAP FAIBLE → HAUTE")
    print("="*70)
    
    yolov5_dir = Path('yolov5')
    if not yolov5_dir.exists():
        print("❌ yolov5 non trouvé!")
        return False
    
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    gpu_info = f"GPU: {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else "CPU"
    
    print(f"\n📋 Configuration d'entraînement optimisée:")
    print(f"  Device: {gpu_info}")
    print(f"  Modèle de base: yolov5s.pt")
    print(f"  Dataset: dataset/data.yaml (5571 train, 2015 val images)")
    print(f"  Epochs: 200 (long entraînement)")
    print(f"  Batch size: 32 (agressif)")
    print(f"  Image size: 640")
    print(f"  Learning rate: 0.01 (SGD)")
    print(f"  Patience: 50 (early stopping)")
    print(f"\n⚡ Data augmentation:")
    print(f"  - HSV: h=0.015, s=0.7, v=0.4")
    print(f"  - Rotation: ±10°")
    print(f"  - Flip: h=0.5, v=0.5")
    print(f"  - Mosaic: 1.0, Mixup: 0.1")
    print(f"  - Cache: RAM (plus rapide)")
    
    # Commande d'entraînement YOLO optimisée
    cmd = [
        sys.executable, str(yolov5_dir / 'train.py'),
        '--weights', 'yolov5s.pt',
        '--data', 'dataset/data.yaml',
        '--epochs', '200',
        '--batch-size', '32',
        '--img', '640',
        '--device', device,
        '--project', 'runs/train',
        '--name', 'epi_optimized_training',
        '--exist-ok',
        '--save-period', '20',  # Sauvegarder tous les 20 epochs
        '--patience', '50',  # Early stopping patience
        '--cache', 'ram',  # Cache en RAM
        '--workers', '8',
        
        # Data augmentation
        '--hsv-h', '0.015',
        '--hsv-s', '0.7',
        '--hsv-v', '0.4',
        '--degrees', '10',
        '--translate', '0.1',
        '--scale', '0.5',
        '--flipud', '0.5',
        '--fliplr', '0.5',
        '--mosaic', '1.0',
        '--mixup', '0.1',
        
        # Optimisation
        '--cos-lr',  # Cosine learning rate
        '--label-smoothing', '0.1',
        '--warmup-epochs', '5',
        
        # Suivi et logs
        '--plots',
    ]
    
    print(f"\n⏳ Démarrage de l'entraînement...")
    print(f"   Ceci peut prendre 2-4 heures selon la GPU")
    print(f"   Surveiller: runs/train/epi_optimized_training/")
    
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print(f"\n✅ ENTRAÎNEMENT RÉUSSI!")
            
            # Copier le meilleur modèle
            best_model = Path('runs/train/epi_optimized_training/weights/best.pt')
            if best_model.exists():
                import shutil
                shutil.copy(best_model, Path('models/best.pt'))
                print(f"✅ Modèle sauvegardé: models/best.pt")
            
            return True
        else:
            print(f"\n❌ Entraînement échoué (code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

def check_training_results():
    """Vérifier et analyser les résultats d'entraînement"""
    print("\n" + "="*70)
    print("📊 ANALYSE DES RÉSULTATS")
    print("="*70)
    
    results_dir = Path('runs/train/epi_optimized_training')
    if not results_dir.exists():
        print("❌ Dossier de résultats non trouvé")
        return
    
    # Chercher results.csv
    results_csv = results_dir / 'results.csv'
    if results_csv.exists():
        print(f"\n✅ Fichier de résultats trouvé")
        
        # Lire les dernières lignes
        import pandas as pd
        try:
            df = pd.read_csv(results_csv)
            
            if len(df) > 0:
                print(f"\n📈 Évolution de l'entraînement (dernières 5 epochs):")
                print(f"\nepoch | train_loss | val_loss | mAP50 | mAP50-95")
                print(f"------|-----------|----------|-------|----------")
                
                for idx, row in df.tail(5).iterrows():
                    epoch = int(row.get('epoch', idx))
                    train_loss = row.get('train/box_loss', row.get('box_loss', 0))
                    val_loss = row.get('val/box_loss', 0)
                    mAP50 = row.get('metrics/mAP50', row.get('mAP50', 0))
                    mAP = row.get('metrics/mAP50-95', row.get('mAP50-95', 0))
                    
                    print(f"{epoch:5d} | {train_loss:9.4f} | {val_loss:8.4f} | {mAP50:5.4f} | {mAP:8.4f}")
                
                # Vérifier l'amélioration
                mAP_final = df['metrics/mAP50-95'].iloc[-1] if 'metrics/mAP50-95' in df.columns else df['mAP50-95'].iloc[-1] if 'mAP50-95' in df.columns else 0
                mAP_initial = df['metrics/mAP50-95'].iloc[0] if 'metrics/mAP50-95' in df.columns else df['mAP50-95'].iloc[0] if 'mAP50-95' in df.columns else 0
                
                improvement = ((mAP_final - mAP_initial) / max(mAP_initial, 0.001)) * 100
                
                if mAP_final > 0.5:
                    print(f"\n✅ mAP50-95 EXCELLENT: {mAP_final:.4f}")
                elif mAP_final > 0.3:
                    print(f"\n✅ mAP50-95 BON: {mAP_final:.4f}")
                elif mAP_final > 0.1:
                    print(f"\n⚠️  mAP50-95 MOYEN: {mAP_final:.4f}")
                else:
                    print(f"\n❌ mAP50-95 TRÈS FAIBLE: {mAP_final:.4f}")
                    print(f"   Amélioration: +{improvement:.0f}% (pas assez)")
                
        except Exception as e:
            print(f"⚠️  Erreur de lecture: {e}")
    else:
        print("⚠️  results.csv non trouvé")

def main():
    print("\n" + "🎯 "*20)
    print("ENTRAÎNEMENT OPTIMISÉ - FIX mAP TRÈS BASSE")
    print("🎯 "*20)
    
    success = train_optimized()
    
    if success:
        check_training_results()
        
        print("\n" + "="*70)
        print("✅ ENTRAÎNEMENT OPTIMISÉ COMPLÉTÉ")
        print("="*70)
        print(f"\nProchaines étapes:")
        print(f"1. Évaluer le modèle: python detect.py --source test_image.jpg")
        print(f"2. Si mAP > 0.3: modèle prêt!")
        print(f"3. Si mAP < 0.1: problème du dataset, réentraîner avec augmentation")
    else:
        print("\n❌ ENTRAÎNEMENT ÉCHOUÉ")
        sys.exit(1)

if __name__ == '__main__':
    main()
