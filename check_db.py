#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('database/epi_detection.db')
cursor = conn.cursor()

# Lister les tables
cursor.execute('SELECT name FROM sqlite_master WHERE type=?', ('table',))
tables = cursor.fetchall()

print('📋 Tables trouvées:')
for t in tables:
    print(f'  • {t[0]}')

print('\n🔍 ANALYSE DE LA TABLE detections')
print('=' * 40)

# Analyser la table détections
if any(t[0] == 'detections' for t in tables):
    cursor.execute('PRAGMA table_info(detections)')
    columns = cursor.fetchall()
    
    print('Colonnes:')
    for col in columns:
        print(f'  • {col[1]} ({col[2]})')
    
    # Compter les enregistrements
    cursor.execute('SELECT COUNT(*) FROM detections')
    count = cursor.fetchone()[0]
    print(f'\n📈 Enregistrements: {count}')
    
    # Récupérer les 5 derniers
    cursor.execute('SELECT timestamp, class_name, confidence FROM detections ORDER BY timestamp DESC LIMIT 5')
    rows = cursor.fetchall()
    
    print('\n🔎 Derniers enregistrements:')
    for row in rows:
        print(f'  • {row[0]} - {row[1]}: {row[2]}')

conn.close()
