#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification des métriques dans la base de données
"""

import sqlite3
import json

conn = sqlite3.connect('database/epi_detection.db')
cursor = conn.cursor()

print('='*80)
print('VÉRIFICATION DES MÉTRIQUES DANS LA BD')
print('='*80)
print()

cursor.execute('''SELECT 
    id,
    timestamp,
    model_name,
    val_precision,
    val_recall,
    val_f1_score,
    val_accuracy,
    class_metrics
FROM training_results WHERE id >= 7 ORDER BY id DESC LIMIT 2''')

rows = cursor.fetchall()

for row in rows:
    print(f'ID: {row[0]}')
    print(f'Timestamp: {row[1]}')
    print(f'Model: {row[2]}')
    print(f'Validation Precision: {row[3]}')
    print(f'Validation Recall: {row[4]}')
    print(f'Validation F1-Score: {row[5]}')
    print(f'Validation Accuracy: {row[6]}')
    if row[7]:
        try:
            metrics = json.loads(row[7])
            print(f'Class Metrics: {list(metrics.keys())}')
        except:
            print(f'Class Metrics: [JSON parsing error]')
    print('-'*80)
    print()

conn.close()
print('✅ Vérification BD complétée!')
