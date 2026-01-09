from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class IoTSensor(db.Model):
    """Modèle pour les capteurs IoT / Simulation TinkerCad"""
    __tablename__ = 'iot_sensors'
    
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(50), unique=True, nullable=False)
    sensor_name = db.Column(db.String(255))
    sensor_type = db.Column(db.String(50))  # 'tinkercad_sim', 'arduino', 'real_sensor'
    location = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive', 'error'
    
    last_data = db.Column(db.Text)  # JSON
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation
    data_logs = db.relationship('IoTDataLog', backref='sensor', lazy=True, cascade='all, delete-orphan')
    
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
            'last_update': self.last_update.isoformat()
        }

class IoTDataLog(db.Model):
    """Modèle pour les logs de données IoT / Simulation TinkerCad"""
    __tablename__ = 'iot_data_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('iot_sensors.id'), nullable=False, index=True)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Données de la simulation
    motion_detected = db.Column(db.Boolean, default=False)
    compliance_level = db.Column(db.Float)
    led_green = db.Column(db.Boolean)
    led_red = db.Column(db.Boolean)
    buzzer_active = db.Column(db.Boolean)
    worker_present = db.Column(db.Boolean)
    
    # Données supplémentaires (JSON)
    raw_data = db.Column(db.Text)
    
    def __repr__(self):
        return f'<IoTDataLog {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'timestamp': self.timestamp.isoformat(),
            'motion_detected': self.motion_detected,
            'compliance_level': self.compliance_level,
            'led_green': self.led_green,
            'led_red': self.led_red,
            'buzzer_active': self.buzzer_active,
            'worker_present': self.worker_present,
            'raw_data': json.loads(self.raw_data) if self.raw_data else None
        }

class Detection(db.Model):
    """Modèle pour stocker les résultats de détection"""
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    image_path = db.Column(db.String(255), nullable=True)
    
    total_persons = db.Column(db.Integer, default=0)
    with_helmet = db.Column(db.Integer, default=0)
    with_vest = db.Column(db.Integer, default=0)
    with_glasses = db.Column(db.Integer, default=0)
    with_boots = db.Column(db.Integer, default=0)
    
    compliance_rate = db.Column(db.Float, default=0.0)
    compliance_level = db.Column(db.String(20))
    alert_type = db.Column(db.String(20))
    
    source = db.Column(db.String(50))
    raw_data = db.Column(db.Text)
    
    alerts = db.relationship('Alert', backref='detection', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Detection {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'total_persons': self.total_persons,
            'compliance_rate': self.compliance_rate,
            'alert_type': self.alert_type
        }

class Alert(db.Model):
    """Modèle pour stocker les alertes"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    detection_id = db.Column(db.Integer, db.ForeignKey('detections.id'), nullable=True)
    
    type = db.Column(db.String(50))
    message = db.Column(db.String(500), nullable=False)
    severity = db.Column(db.String(20))
    
    resolved = db.Column(db.Boolean, default=False, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_notes = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return f'<Alert {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'severity': self.severity,
            'resolved': self.resolved
        }

class Worker(db.Model):
    """Modèle pour stocker les travailleurs"""
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    badge_id = db.Column(db.String(50), unique=True)
    department = db.Column(db.String(100))
    
    last_detection = db.Column(db.DateTime)
    total_detections = db.Column(db.Integer, default=0)
    compliance_score = db.Column(db.Float, default=100.0)
    
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
            'compliance_score': self.compliance_score
        }

class SystemLog(db.Model):
    """Modèle pour les logs système"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    level = db.Column(db.String(20))
    message = db.Column(db.String(500), nullable=False)
    module = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<SystemLog {self.timestamp}>'

class TrainingResult(db.Model):
    """Modèle pour stocker les résultats d'entraînement/validation/test"""
    __tablename__ = 'training_results'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Information générale
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    model_name = db.Column(db.String(255), nullable=False)
    model_version = db.Column(db.String(50))
    dataset_name = db.Column(db.String(255))
    dataset_size = db.Column(db.Integer)
    
    # Configuration d'entraînement
    epochs = db.Column(db.Integer)
    batch_size = db.Column(db.Integer)
    learning_rate = db.Column(db.Float)
    optimizer = db.Column(db.String(50))
    loss_function = db.Column(db.String(100))
    
    # Résultats d'entraînement
    train_loss = db.Column(db.Float)
    train_accuracy = db.Column(db.Float)
    train_precision = db.Column(db.Float)
    train_recall = db.Column(db.Float)
    train_f1_score = db.Column(db.Float)
    
    # Résultats de validation
    val_loss = db.Column(db.Float)
    val_accuracy = db.Column(db.Float)
    val_precision = db.Column(db.Float)
    val_recall = db.Column(db.Float)
    val_f1_score = db.Column(db.Float)
    
    # Résultats de test (optionnel)
    test_loss = db.Column(db.Float, nullable=True)
    test_accuracy = db.Column(db.Float, nullable=True)
    test_precision = db.Column(db.Float, nullable=True)
    test_recall = db.Column(db.Float, nullable=True)
    test_f1_score = db.Column(db.Float, nullable=True)
    
    # Métriques par classe (JSON)
    class_metrics = db.Column(db.Text)  # JSON format
    confusion_matrix = db.Column(db.Text)  # JSON format
    
    # Durée et statut
    training_time_seconds = db.Column(db.Float)
    status = db.Column(db.String(20), default='completed')  # 'training', 'completed', 'failed'
    notes = db.Column(db.Text)
    
    # Chemin des fichiers
    model_path = db.Column(db.String(255))
    weights_path = db.Column(db.String(255))
    metrics_plot_path = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TrainingResult {self.model_name} - {self.timestamp}>'
    
    def to_dict(self):
        """Convertir le modèle en dictionnaire"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'model_name': self.model_name,
            'model_version': self.model_version,
            'dataset_name': self.dataset_name,
            'dataset_size': self.dataset_size,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
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
            'status': self.status,
            'class_metrics': json.loads(self.class_metrics) if self.class_metrics else None,
            'confusion_matrix': json.loads(self.confusion_matrix) if self.confusion_matrix else None
        }
    
    @staticmethod
    def create_from_training(training_data):
        """Créer une instance à partir des données d'entraînement"""
        result = TrainingResult()
        for key, value in training_data.items():
            if hasattr(result, key):
                setattr(result, key, value)
        return result
