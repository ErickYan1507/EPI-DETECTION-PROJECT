#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extraire les métriques d'entraînement détaillées par classe"""

import pandas as pd
import os
from pathlib import Path

# Chemin du fichier de résultats
results_path = 'runs/train/epi_detection_session_003/results.csv'

print('=' * 80)
print('MÉTRIQUES D\'ENTRAÎNEMENT DU MODÈLE BEST.PT')
print('=' * 80)

# Charger les résultats
df = pd.read_csv(results_path)

# Nettoyer les noms de colonnes (supprimer les espaces)
df.columns = df.columns.str.strip()

# Colonnes clés
print('\n' + '=' * 80)
print('RÉSUMÉ GÉNÉRAL DES MÉTRIQUES')
print('=' * 80)

# Afficher les dernières lignes (résultats finaux)
print(f'\nÉpochs entraîné: 0-{len(df)-1} (Total: {len(df)} epochs)')
print(f'\nRÉSULTATS FINAUX (Epoch {len(df)-1}):')
print('-' * 80)

last_row = df.iloc[-1]
print(f'  Precision (Val):    {last_row["metrics/precision"]:.4f} ({last_row["metrics/precision"]*100:.2f}%)')
print(f'  Recall (Val):       {last_row["metrics/recall"]:.4f} ({last_row["metrics/recall"]*100:.2f}%)')
print(f'  mAP@0.5 (Val):      {last_row["metrics/mAP_0.5"]:.4f} ({last_row["metrics/mAP_0.5"]*100:.2f}%)')
print(f'  mAP@0.5:0.95 (Val): {last_row["metrics/mAP_0.5:0.95"]:.4f} ({last_row["metrics/mAP_0.5:0.95"]*100:.2f}%)')

print(f'\n  Loss d\'entraînement:')
print(f'    - Box Loss:   {last_row["train/box_loss"]:.6f}')
print(f'    - Obj Loss:   {last_row["train/obj_loss"]:.6f}')
print(f'    - Cls Loss:   {last_row["train/cls_loss"]:.6f}')

print(f'\n  Loss de validation:')
print(f'    - Box Loss:   {last_row["val/box_loss"]:.6f}')
print(f'    - Obj Loss:   {last_row["val/obj_loss"]:.6f}')
print(f'    - Cls Loss:   {last_row["val/cls_loss"]:.6f}')

# MEILLEUR RÉSULTAT
print('\n' + '=' * 80)
print('MEILLEURE PERFORMANCE')
print('=' * 80)

best_map_idx = df['metrics/mAP_0.5'].idxmax()
best_map_row = df.iloc[best_map_idx]
print(f'\nMeilleur mAP@0.5 à Epoch {best_map_idx}:')
print(f'  mAP@0.5:      {best_map_row["metrics/mAP_0.5"]:.4f} ({best_map_row["metrics/mAP_0.5"]*100:.2f}%)')
print(f'  mAP@0.5:0.95: {best_map_row["metrics/mAP_0.5:0.95"]:.4f} ({best_map_row["metrics/mAP_0.5:0.95"]*100:.2f}%)')
print(f'  Precision:    {best_map_row["metrics/precision"]:.4f} ({best_map_row["metrics/precision"]*100:.2f}%)')
print(f'  Recall:       {best_map_row["metrics/recall"]:.4f} ({best_map_row["metrics/recall"]*100:.2f}%)')

# TENDANCES
print('\n' + '=' * 80)
print('TENDANCES D\'ENTRAÎNEMENT')
print('=' * 80)

# Moyenne des 10 premiers epochs vs 10 derniers
early_epochs = df.head(10)
late_epochs = df.tail(10)

print(f'\nPhase initiale (Epochs 0-9):')
print(f'  Precision moyenne:    {early_epochs["metrics/precision"].mean():.4f}')
print(f'  Recall moyen:         {early_epochs["metrics/recall"].mean():.4f}')
print(f'  mAP@0.5 moyen:        {early_epochs["metrics/mAP_0.5"].mean():.4f}')

print(f'\nPhase finale (Epochs 40-49):')
print(f'  Precision moyenne:    {late_epochs["metrics/precision"].mean():.4f}')
print(f'  Recall moyen:         {late_epochs["metrics/recall"].mean():.4f}')
print(f'  mAP@0.5 moyen:        {late_epochs["metrics/mAP_0.5"].mean():.4f}')

# Progression
precision_prog = ((late_epochs["metrics/precision"].mean() - early_epochs["metrics/precision"].mean()) / 
                  early_epochs["metrics/precision"].mean() * 100) if early_epochs["metrics/precision"].mean() > 0 else 0
recall_prog = ((late_epochs["metrics/recall"].mean() - early_epochs["metrics/recall"].mean()) / 
               early_epochs["metrics/recall"].mean() * 100) if early_epochs["metrics/recall"].mean() > 0 else 0

print(f'\nProgression (Phase finale vs Phase initiale):')
print(f'  Precision:   {precision_prog:+.1f}%')
print(f'  Recall:      {recall_prog:+.1f}%')

# STABILITÉ
print('\n' + '=' * 80)
print('STABILITÉ DU MODÈLE')
print('=' * 80)

print(f'\nVariation des losses (écart-type):')
print(f'  Train Box Loss: {df["train/box_loss"].std():.6f}')
print(f'  Train Obj Loss: {df["train/obj_loss"].std():.6f}')
print(f'  Train Cls Loss: {df["train/cls_loss"].std():.6f}')

print(f'\nVariation des métriques (écart-type):')
print(f'  Precision: {df["metrics/precision"].std():.4f}')
print(f'  Recall:    {df["metrics/recall"].std():.4f}')
print(f'  mAP@0.5:   {df["metrics/mAP_0.5"].std():.4f}')

# Overfitting
print('\n' + '=' * 80)
print('ANALYSE OVERFITTING')
print('=' * 80)

train_loss_final = last_row["train/box_loss"]
val_loss_final = last_row["val/box_loss"]
diff_ratio = (val_loss_final - train_loss_final) / train_loss_final * 100

print(f'\nDernière epoch ({len(df)-1}):')
print(f'  Train Box Loss: {train_loss_final:.6f}')
print(f'  Val Box Loss:   {val_loss_final:.6f}')
print(f'  Écart:          {diff_ratio:+.1f}%')

if diff_ratio < 10:
    print(f'  → Pas d\'overfitting détecté (écart <10%)')
elif diff_ratio < 30:
    print(f'  → Overfitting léger (écart 10-30%)')
else:
    print(f'  → Overfitting modéré (écart >30%)')

# Tableau comparatif
print('\n' + '=' * 80)
print('TABLEAU COMPARATIF - MEILLEURES EPOCHS')
print('=' * 80)

# Top 5 par mAP
top_5 = df.nlargest(5, 'metrics/mAP_0.5')[['epoch', 'metrics/precision', 'metrics/recall', 
                                               'metrics/mAP_0.5', 'metrics/mAP_0.5:0.95']]

print('\nTop 5 epochs par mAP@0.5:')
print(top_5.to_string())

print('\n' + '=' * 80)
print('CONCLUSION')
print('=' * 80)

print(f'''
RÉSUMÉ:
-------
- Modèle entraîné sur 50 epochs
- Meilleur mAP@0.5: {best_map_row["metrics/mAP_0.5"]*100:.2f}%
- Meilleur mAP@0.5:0.95: {best_map_row["metrics/mAP_0.5:0.95"]*100:.2f}%
- Precision finale: {last_row["metrics/precision"]*100:.2f}%
- Recall final: {last_row["metrics/recall"]*100:.2f}%
- État d'entraînement: {"✓ Stable" if diff_ratio < 30 else "⚠ Overfitting"}

PERFORMANCE PAR CLASSE:
- 5 classes: helmet, glasses, person, vest, boots
- Données complètes par classe dans les fichiers confusion_matrix.png et PR_curve.png
''')

print('✓ Rapport généré!')
