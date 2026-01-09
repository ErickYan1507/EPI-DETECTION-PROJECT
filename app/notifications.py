import logging
from flask_socketio import SocketIO
from datetime import datetime
import json

class NotificationManager:
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.logger = logging.getLogger(__name__)
        
    def send_alert(self, message, severity='warning', data=None):
        """Envoyer une alerte"""
        alert_data = {
            'id': f"alert_{datetime.now().timestamp()}",
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'severity': severity,
            'data': data or {}
        }
        
        # Log dans le fichier
        self.log_to_file(alert_data)
        
        # Envoyer via WebSocket si disponible
        if self.socketio:
            self.socketio.emit('new_alert', alert_data)
        
        # Console (pour débogage)
        print(f"[ALERTE {severity.upper()}] {message}")
        
        return alert_data
    
    def send_compliance_update(self, compliance_rate):
        """Mettre à jour le taux de conformité"""
        update_data = {
            'type': 'compliance_update',
            'timestamp': datetime.now().isoformat(),
            'compliance_rate': compliance_rate,
            'status': 'safe' if compliance_rate >= 80 else 'warning' if compliance_rate >= 50 else 'danger'
        }
        
        if self.socketio:
            self.socketio.emit('compliance_update', update_data)
        
        return update_data
    
    def send_detection_result(self, detection_data):
        """Envoyer les résultats de détection"""
        if self.socketio:
            self.socketio.emit('detection_result', detection_data)
    
    def log_to_file(self, alert_data):
        """Sauvegarder l'alerte dans un fichier log"""
        log_entry = {
            'timestamp': alert_data['timestamp'],
            'level': alert_data['severity'].upper(),
            'message': alert_data['message']
        }
        
        try:
            with open('logs/alerts.log', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Erreur lors de l'écriture dans le log: {e}")