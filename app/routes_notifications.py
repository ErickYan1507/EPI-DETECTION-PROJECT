# app/routes_notifications.py - Routes pour les notifications par email
from flask import Blueprint, request, jsonify, render_template
from app.database_unified import db, EmailNotification
from app.email_notifications import EmailNotifier
from app.logger import logger

notifications_bp = Blueprint('notifications', __name__)

email_notifier = EmailNotifier()

@notifications_bp.route('/api/notifications/email', methods=['GET'])
def get_email_notifications():
    """Récupérer toutes les notifications par email"""
    try:
        notifications = EmailNotification.query.all()
        return jsonify([n.to_dict() for n in notifications])
    except Exception as e:
        logger.error(f"Erreur récupération notifications: {e}")
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/api/notifications/email', methods=['POST'])
def add_email_notification():
    """Ajouter une nouvelle notification par email"""
    try:
        data = request.json
        notification = email_notifier.add_email_notification(
            email=data['email_address'],
            notification_type=data['notification_type'],
            include_detections=data.get('include_detections', True),
            include_alerts=data.get('include_alerts', True),
            include_presence=data.get('include_presence', True),
            include_compliance=data.get('include_compliance', True)
        )
        return jsonify(notification.to_dict()), 201
    except Exception as e:
        logger.error(f"Erreur ajout notification: {e}")
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/api/notifications/email/<int:notification_id>', methods=['PUT'])
def update_email_notification(notification_id):
    """Mettre à jour une notification par email"""
    try:
        notification = EmailNotification.query.get_or_404(notification_id)
        data = request.json
        
        notification.email_address = data.get('email_address', notification.email_address)
        notification.notification_type = data.get('notification_type', notification.notification_type)
        notification.include_detections = data.get('include_detections', notification.include_detections)
        notification.include_alerts = data.get('include_alerts', notification.include_alerts)
        notification.include_presence = data.get('include_presence', notification.include_presence)
        notification.include_compliance = data.get('include_compliance', notification.include_compliance)
        notification.is_active = data.get('is_active', notification.is_active)
        
        db.session.commit()
        return jsonify(notification.to_dict())
    except Exception as e:
        logger.error(f"Erreur mise à jour notification: {e}")
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/api/notifications/email/<int:notification_id>', methods=['DELETE'])
def delete_email_notification(notification_id):
    """Supprimer une notification par email"""
    try:
        notification = EmailNotification.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
        return jsonify({'message': 'Notification supprimée'})
    except Exception as e:
        logger.error(f"Erreur suppression notification: {e}")
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/api/notifications/send-test', methods=['POST'])
def send_test_notification():
    """Envoyer une notification de test"""
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email requis'}), 400
        
        # Contenu de test
        subject = "Test - Système de Notification EPI Detection"
        html_content = """
        <html>
        <body>
            <h1>Test de Notification</h1>
            <p>Cette notification confirme que le système d'email fonctionne correctement.</p>
            <p>Système EPI Detection</p>
        </body>
        </html>
        """
        
        success = email_notifier.send_email(email, subject, html_content)
        
        if success:
            return jsonify({'message': 'Test envoyé avec succès'})
        else:
            return jsonify({'error': 'Échec envoi test'}), 500
            
    except Exception as e:
        logger.error(f"Erreur envoi test: {e}")
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/api/notifications/send-scheduled', methods=['POST'])
def send_scheduled_notifications():
    """Déclencher l'envoi des notifications programmées"""
    try:
        email_notifier.send_scheduled_notifications()
        return jsonify({'message': 'Notifications programmées envoyées'})
    except Exception as e:
        logger.error(f"Erreur envoi notifications programmées: {e}")
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications')
def notifications_page():
    """Page de gestion des notifications"""
    return render_template('notifications.html')