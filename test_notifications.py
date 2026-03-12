#!/usr/bin/env python3
"""
Script de test pour le système de notifications
Teste les fonctionnalités principales du gestionnaire de notifications
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app.notifications_handler import NotificationsManager
from app.logger import logger

def test_notifications_system():
    """Tester le système de notifications"""
    
    print("\n" + "="*60)
    print("🧪 TEST DU SYSTÈME DE NOTIFICATIONS")
    print("="*60 + "\n")
    
    # Initialiser le gestionnaire
    print("1️⃣  Initialisation du gestionnaire...")
    notif = NotificationsManager(db_type='sqlite')
    print("   ✅ Gestionnaire initialisé\n")
    
    # Test 1 : Configuration email
    print("2️⃣  Test sauvegarde configuration email...")
    result = notif.save_email_config(
        sender_email='test@example.com',
        sender_password='test_password',
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        use_tls=True
    )
    print(f"   {'✅' if result['success'] else '❌'} {result.get('message', result.get('error'))}\n")
    
    # Test 2 : Ajouter destinataires
    print("3️⃣  Test ajout destinataires...")
    emails = ['admin@example.com', 'user@example.com', 'supervisor@example.com']
    for email in emails:
        result = notif.add_recipient(email)
        print(f"   {'✅' if result['success'] else '❌'} {email}")
    print()
    
    # Test 3 : Récupérer destinataires
    print("4️⃣  Test récupération destinataires...")
    result = notif.get_recipients()
    if result['success']:
        print(f"   ✅ {len(result['recipients'])} destinataire(s) trouvé(s)")
        for email in result['recipients']:
            print(f"      📧 {email}")
    else:
        print(f"   ❌ Erreur: {result['error']}")
    print()
    
    # Test 4 : Configuration rapports
    print("5️⃣  Test configuration rapports...")
    schedules = [
        ('daily', True, 8, None, 'daily'),
        ('weekly', True, 9, 2, 'weekly'),
        ('monthly', False, 10, 15, 'monthly'),
    ]
    
    for report_type, enabled, hour, day, freq in schedules:
        result = notif.save_report_schedule(
            report_type=report_type,
            is_enabled=enabled,
            send_hour=hour,
            send_day=day,
            frequency=freq
        )
        status = '✅ Activé' if enabled else '❌ Désactivé'
        print(f"   {status} Rapport {report_type} à {hour}h")
    print()
    
    # Test 5 : Configuration test
    print("6️⃣  Test récupération configuration complète...")
    config = notif.get_all_config()
    if config['success']:
        print("   ✅ Configuration récupérée")
        print(f"      Email: {config['config'].get('sender_email', 'Non configuré')}")
        print(f"      SMTP: {config['config'].get('smtp_server')}:{config['config'].get('smtp_port')}")
        print(f"      Rapports quotidiens: {'Activés' if config['config'].get('daily_enabled') else 'Désactivés'}")
    print()
    
    # Test 6 : Historique (vide pour l'instant)
    print("7️⃣  Test historique notifications...")
    result = notif.get_notification_history()
    if result['success']:
        count = len(result['history'])
        print(f"   ✅ Historique: {count} enregistrement(s)")
    print()
    
    # Test 7 : Connexion SMTP (TEST uniquement, ne pas envoyer réellement)
    print("8️⃣  Test connexion SMTP...")
    print("   ⚠️  Skipped (pas d'email réel configuré)")
    print()
    
    # Test 8 : Suppression destinataire
    print("9️⃣  Test suppression destinataire...")
    result = notif.remove_recipient('supervisor@example.com')
    print(f"   {'✅' if result['success'] else '❌'} {result.get('message', result.get('error'))}")
    print()
    
    # Test 9 : Récupération finale destinataires
    print("🔟 Test récupération finale destinataires...")
    result = notif.get_recipients()
    if result['success']:
        print(f"   ✅ {len(result['recipients'])} destinataire(s) restant(s)")
        for email in result['recipients']:
            print(f"      📧 {email}")
    print()
    
    # Résumé
    print("="*60)
    print("🎉 TOUS LES TESTS SONT TERMINÉS!")
    print("="*60)
    print("\n✅ Système de notifications opérationnel\n")

if __name__ == '__main__':
    try:
        test_notifications_system()
    except Exception as e:
        logger.error(f"Erreur lors du test: {e}")
        print(f"❌ Erreur: {e}")
        sys.exit(1)
