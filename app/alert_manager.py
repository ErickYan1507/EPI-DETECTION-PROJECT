# app/alert_manager.py
"""
Système d'alertes email pour non-conformité EPI
Utilise SMTP Gmail (gratuit)
"""

import os
import logging
from datetime import datetime
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread

logger = logging.getLogger(__name__)


class AlertManager:
    """Gestionnaire d'alertes email pour détections EPI"""
    
    def __init__(self):
        """Initialiser le gestionnaire d'alertes"""
        self.enabled = os.getenv('ALERT_EMAIL_ENABLED', 'False').lower() == 'true'
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('ALERT_EMAIL_FROM')
        self.sender_password = os.getenv('ALERT_EMAIL_PASSWORD')
        self.recipients = self._parse_recipients()
        
        # Seuils de non-conformité
        self.min_detections_per_minute = int(
            os.getenv('MIN_DETECTIONS_PER_MINUTE', 1)
        )
        self.no_detection_threshold_seconds = int(
            os.getenv('NO_DETECTION_THRESHOLD_SECONDS', 300)
        )
        self.alert_cooldown_seconds = int(
            os.getenv('ALERT_COOLDOWN_SECONDS', 600)
        )
        
        self.last_alert_time = {}
        self.logger = logging.getLogger(__name__)
        
        if self.enabled:
            self.logger.info(f"✅ Alertes email activées ({self.sender_email})")
        else:
            self.logger.info("⚠️ Alertes email désactivées")
    
    def _parse_recipients(self) -> List[str]:
        """Parser la liste des destinataires"""
        recipients_str = os.getenv('ALERT_EMAIL_RECIPIENTS', '')
        if not recipients_str:
            return []
        return [email.strip() for email in recipients_str.split(',')]
    
    def is_configured(self) -> bool:
        """Vérifier si le système est configuré correctement"""
        return (
            self.enabled and 
            self.sender_email and 
            self.sender_password and 
            self.recipients
        )
    
    def send_async(self, subject: str, body: str, html_body: str = None):
        """Envoyer email asynchrone (non-bloquant)"""
        thread = Thread(
            target=self.send,
            args=(subject, body, html_body),
            daemon=True
        )
        thread.start()
    
    def send(self, subject: str, body: str, html_body: str = None) -> bool:
        """Envoyer email"""
        if not self.is_configured():
            self.logger.warning(f"Alertes non configurées: {subject}")
            return False
        
        try:
            # Créer message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = subject
            
            # Ajouter texte
            msg.attach(MIMEText(body, 'plain'))
            
            # Ajouter HTML si fourni
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Envoyer via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            self.logger.info(f"✅ Alerte envoyée: {subject}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            self.logger.error("❌ Erreur authentification SMTP (mot de passe incorrect)")
            return False
        except smtplib.SMTPException as e:
            self.logger.error(f"❌ Erreur SMTP: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Erreur envoi email: {e}")
            return False
    
    def alert_missing_epi(self, detection_type: str, duration_seconds: int):
        """Alerter si un EPI n'a pas été détecté"""
        if not self.is_configured():
            return
        
        alert_key = f"missing_{detection_type}"
        if not self._check_cooldown(alert_key):
            return
        
        subject = f"🚨 ALERTE EPI - {detection_type.upper()} NON DÉTECTÉ"
        
        body = f"""
ALERTE DE NON-CONFORMITÉ

Type EPI manquant: {detection_type.upper()}
Durée sans détection: {duration_seconds} secondes
Heure d'alerte: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

ACTION REQUISE:
- Vérifier le port des équipements de sécurité
- Relancer la caméra de détection si nécessaire
- Contacter le responsable sécurité

Système: EPI Detection
        """
        
        html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2 style="color: #d32f2f;">🚨 ALERTE EPI - NON-CONFORMITÉ</h2>
    <div style="background-color: #fff3e0; padding: 15px; border-left: 4px solid #ff9800;">
      <p><strong>Type EPI manquant:</strong> {detection_type.upper()}</p>
      <p><strong>Durée sans détection:</strong> {duration_seconds} secondes</p>
      <p><strong>Heure:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    </div>
    
    <h3>Actions à prendre:</h3>
    <ul>
      <li>Vérifier le port des équipements de sécurité</li>
      <li>Relancer la caméra de détection si nécessaire</li>
      <li>Contacter le responsable sécurité</li>
    </ul>
    
    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <small style="color: #999;">
      Système EPI Detection - Alerte automatique
    </small>
  </body>
</html>
        """
        
        self.send_async(subject, body, html_body)
    
    def alert_low_detection_rate(self, detection_count: int, time_window_minutes: int):
        """Alerter si le taux de détection est trop bas"""
        if not self.is_configured():
            return
        
        alert_key = "low_detection_rate"
        if not self._check_cooldown(alert_key):
            return
        
        expected = self.min_detections_per_minute * time_window_minutes
        
        subject = f"⚠️ ALERTE - Taux de détection faible ({detection_count}/{expected})"
        
        body = f"""
ALERTE TAUX DE DÉTECTION FAIBLE

Détections sur les {time_window_minutes} dernières minutes: {detection_count}
Minimum attendu: {expected}
Heure: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Possible causes:
- Mauvaise luminosité
- Caméra obstruée
- Modèle désactivé
- Seuil de confiance trop élevé

Système: EPI Detection
        """
        
        html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2 style="color: #ff9800;">⚠️ TAUX DE DÉTECTION FAIBLE</h2>
    <div style="background-color: #fff3e0; padding: 15px; border-left: 4px solid #ff9800;">
      <p><strong>Détections récentes:</strong> {detection_count}</p>
      <p><strong>Minimum attendu:</strong> {expected}</p>
      <p><strong>Fenêtre:</strong> {time_window_minutes} minutes</p>
      <p><strong>Heure:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    </div>
    
    <h3>Causes possibles:</h3>
    <ul>
      <li>Mauvaise luminosité de la zone</li>
      <li>Caméra obstruée ou sale</li>
      <li>Modèle de détection désactivé</li>
      <li>Seuil de confiance trop élevé</li>
    </ul>
    
    <p><strong>Recommandation:</strong> Vérifier les paramètres du système</p>
    
    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <small style="color: #999;">
      Système EPI Detection - Alerte automatique
    </small>
  </body>
</html>
        """
        
        self.send_async(subject, body, html_body)
    
    def alert_system_error(self, error_message: str, error_type: str = "Unknown"):
        """Alerter en cas d'erreur système"""
        if not self.is_configured():
            return
        
        alert_key = f"error_{error_type}"
        if not self._check_cooldown(alert_key):
            return
        
        subject = f"🔴 ERREUR SYSTÈME - {error_type}"
        
        body = f"""
ERREUR SYSTÈME DÉTECTÉE

Type d'erreur: {error_type}
Message: {error_message}
Heure: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Veuillez vérifier les logs du système pour plus de détails.

Système: EPI Detection
        """
        
        html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2 style="color: #d32f2f;">🔴 ERREUR SYSTÈME</h2>
    <div style="background-color: #ffebee; padding: 15px; border-left: 4px solid #d32f2f;">
      <p><strong>Type:</strong> {error_type}</p>
      <p><strong>Message:</strong> {error_message}</p>
      <p><strong>Heure:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    </div>
    
    <p>Veuillez vérifier les logs du système pour plus de détails.</p>
    
    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <small style="color: #999;">
      Système EPI Detection - Alerte automatique
    </small>
  </body>
</html>
        """
        
        self.send_async(subject, body, html_body)
    
    def _check_cooldown(self, alert_key: str) -> bool:
        """Vérifier le cooldown avant d'envoyer alerte"""
        now = datetime.now().timestamp()
        last_time = self.last_alert_time.get(alert_key, 0)
        
        if now - last_time < self.alert_cooldown_seconds:
            return False
        
        self.last_alert_time[alert_key] = now
        return True
    
    def test_configuration(self) -> Dict[str, any]:
        """Tester la configuration des alertes"""
        result = {
            'enabled': self.enabled,
            'configured': self.is_configured(),
            'sender_email': self.sender_email,
            'recipients': self.recipients,
            'recipients_count': len(self.recipients)
        }
        
        if self.is_configured():
            try:
                # Essayer connexion SMTP
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=5) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                result['smtp_connection'] = 'OK'
            except Exception as e:
                result['smtp_connection'] = f'ERROR: {str(e)}'
        
        return result


# Instance globale
alert_manager = AlertManager()
