#!/usr/bin/env python3
"""
Pipeline complet de correction et réentraînement
Exécute tous les steps dans l'ordre correct
"""

import sys
import subprocess
import time
from pathlib import Path

def run_command(script_name, description):
    """Exécuter un script Python"""
    print(f"\n{'='*70}")
    print(f"▶️  {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run([sys.executable, script_name], check=False)
        if result.returncode != 0:
            print(f"\n⚠️  {script_name} a terminé avec erreur (code {result.returncode})")
            return False
        return True
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

def main():
    print("\n" + "🚀 "*20)
    print("PIPELINE COMPLET: CORRECTION mAP BASSE")
    print("🚀 "*20)
    
    steps = [
        ("diagnose_low_map.py", "1️⃣  DIAGNOSTIC - Identifier les problèmes"),
        ("restructure_dataset.py", "2️⃣  RESTRUCTURATION - Nettoyer le dataset"),
        ("augment_and_balance.py", "3️⃣  AUGMENTATION - Équilibrer les classes"),
        ("train_optimized_fixed.py", "4️⃣  ENTRAÎNEMENT - Entraîner le modèle optimisé"),
    ]
    
    completed = []
    
    for script, desc in steps:
        print(f"\n{'*'*70}")
        print(f"Étape {len(completed)+1}/{len(steps)}: {desc}")
        print(f"{'*'*70}")
        
        # Vérifier que le script existe
        if not Path(script).exists():
            print(f"❌ {script} non trouvé!")
            continue
        
        # Exécuter
        if run_command(script, desc):
            completed.append(script)
            print(f"✅ {script} COMPLÉTÉ")
        else:
            print(f"⚠️  {script} a échoué - continuer? (y/n)")
            response = input().lower()
            if response != 'y':
                break
        
        time.sleep(2)  # Pause entre les étapes
    
    # Résumé final
    print("\n" + "="*70)
    print("📋 RÉSUMÉ FINAL")
    print("="*70)
    
    print(f"\n✅ Étapes complétées: {len(completed)}/{len(steps)}")
    for script in completed:
        print(f"   ✓ {script}")
    
    if len(completed) == len(steps):
        print(f"\n🎉 PIPELINE COMPLET RÉUSSI!")
        print(f"\nRésultats attendus:")
        print(f"  ✓ Dataset propre et synchronisé (5,571 train images)")
        print(f"  ✓ Classes équilibrées")
        print(f"  ✓ Modèle entraîné avec config optimisée")
        print(f"\nPour évaluer le modèle:")
        print(f"  python detect.py --source test_image.jpg --weights models/best.pt")
    else:
        print(f"\n⚠️  Pipeline incomplet - {len(steps) - len(completed)} étape(s) manquante(s)")

if __name__ == '__main__':
    main()
