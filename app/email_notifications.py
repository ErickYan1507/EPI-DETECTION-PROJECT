"""
Module de notifications par email pour EPI Detection
Gère l'envoi automatique de rapports périodiques
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, date
import json
from app.database_unified import db, Detection, Alert, DailyPresence, EmailNotification
from app.logger import logger
from config import config

class EmailNotifier:
    """Gestionnaire des notifications par email"""
    
    def __init__(self):
        self.smtp_server = getattr(config, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(config, 'SMTP_PORT', 587)
        self.sender_email = getattr(config, 'SENDER_EMAIL', '')
        self.sender_password = getattr(config, 'SENDER_PASSWORD', '')
        
    def send_email(self, recipient, subject, html_content):
        """Envoyer un email"""
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient
            
            # Ajouter le contenu HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Connexion SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient, msg.as_string())
            server.quit()
            
            logger.info(f"Email envoyé à {recipient}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email à {recipient}: {e}")
            return False
    
    def generate_daily_report(self):
        """Générer le rapport quotidien"""
        yesterday = date.today() - timedelta(days=1)
        
        # Statistiques des détections
        detections = Detection.query.filter(
            db.func.date(Detection.timestamp) == yesterday
        ).all()
        
        # Statistiques des alertes
        alerts = Alert.query.filter(
            db.func.date(Alert.timestamp) == yesterday
        ).all()
        
        # Statistiques des présences
        presences = DailyPresence.query.filter_by(date=yesterday).all()
        
        # Calculs
        total_detections = len(detections)
        avg_compliance = sum(d.compliance_rate for d in detections if d.compliance_rate) / len(detections) if detections else 0
        total_alerts = len(alerts)
        total_presences = len(presences)
        
        # Contenu HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #8B1538; color: white; padding: 20px; border-radius: 5px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: #f5f5f5; padding: 15px; border-radius: 5px; flex: 1; text-align: center; }}
                .stat-value {{ font-size: 2em; font-weight: bold; color: #8B1538; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Rapport Quotidien - EPI Detection</h1>
                <p>Date: {yesterday.strftime('%d/%m/%Y')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{total_detections}</div>
                    <div>Détections</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{avg_compliance:.1f}%</div>
                    <div>Conformité Moyenne</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_alerts}</div>
                    <div>Alertes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_presences}</div>
                    <div>Présences</div>
                </div>
            </div>
            
            <h2>Détails des Détections</h2>
            <table>
                <tr>
                    <th>Heure</th>
                    <th>Personnes</th>
                    <th>Casques</th>
                    <th>Gilets</th>
                    <th>Lunettes</th>
                    <th>Conformité</th>
                </tr>
                {"".join(f"<tr><td>{d.timestamp.strftime('%H:%M')}</td><td>{d.total_persons}</td><td>{d.with_helmet}</td><td>{d.with_vest}</td><td>{d.with_glasses}</td><td>{d.compliance_rate:.1f}%</td></tr>" for d in detections[:10])}
            </table>
            
            <h2>Alertes du Jour</h2>
            <table>
                <tr>
                    <th>Heure</th>
                    <th>Type</th>
                    <th>Message</th>
                    <th>Sévérité</th>
                </tr>
                {"".join(f"<tr><td>{a.timestamp.strftime('%H:%M')}</td><td>{a.type}</td><td>{a.message}</td><td>{a.severity}</td></tr>" for a in alerts)}
            </table>
        </body>
        </html>
        """
        
        return html
    
    def generate_weekly_report(self):
        """Générer le rapport hebdomadaire"""
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=6)
        
        # Statistiques sur 7 jours
        detections = Detection.query.filter(
            db.func.date(Detection.timestamp).between(start_date, end_date)
        ).all()
        
        alerts = Alert.query.filter(
            db.func.date(Alert.timestamp).between(start_date, end_date)
        ).all()
        
        presences = DailyPresence.query.filter(
            DailyPresence.date.between(start_date, end_date)
        ).all()
        
        # Grouper par jour
        daily_stats = {}
        for d in detections:
            day = d.timestamp.date()
            if day not in daily_stats:
                daily_stats[day] = {'detections': 0, 'compliance': [], 'alerts': 0}
            daily_stats[day]['detections'] += 1
            if d.compliance_rate:
                daily_stats[day]['compliance'].append(d.compliance_rate)
        
        for a in alerts:
            day = a.timestamp.date()
            if day not in daily_stats:
                daily_stats[day] = {'detections': 0, 'compliance': [], 'alerts': 0}
            daily_stats[day]['alerts'] += 1
        
        # Contenu HTML pour le rapport hebdomadaire
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #4169E1; color: white; padding: 20px; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Rapport Hebdomadaire - EPI Detection</h1>
                <p>Période: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}</p>
            </div>
            
            <h2>Statistiques Quotidiennes</h2>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Détections</th>
                    <th>Conformité Moyenne</th>
                    <th>Alertes</th>
                </tr>
                {"".join(f"<tr><td>{day.strftime('%d/%m')}</td><td>{stats['detections']}</td><td>{sum(stats['compliance'])/len(stats['compliance']):.1f}%</td><td>{stats['alerts']}</td></tr>" if stats['compliance'] else f"<tr><td>{day.strftime('%d/%m')}</td><td>{stats['detections']}</td><td>N/A</td><td>{stats['alerts']}</td></tr>" for day, stats in sorted(daily_stats.items()))}
            </table>
            
            <h2>Totaux de la Semaine</h2>
            <p>Total détections: {len(detections)}</p>
            <p>Total alertes: {len(alerts)}</p>
            <p>Total présences: {len(presences)}</p>
        </body>
        </html>
        """
        
        return html
    
    def send_scheduled_notifications(self):
        """Envoyer les notifications programmées"""
        notifications = EmailNotification.query.filter_by(is_active=True).all()
        
        for notification in notifications:
            try:
                # Vérifier si c'est le moment d'envoyer
                now = datetime.utcnow()
                should_send = False
                
                if notification.notification_type == 'daily':
                    # Envoyer si pas envoyé aujourd'hui
                    if not notification.last_sent or notification.last_sent.date() < date.today():
                        should_send = True
                        content = self.generate_daily_report()
                        subject = f"Rapport Quotidien EPI Detection - {date.today().strftime('%d/%m/%Y')}"
                        
                elif notification.notification_type == 'weekly':
                    # Envoyer le lundi si pas envoyé cette semaine
                    if now.weekday() == 0:  # Lundi
                        week_start = date.today() - timedelta(days=date.today().weekday())
                        if not notification.last_sent or notification.last_sent.date() < week_start:
                            should_send = True
                            content = self.generate_weekly_report()
                            subject = f"Rapport Hebdomadaire EPI Detection - Semaine {week_start.strftime('%W')}"
                            
                elif notification.notification_type == 'monthly':
                    # Envoyer le 1er du mois
                    if date.today().day == 1:
                        month_start = date.today().replace(day=1)
                        if not notification.last_sent or notification.last_sent.date() < month_start:
                            should_send = True
                            # Pour le rapport mensuel, utiliser la logique hebdomadaire étendue
                            content = self.generate_weekly_report()  # À améliorer pour mensuel
                            subject = f"Rapport Mensuel EPI Detection - {date.today().strftime('%B %Y')}"
                
                if should_send:
                    if self.send_email(notification.email_address, subject, content):
                        notification.last_sent = now
                        db.session.commit()
                        
            except Exception as e:
                logger.error(f"Erreur envoi notification {notification.id}: {e}")
    
    def add_email_notification(self, email, notification_type, **kwargs):
        """Ajouter une nouvelle notification par email"""
        notification = EmailNotification(
            email_address=email,
            notification_type=notification_type,
            include_detections=kwargs.get('include_detections', True),
            include_alerts=kwargs.get('include_alerts', True),
            include_presence=kwargs.get('include_presence', True),
            include_compliance=kwargs.get('include_compliance', True)
        )
        db.session.add(notification)
        db.session.commit()
        return notification