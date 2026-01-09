# API Documentation

## 📚 Overview

L'API REST fournit des endpoints pour:
- Détection d'EPI via image
- Récupération de statistiques
- Gestion des sessions
- Configuration système

## 🔗 Base URL

```
http://localhost:5000/api
```

## 🔐 Authentification

Actuellement: **Aucune** (développement)

Production: À implémenter JWT si nécessaire

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/api/detect
```

## 📋 Endpoints

### 1. POST /detect

Détecte les EPI dans une image base64.

**Request:**
```bash
curl -X POST http://localhost:5000/api/detect \
  -H "Content-Type: application/json" \
  -d '{
    "image": "iVBORw0KGgoAAAANSUhE...",
    "confidence_threshold": 0.5
  }'
```

**Response 200:**
```json
{
  "success": true,
  "detections": [
    {
      "id": "det_001",
      "class": "helmet",
      "confidence": 0.95,
      "bbox": {
        "x": 100,
        "y": 50,
        "width": 150,
        "height": 200
      },
      "timestamp": "2026-01-09T10:30:45Z"
    }
  ],
  "metadata": {
    "image_size": [640, 480],
    "inference_time_ms": 35,
    "fps": 28,
    "model_version": "yolov5s-best",
    "accuracy": 0.92
  }
}
```

**Error 400:**
```json
{
  "success": false,
  "error": "Invalid base64 image",
  "code": "INVALID_INPUT"
}
```

### 2. GET /stats

Récupère les statistiques de détection.

**Request:**
```bash
curl http://localhost:5000/api/stats?period=today
```

**Query Parameters:**
- `period`: `hour`, `today`, `week`, `month` (default: `today`)
- `class_filter`: `helmet`, `vest`, `glasses`, `boots` (optionnel)

**Response 200:**
```json
{
  "success": true,
  "stats": {
    "total_detections": 1250,
    "total_sessions": 45,
    "average_confidence": 0.924,
    "detections_by_class": {
      "helmet": 450,
      "vest": 380,
      "glasses": 250,
      "boots": 170
    },
    "top_detection_hour": "10:00",
    "uptime_hours": 23.5
  }
}
```

### 3. GET /health

Vérify l'état du service.

**Request:**
```bash
curl http://localhost:5000/api/health
```

**Response 200:**
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "database": "connected",
  "model": "loaded",
  "timestamp": "2026-01-09T10:30:45Z"
}
```

### 4. POST /session/start

Démarre une session de détection.

**Request:**
```bash
curl -X POST http://localhost:5000/api/session/start \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assembly Line A",
    "location": "Factory Floor"
  }'
```

**Response 200:**
```json
{
  "session_id": "sess_abc123",
  "start_time": "2026-01-09T10:30:45Z",
  "status": "active"
}
```

### 5. POST /session/end

Termine une session.

**Request:**
```bash
curl -X POST http://localhost:5000/api/session/end \
  -H "Content-Type: application/json" \
  -d '{"session_id": "sess_abc123"}'
```

**Response 200:**
```json
{
  "session_id": "sess_abc123",
  "end_time": "2026-01-09T11:30:45Z",
  "total_detections": 250,
  "duration_minutes": 60
}
```

## ⚠️ Codes d'Erreur

| Code | HTTP | Description |
|------|------|-------------|
| SUCCESS | 200 | Requête réussie |
| INVALID_INPUT | 400 | Données invalides |
| UNAUTHORIZED | 401 | Authentification requise |
| FORBIDDEN | 403 | Accès refusé |
| NOT_FOUND | 404 | Ressource inexistante |
| SERVER_ERROR | 500 | Erreur serveur |

## 🔄 Rate Limiting

À implémenter:
- 100 requêtes par minute (par IP)
- 10,000 requêtes par jour (par API key)

## 📊 Exemples d'Utilisation

### Python
```python
import requests
import base64

with open('image.jpg', 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode()

response = requests.post(
    'http://localhost:5000/api/detect',
    json={'image': image_base64}
)

detections = response.json()['detections']
for det in detections:
    print(f"{det['class']}: {det['confidence']:.1%}")
```

### JavaScript
```javascript
async function detectEPI(imageSrc) {
  const response = await fetch('http://localhost:5000/api/detect', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({image: imageSrc})
  })
  
  return await response.json()
}
```

### cURL
```bash
# Détection
curl -X POST http://localhost:5000/api/detect \
  -H "Content-Type: application/json" \
  -d @payload.json

# Statistiques
curl "http://localhost:5000/api/stats?period=week"

# Santé
curl http://localhost:5000/api/health
```

## 📝 Notes

- Images acceptées: JPEG, PNG, BMP
- Format base64 requis pour POST /detect
- Réponses toujours en JSON
- CORS activé pour localhost
