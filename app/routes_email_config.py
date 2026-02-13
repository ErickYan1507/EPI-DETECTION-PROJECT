"""
Routes pour la configuration email via l'interface web
Endpoints RESTful pour gérer les paramètres de notification
"""

from flask import Blueprint, request, jsonify
from config import config
from app.email_notifications import EmailNotifier
from app.logger import logger
import json
import os
from pathlib import Path

email_bp = Blueprint('email', __name__, url_prefix='/api/email')

# Chemin du fichier de configuration email
EMAIL_CONFIG_FILE = Path(__file__).parent.parent / '.env.email'
RECIPIENTS_FILE = Path(__file__).parent.parent / '.email_recipients'

# ====== CONFIGURATION SMTP ======
@email_bp.route('/config', methods=['GET'])
def get_email_config():
    """Récupère la configuration email actuelle"""
    try:
        config_data = {
            'SENDER_EMAIL': getattr(config, 'SENDER_EMAIL', ''),
            'SENDER_PASSWORD': getattr(config, 'SENDER_PASSWORD', ''),
            'SMTP_SERVER': getattr(config, 'SMTP_SERVER', 'smtp.gmail.com'),
            'SMTP_PORT': getattr(config, 'SMTP_PORT', 587),
            'DAILY_REPORT_HOUR': getattr(config, 'DAILY_REPORT_HOUR', 8),
            'WEEKLY_REPORT_DAY': getattr(config, 'WEEKLY_REPORT_DAY', 1),
            'WEEKLY_REPORT_HOUR': getattr(config, 'WEEKLY_REPORT_HOUR', 9),
            'MONTHLY_REPORT_DAY': getattr(config, 'MONTHLY_REPORT_DAY', 1),
            'MONTHLY_REPORT_HOUR': getattr(config, 'MONTHLY_REPORT_HOUR', 9),
            'SEND_ALERTS_ENABLED': getattr(config, 'SEND_ALERTS_ENABLED', True),
            'ALERT_THRESHOLD': getattr(config, 'ALERT_THRESHOLD', 80),
        }
        return jsonify({'success': True, 'config': config_data})
    except Exception as e:
        logger.error(f"Erreur lecture config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@email_bp.route('/config', methods=['POST'])
def save_email_config():
    """Sauvegarde la configuration email dans .env.email"""
    try:
        data = request.json
        
        # Lire le fichier .env.email existant
        env_file = EMAIL_CONFIG_FILE
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # Mettre à jour les valeurs
        keys_to_update = {
            'SENDER_EMAIL': data.get('SENDER_EMAIL'),
            'SENDER_PASSWORD': data.get('SENDER_PASSWORD'),
            'SMTP_SERVER': data.get('SMTP_SERVER', 'smtp.gmail.com'),
            'SMTP_PORT': data.get('SMTP_PORT', 587),
        }
        
        for key, value in keys_to_update.items():
            if value:
                # Remplacer ou ajouter la ligne
                if f'{key}=' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith(f'{key}='):
                            lines[i] = f'{key}={value}'
                    content = '\n'.join(lines)
                else:
                    content += f'\n{key}={value}\n'
        
        # Sauvegarder
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("Configuration email sauvegardée")
        return jsonify({'success': True, 'message': 'Configuration sauvegardée'})
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ====== TEST DE CONNEXION ======
@email_bp.route('/test-connection', methods=['POST'])
def test_smtp_connection():
    """Teste la connexion SMTP"""
    try:
        import smtplib
        
        server = getattr(config, 'SMTP_SERVER', 'smtp.gmail.com')
        port = int(getattr(config, 'SMTP_PORT', 587))
        email = getattr(config, 'SENDER_EMAIL', '')
        password = getattr(config, 'SENDER_PASSWORD', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email et/ou mot de passe non configurés'
            })
        
        # Test de connexion
        smtp = smtplib.SMTP(server, port, timeout=5)
        smtp.starttls()
        smtp.login(email, password)
        smtp.quit()
        
        logger.info(f"Test SMTP réussi")
        return jsonify({
            'success': True,
            'server': server,
            'port': port,
            'message': 'Connexion réussie'
        })
        
    except smtplib.SMTPAuthenticationError:
        logger.error("Erreur d'authentification SMTP")
        return jsonify({
            'success': False,
            'error': 'Authentification échouée. Vérifiez email et mot de passe.'
        })
    except Exception as e:
        logger.error(f"Erreur connexion SMTP: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ====== EMAIL DE TEST ======
@email_bp.route('/send-test', methods=['POST'])
def send_test_email():
    """Envoie un email de test"""
    try:
        data = request.json
        recipient = data.get('recipient')
        
        if not recipient:
            return jsonify({'success': False, 'error': 'Destinataire requis'})
        
        notifier = EmailNotifier()
        
        subject = "🎉 Test Email - EPI Detection System"
        html = """
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <h1 style="color: #8B1538;">🎉 Configuration Email Réussie</h1>
            <p>Cet email confirme que votre configuration SMTP fonctionne correctement!</p>
            <hr>
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
                <p><strong>Prochaines étapes:</strong></p>
                <ul>
                    <li>✅ Configuration SMTP testée</li>
                    <li>📧 Rapports quotidiens configurés</li>
                    <li>🔔 Alertes automatiques activées</li>
                    <li>📊 Rapports attendus selon l'horaire défini</li>
                </ul>
            </div>
            <p style="color: green; margin-top: 20px;"><strong>Vous pouvez maintenant profiter des rapports automatiques!</strong></p>
        </body>
        </html>
        """
        
        success = notifier.send_email(recipient, subject, html)
        
        if success:
            logger.info(f"Email test envoyé à {recipient}")
            return jsonify({'success': True, 'message': f'Email envoyé à {recipient}'})
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de l\'envoi'})
            
    except Exception as e:
        logger.error(f"Erreur envoi email test: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ====== DESTINATAIRES ======
@email_bp.route('/recipients', methods=['GET'])
def get_recipients():
    """Récupère la liste des destinataires"""
    try:
        recipients = []
        if RECIPIENTS_FILE.exists():
            with open(RECIPIENTS_FILE, 'r') as f:
                recipients = [line.strip() for line in f if line.strip()]
        
        # Fallback à RECIPIENT_EMAILS de config
        if not recipients:
            env_recipients = getattr(config, 'RECIPIENT_EMAILS', '')
            if env_recipients:
                recipients = [e.strip() for e in env_recipients.split(',')]
        
        return jsonify({'success': True, 'recipients': recipients})
    except Exception as e:
        logger.error(f"Erreur lecture destinataires: {e}")
        return jsonify({'success': False, 'recipients': []})

@email_bp.route('/recipients', methods=['POST'])
def add_recipient():
    """Ajoute un destinataire"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email requis'})
        
        recipients = []
        if RECIPIENTS_FILE.exists():
            with open(RECIPIENTS_FILE, 'r') as f:
                recipients = [line.strip() for line in f if line.strip()]
        
        if email in recipients:
            return jsonify({'success': False, 'error': 'Email déjà présent'})
        
        recipients.append(email)
        
        with open(RECIPIENTS_FILE, 'w') as f:
            f.write('\n'.join(recipients))
        
        logger.info(f"Destinataire ajouté: {email}")
        return jsonify({'success': True, 'message': f'Email {email} ajouté'})
        
    except Exception as e:
        logger.error(f"Erreur ajout destinataire: {e}")
        return jsonify({'success': False, 'error': str(e)})

@email_bp.route('/recipients', methods=['DELETE'])
def remove_recipient():
    """Supprime un destinataire"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email requis'})
        
        if not RECIPIENTS_FILE.exists():
            return jsonify({'success': False, 'error': 'Aucun fichier de destinataires'})
        
        with open(RECIPIENTS_FILE, 'r') as f:
            recipients = [line.strip() for line in f if line.strip()]
        
        recipients = [r for r in recipients if r != email]
        
        with open(RECIPIENTS_FILE, 'w') as f:
            f.write('\n'.join(recipients))
        
        logger.info(f"Destinataire supprimé: {email}")
        return jsonify({'success': True, 'message': f'Email {email} supprimé'})
        
    except Exception as e:
        logger.error(f"Erreur suppression destinataire: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ====== HORAIRES ======
@email_bp.route('/schedules', methods=['POST'])
def save_schedules():
    """Sauvegarde les horaires de rapports"""
    try:
        data = request.json
        
        env_file = EMAIL_CONFIG_FILE
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        keys = [
            'DAILY_REPORT_HOUR',
            'WEEKLY_REPORT_DAY',
            'WEEKLY_REPORT_HOUR',
            'MONTHLY_REPORT_DAY',
            'MONTHLY_REPORT_HOUR',
            'SEND_ALERTS_ENABLED',
            'ALERT_THRESHOLD',
        ]
        
        for key in keys:
            if key in data:
                value = data[key]
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                
                if f'{key}=' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith(f'{key}='):
                            lines[i] = f'{key}={value}'
                    content = '\n'.join(lines)
                else:
                    content += f'\n{key}={value}\n'
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("Horaires sauvegardés")
        return jsonify({'success': True, 'message': 'Horaires sauvegardés'})
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde horaires: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ====== ENVOI DE RAPPORTS ======
@email_bp.route('/send-report', methods=['POST'])
def send_report():
    """Envoie un rapport maintenant"""
    try:
        data = request.json
        report_type = data.get('type', 'daily')
        
        notifier = EmailNotifier()
        recipients = []
        
        # Récupérer les destinataires
        if RECIPIENTS_FILE.exists():
            with open(RECIPIENTS_FILE, 'r') as f:
                recipients = [line.strip() for line in f if line.strip()]
        
        if not recipients:
            return jsonify({'success': False, 'error': 'Aucun destinataire configuré'})
        
        # Générer et envoyer le rapport
        if report_type == 'daily':
            html = notifier.generate_daily_report()
            subject = f"📊 Rapport Quotidien - {__import__('datetime').date.today()}"
        elif report_type == 'weekly':
            html = notifier.generate_weekly_report()
            subject = f"📅 Rapport Hebdomadaire"
        elif report_type == 'monthly':
            html = notifier.generate_monthly_report()
            subject = f"📆 Rapport Mensuel"
        else:
            return jsonify({'success': False, 'error': 'Type de rapport inconnu'})
        
        # Envoyer à tous les destinataires
        for recipient in recipients:
            notifier.send_email(recipient, subject, html)
        
        logger.info(f"Rapport {report_type} envoyé à {len(recipients)} destinataire(s)")
        return jsonify({'success': True, 'message': f'Rapport envoyé à {len(recipients)} destinataire(s)'})
        
    except Exception as e:
        logger.error(f"Erreur envoi rapport: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ====== ÉTAT SYSTÈME ======
@email_bp.route('/status', methods=['GET'])
def get_email_status():
    """Récupère l'état du système email"""
    try:
        smtp_server = getattr(config, 'SMTP_SERVER', '')
        smtp_port = getattr(config, 'SMTP_PORT', '')
        sender_email = getattr(config, 'SENDER_EMAIL', '')
        sender_password = getattr(config, 'SENDER_PASSWORD', '')
        
        # Vérifier si SMTP est configuré
        smtp_configured = bool(sender_email and sender_password)
        
        # Vérifier la connexion
        smtp_connected = False
        if smtp_configured:
            try:
                import smtplib
                smtp = smtplib.SMTP(smtp_server, int(smtp_port), timeout=3)
                smtp.starttls()
                smtp.login(sender_email, sender_password)
                smtp.quit()
                smtp_connected = True
            except:
                smtp_connected = False
        
        # Compter les destinataires
        recipients_count = 0
        if RECIPIENTS_FILE.exists():
            with open(RECIPIENTS_FILE, 'r') as f:
                recipients_count = len([line.strip() for line in f if line.strip()])
        
        # Vérifier le scheduler
        from app.report_scheduler import get_report_scheduler
        scheduler = get_report_scheduler()
        scheduler_running = scheduler is not None and scheduler.scheduler.running if scheduler else False
        
        return jsonify({
            'success': True,
            'smtp_configured': smtp_configured,
            'smtp_connected': smtp_connected,
            'recipients_count': recipients_count,
            'scheduler_running': scheduler_running,
            'scheduled_jobs': 0  # À améliorer
        })
        
    except Exception as e:
        logger.error(f"Erreur état système: {e}")
        return jsonify({'success': False, 'error': str(e)})

@email_bp.route('/scheduler-status', methods=['GET'])
def get_scheduler_status():
    """Récupère la statut du scheduler"""
    try:
        from app.report_scheduler import get_report_scheduler
        scheduler = get_report_scheduler()
        
        jobs = []
        if scheduler and scheduler.scheduler:
            for job in scheduler.scheduler.get_jobs():
                jobs.append({
                    'name': job.name,
                    'next_run': str(job.next_run_time) if job.next_run_time else 'N/A'
                })
        
        return jsonify({'success': True, 'jobs': jobs})
        
    except Exception as e:
        logger.error(f"Erreur statut scheduler: {e}")
        return jsonify({'success': False, 'error': str(e)})

def register_email_routes(app):
    """Enregistre les routes email dans l'app"""
    app.register_blueprint(email_bp)
