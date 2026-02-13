"""
Modèle de base de données unifié pour EPI Detection
Supporte SQLite et MySQL avec tous les domaines intégrés:
- Training Results (résultats d'entraînement YOLOv5)
- Detections (détections en temps réel)
- Alerts (alertes)
- IoT/TinkerCad (capteurs IoT et simulation)
- Workers (travailleurs)
- System Logs (logs système)
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

# ============== UTILITAIRES POUR FUSEAU HORAIRE ==============
# Décalage horaire pour Madagascar (UTC+3 toute l'année)
TIMEZONE_OFFSET = timedelta(hours=3)  # À ajuster selon votre fuseau horaire

def utc_to_local(utc_datetime):
    """Convertir un datetime UTC en heure locale"""
    if utc_datetime is None:
        return None
    if isinstance(utc_datetime, datetime):
        return utc_datetime + TIMEZONE_OFFSET
    return utc_datetime
# ============================================================

# ============================================================================
# TRAINING RESULTS - Résultats d'entraînement YOLOv5
# ============================================================================

class TrainingResult(db.Model):
    """Modèle pour stocker les résultats d'entraînement YOLOv5"""
    __tablename__ = 'training_results'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Identifiant du modèle
    model_name = db.Column(db.String(255), nullable=False)
    model_version = db.Column(db.String(50))
    model_family = db.Column(db.String(100), default='YOLOv5')
    
    # Dataset
    dataset_name = db.Column(db.String(255))
    dataset_path = db.Column(db.String(500))
    dataset_size = db.Column(db.Integer)
    num_classes = db.Column(db.Integer, default=4)
    class_names = db.Column(db.Text)  # JSON: ["helmet", "vest", "glasses", "person"]
    
    # Configuration d'entraînement
    epochs = db.Column(db.Integer)
    batch_size = db.Column(db.Integer)
    image_size = db.Column(db.Integer)  # 320, 416, 640 etc.
    learning_rate = db.Column(db.Float)
    optimizer = db.Column(db.String(50))
    loss_function = db.Column(db.String(100))
    patience = db.Column(db.Integer)
    
    # Métriques d'entraînement
    train_loss = db.Column(db.Float)
    train_accuracy = db.Column(db.Float)
    train_precision = db.Column(db.Float)
    train_recall = db.Column(db.Float)
    train_f1_score = db.Column(db.Float)
    
    # Métriques de validation
    val_loss = db.Column(db.Float)
    val_accuracy = db.Column(db.Float)
    val_precision = db.Column(db.Float)
    val_recall = db.Column(db.Float)
    val_f1_score = db.Column(db.Float)
    
    # Métriques de test
    test_loss = db.Column(db.Float, nullable=True)
    test_accuracy = db.Column(db.Float, nullable=True)
    test_precision = db.Column(db.Float, nullable=True)
    test_recall = db.Column(db.Float, nullable=True)
    test_f1_score = db.Column(db.Float, nullable=True)
    
    # Données détaillées
    class_metrics = db.Column(db.Text)  # JSON: {class: {precision, recall, ap}}
    confusion_matrix = db.Column(db.Text)  # JSON
    epoch_losses = db.Column(db.Text)  # JSON: list of losses per epoch
    
    # Performance
    training_time_seconds = db.Column(db.Float)
    inference_time_ms = db.Column(db.Float)  # Temps moyen par image
    fps = db.Column(db.Float)  # Images/sec
    gpu_memory_mb = db.Column(db.Float)
    
    # Artifacts
    model_path = db.Column(db.String(255))
    weights_path = db.Column(db.String(255))
    metrics_plot_path = db.Column(db.String(255))
    confusion_matrix_plot_path = db.Column(db.String(255))
    training_log_path = db.Column(db.String(255))
    
    # Status
    status = db.Column(db.String(20), default='completed')  # 'training', 'completed', 'failed'
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    detections = db.relationship('Detection', backref='training_result', lazy=True)
    
    def __repr__(self):
        return f'<TrainingResult {self.model_name} v{self.model_version} - {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': utc_to_local(self.timestamp).strftime('%H:%M:%S') if self.timestamp else None,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'model_family': self.model_family,
            'dataset_name': self.dataset_name,
            'dataset_size': self.dataset_size,
            'num_classes': self.num_classes,
            'class_names': json.loads(self.class_names) if self.class_names else None,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'image_size': self.image_size,
            'training': {
                'loss': self.train_loss,
                'accuracy': self.train_accuracy,
                'precision': self.train_precision,
                'recall': self.train_recall,
                'f1_score': self.train_f1_score
            },
            'validation': {
                'loss': self.val_loss,
                'accuracy': self.val_accuracy,
                'precision': self.val_precision,
                'recall': self.val_recall,
                'f1_score': self.val_f1_score
            },
            'test': {
                'loss': self.test_loss,
                'accuracy': self.test_accuracy,
                'precision': self.test_precision,
                'recall': self.test_recall,
                'f1_score': self.test_f1_score
            } if self.test_accuracy is not None else None,
            'training_time_seconds': self.training_time_seconds,
            'inference_time_ms': self.inference_time_ms,
            'fps': self.fps,
            'status': self.status,
            'class_metrics': json.loads(self.class_metrics) if self.class_metrics else None,
            'confusion_matrix': json.loads(self.confusion_matrix) if self.confusion_matrix else None
        }


# ============================================================================
# DETECTIONS - Résultats de détection en temps réel
# ============================================================================

class Detection(db.Model):
    """Modèle pour stocker les résultats de détection"""
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Lien au modèle d'entraînement utilisé
    training_result_id = db.Column(db.Integer, db.ForeignKey('training_results.id'), nullable=True)
    
    # Source et localisation
    source = db.Column(db.String(50), nullable=False)  # 'camera', 'image', 'video', 'iot'
    image_path = db.Column(db.String(255), nullable=True)
    video_path = db.Column(db.String(255), nullable=True)
    camera_id = db.Column(db.Integer, nullable=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('iot_sensors.id'), nullable=True)
    
    # Détections par classe
    total_persons = db.Column(db.Integer, default=0)
    with_helmet = db.Column(db.Integer, default=0)
    with_vest = db.Column(db.Integer, default=0)
    with_glasses = db.Column(db.Integer, default=0)
    with_boots = db.Column(db.Integer, default=0)
    
    # Évaluation de conformité
    compliance_rate = db.Column(db.Float, default=0.0)
    compliance_level = db.Column(db.String(20))  # 'excellent', 'good', 'warning', 'critical'
    alert_type = db.Column(db.String(20))  # 'safe', 'warning', 'danger'
    
    # Détails bruts
    raw_data = db.Column(db.Text)  # JSON: liste des détections brutes
    inference_time_ms = db.Column(db.Float)  # Temps d'inférence
    
    # Traçabilité multi-modèles
    model_used = db.Column(db.String(255), default='best.pt')  # Modèle(s) utilisé(s)
    ensemble_mode = db.Column(db.Boolean, default=False)  # Mode ensemble activé
    model_votes = db.Column(db.Text)  # JSON: {model_name: {stats}}
    aggregation_method = db.Column(db.String(50))  # 'union_nms', 'weighted_voting', etc.
    
    # Relations
    alerts = db.relationship('Alert', backref='detection', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Detection {self.id} - {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': utc_to_local(self.timestamp).strftime('%H:%M:%S') if self.timestamp else None,
            'source': self.source,
            'total_persons': self.total_persons,
            'with_helmet': self.with_helmet,
            'with_vest': self.with_vest,
            'with_glasses': self.with_glasses,
            'with_boots': self.with_boots,
            'compliance_rate': self.compliance_rate,
            'model_used': self.model_used,
            'ensemble_mode': self.ensemble_mode,
            'aggregation_method': self.aggregation_method,
            'compliance_level': self.compliance_level,
            'alert_type': self.alert_type,
            'inference_time_ms': self.inference_time_ms,
            'raw_data': json.loads(self.raw_data) if self.raw_data else None
        }


# ============================================================================
# ALERTS - Alertes et incidents
# ============================================================================

class Alert(db.Model):
    """Modèle pour stocker les alertes"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    detection_id = db.Column(db.Integer, db.ForeignKey('detections.id'), nullable=True)
    
    # Type et gravité
    type = db.Column(db.String(50), nullable=False)  # 'compliance', 'equipment_failure', 'system'
    message = db.Column(db.String(500), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    
    # Statut
    resolved = db.Column(db.Boolean, default=False, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_notes = db.Column(db.String(500), nullable=True)
    
    # Métadonnées
    data = db.Column(db.Text)  # JSON: données additionnelles
    
    def __repr__(self):
        return f'<Alert {self.id} - {self.severity}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': utc_to_local(self.timestamp).strftime('%d/%m/%Y %H:%M:%S') if self.timestamp else None,
            'type': self.type,
            'message': self.message,
            'severity': self.severity,
            'resolved': self.resolved,
            'resolved_at': utc_to_local(self.resolved_at).strftime('%d/%m/%Y %H:%M:%S') if self.resolved_at else None
        }


# ============================================================================
# IoT SENSORS AND LOGS - Capteurs IoT et simulation TinkerCad
# ============================================================================

class IoTSensor(db.Model):
    """Modèle pour les capteurs IoT / Simulation TinkerCad"""
    __tablename__ = 'iot_sensors'
    
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(50), unique=True, nullable=False)
    sensor_name = db.Column(db.String(255), nullable=False)
    sensor_type = db.Column(db.String(50))  # 'tinkercad_sim', 'arduino', 'mqtt'
    location = db.Column(db.String(255))
    description = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive', 'error'
    
    last_data = db.Column(db.Text)  # JSON: dernières données
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Configuration
    config_data = db.Column(db.Text)  # JSON: configuration spécifique au capteur
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    data_logs = db.relationship('IoTDataLog', backref='sensor', lazy=True, cascade='all, delete-orphan')
    detections = db.relationship('Detection', backref='iot_sensor', lazy=True)
    
    def __repr__(self):
        return f'<IoTSensor {self.sensor_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'sensor_name': self.sensor_name,
            'sensor_type': self.sensor_type,
            'location': self.location,
            'status': self.status,
            'last_data': json.loads(self.last_data) if self.last_data else None,
            'last_update': utc_to_local(self.last_update).strftime('%H:%M:%S') if self.last_update else None
        }


class IoTDataLog(db.Model):
    """Modèle pour les logs de données IoT"""
    __tablename__ = 'iot_data_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('iot_sensors.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Données de simulation TinkerCad
    motion_detected = db.Column(db.Boolean, default=False)
    compliance_level = db.Column(db.Float)
    led_green = db.Column(db.Boolean)
    led_red = db.Column(db.Boolean)
    buzzer_active = db.Column(db.Boolean)
    worker_present = db.Column(db.Boolean)
    
    # Données génériques (JSON)
    raw_data = db.Column(db.Text)
    
    def __repr__(self):
        return f'<IoTDataLog {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'timestamp': utc_to_local(self.timestamp).strftime('%H:%M:%S') if self.timestamp else None,
            'motion_detected': self.motion_detected,
            'compliance_level': self.compliance_level,
            'led_green': self.led_green,
            'led_red': self.led_red,
            'buzzer_active': self.buzzer_active,
            'worker_present': self.worker_present,
            'raw_data': json.loads(self.raw_data) if self.raw_data else None
        }


# ============================================================================
# DAILY PRESENCE - Suivi des présences quotidiennes
# ============================================================================

class DailyPresence(db.Model):
    """Modèle pour suivre les présences quotidiennes des travailleurs"""
    __tablename__ = 'daily_presence'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=True)  # Peut être null si pas identifié
    badge_id = db.Column(db.String(50))  # ID du badge ou identifiant temporaire
    date = db.Column(db.Date, nullable=False, index=True)  # Date de la présence
    
    first_detection = db.Column(db.DateTime, nullable=False)  # Première détection du jour
    last_detection = db.Column(db.DateTime, nullable=False)  # Dernière détection du jour
    detection_count = db.Column(db.Integer, default=1)  # Nombre de détections dans la journée
    
    # État de conformité pour la journée
    compliance_score = db.Column(db.Float)  # Score moyen de conformité
    equipment_status = db.Column(db.Text)  # JSON: {'helmet': true, 'vest': true, etc.}
    
    # Métadonnées
    source = db.Column(db.String(50))  # 'camera', 'iot', 'manual'
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    worker = db.relationship('Worker', backref='daily_presences', lazy=True)
    
    def __repr__(self):
        return f'<DailyPresence {self.badge_id or "Unknown"} - {self.date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'worker_id': self.worker_id,
            'badge_id': self.badge_id,
            'date': self.date.isoformat() if self.date else None,
            'first_detection': utc_to_local(self.first_detection).strftime('%H:%M:%S') if self.first_detection else None,
            'last_detection': utc_to_local(self.last_detection).strftime('%H:%M:%S') if self.last_detection else None,
            'detection_count': self.detection_count,
            'compliance_score': self.compliance_score,
            'equipment_status': json.loads(self.equipment_status) if self.equipment_status else None,
            'source': self.source
        }


# ============================================================================
# EMAIL NOTIFICATIONS - Configuration des notifications par email
# ============================================================================

class EmailNotification(db.Model):
    """Modèle pour configurer les notifications par email"""
    __tablename__ = 'email_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(255), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'daily', 'weekly', 'monthly'
    
    # Types de rapports à inclure
    include_detections = db.Column(db.Boolean, default=True)
    include_alerts = db.Column(db.Boolean, default=True)
    include_presence = db.Column(db.Boolean, default=True)
    include_compliance = db.Column(db.Boolean, default=True)
    
    is_active = db.Column(db.Boolean, default=True)
    
    last_sent = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailNotification {self.email_address} - {self.notification_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email_address': self.email_address,
            'notification_type': self.notification_type,
            'include_detections': self.include_detections,
            'include_alerts': self.include_alerts,
            'include_presence': self.include_presence,
            'include_compliance': self.include_compliance,
            'is_active': self.is_active,
            'last_sent': utc_to_local(self.last_sent).strftime('%H:%M:%S') if self.last_sent else None
        }


# ============================================================================
# WORKERS - Information sur les travailleurs
# ============================================================================

class Worker(db.Model):
    """Modèle pour stocker les informations des travailleurs"""
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    badge_id = db.Column(db.String(50), unique=True)
    department = db.Column(db.String(100))
    role = db.Column(db.String(100))
    
    last_detection = db.Column(db.DateTime)
    compliance_score = db.Column(db.Float)
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Worker {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'badge_id': self.badge_id,
            'department': self.department,
            'role': self.role,
            'last_detection': utc_to_local(self.last_detection).strftime('%H:%M:%S') if self.last_detection else None,
            'compliance_score': self.compliance_score
        }


# ============================================================================
# SYSTEM LOGS - Logs système
# ============================================================================

class SystemLog(db.Model):
    """Modèle pour stocker les logs système"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    level = db.Column(db.String(20))  # 'debug', 'info', 'warning', 'error', 'critical'
    message = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(100))  # Module/fonction source
    
    exception_info = db.Column(db.Text)  # Traceback complet si exception
    
    def __repr__(self):
        return f'<SystemLog {self.level} - {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'level': self.level,
            'message': self.message,
            'source': self.source
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_db(app):
    """Initialiser la base de données avec l'app Flask"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        return db


def clear_old_data(days=30):
    """Nettoyer les données anciennes (pour économiser l'espace)"""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    Detection.query.filter(Detection.timestamp < cutoff).delete()
    Alert.query.filter(Alert.timestamp < cutoff).delete()
    IoTDataLog.query.filter(IoTDataLog.timestamp < cutoff).delete()
    SystemLog.query.filter(SystemLog.timestamp < cutoff).delete()
    
    db.session.commit()
    return True
