from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(200))
    total_persons = db.Column(db.Integer)
    with_helmet = db.Column(db.Integer)
    with_vest = db.Column(db.Integer)
    with_glasses = db.Column(db.Integer)
    compliance_rate = db.Column(db.Float)
    alert_type = db.Column(db.String(50))  # 'safe', 'warning', 'danger'
    
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(50))
    message = db.Column(db.String(200))
    severity = db.Column(db.String(20))  # 'low', 'medium', 'high'
    resolved = db.Column(db.Boolean, default=False)

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    last_detection = db.Column(db.DateTime)
    compliance_score = db.Column(db.Float)

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(20))  # 'info', 'warning', 'error'
    message = db.Column(db.String(500))
    source = db.Column(db.String(100))

class TrainingResult(db.Model):
    __tablename__ = 'training_results'
    
    id = db.Column(db.Integer, primary_key=True)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    model_name = db.Column(db.String(255), nullable=False)
    model_version = db.Column(db.String(50))
    dataset_name = db.Column(db.String(255))
    dataset_size = db.Column(db.Integer)
    
    epochs = db.Column(db.Integer)
    batch_size = db.Column(db.Integer)
    learning_rate = db.Column(db.Float)
    optimizer = db.Column(db.String(50))
    loss_function = db.Column(db.String(100))
    
    train_loss = db.Column(db.Float)
    train_accuracy = db.Column(db.Float)
    train_precision = db.Column(db.Float)
    train_recall = db.Column(db.Float)
    train_f1_score = db.Column(db.Float)
    
    val_loss = db.Column(db.Float)
    val_accuracy = db.Column(db.Float)
    val_precision = db.Column(db.Float)
    val_recall = db.Column(db.Float)
    val_f1_score = db.Column(db.Float)
    
    test_loss = db.Column(db.Float, nullable=True)
    test_accuracy = db.Column(db.Float, nullable=True)
    test_precision = db.Column(db.Float, nullable=True)
    test_recall = db.Column(db.Float, nullable=True)
    test_f1_score = db.Column(db.Float, nullable=True)
    
    class_metrics = db.Column(db.Text)
    confusion_matrix = db.Column(db.Text)
    
    training_time_seconds = db.Column(db.Float)
    status = db.Column(db.String(20), default='completed')
    notes = db.Column(db.Text)
    
    model_path = db.Column(db.String(255))
    weights_path = db.Column(db.String(255))
    metrics_plot_path = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TrainingResult {self.model_name} - {self.timestamp}>'
    
    def to_dict(self):
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