"""
Service de Notification - Gestion des notifications manuelles et automatiques
Supports envoi manuel via formulaire, rapports quotidien/hebdomadaire/mensuel
"""

import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date, timedelta
from pathlib import Path
from app.logger import logger
from config import config

# Fichiers de stockage
NOTIFICATIONS_DB_FILE = Path(__file__).parent.parent / '.notifications_db.json'
RECIPIENTS_FILE = Path(__file__).parent.parent / '.notification_recipients'
CONFIG_FILE = Path(__file__).parent.parent / '.notification_config.json'


class NotificationService:
    """Service central pour gérer les notifications"""
    
    def __init__(self):
        self.config = self._load_config()
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Créer les fichiers s'ils n'existent pas"""
        if not RECIPIENTS_FILE.exists():
            RECIPIENTS_FILE.touch()
        if not NOTIFICATIONS_DB_FILE.exists():
            NOTIFICATIONS_DB_FILE.write_text(json.dumps([]))
        if not CONFIG_FILE.exists():
            CONFIG_FILE.write_text(json.dumps({
                'sender_email': '',
                'sender_password': '',
                'daily_enabled': True,
                'daily_hour': 8,
                'weekly_enabled': False,
                'weekly_day': 0,
                'weekly_hour': 9,
                'monthly_enabled': False,
                'monthly_day': 1,
                'monthly_hour': 9
            }))
    
    def _load_config(self) -> dict:
        """Charger la configuration sauvegardée"""
        try:
            if CONFIG_FILE.exists():
                return json.loads(CONFIG_FILE.read_text())
        except Exception as e:
            logger.error(f"Erreur chargement config: {e}")
        
        return {
            'sender_email': getattr(config, 'SENDER_EMAIL', ''),
            'sender_password': getattr(config, 'SENDER_PASSWORD', ''),
            'daily_enabled': True,
            'daily_hour': 8,
            'weekly_enabled': False,
            'weekly_day': 0,
            'weekly_hour': 9,
            'monthly_enabled': False,
            'monthly_day': 1,
            'monthly_hour': 9
        }
    
    def _save_config(self):
        """Sauvegarder la configuration"""
        try:
            CONFIG_FILE.write_text(json.dumps(self.config, indent=2))
        except Exception as e:
            logger.error(f"Erreur sauvegarde config: {e}")
    
    def get_config(self) -> dict:
        """Récupérer la configuration actuelle"""
        return self.config
    
    def save_config(self, config_data: dict) -> bool:
        """Sauvegarder la nouvelle configuration"""
        try:
            self.config.update(config_data)
            self._save_config()
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    # ====== GESTION DES DESTINATAIRES ======
    
    def get_recipients(self) -> list:
        """Récupérer la liste des destinataires"""
        try:
            if RECIPIENTS_FILE.exists():
                content = RECIPIENTS_FILE.read_text().strip()
                if content:
                    return [r.strip() for r in content.split('\n') if r.strip()]
        except Exception as e:
            logger.error(f"Erreur lecture destinataires: {e}")
        return []
    
    def add_recipient(self, email: str) -> bool:
        """Ajouter un destinataire"""
        try:
            # Validation basique
            if not email or '@' not in email:
                return False
            
            recipients = self.get_recipients()
            if email in recipients:
                return False  # Déjà présent
            
            recipients.append(email)
            RECIPIENTS_FILE.write_text('\n'.join(recipients))
            logger.info(f"Destinataire ajouté: {email}")
            return True
        except Exception as e:
            logger.error(f"Erreur ajout destinataire: {e}")
            return False
    
    def remove_recipient(self, email: str) -> bool:
        """Supprimer un destinataire"""
        try:
            recipients = self.get_recipients()
            if email in recipients:
                recipients.remove(email)
                RECIPIENTS_FILE.write_text('\n'.join(recipients))
                logger.info(f"Destinataire supprimé: {email}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur suppression destinataire: {e}")
            return False
    
    # ====== ENVOI D'EMAIL ======
    
    def send_email(self, recipient: str, subject: str, html_content: str, notif_type: str = 'manual') -> bool:
        """Envoyer un email"""
        try:
            sender_email = self.config.get('sender_email')
            sender_password = self.config.get('sender_password')
            
            if not sender_email or not sender_password:
                logger.error("Email expéditeur ou mot de passe manquant")
                return False
            
            # Déterminer le serveur SMTP à utiliser
            smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')  # Default Gmail
            smtp_port = self.config.get('smtp_port', 587)
            
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipient
            
            # Ajouter le contenu HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Envoyer via SMTP
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())
            server.quit()
            
            logger.info(f"Email envoyé à {recipient}: {subject}")
            
            # Enregistrer dans l'historique
            self._record_notification(recipient, notif_type, subject, 'success')
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email à {recipient}: {e}")
            self._record_notification(recipient, notif_type, subject, 'error', str(e))
            return False
    
    def test_connection(self) -> dict:
        """Tester la connexion email"""
        try:
            sender_email = self.config.get('sender_email')
            sender_password = self.config.get('sender_password')
            
            if not sender_email or not sender_password:
                return {'success': False, 'error': 'Credentials not configured'}
            
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
            server.starttls()
            server.login(sender_email, sender_password)
            server.quit()
            
            logger.info("Test de connexion réussi")
            return {'success': True, 'message': 'Connection successful'}
            
        except Exception as e:
            logger.error(f"Erreur test connexion: {e}")
            return {'success': False, 'error': str(e)}
    
    # ====== NOTIFICATIONS MANUELLES ======
    
    def send_manual_notification(self, subject: str, message: str, recipient: str) -> bool:
        """Envoyer une notification manuelle"""
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #8B1538; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f5f5f5; padding: 20px; border-radius: 0 0 5px 5px; }}
                .message {{ white-space: pre-wrap; line-height: 1.8; }}
                .footer {{ margin-top: 20px; font-size: 0.9em; color: #999; border-top: 1px solid #ddd; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">{subject}</h2>
                </div>
                <div class="content">
                    <div class="message">{message}</div>
                    <div class="footer">
                        <p>Notification envoyée depuis EPI Detection</p>
                        <p>{datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(recipient, subject, html_content, 'manual')
    
    # ====== RAPPORTS AUTOMATIQUES ======
    
    def generate_daily_report(self) -> str:
        """Générer le rapport quotidien en HTML"""
        from app.database_unified import db, Detection, Alert, DailyPresence
        
        yesterday = date.today() - timedelta(days=1)
        
        try:
            # Récupérer les données
            detections = Detection.query.filter(
                db.func.date(Detection.timestamp) == yesterday
            ).all()
            
            alerts = Alert.query.filter(
                db.func.date(Alert.timestamp) == yesterday
            ).all()
            
            presences = DailyPresence.query.filter_by(date=yesterday).all()
            
            # Calculs
            total_detections = len(detections)
            compliance_rate = sum(d.compliance_rate for d in detections if d.compliance_rate) / len(detections) if detections else 0
            total_alerts = len(alerts)
            total_presences = len(presences)
            
        except Exception as e:
            logger.error(f"Erreur génération rapport: {e}")
            total_detections = 0
            compliance_rate = 0
            total_alerts = 0
            total_presences = 0
        
        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #8B1538 0%, #6d0e2a 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 2em; }}
                .header p {{ margin: 5px 0 0 0; opacity: 0.9; }}
                .stats {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; padding: 30px; }}
                .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #8B1538; }}
                .stat-value {{ font-size: 2.5em; font-weight: bold; color: #8B1538; margin: 10px 0; }}
                .stat-label {{ font-size: 0.9em; color: #666; }}
                .content {{ padding: 30px; }}
                .section {{ margin-bottom: 20px; }}
                .section h3 {{ color: #8B1538; margin-top: 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 0.9em; color: #999; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Rapport Quotidien</h1>
                    <p>EPI Detection - {yesterday.strftime('%d/%m/%Y')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{total_detections}</div>
                        <div class="stat-label">Détections</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{compliance_rate:.1f}%</div>
                        <div class="stat-label">Conformité</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{total_alerts}</div>
                        <div class="stat-label">Alertes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{total_presences}</div>
                        <div class="stat-label">Présences</div>
                    </div>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h3>Résumé</h3>
                        <p>Rapport généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>EPI Detection System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_weekly_report(self) -> str:
        """Générer le rapport hebdomadaire en HTML"""
        from app.database_unified import db, Detection
        
        today = date.today()
        seven_days_ago = today - timedelta(days=7)
        
        try:
            detections = Detection.query.filter(
                db.func.date(Detection.timestamp) >= seven_days_ago,
                db.func.date(Detection.timestamp) <= today
            ).all()
            
            total_detections = len(detections)
            compliance_rate = sum(d.compliance_rate for d in detections if d.compliance_rate) / len(detections) if detections else 0
            
        except Exception as e:
            logger.error(f"Erreur génération rapport hebdo: {e}")
            total_detections = 0
            compliance_rate = 0
        
        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 2em; }}
                .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 30px; }}
                .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #17a2b8; }}
                .stat-value {{ font-size: 2.5em; font-weight: bold; color: #17a2b8; margin: 10px 0; }}
                .stat-label {{ font-size: 0.9em; color: #666; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 0.9em; color: #999; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Rapport Hebdomadaire</h1>
                    <p>EPI Detection - Semaine du {seven_days_ago.strftime('%d/%m/%Y')} au {today.strftime('%d/%m/%Y')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{total_detections}</div>
                        <div class="stat-label">Total Détections</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{compliance_rate:.1f}%</div>
                        <div class="stat-label">Conformité Moyenne</div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>EPI Detection System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_monthly_report(self) -> str:
        """Générer le rapport mensuel en HTML"""
        from app.database_unified import db, Detection
        
        today = date.today()
        first_day = date(today.year, today.month, 1)
        
        try:
            detections = Detection.query.filter(
                db.func.date(Detection.timestamp) >= first_day,
                db.func.date(Detection.timestamp) <= today
            ).all()
            
            total_detections = len(detections)
            compliance_rate = sum(d.compliance_rate for d in detections if d.compliance_rate) / len(detections) if detections else 0
            
        except Exception as e:
            logger.error(f"Erreur génération rapport mensuel: {e}")
            total_detections = 0
            compliance_rate = 0
        
        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #ffc107 0%, #f39c12 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 2em; }}
                .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 30px; }}
                .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #ffc107; }}
                .stat-value {{ font-size: 2.5em; font-weight: bold; color: #f39c12; margin: 10px 0; }}
                .stat-label {{ font-size: 0.9em; color: #666; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 0.9em; color: #999; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Rapport Mensuel</h1>
                    <p>EPI Detection - {today.strftime('%B %Y')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{total_detections}</div>
                        <div class="stat-label">Total Détections</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{compliance_rate:.1f}%</div>
                        <div class="stat-label">Conformité Moyenne</div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>EPI Detection System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    # ====== HISTORIQUE DES NOTIFICATIONS ======
    
    def _record_notification(self, recipient: str, notif_type: str, subject: str, status: str, error: str = None):
        """Enregistrer une notification dans l'historique"""
        try:
            history = json.loads(NOTIFICATIONS_DB_FILE.read_text())
            
            entry = {
                'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'type': notif_type,
                'recipient': recipient,
                'subject': subject,
                'status': status,
                'details': error or 'OK'
            }
            
            history.insert(0, entry)  # Ajouter au début
            history = history[:500]  # Garder les 500 dernières
            
            NOTIFICATIONS_DB_FILE.write_text(json.dumps(history, indent=2))
        except Exception as e:
            logger.error(f"Erreur enregistrement historique: {e}")
    
    def get_history(self, limit: int = 100) -> list:
        """Récupérer l'historique des notifications"""
        try:
            if NOTIFICATIONS_DB_FILE.exists():
                history = json.loads(NOTIFICATIONS_DB_FILE.read_text())
                return history[:limit]
        except Exception as e:
            logger.error(f"Erreur lecture historique: {e}")
        return []
    
    def send_report(self, report_type: str) -> bool:
        """Envoyer un rapport à tous les destinataires"""
        recipients = self.get_recipients()
        
        if not recipients:
            logger.warning(f"Aucun destinataire pour le rapport {report_type}")
            return False
        
        # Générer le rapport
        if report_type == 'daily':
            html_content = self.generate_daily_report()
            subject = f"Rapport Quotidien - EPI Detection {date.today().strftime('%d/%m/%Y')}"
        elif report_type == 'weekly':
            html_content = self.generate_weekly_report()
            yesterday = date.today() - timedelta(days=1)
            subject = f"Rapport Hebdomadaire - EPI Detection {yesterday.strftime('%d/%m/%Y')}"
        elif report_type == 'monthly':
            html_content = self.generate_monthly_report()
            subject = f"Rapport Mensuel - EPI Detection {date.today().strftime('%B %Y')}"
        else:
            return False
        
        # Envoyer à tous les destinataires
        success_count = 0
        for recipient in recipients:
            if self.send_email(recipient, subject, html_content, report_type):
                success_count += 1
        
        logger.info(f"Rapport {report_type} envoyé à {success_count}/{len(recipients)} destinataires")
        return success_count > 0


# Instance globale
notification_service = NotificationService()
