# app/routes_alerts.py
"""
Routes API pour gestion des alertes
"""

from flask import Blueprint, request, jsonify
from flask import render_template
from app.alert_manager import alert_manager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

alert_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')


@alert_bp.route('/config', methods=['GET'])
def get_alert_config():
    """
    GET /api/alerts/config
    Récupère la configuration des alertes
    """
    return jsonify({
        'enabled': alert_manager.enabled,
        'configured': alert_manager.is_configured(),
        'recipients': alert_manager.recipients,
        'sender_email': alert_manager.sender_email.replace('@', '[at]') if alert_manager.sender_email else None,
        'no_detection_threshold_seconds': alert_manager.no_detection_threshold_seconds,
        'min_detections_per_minute': alert_manager.min_detections_per_minute,
        'alert_cooldown_seconds': alert_manager.alert_cooldown_seconds
    }), 200


@alert_bp.route('/test', methods=['POST'])
def test_alerts():
    """
    POST /api/alerts/test
    Envoyer un email de test
    
    Body:
    {
        "email": "your.email@gmail.com"  (optionnel)
    }
    """
    if not alert_manager.is_configured():
        return jsonify({
            'success': False,
            'message': 'Alertes non configurées',
            'config': alert_manager.test_configuration()
        }), 400
    
    success = alert_manager.send(
        subject='🧪 TEST - Alerte Email EPI Detection',
        body=f"""
Ceci est un email de test du système d'alertes.

Heure du test: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Destinataire: {', '.join(alert_manager.recipients)}

Si vous recevez ce message, le système d'alertes fonctionne correctement!

Système: EPI Detection
        """,
        html_body="""
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2 style="color: #4CAF50;">🧪 TEST - Alerte Email</h2>
    <div style="background-color: #f1f8e9; padding: 15px; border-left: 4px solid #4CAF50;">
      <p>Ceci est un email de <strong>test</strong> du système d'alertes.</p>
      <p><strong>Heure:</strong> """ + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + """</p>
      <p style="color: #4CAF50;"><strong>✅ Le système fonctionne correctement!</strong></p>
    </div>
    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <small style="color: #999;">EPI Detection - Test système</small>
  </body>
</html>
        """
    )
    
    return jsonify({
        'success': success,
        'message': 'Email de test envoyé' if success else 'Erreur lors de l\'envoi'
    }), 200 if success else 500


@alert_bp.route('/missing-epi', methods=['POST'])
def alert_missing_epi():
    """
    POST /api/alerts/missing-epi
    Déclencher alerte pour EPI manquant
    
    Body:
    {
        "epi_type": "helmet",
        "duration_seconds": 300
    }
    """
    data = request.get_json()
    
    epi_type = data.get('epi_type', 'unknown')
    duration = data.get('duration_seconds', 0)
    
    alert_manager.alert_missing_epi(epi_type, duration)
    
    return jsonify({
        'success': True,
        'message': f'Alerte envoyée pour {epi_type} absent pendant {duration}s'
    }), 200


@alert_bp.route('/low-detection', methods=['POST'])
def alert_low_detection():
    """
    POST /api/alerts/low-detection
    Alerte taux de détection faible
    
    Body:
    {
        "detection_count": 5,
        "time_window_minutes": 10
    }
    """
    data = request.get_json()
    
    detection_count = data.get('detection_count', 0)
    time_window = data.get('time_window_minutes', 10)
    
    alert_manager.alert_low_detection_rate(detection_count, time_window)
    
    return jsonify({
        'success': True,
        'message': f'Alerte taux de détection faible: {detection_count} détections en {time_window} min'
    }), 200


@alert_bp.route('/error', methods=['POST'])
def alert_error():
    """
    POST /api/alerts/error
    Alerte erreur système
    
    Body:
    {
        "error_message": "Webcam not found",
        "error_type": "WebcamError"
    }
    """
    data = request.get_json()
    
    error_msg = data.get('error_message', 'Unknown error')
    error_type = data.get('error_type', 'SystemError')
    
    alert_manager.alert_system_error(error_msg, error_type)
    
    return jsonify({
        'success': True,
        'message': f'Alerte erreur envoyée: {error_type}'
    }), 200


@alert_bp.route('/status', methods=['GET'])
def get_alert_status():
    """
    GET /api/alerts/status
    État du système d'alertes
    """
    status = alert_manager.test_configuration()
    
    return jsonify({
        'status': 'operational' if status['configured'] else 'not_configured',
        'configuration': status,
        'timestamp': datetime.now().isoformat()
    }), 200


@alert_bp.route('/dashboard', methods=['GET'])
def alerts_dashboard():
    """
    GET /alerts/dashboard
    Affiche le dashboard de gestion des alertes
    """
    return render_template('alert_dashboard.html')
