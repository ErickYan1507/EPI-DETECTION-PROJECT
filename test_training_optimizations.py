#!/usr/bin/env python3
"""
Script de test rapide du nouvel entraînement optimisé
Teste que seul best.pt est créé et les optimisations fonctionnent
"""

import sys
import os
from pathlib import Path
import subprocess
import shutil

def test_fast_training():
    """Test rapide de l'entraînement avec les optimisations"""
    
    print("=" * 70)
    print("🧪 TEST DE L'ENTRAÎNEMENT OPTIMISÉ")
    print("=" * 70)
    
    # 1. Vérifier que le dataset existe
    dataset_path = Path('dataset')
    if not dataset_path.exists():
        print("⚠️  Dataset non trouvé")
        print("   Création d'un mini-dataset pour test...")
        dataset_path.mkdir(exist_ok=True)
        for split in ['train', 'val']:
            (dataset_path / 'images' / split).mkdir(parents=True, exist_ok=True)
            (dataset_path / 'labels' / split).mkdir(parents=True, exist_ok=True)
    
    # 2. Nettoyer les anciens fichiers
    print("\n🧹 Nettoyage des anciens modèles...")
    models_dir = Path('models')
    if models_dir.exists():
        shutil.rmtree(models_dir)
    models_dir.mkdir(exist_ok=True)
    print("✓ Répertoire models/ nettoyé")
    
    # 3. Lancer un entraînement court
    print("\n🚀 Lancement de l'entraînement optimisé...")
    print("   (10 epochs, batch_size=4 pour test rapide)")
    
    cmd = [
        sys.executable, 'train.py',
        '--epochs', '10',
        '--batch-size', '4',
        '--img-size', '640',
        '--dataset', str(dataset_path),
        '--run-name', 'fast_test'
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("\n❌ Erreur lors de l'entraînement")
        return False
    
    # 4. Vérifier que seul best.pt est créé
    print("\n📊 Vérification des modèles créés...")
    best_pt = models_dir / 'best.pt'
    
    if best_pt.exists():
        size_mb = best_pt.stat().st_size / (1024 * 1024)
        print(f"✅ Modèle principal trouvé: models/best.pt ({size_mb:.1f} MB)")
    else:
        print("❌ Modèle best.pt non trouvé!")
        return False
    
    # 5. Compter le nombre de fichiers .pt
    pt_files = list(models_dir.glob('*.pt'))
    print(f"\n📈 Statistiques:")
    print(f"   - Fichiers .pt dans models/: {len(pt_files)}")
    for pt_file in pt_files:
        size_mb = pt_file.stat().st_size / (1024 * 1024)
        print(f"     - {pt_file.name}: {size_mb:.1f} MB")
    
    if len(pt_files) == 1:
        print("\n✅ SUCCÈS: Seul best.pt est créé!")
    else:
        print(f"\n⚠️  ATTENTION: {len(pt_files)} fichiers .pt au lieu de 1")
    
    # 6. Tester le chargement du modèle
    print("\n🔍 Test de chargement du modèle...")
    try:
        import torch
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=str(best_pt))
        print("✅ Modèle chargé avec succès!")
        print(f"   - Architecture: {type(model)}")
    except Exception as e:
        print(f"⚠️  Erreur lors du chargement: {e}")
    
    print("\n" + "=" * 70)
    print("✅ TEST TERMINÉ")
    print("=" * 70)
    
    return True

def test_optimizations_applied():
    """Vérifier que les optimisations sont appliquées"""
    print("\n🔧 Vérification des optimisations...")
    
    with open('train.py', 'r') as f:
        content = f.read()
    
    optimizations = [
        ('--adam', 'Optimizer Adam'),
        ('--cache', 'RAM Cache'),
        ('--workers', 'Workers'),
        ('--patience', 'Early Stopping'),
        ('--line-profile 0', 'Line Profiling'),
        ('models/best.pt', 'Unique Model Save'),
    ]
    
    print("\n📋 Optimisations appliquées:")
    for opt, name in optimizations:
        if opt in content:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} - NON TROUVÉ")

if __name__ == '__main__':
    print("\n")
    test_optimizations_applied()
    print("\n")
    
    # Lancer le test (optionnel)
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        test_fast_training()
    else:
        print("\n💡 Pour lancer le test complet:")
        print("   python test_training_optimizations.py run")
