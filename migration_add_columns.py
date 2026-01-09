#!/usr/bin/env python
"""
Script de migration pour ajouter les colonnes manquantes à la table detections
"""
import sqlite3
import sys

db_path = 'database/epi_detection.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ajouter les colonnes manquantes
    columns_to_add = [
        ('model_used', "VARCHAR(255) DEFAULT 'best.pt'"),
        ('ensemble_mode', "BOOLEAN DEFAULT 0"),
        ('model_votes', "TEXT"),
        ('aggregation_method', "VARCHAR(50)")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f'ALTER TABLE detections ADD COLUMN {col_name} {col_type}')
            print(f'✓ Colonne {col_name} ajoutée')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print(f'⚠ Colonne {col_name} existe déjà')
            else:
                print(f'✗ Erreur {col_name}: {e}')
    
    conn.commit()
    conn.close()
    print('\n✓ Migration terminée avec succès!')
    sys.exit(0)
    
except Exception as e:
    print(f'✗ Erreur de migration: {e}')
    sys.exit(1)
