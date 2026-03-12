#!/usr/bin/env python3
"""
Debug base de données - Vérifier if emails/notifications sont bien enregistrés
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database_unified import db, EmailNotification, Detection
from app.main import app

with app.app_context():
    print("="*70)
    print("VÉRIFICATION DE LA BASE DE DONNÉES")
    print("="*70)
    
    print("\n📊 Étape 1: Compter les notifications emails...")
    try:
        count = db.session.query(EmailNotification).count()
        print(f"  ✓ Nombre de notifications dans EmailNotification: {count}")
        
        if count > 0:
            # Afficher les 5 dernières
            recent = db.session.query(EmailNotification).order_by(
                EmailNotification.last_sent.desc()
            ).limit(5).all()
            
            print(f"\n  📋 5 Dernières notifications:")
            for notif in recent:
                last_sent = notif.last_sent.strftime('%Y-%m-%d %H:%M:%S') if notif.last_sent else "Jamais"
                print(f"     - {notif.email_address} | Type: {notif.notification_type} | Dernier envoi: {last_sent}")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
    
    print("\n📊 Étape 2: Compter les détections...")
    try:
        count = db.session.query(Detection).count()
        print(f"  ✓ Nombre de détections: {count}")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
    
    print("\n📋 Étape 3: Vérifier le fichier .email_recipients...")
    try:
        with open('.email_recipients', 'r') as f:
            recipients = [line.strip() for line in f if line.strip()]
        print(f"  ✓ Destinataires configurés: {len(recipients)}")
        for r in recipients:
            print(f"     - {r}")
    except FileNotFoundError:
        print("  ✗ Fichier .email_recipients non trouvé")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
    
    print("\n📋 Étape 4: Vérifier .env.email...")
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv('.env.email')
        
        sender = os.getenv('SENDER_EMAIL')
        password = os.getenv('SENDER_PASSWORD')
        
        if sender and password:
            print(f"  ✓ Configuration SMTP valide")
            print(f"     - Sender: {sender}")
        else:
            print(f"  ✗ Configuration SMTP incomplète")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
    
    print("\n" + "="*70)
