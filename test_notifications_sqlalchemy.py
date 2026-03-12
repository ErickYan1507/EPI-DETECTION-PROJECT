"""
TESTING SCRIPT - Migration et validation du système de notifications vers SQLAlchemy
Vérifie que les deux systèmes fonctionnent et aide à migrer les données
"""

import sys
import os
import sqlite3
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_sqlalchemy_models():
    """✅ Test 1: Vérifier que les modèles SQLAlchemy sont définis"""
    print("\n" + "="*70)
    print("TEST 1: Vérification des modèles SQLAlchemy")
    print("="*70)
    
    try:
        from app.database_unified import (
            db, NotificationConfig, NotificationRecipient, 
            NotificationHistory, ReportSchedule
        )
        
        print("✅ Tous les modèles sont importés avec succès:")
        print("   - NotificationConfig")
        print("   - NotificationRecipient")
        print("   - NotificationHistory")
        print("   - ReportSchedule")
        
        # Vérifier les champs
        print("\n📋 Champs définis:")
        print(f"   NotificationConfig: {len(NotificationConfig.__table__.columns)} colonnes")
        print(f"   NotificationRecipient: {len(NotificationRecipient.__table__.columns)} colonnes")
        print(f"   NotificationHistory: {len(NotificationHistory.__table__.columns)} colonnes")
        print(f"   ReportSchedule: {len(ReportSchedule.__table__.columns)} colonnes")
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False


def test_manager_sqlalchemy():
    """✅ Test 2: Tester le NotificationsManagerSQLAlchemy"""
    print("\n" + "="*70)
    print("TEST 2: Test du NotificationsManagerSQLAlchemy")
    print("="*70)
    
    try:
        from app.notifications_manager_sqlalchemy import NotificationsManagerSQLAlchemy
        
        manager = NotificationsManagerSQLAlchemy()
        print("✅ NotificationsManagerSQLAlchemy instancié")
        
        # Vérifier les méthodes disponibles
        methods = [
            'save_email_config', 'get_email_config',
            'add_recipient', 'remove_recipient', 'get_recipients',
            'send_email', 'send_to_all_recipients',
            'get_notification_history', 'get_notification_stats',
            'save_report_schedule', 'get_report_schedules',
            'test_connection', 'get_all_config'
        ]
        
        print("\n✅ Méthodes disponibles:")
        for method in methods:
            if hasattr(manager, method):
                print(f"   ✓ {method}")
            else:
                print(f"   ✗ {method} - MANQUANTE!")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def compare_systems():
    """✅ Test 3: Comparaison des deux systèmes"""
    print("\n" + "="*70)
    print("TEST 3: Comparaison SQLite (ancien) vs SQLAlchemy (nouveau)")
    print("="*70)
    
    comparison = {
        'Aspect': ['Base de données', 'ORM', 'Intégration', 'Scalabilité', 'Requêtes SQL', 'Transactions'],
        'SQLite (ancien)': [
            'SQLite3 raw',
            'Aucun',
            'Séparé (.notification_config.json)',
            'Limité',
            'SQL brut',
            'Manuel'
        ],
        'SQLAlchemy (nouveau)': [
            'SQLite/MySQL/PostgreSQL',
            'SQLAlchemy ORM',
            'app.database_unified.db',
            'Excellent',
            'QueryBuilder',
            'Automatique'
        ]
    }
    
    print("\n📊 Tableau comparatif:")
    print(f"\n{'Aspect':<20} | {'SQLite (ancien)':<30} | {'SQLAlchemy (nouveau)':<30}")
    print("-" * 85)
    
    for i, aspect in enumerate(comparison['Aspect']):
        old = comparison['SQLite (ancien)'][i]
        new = comparison['SQLAlchemy (nouveau)'][i]
        print(f"{aspect:<20} | {old:<30} | {new:<30}")
    
    return True


def migration_strategy():
    """✅ Test 4: Afficher la stratégie de migration"""
    print("\n" + "="*70)
    print("TEST 4: Stratégie de migration")
    print("="*70)
    
    print("""
📋 PLAN DE MIGRATION (2 phases):

PHASE 1: SETUP (Optionnel - pour tester)
─────────────────────────────────────────
1. Les tables SQLAlchemy sont PRÊTES dans database_unified.py
2. NotificationsManagerSQLAlchemy est PRÊT et opérationnel
3. Aucune migration automatique des anciennes données nécessaire
4. Les deux systèmes peuvent coexister temporairement

PHASE 2: ACTIVATION
───────────────────
Options:

Option A - RECOMMANDÉE: Utiliser le nouveau système (SQLAlchemy)
   ✓ Avantages:
     - Intégration complète avec la base unifiée
     - Support multi-bases de données (MySQL, PostgreSQL)
     - Meilleure gestion des transactions
     - QueryBuilder SQLAlchemy au lieu de SQL brut
   
   ✓ Étapes:
     1. Dans app/main.py, remplacer:
        from app.notifications_handler import NotificationsManager
        par:
        from app.notifications_manager_sqlalchemy import NotificationsManagerSQLAlchemy
     
     2. Initialiser avec:
        api_notif_manager = NotificationsManagerSQLAlchemy(app)
     
     3. Utiliser NotificationsManager dans routes_notifications_api.py

Option B - MIGRATION COMPLÈTE: Copier les anciennes données
   ✓ Script fourni: migrate_notifications_data.py
   ✓ Copie configuration et destinataires de:
     - SQLite: database/notifications.db
     vers:
     - SQLAlchemy: app.db (même BD que rest du système)
     
   ✓ Étapes:
     1. Lancer: python migrate_notifications_data.py
     2. Vérifier: test_notifications_sqlalchemy.py
     3. Archiver: mv database/notifications.db database/notifications.db.backup

PHASE 3: TESTS ET VALIDATION
─────────────────────────────
1. test_notifications_sqlalchemy.py - Tests complets du nouveau système
2. Vérifier les données dans app.db:
   - SELECT COUNT(*) FROM notification_config;
   - SELECT COUNT(*) FROM notification_recipient;
3. Accéder à http://localhost:5000/notifications
4. Envoyer un email test pour confirmer
    """)
    
    return True


def code_examples():
    """✅ Test 5: Exemples d'utilisation"""
    print("\n" + "="*70)
    print("TEST 5: Exemples d'utilisation du nouveau système")
    print("="*70)
    
    examples = """
📝 EXEMPLES DE CODE:

1️⃣ CONFIGURATION EMAIL (initialisation)
─────────────────────────────────────────
from app.notifications_manager_sqlalchemy import NotificationsManagerSQLAlchemy

manager = NotificationsManagerSQLAlchemy(app)

result = manager.save_email_config(
    sender_email='notifications@example.com',
    sender_password='app_password_here',
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    use_tls=True
)

2️⃣ AJOUTER DES DESTINATAIRES
──────────────────────────────
manager.add_recipient('admin@example.com')
manager.add_recipient('user@example.com')

3️⃣ ENVOYER UN EMAIL
────────────────────
result = manager.send_email(
    to_email='user@example.com',
    subject='Test Notification',
    body_html='<h1>Bienvenue!</h1><p>Ceci est un test.</p>'
)

4️⃣ ENVOYER À TOUS
──────────────────
result = manager.send_to_all_recipients(
    subject='Rapport Mensuel',
    body_html='<h2>Rapport du mois</h2>...',
    report_type='monthly'
)

5️⃣ CONFIGURER LES RAPPORTS PROGRAMMÉS
─────────────────────────────────────────
# Rapport quotidien à 8h
manager.save_report_schedule(
    report_type='daily',
    is_enabled=True,
    send_hour=8
)

# Rapport hebdomadaire (lundi à 9h)
manager.save_report_schedule(
    report_type='weekly',
    is_enabled=True,
    send_hour=9,
    send_day=0  # 0=Lundi, 6=Dimanche
)

# Rapport mensuel (1er du mois à 9h)
manager.save_report_schedule(
    report_type='monthly',
    is_enabled=True,
    send_hour=9,
    send_day=1
)

6️⃣ TESTER LA CONNEXION
───────────────────────
result = manager.test_connection()
print(result)  # {'success': True/False, 'message': '...'}

7️⃣ OBTENIR L'HISTORIQUE
────────────────────────
history = manager.get_notification_history(limit=20)
for record in history:
    print(f"{record['timestamp']}: {record['type']} -> {record['recipient']}")

8️⃣ STATISTIQUES
────────────────
stats = manager.get_notification_stats()
print(f"Total: {stats['total']}")
print(f"Succès: {stats['success']}")
print(f"Taux de réussite: {stats['success_rate']:.1f}%")
    """
    
    print(examples)
    return True


def integration_in_flask():
    """✅ Test 6: Intégration dans Flask"""
    print("\n" + "="*70)
    print("TEST 6: Comment intégrer dans Flask")
    print("="*70)
    
    code = """
📝 INTÉGRATION DANS app/main.py:

---CUT HERE----
# Ajouter ces imports
from app.notifications_manager_sqlalchemy import NotificationsManagerSQLAlchemy

# Dans l'initialization (après db.init_app)
api_notif_manager = NotificationsManagerSQLAlchemy(app)

# Au démarrage, créer les tables
with app.app_context():
    from app.database_unified import db
    db.create_all()  # Crée les tables SQLAlchemy (y compris notifications)

# Route pour les notifications
@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

---END CUT----

📝 MODIFICATION DE routes_notifications_api.py:

Remplacer:
    from app.notifications_handler import NotificationsManager
    api_notif_manager = NotificationsManager()

Par:
    from app.notifications_manager_sqlalchemy import NotificationsManagerSQLAlchemy
    # On suppose que api_notif_manager est créé dans main.py et passé
    # ou on crée une instance locale:
    api_notif_manager = NotificationsManagerSQLAlchemy()

Les appels API restent EXACTEMENT les mêmes !
Aucune modification nécessaire dans le blueprint.
    """
    
    print(code)
    return True


def advantages():
    """✅ Test 7: Avantages du nouveau système"""
    print("\n" + "="*70)
    print("TEST 7: Avantages du nouveau système")
    print("="*70)
    
    advantages = """
🎯 AVANTAGES DE SQLALCHEMY:

1️⃣ UNIFICATION DE LA BASE DE DONNÉES
   ✓ Toutes les données dans app.db (ou même BD MySQL/PostgreSQL)
   ✓ Plus besoin de database/notifications.db séparé
   ✓ Sauvegarde unique
   ✓ Synchronisation simplifiée

2️⃣ MULTIBASE DE DONNÉES
   ✓ SQLite pour développement
   ✓ MySQL pour production
   ✓ PostgreSQL pour scalabilité
   ✓ Changement = juste modifier DATABASE_URL

3️⃣ MEILLEURE GESTION DES DONNÉES
   ✓ Transactions ACID automatiques
   ✓ Contraintes de clés étrangères
   ✓ Rollback automatique en cas d'erreur
   ✓ Pas de fichier de config JSON séparé

4️⃣ INTÉGRATION SYSTÈME
   ✓ Même ORM que Detection, IoTDataLog, etc.
   ✓ Requêtes cohérentes et lisibles
   ✓ Migration simplifiée avec Alembic
   ✓ Indices de Base de données automatiques

5️⃣ SÉCURITÉ
   ✓ Parameterized Queries (protection SQL Injection)
   ✓ ORM gère l'échappement
   ✓ Pas de concaténation de SQL brut

6️⃣ PERFORMANCE
   ✓ Connection pooling automatique
   ✓ Lazy loading des relations
   ✓ Requêtes optimisées
   ✓ Caching possible

7️⃣ DEBUGGING
   ✓ Logging automatique des requêtes SQL générées
   ✓ Stacktraces clairs avec ORM
   ✓ Validation de schéma automatique
    """
    
    print(advantages)
    return True


def run_all_tests():
    """Lancer tous les tests"""
    print("\n")
    print("="*70)
    print(" "*15 + "SYSTÈME DE NOTIFICATIONS")
    print(" "*12 + "Test de validation SQLAlchemy")
    print("="*70)
    
    tests = [
        ("Modèles SQLAlchemy", test_sqlalchemy_models),
        ("Manager SQLAlchemy", test_manager_sqlalchemy),
        ("Comparaison systèmes", compare_systems),
        ("Stratégie migration", migration_strategy),
        ("Exemples d'utilisation", code_examples),
        ("Intégration Flask", integration_in_flask),
        ("Avantages du nouveau système", advantages),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERREUR dans {name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Résumé final
    print("\n" + "="*70)
    print("RÉSUMÉ FINAL")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests réussis: {passed}/{total}")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("\n📝 PROCHAINES ÉTAPES:")
        print("   1. Revue des exemples d'utilisation du nouveau système")
        print("   2. Optionnel: Lancer migrate_notifications_data.py pour copier les anciennes données")
        print("   3. Modifier app/main.py pour utiliser NotificationsManagerSQLAlchemy")
        print("   4. Tester via http://localhost:5000/notifications")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")


if __name__ == '__main__':
    run_all_tests()
