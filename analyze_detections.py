#!/usr/bin/env python
import sqlite3
import json

conn = sqlite3.connect('database/epi_detection.db')
cursor = conn.cursor()

print('🔍 ANALYSE DÉTAILLÉE - POURQUOI PAS DE LUNETTES DÉTECTÉES')
print('=' * 55)

# Récupérer les 10 derniers enregistrements
cursor.execute('''
SELECT id, timestamp, total_persons, with_helmet, with_vest, with_glasses, with_boots, raw_data
FROM detections 
ORDER BY timestamp DESC 
LIMIT 10
''')

rows = cursor.fetchall()

print(f'\n📊 Derniers 10 enregistrements de détection:')
print('-' * 55)

for row in rows:
    detection_id, timestamp, persons, helmet, vest, glasses, boots, raw_data = row
    
    print(f'\n🆔 {detection_id} - {timestamp}')
    print(f'  👥 Personnes: {persons}')
    print(f'  🪖 Casque: {helmet}')
    print(f'  👔 Gilet: {vest}')
    print(f'  👓 Lunettes: {glasses}')
    print(f'  👢 Chaussures: {boots}')
    
    # Analyser les données brutes
    if raw_data:
        try:
            data = json.loads(raw_data)
            detections = data.get('detections', [])
            print(f'  📈 Détections brutes: {len(detections)}')
            
            # Compter par classe
            class_counts = {}
            for d in detections:
                cls = d.get('class', 'unknown')
                class_counts[cls] = class_counts.get(cls, 0) + 1
            
            print(f'  📊 Par classe: {class_counts}')
            
            # Vérifier les lunettes
            glasses_detections = [d for d in detections if d.get('class') == 'glasses']
            if glasses_detections:
                print(f'  ✅ Lunettes trouvées: {len(glasses_detections)}')
                for g in glasses_detections[:2]:  # Afficher les 2 premiers
                    print(f'    • Confiance: {g.get("confidence", "N/A")}')
            else:
                print(f'  ❌ Aucune lunette détectée')
                
        except json.JSONDecodeError:
            print(f'  ⚠️  Erreur décodage JSON')

conn.close()
