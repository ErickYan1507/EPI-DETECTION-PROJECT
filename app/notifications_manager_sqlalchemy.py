"""
Gestionnaire de notifications utilisant Flask-SQLAlchemy
Remplace notifications_handler.py pour une intégration complète avec la base de données unifiée
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
import json
from typing import List, Dict, Optional, Tuple

from app.database_unified import (
    db, 
    NotificationConfig, 
    NotificationRecipient, 
    NotificationHistory, 
    ReportSchedule
)

logger = logging.getLogger(__name__)


class NotificationsManagerSQLAlchemy:
    """
    Gestionnaire de notifications utilisant Flask-SQLAlchemy
    Supporte SQLite, MySQL, PostgreSQL via SQLAlchemy
    """
    
    def __init__(self, app=None):
        self.app = app
        self.logger = logger
    
    # =========================================================================
    # Configuration SMTP
    # =========================================================================
    
    def save_email_config(self, sender_email: str, sender_password: str, 
                         smtp_server: str = 'smtp.gmail.com', 
                         smtp_port: int = 587,
                         use_tls: bool = True) -> Dict:
        """Sauvegarder ou mettre à jour la configuration email"""
        try:
            # Désactiver les anciennes configurations pour garantir
            # une seule configuration active à la fois.
            NotificationConfig.query.update({'is_active': False})

            config = NotificationConfig.query.filter_by(sender_email=sender_email).first()
            
            if config:
                config.sender_password = sender_password
                config.smtp_server = smtp_server
                config.smtp_port = smtp_port
                config.use_tls = use_tls
                config.is_active = True
                config.updated_date = datetime.utcnow()
            else:
                config = NotificationConfig(
                    sender_email=sender_email,
                    sender_password=sender_password,
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    use_tls=use_tls,
                    is_active=True
                )
                db.session.add(config)
            
            db.session.commit()
            return {
                'success': True,
                'message': 'Configuration email sauvegardée',
                'config': config.to_dict()
            }
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Erreur saving email config: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_email_config(self) -> Optional[Dict]:
        """Récupérer la configuration email active"""
        try:
            config = NotificationConfig.query.filter_by(is_active=True).first()
            return config.to_dict() if config else None
        except Exception as e:
            self.logger.error(f"Erreur getting email config: {str(e)}")
            return None
    
    # =========================================================================
    # Gestion des destinataires
    # =========================================================================
    
    def add_recipient(self, email: str) -> Dict:
        """Ajouter un destinataire"""
        try:
            # Validation simple de l'email
            if not self._validate_email(email):
                return {
                    'success': False,
                    'message': 'Format email invalide'
                }
            
            # Vérifier si existe déjà
            existing = NotificationRecipient.query.filter_by(email=email).first()
            if existing:
                return {
                    'success': False,
                    'message': f'Le destinataire {email} existe déjà'
                }
            
            recipient = NotificationRecipient(email=email)
            db.session.add(recipient)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Destinataire {email} ajouté',
                'recipient': recipient.to_dict()
            }
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Erreur adding recipient: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def remove_recipient(self, email: str) -> Dict:
        """Supprimer un destinataire"""
        try:
            recipient = NotificationRecipient.query.filter_by(email=email).first()
            if not recipient:
                return {
                    'success': False,
                    'message': f'Destinataire {email} non trouvé'
                }
            
            db.session.delete(recipient)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Destinataire {email} supprimé'
            }
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Erreur removing recipient: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_recipients(self, active_only: bool = True) -> List[Dict]:
        """Obtenir la liste des destinataires"""
        try:
            query = NotificationRecipient.query
            if active_only:
                query = query.filter_by(is_active=True)
            
            recipients = query.all()
            return [r.to_dict() for r in recipients]
        except Exception as e:
            self.logger.error(f"Erreur getting recipients: {str(e)}")
            return []
    
    # =========================================================================
    # Envoi de notifications
    # =========================================================================
    
    def send_email(self, to_email: str, subject: str, body_html: str, 
                   body_text: Optional[str] = None, log_history: bool = True) -> Dict:
        """Envoyer un email"""
        try:
            config = self.get_email_config()
            if not config:
                return {
                    'success': False,
                    'message': 'Configuration email non disponible'
                }
            
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = config['sender_email']
            msg['To'] = to_email
            
            # Ajouter les parties texte et HTML
            if body_text:
                part1 = MIMEText(body_text, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(body_html, 'html')
            msg.attach(part2)
            
            # Envoyer l'email
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                if config['use_tls']:
                    server.starttls()
                server.login(config['sender_email'], config['sender_password'])
                server.send_message(msg)
            
            # Logger l'historique
            if log_history:
                self._log_notification('manual', to_email, subject, body_text or body_html, 'success')
            
            return {
                'success': True,
                'message': f'Email envoyé à {to_email}'
            }
        except Exception as e:
            self.logger.error(f"Erreur sending email: {str(e)}")
            
            # Logger l'erreur
            if log_history:
                self._log_notification('manual', to_email, subject, str(e), 'error', str(e))
            
            return {
                'success': False,
                'message': f'Erreur: {str(e)}'
            }
    
    def send_to_all_recipients(self, subject: str, body_html: str, 
                               body_text: Optional[str] = None,
                               report_type: Optional[str] = None) -> Dict:
        """Envoyer un email à tous les destinataires"""
        recipients = self.get_recipients()
        if not recipients:
            return {
                'success': False,
                'message': 'Aucun destinataire configuré'
            }
        
        results = {
            'success': True,
            'sent': 0,
            'failed': 0,
            'details': []
        }
        
        for recipient in recipients:
            result = self.send_email(
                recipient['email'], 
                subject, 
                body_html, 
                body_text
            )
            
            if result['success']:
                results['sent'] += 1
                # Mettre à jour la date de dernière notification
                recipient_obj = NotificationRecipient.query.filter_by(
                    email=recipient['email']
                ).first()
                if recipient_obj:
                    recipient_obj.last_notification = datetime.utcnow()
                    db.session.commit()
            else:
                results['failed'] += 1
            
            results['details'].append({
                'email': recipient['email'],
                'status': 'success' if result['success'] else 'error',
                'message': result['message']
            })
        
        return results
    
    # =========================================================================
    # Historique des notifications
    # =========================================================================
    
    def _log_notification(self, notification_type: str, recipient: str, 
                         subject: str, message_preview: str,
                         status: str = 'pending', error_message: Optional[str] = None,
                         report_type: Optional[str] = None):
        """Logger une notification dans l'historique"""
        try:
            history = NotificationHistory(
                notification_type=notification_type,
                recipient=recipient,
                subject=subject,
                message_preview=message_preview[:500] if message_preview else None,
                status=status,
                error_message=error_message,
                report_type=report_type
            )
            db.session.add(history)
            db.session.commit()
        except Exception as e:
            self.logger.error(f"Erreur logging notification: {str(e)}")
            db.session.rollback()

    def log_notification(self, notification_type: str, recipient: str,
                         subject: str, status: str = 'pending',
                         error_message: Optional[str] = None,
                         report_type: Optional[str] = None,
                         message_preview: Optional[str] = None):
        """Public wrapper compatible avec l'ancien API pour logger une notification"""
        self._log_notification(notification_type, recipient, subject, message_preview or '', status, error_message, report_type)
    
    def get_notification_history(self, limit: int = 100, 
                                offset: int = 0) -> List[Dict]:
        """Obtenir l'historique des notifications"""
        try:
            history = NotificationHistory.query.order_by(
                NotificationHistory.timestamp.desc()
            ).limit(limit).offset(offset).all()
            
            return [h.to_dict() for h in history]
        except Exception as e:
            self.logger.error(f"Erreur getting history: {str(e)}")
            return []
    
    def get_notification_stats(self) -> Dict:
        """Obtenir les statistiques des notifications"""
        try:
            total = NotificationHistory.query.count()
            success = NotificationHistory.query.filter_by(status='success').count()
            errors = NotificationHistory.query.filter_by(status='error').count()
            
            # Statistiques par type
            by_type = {}
            types = db.session.query(NotificationHistory.notification_type).distinct()
            for row in types:
                ntype = row[0]
                by_type[ntype] = NotificationHistory.query.filter_by(
                    notification_type=ntype
                ).count()
            
            return {
                'total': total,
                'success': success,
                'errors': errors,
                'success_rate': (success / total * 100) if total > 0 else 0,
                'by_type': by_type
            }
        except Exception as e:
            self.logger.error(f"Erreur getting stats: {str(e)}")
            return {}
    
    # =========================================================================
    # Planification des rapports
    # =========================================================================
    
    def save_report_schedule(self, report_type: str, is_enabled: bool,
                            send_hour: int, send_minute: int = 0,
                            send_day: Optional[int] = None) -> Dict:
        """Sauvegarder la planification d'un rapport"""
        try:
            schedule = ReportSchedule.query.filter_by(report_type=report_type).first()
            
            if schedule:
                schedule.is_enabled = is_enabled
                schedule.send_hour = send_hour
                schedule.send_minute = send_minute
                if send_day is not None:
                    schedule.send_day = send_day
            else:
                schedule = ReportSchedule(
                    report_type=report_type,
                    is_enabled=is_enabled,
                    send_hour=send_hour,
                    send_minute=send_minute,
                    send_day=send_day,
                    frequency=report_type
                )
                db.session.add(schedule)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Planification {report_type} sauvegardée',
                'schedule': schedule.to_dict()
            }
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Erreur saving report schedule: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_report_schedules(self) -> List[Dict]:
        """Obtenir toutes les planifications de rapports"""
        try:
            schedules = ReportSchedule.query.all()
            return [s.to_dict() for s in schedules]
        except Exception as e:
            self.logger.error(f"Erreur getting schedules: {str(e)}")
            return []
    
    # =========================================================================
    # Tests et validation
    # =========================================================================
    
    def test_connection(self) -> Dict:
        """Tester la connexion SMTP"""
        try:
            config = self.get_email_config()
            if not config:
                return {
                    'success': False,
                    'message': 'Configuration email non disponible'
                }
            
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                if config['use_tls']:
                    server.starttls()
                server.login(config['sender_email'], config['sender_password'])
            
            # Mettre à jour le statut de test
            notification_config = NotificationConfig.query.filter_by(
                sender_email=config['sender_email']
            ).first()
            if notification_config:
                notification_config.last_test = datetime.utcnow()
                notification_config.test_status = 'success'
                db.session.commit()
            
            return {
                'success': True,
                'message': 'Connexion SMTP réussie'
            }
        except Exception as e:
            # Mettre à jour le statut d'erreur
            try:
                notification_config = NotificationConfig.query.filter_by(
                    is_active=True
                ).first()
                if notification_config:
                    notification_config.last_test = datetime.utcnow()
                    notification_config.test_status = 'error'
                    db.session.commit()
            except:
                pass
            
            self.logger.error(f"Erreur testing connection: {str(e)}")
            return {
                'success': False,
                'message': f'Erreur SMTP: {str(e)}'
            }
    
    # =========================================================================
    # Utilitaires
    # =========================================================================
    
    def _validate_email(self, email: str) -> bool:
        """Validation simple d'une adresse email"""
        return '@' in email and '.' in email.split('@')[-1]
    
    def get_all_config(self) -> Dict:
        """Obtenir toute la configuration"""
        return {
            'email_config': self.get_email_config(),
            'recipients': self.get_recipients(),
            'schedules': self.get_report_schedules(),
            'stats': self.get_notification_stats()
        }


def init_notifications(app):
    """Initialiser le système de notifications avec Flask-SQLAlchemy"""
    return NotificationsManagerSQLAlchemy(app)
