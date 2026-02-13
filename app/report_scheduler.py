"""
Scheduler pour les rapports email automatiques
Gère l'envoi programmé des rapports quotidiens, hebdomadaires et mensuels
"""

from datetime import datetime, timedelta, date
from apscheduler.schedulers.background import BackgroundScheduler
from app.email_notifications import EmailNotifier
from config import config
from app.logger import logger

class ReportScheduler:
    """Gestionnaire des rapports automatiques"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.notifier = EmailNotifier()
        self.setup_jobs()
    
    def setup_jobs(self):
        """Configurer les tâches planifiées"""
        
        # Vérifier si les variables sont configurées
        if not config.SENDER_EMAIL or not config.SENDER_PASSWORD:
            logger.warning("Email config not complete - skipping scheduler")
            return
        
        recipient_emails = config.RECIPIENT_EMAILS if hasattr(config, 'RECIPIENT_EMAILS') else ''
        if not recipient_emails:
            logger.warning("No recipient emails configured - skipping scheduler")
            return
        
        recipients = [e.strip() for e in recipient_emails.split(',')]
        
        # Rapport quotidien
        try:
            daily_hour = int(getattr(config, 'DAILY_REPORT_HOUR', 8))
            self.scheduler.add_job(
                self.send_daily_report,
                'cron',
                hour=daily_hour,
                minute=0,
                id='daily_report',
                name='Rapport Quotidien',
                args=[recipients]
            )
            logger.info(f"✅ Rapport quotidien programmé à {daily_hour}h00")
        except Exception as e:
            logger.error(f"Erreur configuration rapport quotidien: {e}")
        
        # Rapport hebdomadaire
        try:
            weekly_day = int(getattr(config, 'WEEKLY_REPORT_DAY', 1))  # 1=mardi
            weekly_hour = int(getattr(config, 'WEEKLY_REPORT_HOUR', 9))
            self.scheduler.add_job(
                self.send_weekly_report,
                'cron',
                day_of_week=weekly_day,
                hour=weekly_hour,
                minute=0,
                id='weekly_report',
                name='Rapport Hebdomadaire',
                args=[recipients]
            )
            days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            logger.info(f"✅ Rapport hebdomadaire programmé {days[weekly_day]} à {weekly_hour}h00")
        except Exception as e:
            logger.error(f"Erreur configuration rapport hebdomadaire: {e}")
        
        # Rapport mensuel
        try:
            monthly_day = int(getattr(config, 'MONTHLY_REPORT_DAY', 1))
            monthly_hour = int(getattr(config, 'MONTHLY_REPORT_HOUR', 9))
            self.scheduler.add_job(
                self.send_monthly_report,
                'cron',
                day=monthly_day,
                hour=monthly_hour,
                minute=0,
                id='monthly_report',
                name='Rapport Mensuel',
                args=[recipients]
            )
            logger.info(f"✅ Rapport mensuel programmé le {monthly_day} à {monthly_hour}h00")
        except Exception as e:
            logger.error(f"Erreur configuration rapport mensuel: {e}")
    
    def send_daily_report(self, recipients):
        """Envoyer le rapport quotidien"""
        try:
            logger.info("📊 Envoi rapport quotidien...")
            notifier = EmailNotifier()
            html = notifier.generate_daily_report()
            
            subject = f"📊 Rapport Quotidien EPI Detection - {date.today()}"
            
            for recipient in recipients:
                success = notifier.send_email(recipient, subject, html)
                if success:
                    logger.info(f"✅ Rapport quotidien envoyé à {recipient}")
                else:
                    logger.error(f"❌ Erreur envoi rapport à {recipient}")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du rapport quotidien: {e}")
    
    def send_weekly_report(self, recipients):
        """Envoyer le rapport hebdomadaire"""
        try:
            logger.info("📅 Envoi rapport hebdomadaire...")
            notifier = EmailNotifier()
            html = notifier.generate_weekly_report()
            
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            subject = f"📅 Rapport Hebdomadaire EPI Detection - {week_start.strftime('%d/%m/%Y')}"
            
            for recipient in recipients:
                success = notifier.send_email(recipient, subject, html)
                if success:
                    logger.info(f"✅ Rapport hebdomadaire envoyé à {recipient}")
                else:
                    logger.error(f"❌ Erreur envoi rapport à {recipient}")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du rapport hebdomadaire: {e}")
    
    def send_monthly_report(self, recipients):
        """Envoyer le rapport mensuel"""
        try:
            logger.info("📆 Envoi rapport mensuel...")
            notifier = EmailNotifier()
            html = notifier.generate_monthly_report()
            
            today = date.today()
            subject = f"📆 Rapport Mensuel EPI Detection - {today.strftime('%B %Y')}"
            
            for recipient in recipients:
                success = notifier.send_email(recipient, subject, html)
                if success:
                    logger.info(f"✅ Rapport mensuel envoyé à {recipient}")
                else:
                    logger.error(f"❌ Erreur envoi rapport à {recipient}")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du rapport mensuel: {e}")
    
    def start(self):
        """Démarrer le scheduler"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("✅ Scheduler de rapports démarré")
        except Exception as e:
            logger.error(f"Erreur démarrage scheduler: {e}")
    
    def stop(self):
        """Arrêter le scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("✅ Scheduler arrêté")
        except Exception as e:
            logger.error(f"Erreur arrêt scheduler: {e}")

# Instance globale
report_scheduler = None

def init_report_scheduler():
    """Initialiser le scheduler de rapports"""
    global report_scheduler
    try:
        report_scheduler = ReportScheduler()
        report_scheduler.start()
    except Exception as e:
        logger.error(f"Impossible initialiser scheduler: {e}")
        logger.warning("Les rapports automatiques ne seront pas envoyés")

def get_report_scheduler():
    """Obtenir l'instance du scheduler"""
    return report_scheduler
