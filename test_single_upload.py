#!/usr/bin/env python3
"""Test upload unique - vérifier que tout fonctionne en un seul essai"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, '.')
os.environ['FLASK_ENV'] = 'development'

from app.main import app
from app.database_unified import db, Detection

print('🧪 Test d\'upload unique\n')

# Nettoyer les anciens uploads
import shutil
upload_dir = 'static/uploads/images'
if os.path.exists(upload_dir):
    for f in os.listdir(upload_dir):
        fpath = os.path.join(upload_dir, f)
        try:
            if os.path.isfile(fpath):
                os.remove(fpath)
            elif os.path.isdir(fpath):
                shutil.rmtree(fpath)
        except:
            pass

with app.app_context():
    # Compter les détections avant
    count_before = db.session.query(Detection).count()
    print(f'1️⃣ Détections avant: {count_before}')
    
    # Créer une image test
    from PIL import Image
    img = Image.new('RGB', (640, 480), color='white')
    img.save('test_image.jpg')
    
    # Simuler un upload
    with app.test_client() as client:
        with open('test_image.jpg', 'rb') as f:
            print(f'2️⃣ Envoi du fichier...')
            response = client.post(
                '/upload',
                data={
                    'file': (f, 'test_image.jpg'),
                    'type': 'image'
                }
            )
            
            print(f'   Status: {response.status_code}')
            result = response.get_json() if response.content_type == 'application/json' else None
            
            if result and result.get('success'):
                print(f'   ✅ Upload réussi!')
                print(f'   Image URL: {result.get("image_url", "N/A")}')
                stats = result.get("statistics", {})
                print(f'   Persons: {stats.get("total_persons", 0)}, Helmet: {stats.get("with_helmet", 0)}')
                
                # Compter après
                count_after = db.session.query(Detection).count()
                print(f'\n3️⃣ Détections après: {count_after}')
                print(f'   Nouvelles détections: {count_after - count_before}')
                
                if count_after > count_before:
                    print('\n✅ SUCCÈS: Upload + DB record en un seul essai!')
                else:
                    print('\n❌ PROBLÈME: Pas de détections enregistrées!')
            else:
                print(f'   ❌ Erreur: Status {response.status_code}')
    
    os.remove('test_image.jpg')
