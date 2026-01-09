# Backend Architecture

## 🏗️ Structure Application

```
app/
├── main.py              # Point d'entrée Flask
├── detection.py         # Logique détection YOLOv5
├── routes_api.py        # Endpoints REST
├── routes_stats.py      # Routes statistiques
├── database.py          # ORM/Gestion DB
├── database_unified.py  # BD unifiée
├── logger.py            # Logging configuré
├── utils.py             # Fonctions utilitaires
├── constants.py         # Constantes globales
├── audio_manager.py     # Gestion audio
├── camera_options.py    # Options webcam
├── pdf_export.py        # Export PDF
├── powerbi_export.py    # Connecteur Power BI
└── __init__.py
```

## 🚀 Point d'Entrée - main.py

```python
from flask import Flask, render_template
from app.detection import EPIDetector
from app.routes_api import api_bp
from app.logger import setup_logger

app = Flask(__name__)

# Configuration
app.config['DATABASE'] = 'database/epi_detection.db'
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialisation
detector = EPIDetector(model_path='models/best.pt')
logger = setup_logger(__name__)

# Blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/unified')
def unified_dashboard():
    return render_template('unified_monitoring.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

## 🤖 Détecteur YOLOv5 - detection.py

```python
class EPIDetector:
    def __init__(self, model_path='models/best.pt'):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', 
                                     path=model_path)
        self.model.conf = 0.25
        self.model.iou = 0.45
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
    
    def detect(self, image):
        """
        Détect EPI dans image
        
        Args:
            image: np.ndarray (H, W, 3)
        
        Returns:
            dict: {detections, fps, inference_time_ms}
        """
        start = time.time()
        results = self.model(image)
        inference_time = (time.time() - start) * 1000
        
        detections = self._format_results(results)
        fps = 1000 / inference_time
        
        return {
            'detections': detections,
            'inference_time_ms': inference_time,
            'fps': fps
        }
    
    def _format_results(self, results):
        """Formate les résultats YOLOv5"""
        detections = []
        for det in results.xyxy[0]:
            detections.append({
                'class': self.model.names[int(det[5])],
                'confidence': float(det[4]),
                'bbox': [int(x) for x in det[:4]]
            })
        return detections
```

## 🔌 Routes API - routes_api.py

```python
from flask import Blueprint, request, jsonify
from app.detection import EPIDetector
import base64
import cv2
import numpy as np

api_bp = Blueprint('api', __name__)
detector = EPIDetector()

@api_bp.route('/detect', methods=['POST'])
def detect():
    """POST /api/detect - Détecte EPI dans image"""
    try:
        data = request.get_json()
        image_data = base64.b64decode(data['image'])
        image = cv2.imdecode(np.frombuffer(image_data, np.uint8), 
                            cv2.IMREAD_COLOR)
        
        result = detector.detect(image)
        
        return jsonify({
            'success': True,
            'detections': result['detections'],
            'metadata': {
                'inference_time_ms': result['inference_time_ms'],
                'fps': result['fps']
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/health', methods=['GET'])
def health():
    """GET /api/health - Vérifie l'état du service"""
    return jsonify({
        'status': 'healthy',
        'model': 'loaded',
        'database': 'connected'
    }), 200
```

## 💾 Gestion Base de Données - database.py

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Detection(db.Model):
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50))
    class_name = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    bbox_data = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'class': self.class_name,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat()
        }

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), unique=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    detections = db.relationship('Detection', backref='session')
```

## 📊 Routes Statistiques - routes_stats.py

```python
@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """GET /api/stats - Retourne les statistiques"""
    period = request.args.get('period', 'today')
    
    # Calculer stats depuis BD
    total = Detection.query.count()
    by_class = db.session.query(
        Detection.class_name, 
        db.func.count(Detection.id)
    ).group_by(Detection.class_name).all()
    
    avg_confidence = db.session.query(
        db.func.avg(Detection.confidence)
    ).scalar()
    
    return jsonify({
        'total_detections': total,
        'average_confidence': avg_confidence,
        'detections_by_class': dict(by_class)
    }), 200
```

## 🔄 Request/Response Lifecycle

```
1. Client POST /api/detect
   └─> JSON avec image base64
       
2. Flask reçoit request
   └─> Vérifie Content-Type
   └─> Décode JSON
   
3. Validation
   └─> Check base64 valide
   └─> Check image décodable
   
4. Processing
   └─> cv2.imdecode() → numpy array
   └─> EPIDetector.detect() → YOLOv5
   └─> Format résultats
   
5. Response JSON
   └─> jsonify({success, detections, metadata})
   └─> HTTP 200/400
   
6. DB Storage (optionnel)
   └─> Sauvegarder détections
   └─> Enregistrer statistiques
```

## ⚙️ Initialisation Application

```bash
# Créer instance Flask
python -c "from app.main import app; app.app_context().push()"

# Initialiser BD
python -c "from app import db, app; app.app_context().push(); db.create_all()"

# Lancer le serveur
python app/main.py
```

## 🧪 Testing Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# Détection
curl -X POST http://localhost:5000/api/detect \
  -H "Content-Type: application/json" \
  -d @test_payload.json

# Statistiques
curl http://localhost:5000/api/stats?period=today
```

## 🚀 Performance Tips

1. **Caching**
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@api_bp.route('/stats')
@cache.cached(timeout=300)
def get_stats():
    ...
```

2. **Async Tasks**
```python
from celery import Celery
celery = Celery(app.name)

@celery.task
def detect_async(image_data):
    ...
```

3. **Database Optimization**
```python
# Index sur colonnes fréquemment interrogées
class Detection(db.Model):
    timestamp = db.Column(db.DateTime, index=True)
    class_name = db.Column(db.String(50), index=True)
```

## 📝 Logging Configuration

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('logs/app.log')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

Voir [Logs et Monitoring](../maintenance/monitoring.md) pour plus.
