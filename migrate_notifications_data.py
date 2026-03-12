"""
MIGRATION SCRIPT - Migrants les données du système SQLite ancien
vers le système SQLAlchemy nouveau (database_unified.db)

Usage:
    python migrate_notifications_data.py
"""

import sqlite3
import os
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NotificationsDataMigrator:
    """Migrer les données du système ancien SQLite vers SQLAlchemy"""
    
    def __init__(self):
        self.old_db_path = 'database/notifications.db'
        self.old_config_path = '.notification_config.json'
        
        # On importe après vérification que les fichiers existent
        self.new_db_session = None
        self.migration_stats = {
            'email_configs': 0,
            'recipients': 0,
            'schedules': 0,
            'history': 0,
            'errors': 0
        }
    
    def check_old_system_exists(self) -> bool:
        """Vérifier que l'ancien système existe"""
        print("\n" + "="*70)
        print("VÉRIFICATION DE L'ANCIEN SYSTÈME")
        print("="*70)
        
        db_exists = os.path.exists(self.old_db_path)
        config_exists = os.path.exists(self.old_config_path)
        
        print(f"\n📁 Ancien système SQLite: {'✓ Trouvé' if db_exists else '✗ Non trouvé'}")
        if db_exists:
            size = os.path.getsize(self.old_db_path)
            print(f"   Taille: {size} bytes")
        
        print(f"📁 Ancien config JSON: {'✓ Trouvé' if config_exists else '✗ Non trouvé'}")
        if config_exists:
            size = os.path.getsize(self.old_config_path)
            print(f"   Taille: {size} bytes")
        
        if not db_exists and not config_exists:
            print("\n⚠️  Aucune donnée ancienne à migrer")
            return False
        
        return True
    
    def init_new_system(self):
        """Initialiser le session SQLAlchemy du nouveau système"""
        try:
            import sys
            from pathlib import Path
            
            # Ajouter le chemin du projet
            project_root = Path(__file__).resolve().parent
            sys.path.insert(0, str(project_root))
            
            # Importer directement depuis main.py
            from app.main import app, db
            from app.database_unified import NotificationConfig, NotificationRecipient
            
            logger.info("Création des tables SQLAlchemy...")
            
            with app.app_context():
                db.create_all()
                logger.info("✓ Tables SQLAlchemy créées")
                
                self.new_db_session = db
                self.app = app
                self.models = {
                    'NotificationConfig': NotificationConfig,
                    'NotificationRecipient': NotificationRecipient,
                }
                
                return True
        except Exception as e:
            logger.error(f"Erreur initialisant le nouveau système: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def migrate_email_config(self) -> bool:
        """Migrer la configuration email"""
        print("\n" + "="*70)
        print("MIGRATION: Configuration Email")
        print("="*70)
        
        if not os.path.exists(self.old_config_path):
            print("✓ Pas de configuration JSON à migrer")
            return True
        
        try:
            with open(self.old_config_path, 'r') as f:
                config = json.load(f)
            
            logger.info(f"Lecture config: {config.get('email', 'N/A')}")
            
            if 'email' not in config:
                print("⚠️  Pas de configuration email dans le JSON")
                return True
            
            from app.database_unified import NotificationConfig
            
            new_config = NotificationConfig(
                sender_email=config['email'],
                sender_password=config.get('password', ''),
                smtp_server=config.get('smtp_server', 'smtp.gmail.com'),
                smtp_port=int(config.get('smtp_port', 587)),
                use_tls=config.get('use_tls', True),
                daily_enabled=config.get('daily_enabled', True),
                daily_hour=config.get('daily_hour', 8),
                weekly_enabled=config.get('weekly_enabled', False),
                weekly_day=config.get('weekly_day', 0),
                weekly_hour=config.get('weekly_hour', 9),
                monthly_enabled=config.get('monthly_enabled', False),
                monthly_day=config.get('monthly_day', 1),
                monthly_hour=config.get('monthly_hour', 9),
            )
            
            self.new_db_session.session.add(new_config)
            self.new_db_session.session.commit()
            
            self.migration_stats['email_configs'] += 1
            print(f"✓ Configuration email migrée: {config['email']}")
            return True
        
        except Exception as e:
            logger.error(f"Erreur migrant email config: {str(e)}")
            self.migration_stats['errors'] += 1
            self.new_db_session.session.rollback()
            return False
    
    def migrate_recipients(self) -> bool:
        """Migrer les destinataires"""
        print("\n" + "="*70)
        print("MIGRATION: Destinataires")
        print("="*70)
        
        if not os.path.exists(self.old_db_path):
            print("✓ Pas de base de données SQLite à migrer")
            return True
        
        try:
            conn = sqlite3.connect(self.old_db_path)
            cursor = conn.cursor()
            
            # Vérifier si la table existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='recipients'
            """)
            
            if not cursor.fetchone():
                print("⚠️  Pas de table recipients dans l'ancien système")
                conn.close()
                return True
            
            # Récupérer les destinataires
            cursor.execute("SELECT email FROM recipients")
            recipients = cursor.fetchall()
            
            from app.database_unified import NotificationRecipient
            
            for (email,) in recipients:
                try:
                    # Vérifier si n'existe pas déjà (dans le contexte de l'app)
                    existing = self.new_db_session.session.query(NotificationRecipient).filter_by(email=email).first()
                    if existing:
                        logger.debug(f"Destinataire {email} existe déjà, skipped")
                        continue
                    
                    recipient = NotificationRecipient(email=email)
                    self.new_db_session.session.add(recipient)
                    self.migration_stats['recipients'] += 1
                    logger.info(f"✓ Destinataire migré: {email}")
                
                except Exception as e:
                    logger.error(f"Erreur migrant recipient {email}: {str(e)}")
                    self.migration_stats['errors'] += 1
            
            self.new_db_session.session.commit()
            conn.close()
            
            print(f"✓ {self.migration_stats['recipients']} destinataires migrés")
            return True
        
        except Exception as e:
            logger.error(f"Erreur migrant recipients: {str(e)}")
            self.migration_stats['errors'] += 1
            self.new_db_session.session.rollback()
            return False
    
    def migrate_report_schedules(self) -> bool:
        """Migrer les planifications de rapports"""
        print("\n" + "="*70)
        print("MIGRATION: Planifications de Rapports")
        print("="*70)
        
        if not os.path.exists(self.old_db_path):
            print("✓ Pas de base de données SQLite à migrer")
            return True
        
        try:
            conn = sqlite3.connect(self.old_db_path)
            cursor = conn.cursor()
            
            # Vérifier si la table existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='report_schedules'
            """)
            
            if not cursor.fetchone():
                print("⚠️  Pas de table report_schedules dans l'ancien système")
                conn.close()
                return True
            
            cursor.execute("SELECT * FROM report_schedules")
            schedules = cursor.fetchall()
            
            from app.database_unified import ReportSchedule
            
            for schedule in schedules:
                try:
                    report_type = schedule[1] if len(schedule) > 1 else 'custom'
                    
                    schedule_new = ReportSchedule(
                        report_type=report_type,
                        is_enabled=True,
                        send_hour=8,
                        send_minute=0,
                        frequency=report_type
                    )
                    self.new_db_session.session.add(schedule_new)
                    self.migration_stats['schedules'] += 1
                    logger.info(f"✓ Planification migrée: {report_type}")
                
                except Exception as e:
                    logger.error(f"Erreur migrant schedule: {str(e)}")
                    self.migration_stats['errors'] += 1
            
            self.new_db_session.session.commit()
            conn.close()
            
            print(f"✓ {self.migration_stats['schedules']} planifications migrées")
            return True
        
        except Exception as e:
            logger.error(f"Erreur migrant schedules: {str(e)}")
            self.migration_stats['errors'] += 1
            self.new_db_session.session.rollback()
            return False
    
    def migrate_notification_history(self) -> bool:
        """Migrer l'historique des notifications"""
        print("\n" + "="*70)
        print("MIGRATION: Historique des Notifications")
        print("="*70)
        
        if not os.path.exists(self.old_db_path):
            print("✓ Pas de base de données SQLite à migrer")
            return True
        
        try:
            conn = sqlite3.connect(self.old_db_path)
            cursor = conn.cursor()
            
            # Vérifier si la table existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='notification_history'
            """)
            
            if not cursor.fetchone():
                print("⚠️  Pas de table notification_history dans l'ancien système")
                conn.close()
                return True
            
            cursor.execute("SELECT * FROM notification_history LIMIT 100")
            history_records = cursor.fetchall()
            
            from app.database_unified import NotificationHistory
            
            for record in history_records:
                try:
                    # Adapter selon la structure réelle
                    hist = NotificationHistory(
                        notification_type='migrated',
                        recipient=record[1] if len(record) > 1 else 'unknown',
                        status='success',
                        message_preview='Migré de l\'ancien système'
                    )
                    self.new_db_session.session.add(hist)
                    self.migration_stats['history'] += 1
                
                except Exception as e:
                    logger.error(f"Erreur migrant history record: {str(e)}")
                    self.migration_stats['errors'] += 1
            
            self.new_db_session.session.commit()
            conn.close()
            
            print(f"✓ {self.migration_stats['history']} enregistrements historiques migrés")
            return True
        
        except Exception as e:
            logger.error(f"Erreur migrant history: {str(e)}")
            self.migration_stats['errors'] += 1
            self.new_db_session.session.rollback()
            return False
    
    def backup_old_database(self) -> bool:
        """Créer une sauvegarde des anciennes données"""
        print("\n" + "="*70)
        print("SAUVEGARDE: Ancien système")
        print("="*70)
        
        import shutil
        
        if os.path.exists(self.old_db_path):
            backup_path = f"{self.old_db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                shutil.copy2(self.old_db_path, backup_path)
                print(f"✓ Sauvegarde de {self.old_db_path}")
                print(f"  → {backup_path}")
                return True
            except Exception as e:
                logger.error(f"Erreur sauvegardant la base: {str(e)}")
                return False
        
        return True
    
    def migrate(self):
        """Lancer la migration complète"""
        print("\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*15 + "MIGRATION DES DONNÉES DE NOTIFICATIONS" + " "*15 + "║")
        print("║" + " "*12 + "SQLite ancien → SQLAlchemy nouveau" + " "*22 + "║")
        print("╚" + "="*68 + "╝")
        
        # Vérifier l'ancien système
        if not self.check_old_system_exists():
            print("\n⏭️  Migration annulée (aucune donnée ancienne)")
            return False
        
        # Initialiser le nouveau
        if not self.init_new_system():
            print("\n❌ Erreur initialisant le nouveau système")
            return False
        
        with self.app.app_context():
            # Migrer les données
            success = True
            success &= self.migrate_email_config()
            success &= self.migrate_recipients()
            success &= self.migrate_report_schedules()
            success &= self.migrate_notification_history()
            
            # Sauvegarder l'ancien système
            self.backup_old_database()
        
        # Résumé
        self.print_summary(success)
        
        return success
    
    def print_summary(self, success: bool):
        """Afficher le résumé de la migration"""
        print("\n" + "="*70)
        print("RÉSUMÉ DE LA MIGRATION")
        print("="*70)
        
        total_migrated = sum(self.migration_stats.values()) - self.migration_stats['errors']
        
        print("\n📊 Statistiques:")
        for key, value in self.migration_stats.items():
            if key == 'errors':
                if value > 0:
                    print(f"   ❌ {key}: {value}")
            else:
                print(f"   ✓ {key}: {value}")
        
        total_migrated = (self.migration_stats['email_configs'] + 
                         self.migration_stats['recipients'] +
                         self.migration_stats['schedules'] +
                         self.migration_stats['history'])
        
        print(f"\n📈 Total migré: {total_migrated} éléments")
        print(f"❌ Erreurs: {self.migration_stats['errors']}")
        
        if success and self.migration_stats['errors'] == 0:
            print("\n✅ MIGRATION RÉUSSIE!")
            print("\n📋 Prochaines étapes:")
            print("   1. Vérifier les données dans app.db:")
            print("      - SELECT COUNT(*) FROM notification_recipient;")
            print("   2. Tester l'interface web:")
            print("      - Aller à http://localhost:5000/notifications")
            print("   3. Optionnel: Supprimer l'ancien système")
            print("      - rm database/notifications.db")
            print("      - rm .notification_config.json")
        else:
            print("\n⚠️  La migration a rencontré des problèmes.")
            print("   Vérifiez les logs ci-dessus.")


if __name__ == '__main__':
    import sys
    
    # Vérifier qu'on est à la bonne place
    if not os.path.exists('app'):
        print("❌ Erreur: Lancez ce script depuis la racine du projet")
        sys.exit(1)
    
    migrator = NotificationsDataMigrator()
    success = migrator.migrate()
    
    sys.exit(0 if success else 1)
