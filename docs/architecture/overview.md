# Vue d'Ensemble Architecture

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT (Browser)                     │
│  HTML5 Canvas + JavaScript + Fetch API                  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON
                     │
┌────────────────────▼────────────────────────────────────┐
│                   FLASK API (Port 5000)                 │
│  ├─ Routes API (/api/detect, /api/stats)               │
│  ├─ Routes Web (/unified, /dashboard)                  │
│  └─ Gestion Session                                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌────────┐ ┌──────────┐
│  YOLOv5      │ │ SQLite │ │ Arduino  │
│ (best.pt)    │ │  DB    │ │ Serial   │
│ Inférence    │ │        │ │ Comm     │
└──────────────┘ └────────┘ └──────────┘
```

## 🔄 Pipeline de Détection

### 1. Frontend → Acquisition Image
```javascript
canvas.getContext('2d').drawImage(video, ...)
imageData = canvas.toDataURL('image/jpeg')
base64 = imageData.split(',')[1]
```

### 2. HTTP Request
```json
POST /api/detect
Content-Type: application/json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAAA..."
}
```

### 3. Backend - Décodage
```python
image_data = base64.b64decode(request.json['image'])
image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
```

### 4. Inférence YOLOv5
```python
results = detector.detect(image)
# Format: {
#   "detections": [...],
#   "fps": 30,
#   "confidence": 0.92
# }
```

### 5. Response JSON
```json
{
  "detections": [
    {
      "class": "helmet",
      "confidence": 0.95,
      "bbox": [100, 50, 200, 150]
    }
  ],
  "fps": 25,
  "inference_time_ms": 35
}
```

### 6. Frontend - Rendu
```javascript
detections.forEach(det => {
  drawBoundingBox(det.bbox, det.class)
})
updateCharts(fps, confidence)
```

## 📦 Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| **Backend** | Flask | 2.x |
| **ML** | PyTorch + YOLOv5 | 2.0 |
| **Computer Vision** | OpenCV | 4.x |
| **Database** | SQLite | 3.x |
| **Frontend** | HTML5 + JS | ES6+ |
| **API Client** | Fetch API | Native |
| **Container** | Docker | Latest |
| **Python** | CPython | 3.13 |

## 🔐 Sécurité

- ✅ CORS configuré
- ✅ Input validation (base64)
- ✅ Rate limiting possible
- ✅ HTTPS en production
- ✅ JWT optional
- ✅ CSRF protection

## 📊 Base de Données

```sql
-- Tables principales
CREATE TABLE sessions (
  id INTEGER PRIMARY KEY,
  start_time TIMESTAMP,
  detection_count INTEGER
)

CREATE TABLE detections (
  id INTEGER PRIMARY KEY,
  session_id INTEGER,
  class TEXT,
  confidence FLOAT,
  bbox_data TEXT,
  timestamp TIMESTAMP
)

CREATE TABLE model_metrics (
  id INTEGER PRIMARY KEY,
  accuracy FLOAT,
  loss FLOAT,
  epoch INTEGER
)
```

## ⚡ Performance

| Aspect | Valeur | Notes |
|--------|--------|-------|
| Inference | 20-50ms | Par image 640x640 |
| FPS | 20-30 | Dépend du CPU |
| API Latency | ~100ms | Incluant réseau |
| Modèle Size | 7MB | YOLOv5s |
| Accuracy | 92%+ | 5 classes |

## 🔌 Intégrations Externes

### Arduino
- Liaison série (COM3-COM10)
- Envoi alertes détections
- Réception commandes

### Exports
- PDF Reports
- Power BI Connectors
- SQL Dumps

## 📈 Scalabilité

### Améliorations Futures
- [ ] PostgreSQL au lieu SQLite
- [ ] Redis pour cache
- [ ] Kubernetes orchestration
- [ ] Load balancing Nginx
- [ ] Queue job (Celery)
- [ ] Multiple GPUs

Voir [Déploiement Production](../deployment/production.md) pour détails.
