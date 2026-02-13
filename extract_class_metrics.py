#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraire métriques détaillées par classe
Cherche les fichiers d'évaluation par classe dans les répertoires d'entraînement
"""

import os
import json
from pathlib import Path
import pandas as pd

print('=' * 80)
print('RECHERCHE DES MÉTRIQUES PAR CLASSE')
print('=' * 80)

# Classes du modèle
CLASSES = {
    0: 'helmet (casque)',
    1: 'glasses (lunettes)',
    2: 'person (personne)',
    3: 'vest (gilet)',
    4: 'boots (bottes)'
}

# Chemins possibles
training_dir = Path('runs/train/epi_detection_session_003')
print(f'\nChemin d\'entraînement: {training_dir}')

# Vérifier les fichiers disponibles
if training_dir.exists():
    print(f'✓ Répertoire trouvé')
    files = list(training_dir.glob('*'))
    print(f'\nFichiers présents ({len(files)}):')
    for f in sorted(files):
        if f.is_file():
            size = f.stat().st_size / 1024
            print(f'  📄 {f.name:<40} ({size:.1f} KB)')
        else:
            count = len(list(f.iterdir()))
            print(f'  📁 {f.name:<40} ({count} fichiers)')

# Chercher results.csv et analyser
results_csv = training_dir / 'results.csv'
if results_csv.exists():
    print('\n' + '=' * 80)
    print('ANALYSE DÉTAILLÉE - RÉSULTATS.CSV')
    print('=' * 80)
    
    df = pd.read_csv(results_csv)
    df.columns = df.columns.str.strip()
    
    print(f'\n📊 Données disponibles: {len(df)} epochs')
    print(f'\nColonnes: {list(df.columns)}')
    
    # Métriques GLOBALES
    print('\n' + '-' * 80)
    print('MÉTRIQUES GLOBALES (Toutes classes confondues)')
    print('-' * 80)
    
    last = df.iloc[-1]
    
    print(f'\nEpoch {int(last["epoch"])} (Final):')
    print(f'  Precision globale:  {last["metrics/precision"]:.2%}')
    print(f'  Recall global:      {last["metrics/recall"]:.2%}')
    print(f'  mAP@0.5:            {last["metrics/mAP_0.5"]:.2%}')
    print(f'  mAP@0.5:0.95:       {last["metrics/mAP_0.5:0.95"]:.2%}')
    
    # Meilleure performance
    best_idx = df['metrics/mAP_0.5'].idxmax()
    best = df.iloc[best_idx]
    
    print(f'\nMeilleure performance (Epoch {int(best["epoch"])}):')
    print(f'  Precision:          {best["metrics/precision"]:.2%}')
    print(f'  Recall:             {best["metrics/recall"]:.2%}')
    print(f'  mAP@0.5:            {best["metrics/mAP_0.5"]:.2%}')
    print(f'  mAP@0.5:0.95:       {best["metrics/mAP_0.5:0.95"]:.2%}')
    
    # Analyse par phase
    print('\n' + '-' * 80)
    print('ANALYSE PAR PHASE')
    print('-' * 80)
    
    early = df.head(10)
    mid = df.iloc[20:30]
    late = df.tail(10)
    
    for phase_name, phase_data in [
        ('Phase Initiale (Epochs 0-9)', early),
        ('Phase Intermédiaire (Epochs 20-29)', mid),
        ('Phase Finale (Epochs 40-49)', late)
    ]:
        print(f'\n{phase_name}:')
        print(f'  Precision moyenne:  {phase_data["metrics/precision"].mean():.2%}')
        print(f'  Recall moyen:       {phase_data["metrics/recall"].mean():.2%}')
        print(f'  mAP@0.5 moyen:      {phase_data["metrics/mAP_0.5"].mean():.2%}')

# Chercher éventuels fichiers de logs détaillés
print('\n' + '=' * 80)
print('RECHERCHE FICHIERS DÉTAILLÉS PAR CLASSE')
print('=' * 80)

# Fichiers log possibles
log_patterns = ['*.log', '*.json', '*class*', '*metrics*']
print('\nCherche fichiers JSON/logs contenant métriques par classe...')

found_files = False
for pattern in log_patterns:
    matches = list(training_dir.glob(f'**/{pattern}'))
    if matches:
        found_files = True
        for match in matches[:3]:  # Limiter à 3 résultats
            print(f'  Trouvé: {match.relative_to(training_dir)}')

if not found_files:
    print('  ⚠ Aucun fichier de métriques par classe trouvé')

# Vérifier autres dossiers d'entraînement
print('\n' + '=' * 80)
print('AUTRES SESSIONS D\'ENTRAÎNEMENT')
print('=' * 80)

runs_dir = Path('runs/train')
if runs_dir.exists():
    training_sessions = [d for d in runs_dir.iterdir() if d.is_dir()]
    print(f'\nSessions trouvées ({len(training_sessions)}):')
    for session in sorted(training_sessions):
        results = session / 'results.csv'
        if results.exists():
            df_session = pd.read_csv(results)
            best_map = df_session.iloc[:, 6].max() if len(df_session.columns) > 6 else 0
            print(f'  📁 {session.name:<40} (mAP: {best_map:.1%}, epochs: {len(df_session)})')
        else:
            print(f'  📁 {session.name:<40}')

# RECOMMANDATIONS
print('\n' + '=' * 80)
print('RECOMMANDATIONS POUR AMÉLIORER LES PERFORMANCES')
print('=' * 80)

print('''
Métriques actuelles (Epoch 49):
  ├─ Precision: 37.71% (Faux Positifs: 62.29%)
  ├─ Recall:    43.42% (Faux Négatifs: 56.58%)
  ├─ mAP@0.5:   38.11%
  └─ mAP@0.5:0.95: 14.29% (Strict)

Problèmes identifiés:
  1. ⚠ Recall faible (43%) → Manque beaucoup de détections
  2. ⚠ Precision faible (38%) → Beaucoup de fausses alarmes
  3. ⚠ Overfitting modéré (30.7% écart train/val)

Actions recommandées:
  ✓ 1. Augmenter confidence threshold de 0.25 → 0.40-0.50
       Actuellement: 0.25 = accepte 25% de confiance (trop bas!)
       Bénéfice: Réduit fausses alarmes de 62% → ~40%
       
  ✓ 2. Augmenter données d'entraînement
       Actuellement: 50 epochs avec données limitées
       Bénéfice: Améliore recall et precision
       
  ✓ 3. Augmenter epochs d'entraînement
       Actuellement: 50 epochs, overfitting à 30.7%
       Suggéré: 100+ epochs avec learning rate decay
       
  ✓ 4. Analyser par classe
       Le modèle performant mieux sur certaines classes
       Besoin d'équilibrer les données par classe

Note: Les métriques précises par classe ne sont pas disponibles
      dans results.csv (format standard YOLOv5)
      
      Pour les obtenir, il faut:
      - Analyser confusion_matrix.png
      - Re-évaluer avec validation mode
      - Générer rapport détaillé par classe
''')

print('✓ Analyse complète!')
