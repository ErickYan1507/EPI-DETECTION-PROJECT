#!/usr/bin/env python
import sqlite3

# Vérifier la structure de la base de données
print('🔍 STRUCTURE DE LA BASE DE DONNÉES')
print('=' * 35)

conn = sqlite3.connect('database/unified_monitoring.db')
cursor = conn.cursor()

# Lister toutes les tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()

print(f'📋 Tables trouvées: {[t[0] for t in tables]}')

for table_name in [t[0] for t in tables]:
    print(f'\n📊 Table: {table_name}')
    
    # Décrire la structure
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    
    print('  Colonnes:')
    for col in columns:
        print(f'    • {col[1]} ({col[2]})')
    
    # Compter les enregistrements
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f'  📈 Enregistrements: {count}')
    
    if count > 0:
        # Montrer un exemple
        cursor.execute(f'SELECT * FROM {table_name} LIMIT 1')
        sample = cursor.fetchone()
        print(f'  💡 Exemple: {sample}')

conn.close()
