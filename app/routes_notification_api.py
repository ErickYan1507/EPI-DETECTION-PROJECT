"""
Routes API pour le système des notifications manuelle et automatique
Gère la configuration, l'envoi manuel, les rapports programmés, et l'historique
"""

from flask import Blueprint, request, jsonify, render_template
from app.notification_service import notification_service
from app.logger import logger

# Créer le blueprint
notification_api_bp = Blueprint('notification_api', __name__, url_prefix='/api/notifications')


# ====== CONFIGURATION ======
@notification_api_bp.route('/config', methods=['GET'])
def get_notification_config():
    """Récupérer la configuration actuelle des notifications"""
    try:
        config = notification_service.get_config()
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        logger.error(f"Erreur récupération config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@notification_api_bp.route('/config', methods=['POST'])
def save_notification_config():
    """Sauvegarder la configuration des notifications"""
    try:
        data = request.json
        
        if notification_service.save_config(data):
            logger.info(f"Configuration notifications sauvegardée")
            return jsonify({'success': True, 'message': 'Configuration sauvegardée'})
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de la sauvegarde'}), 500
            
    except Exception as e:
        logger.error(f"Erreur sauvegarde config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ====== GESTION DES DESTINATAIRES ======
@notification_api_bp.route('/recipients', methods=['GET'])
def get_recipients():
    """Récupérer la liste des destinataires"""
    try:
        recipients = notification_service.get_recipients()
        return jsonify({
            'success': True,
            'recipients': recipients
        })
    except Exception as e:
        logger.error(f"Erreur récupération destinataires: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@notification_api_bp.route('/recipients', methods=['POST'])
def add_recipient_endpoint():
    """Ajouter un destinataire"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email requis'}), 400
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'error': 'Format d\'email invalide'}), 400
        
        if notification_service.add_recipient(email):
            logger.info(f"Destinataire ajouté: {email}")
            return jsonify({
                'success': True,
                'message': f'Destinataire {email} ajouté'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Destinataire déjà existant ou erreur'
            }), 400
            
    except Exception as e:
        logger.error(f"Erreur ajout destinataire: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@notification_api_bp.route('/recipients', methods=['DELETE'])
def remove_recipient_endpoint():
    """Supprimer un destinataire"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email requis'}), 400
        
        if notification_service.remove_recipient(email):
            logger.info(f"Destinataire supprimé: {email}")
            return jsonify({
                'success': True,
                'message': f'Destinataire {email} supprimé'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Destinataire non trouvé'
            }), 404
            
    except Exception as e:
        logger.error(f"Erreur suppression destinataire: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ====== TEST DE CONNEXION ======
@notification_api_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """Tester la connexion email"""
    try:
        result = notification_service.test_connection()
        if result['success']:
            return jsonify({'success': True, 'message': 'Connexion réussie'})
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Erreur de connexion')
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur test connexion: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ====== ENVOI MANUEL DE NOTIFICATION ======
@notification_api_bp.route('/send-manual', methods=['POST'])
def send_manual():
    """Envoyer une notification manuelle"""
    try:
        data = request.json
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        recipient = data.get('recipient', '').strip()
        
        # Validations
        if not subject:
            return jsonify({'success': False, 'error': 'Objet requis'}), 400
        if not message:
            return jsonify({'success': False, 'error': 'Message requis'}), 400
        if not recipient:
            return jsonify({'success': False, 'error': 'Destinataire requis'}), 400
        
        # Envoyer la notification
        if notification_service.send_manual_notification(subject, message, recipient):
            logger.info(f"Notification manuelle envoyée à {recipient}")
            return jsonify({
                'success': True,
                'message': f'Notification envoyée à {recipient}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'envoi'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur envoi manuel: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ====== CONFIGURATION DES RAPPORTS ======
@notification_api_bp.route('/reports-config', methods=['POST'])
def save_reports_config():
    """Sauvegarder la configuration des rapports programmés"""
    try:
        data = request.json
        
        config_update = {
            'daily_enabled': data.get('daily_enabled', True),
            'daily_hour': int(data.get('daily_hour', 8)),
            'weekly_enabled': data.get('weekly_enabled', False),
            'weekly_day': int(data.get('weekly_day', 0)),
            'weekly_hour': int(data.get('weekly_hour', 9)),
            'monthly_enabled': data.get('monthly_enabled', False),
            'monthly_day': int(data.get('monthly_day', 1)),
            'monthly_hour': int(data.get('monthly_hour', 9)),
        }
        
        if notification_service.save_config(config_update):
            logger.info(f"Configuration des rapports sauvegardée")
            return jsonify({
                'success': True,
                'message': 'Configuration des rapports sauvegardée'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erreur lors de la sauvegarde'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur sauvegarde config rapports: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ====== ENVOI DE RAPPORTS ======
@notification_api_bp.route('/send-report', methods=['POST'])
def send_report():
    """Envoyer un rapport (daily/weekly/monthly)"""
    try:
        data = request.json
        report_type = data.get('type', '').lower()
        
        if report_type not in ['daily', 'weekly', 'monthly']:
            return jsonify({
                'success': False,
                'error': 'Type de rapport invalide'
            }), 400
        
        recipients = notification_service.get_recipients()
        if not recipients:
            return jsonify({
                'success': False,
                'error': 'Aucun destinataire configuré'
            }), 400
        
        # Générer le rapport
        if report_type == 'daily':
            html_content = notification_service.generate_daily_report()
            subject = f"Rapport Quotidien - EPI Detection"
        elif report_type == 'weekly':
            html_content = notification_service.generate_weekly_report()
            subject = f"Rapport Hebdomadaire - EPI Detection"
        else:  # monthly
            html_content = notification_service.generate_monthly_report()
            subject = f"Rapport Mensuel - EPI Detection"
        
        # Envoyer à tous les destinataires
        success_count = 0
        for recipient in recipients:
            if notification_service.send_email(recipient, subject, html_content, report_type):
                success_count += 1
        
        if success_count > 0:
            logger.info(f"Rapport {report_type} envoyé à {success_count}/{len(recipients)} destinataires")
            return jsonify({
                'success': True,
                'message': f'Rapport envoyé à {success_count} destinataire(s)',
                'sent_count': success_count,
                'total_count': len(recipients)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Impossible d\'envoyer le rapport'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur envoi rapport: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ====== HISTORIQUE DES NOTIFICATIONS ======
@notification_api_bp.route('/history', methods=['GET'])
def get_history():
    """Récupérer l'historique des notifications"""
    try:
        limit = request.args.get('limit', 100, type=int)
        history = notification_service.get_history(limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
    except Exception as e:
        logger.error(f"Erreur récupération historique: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ====== DEBUG ======
@notification_api_bp.route('/debug', methods=['GET'])
def debug_page():
    """Page de debug pour les destinataires"""
    return render_template('notifications_debug.html')


@notification_api_bp.route('/simple', methods=['GET'])
def simple_page():
    """Page simple pour tester les destinataires"""
    return render_template('notifications_simple.html')
