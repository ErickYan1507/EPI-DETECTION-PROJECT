"""
Script de monitoring de l'entraînement YOLOv5
"""

import os
import time
import json
from pathlib import Path

def monitor_training():
    print("📊 MONITORING ENTRAÎNEMENT YOLOv5")
    print("=" * 50)

    runs_dir = Path('runs/train')
    if not runs_dir.exists():
        print("❌ Aucun dossier runs/train trouvé")
        return

    # Trouver le run le plus récent
    subdirs = [d for d in runs_dir.iterdir() if d.is_dir() and 'epi_cpu' in d.name]
    if not subdirs:
        print("❌ Aucun run d'entraînement trouvé")
        return

    latest_run = max(subdirs, key=lambda x: x.stat().st_ctime)
    print(f"📁 Run monitoré: {latest_run.name}")
    print()

    # Fichiers à surveiller
    results_file = latest_run / 'results.csv'
    weights_dir = latest_run / 'weights'

    last_results = None
    last_weights_count = 0

    try:
        while True:
            # Vérifier les résultats
            if results_file.exists():
                with open(results_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        current_results = lines[-1].strip()
                        if current_results != last_results:
                            print(f"📈 Résultats: {current_results}")
                            last_results = current_results

            # Vérifier les poids sauvegardés
            if weights_dir.exists():
                weights_files = list(weights_dir.glob('*.pt'))
                current_weights_count = len(weights_files)
                if current_weights_count > last_weights_count:
                    new_weights = weights_files[-1]
                    print(f"💾 Nouveau checkpoint: {new_weights.name}")
                    last_weights_count = current_weights_count

            # Vérifier les logs TensorBoard
            events_files = list(latest_run.glob('events.out.tfevents.*'))
            if events_files:
                latest_event = max(events_files, key=lambda x: x.stat().st_mtime)
                time_diff = time.time() - latest_event.stat().st_mtime
                if time_diff < 300:  # Moins de 5 minutes
                    print(f"🔄 Entraînement actif (dernier log il y a {time_diff:.1f}s)")
                else:
                    print(f"⏸️  Entraînement semble arrêté (dernier log il y a {time_diff/60:.1f} min)")

            time.sleep(30)  # Vérifier toutes les 30 secondes

    except KeyboardInterrupt:
        print("\n⏹️  Monitoring arrêté par l'utilisateur")

def show_training_status():
    """Affiche le statut actuel de l'entraînement"""
    print("📋 STATUT ACTUEL DE L'ENTRAÎNEMENT")
    print("=" * 50)

    runs_dir = Path('runs/train')
    if not runs_dir.exists():
        print("❌ Aucun entraînement trouvé")
        return

    subdirs = [d for d in runs_dir.iterdir() if d.is_dir() and 'epi_cpu' in d.name]
    if not subdirs:
        print("❌ Aucun run d'entraînement EPI trouvé")
        return

    latest_run = max(subdirs, key=lambda x: x.stat().st_ctime)
    print(f"📁 Dernier run: {latest_run.name}")

    # Résultats
    results_file = latest_run / 'results.csv'
    if results_file.exists():
        with open(results_file, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:  # Header + au moins 1 ligne de données
                last_line = lines[-1].strip().split(',')
                if len(last_line) >= 8:
                    epoch = last_line[0]
                    train_box_loss = last_line[1]
                    train_obj_loss = last_line[2]
                    train_cls_loss = last_line[3]
                    precision = last_line[4]
                    recall = last_line[5]
                    map50 = last_line[6]
                    map50_95 = last_line[7]

                    print(f"📊 Époque: {epoch}")
                    print(f"🎯 Pertes - Box: {train_box_loss}, Obj: {train_obj_loss}, Cls: {train_cls_loss}")
                    print(f"📈 Métriques - Precision: {precision}, Recall: {recall}")
                    print(f"🏆 mAP@0.5: {map50}, mAP@0.5:0.95: {map50_95}")
                else:
                    print("⚠️  Format des résultats inattendu")
            else:
                print("📝 Résultats en cours de génération...")
    else:
        print("📝 Aucun résultat trouvé")

    # Poids
    weights_dir = latest_run / 'weights'
    if weights_dir.exists():
        weights_files = list(weights_dir.glob('*.pt'))
        print(f"💾 Checkpoints: {len(weights_files)} sauvegardé(s)")
        for wf in sorted(weights_files):
            size_mb = wf.stat().st_size / (1024 * 1024)
            print(f"  • {wf.name}: {size_mb:.1f} MB")
    print()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        show_training_status()
    else:
        monitor_training()
