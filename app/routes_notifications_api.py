"""
Routes API pour le système de notifications complet
Support MySQL et SQLite
"""

from flask import Blueprint, request, jsonify, render_template
from app.notifications_manager_sqlalchemy import NotificationsManagerSQLAlchemy
from app.logger import logger
from datetime import datetime

# Créer le blueprint
notifications_api = Blueprint('notifications_api', __name__, url_prefix='/api/notifications')

# Initialiser le gestionnaire
notif_manager = NotificationsManagerSQLAlchemy()

# ============== CONFIGURATION EMAIL ==============

@notifications_api.route('/config', methods=['GET'])
def get_config():
    """Récupérer la configuration actuelle"""
    return jsonify(notif_manager.get_all_config())

@notifications_api.route('/config', methods=['POST'])
def save_config():
    """Sauvegarder la configuration email"""
    data = request.get_json()
    
    sender_email = data.get('sender_email', '').strip()
    sender_password = data.get('sender_password', '')
    
    if not sender_email:
        return jsonify({'success': False, 'error': 'Email expéditeur requis'}), 400
    
    # Ne pas écraser le mot de passe SMTP avec une valeur vide.
    # Si l'utilisateur laisse le champ vide, on réutilise le mot de passe
    # déjà enregistré pour ce même expéditeur si disponible.
    if sender_password == '':
        existing_for_sender = None
        try:
            from app.database_unified import NotificationConfig
            existing_for_sender = NotificationConfig.query.filter_by(
                sender_email=sender_email
            ).first()
        except Exception:
            existing_for_sender = None

        if existing_for_sender and existing_for_sender.sender_password:
            sender_password = existing_for_sender.sender_password
        else:
            return jsonify({
                'success': False,
                'error': 'Mot de passe SMTP requis pour ce nouvel expéditeur'
            }), 400

    result = notif_manager.save_email_config(
        sender_email=sender_email,
        sender_password=sender_password,
        smtp_server=data.get('smtp_server', 'smtp.gmail.com'),
        smtp_port=data.get('smtp_port', 587),
        use_tls=data.get('use_tls', True)
    )
    
    return jsonify(result)

@notifications_api.route('/test-connection', methods=['POST'])
def test_connection():
    """Tester la connexion SMTP"""
    result = notif_manager.test_connection()
    return jsonify(result)

# ============== GESTION DES DESTINATAIRES ==============

@notifications_api.route('/recipients', methods=['GET'])
def get_recipients():
    """Récupérer tous les destinataires"""
    result = notif_manager.get_recipients()
    return jsonify({
        'success': True,
        'recipients': result,
        'value': result
    })

@notifications_api.route('/recipients', methods=['POST'])
def add_recipient():
    """Ajouter un destinataire"""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'success': False, 'error': 'Email requis'}), 400
    
    if '@' not in email:
        return jsonify({'success': False, 'error': 'Format email invalide'}), 400
    
    result = notif_manager.add_recipient(email)
    return jsonify(result)

@notifications_api.route('/recipients', methods=['DELETE'])
def remove_recipient():
    """Supprimer un destinataire"""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'success': False, 'error': 'Email requis'}), 400
    
    result = notif_manager.remove_recipient(email)
    return jsonify(result)

# ============== ENVOI MANUEL DE NOTIFICATIONS ==============

@notifications_api.route('/send-manual', methods=['POST'])
def send_manual_notification():
    """Envoyer une notification manuelle"""
    data = request.get_json()
    
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()
    recipient = data.get('recipient', '').strip()
    
    if not subject or not message or not recipient:
        return jsonify({'success': False, 'error': 'Tous les champs sont requis'}), 400
    
    try:
        # Créer le HTML pour l'email
        html_body = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #8B1538 0%, #6d0e2a 100%); color: white; padding: 20px; border-radius: 5px 5px 0 0; text-align: center; }}
                    .content {{ padding: 20px; color: #333; line-height: 1.6; }}
                    .footer {{ border-top: 1px solid #ddd; padding-top: 20px; margin-top: 20px; color: #999; font-size: 0.9em; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>{subject}</h2>
                    </div>
                    <div class="content">
                        <p>{message.replace(chr(10), '<br>')}</p>
                    </div>
                    <div class="footer">
                        <p>Système EPI Detection - Notification automatique</p>
                        <p>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Envoyer l'email
        result = notif_manager.send_email(
            to_email=recipient,
            subject=f"[EPI Detection] {subject}",
            body_html=html_body,
            body_text=message
        )
        
        # Enregistrer dans l'historique
        status = 'success' if result.get('success') else 'error'
        notif_manager.log_notification(
            notification_type='manual',
            recipient=recipient,
            subject=subject,
            status=status,
            message_preview=message
        )
        
        if result.get('success'):
            return jsonify({'success': True, 'message': 'Notification envoyée avec succès'})
        else:
            return jsonify({'success': False, 'error': result.get('message', 'Erreur lors de l\'envoi')}), 500
    
    except Exception as e:
        logger.error(f"❌ Erreur envoi notification: {e}")
        notif_manager.log_notification(
            notification_type='manual',
            recipient=recipient,
            subject=subject,
            status='error',
            error_message=str(e)
        )
        return jsonify({'success': False, 'error': str(e)}), 500

# ============== CONFIGURATION DES RAPPORTS ==============

@notifications_api.route('/reports-config', methods=['POST'])
def save_reports_config():
    """Sauvegarder la configuration des rapports"""
    data = request.get_json()
    
    # Sauvegarder les configurations
    try:
        if data.get('daily_enabled') is not None:
            notif_manager.save_report_schedule(
                report_type='daily',
                is_enabled=data.get('daily_enabled'),
                send_hour=data.get('daily_hour', 8),
                frequency='daily'
            )
        
        if data.get('weekly_enabled') is not None:
            notif_manager.save_report_schedule(
                report_type='weekly',
                is_enabled=data.get('weekly_enabled'),
                send_hour=data.get('weekly_hour', 9),
                send_day=data.get('weekly_day', 0),
                frequency='weekly'
            )
        
        if data.get('monthly_enabled') is not None:
            notif_manager.save_report_schedule(
                report_type='monthly',
                is_enabled=data.get('monthly_enabled'),
                send_hour=data.get('monthly_hour', 9),
                send_day=data.get('monthly_day', 1),
                frequency='monthly'
            )
        
        return jsonify({'success': True, 'message': 'Configuration des rapports sauvegardée'})
    
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde config rapports: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_api.route('/reports-config', methods=['GET'])
def get_reports_config():
    """Récupérer la configuration des rapports"""
    result = notif_manager.get_report_schedules()
    return jsonify(result)

# ============== ENVOI DE RAPPORTS ==============

@notifications_api.route('/send-report', methods=['POST'])
def send_report():
    """Envoyer un rapport immédiatement"""
    data = request.get_json()
    report_type = data.get('type', '').lower()
    
    if report_type not in ['daily', 'weekly', 'monthly']:
        return jsonify({'success': False, 'error': 'Type de rapport invalide'}), 400
    
    try:
        # Récupérer les destinataires
        recipients = notif_manager.get_recipients()
        if not recipients:
            return jsonify({'success': False, 'error': 'Aucun destinataire configuré'}), 400
        
        # Créer le contenu du rapport (simplifié pour cet exemple)
        subject = f"Rapport {report_type.capitalize()} - EPI Detection"
        html_body = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 5px; }}
                    .header {{ background: linear-gradient(135deg, #8B1538 0%, #6d0e2a 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                    .section {{ margin-top: 20px; padding: 15px; background: #f8f9fa; border-left: 4px solid #8B1538; }}
                    .stat {{ font-size: 1.2em; font-weight: bold; color: #8B1538; }}
                    .footer {{ border-top: 1px solid #ddd; padding-top: 20px; margin-top: 20px; color: #999; font-size: 0.9em; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>{subject}</h2>
                    </div>
                    <div class="section">
                        <p><strong>Période:</strong> {report_type.capitalize()}</p>
                        <p><strong>Date génération:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                    </div>
                    <div class="section">
                        <p>Rapport automatique généré par le système EPI Detection</p>
                    </div>
                    <div class="footer">
                        <p>Système EPI Detection</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Envoyer à tous les destinataires
        sent_count = 0
        for r in recipients:
            to_email = r.get('email') if isinstance(r, dict) else r
            result = notif_manager.send_email(
                to_email=to_email,
                subject=subject,
                body_html=html_body
            )

            if result.get('success'):
                sent_count += 1

            notif_manager.log_notification(
                notification_type='report',
                recipient=to_email,
                subject=subject,
                status='success' if result.get('success') else 'error',
                report_type=report_type,
                message_preview=subject
            )
        
        return jsonify({
            'success': True,
            'message': f'Rapport {report_type} envoyé à {sent_count}/{len(recipients)} destinataires'
        })
    
    except Exception as e:
        logger.error(f"❌ Erreur envoi rapport: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============== HISTORIQUE ==============

@notifications_api.route('/history', methods=['GET'])
def get_history():
    """Récupérer l'historique des notifications"""
    result = notif_manager.get_notification_history(limit=100)
    return jsonify({
        'success': True,
        'history': result,
        'value': result
    })

# ============== PAGE PRINCIPALE ==============

@notifications_api.route('/', methods=['GET'])
def notifications_page():
    """Afficher la page des notifications"""
    return render_template('notifications.html')
