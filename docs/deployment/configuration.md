# Configuration Système

## 🔧 Variables d'Environnement

Créer un fichier `.env` à la racine du projet:

```bash
# FLASK Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=sqlite:///database/epi_detection.db
# Ou PostgreSQL en production:
# DATABASE_URL=postgresql://user:password@localhost:5432/epi_detection

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Detection Settings
CONFIDENCE_THRESHOLD=0.25
IOU_THRESHOLD=0.45
MODEL_PATH=models/best.pt

# Performance
MAX_WORKERS=4
BATCH_SIZE=1
INFERENCE_DEVICE=cpu  # ou 'cuda' si GPU disponible

# API
API_RATE_LIMIT=100/minute
API_TIMEOUT=30

# Arduino
ARDUINO_PORT=COM3
ARDUINO_BAUD_RATE=9600
ARDUINO_ENABLED=True

# Web
HOST=0.0.0.0
PORT=5000
WORKERS=4
```

## 📄 Fichier .env.example

Copier `.env.example` et renommer en `.env`:
```bash
cp .env.example .env
```

## 🐳 Configuration Docker

### Dockerfile Multi-stage

Le `Dockerfile` fourni utilise:
- **Stage 1:** Builder avec compilations
- **Stage 2:** Runtime léger (sans build tools)

Taille image finale: ~2.5GB (PyTorch + OpenCV)

### Docker Compose

Services disponibles:
- `epi-detection-app`: Application principale
- `postgres`: (commenté) Base de données PostgreSQL
- `nginx`: (commenté) Reverse proxy

## 🌐 Configuration Network

### Local (Développement)
```
http://localhost:5000
```

### Production avec Nginx
```
http://example.com
HTTPS avec Let's Encrypt
```

Exemple config Nginx:
```nginx
upstream epi_detection {
  server epi-detection-app:5000;
}

server {
  listen 80;
  server_name example.com;
  
  location / {
    proxy_pass http://epi_detection;
    proxy_set_header Host $host;
  }
}
```

## 🔐 Sécurité

### En Production

1. **Secret Key**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Ajouter à `.env`: `SECRET_KEY=<generated_value>`

2. **HTTPS/SSL**
```bash
# Avec Let's Encrypt (certbot)
certbot certonly --standalone -d example.com
```

3. **CORS**
```python
# app/main.py
CORS(app, resources={
  r"/api/*": {"origins": ["https://example.com"]}
})
```

4. **Rate Limiting**
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)
@limiter.limit("100 per minute")
```

## 📊 Base de Données

### SQLite (Développement)
```python
DATABASE_URL=sqlite:///database/epi_detection.db
```

### PostgreSQL (Production)
```python
DATABASE_URL=postgresql://user:pass@postgres:5432/epi_detection
```

Créer la BD:
```bash
python -c "from app import db; db.create_all()"
```

## 📈 Monitoring & Logs

### Fichiers de Logs
```
logs/
├── app.log          # Logs application
├── access.log       # Accès HTTP
└── error.log        # Erreurs
```

### Format Log
```python
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

### Rotation
```python
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(
  'logs/app.log',
  maxBytes=10485760,  # 10MB
  backupCount=10
)
```

## 🔌 Intégrations Externes

### Arduino Serial
```python
ARDUINO_PORT = 'COM3'  # Windows: COM3, Linux: /dev/ttyUSB0
ARDUINO_BAUD_RATE = 9600
```

### API Externes
À ajouter si nécessaire:
- Slack notifications
- Email alerts
- Power BI connector

## ✅ Checklist Configuration

- [ ] `.env` créé avec SECRET_KEY unique
- [ ] Database URL correcte
- [ ] LOG_LEVEL approprié
- [ ] MODEL_PATH pointe vers best.pt
- [ ] ARDUINO_PORT/ENABLED configurés
- [ ] FLASK_ENV=production en prod
- [ ] CORS origins restreints en prod
- [ ] SSL/HTTPS activé en prod
- [ ] Rate limiting activé en prod
- [ ] Logs rotatifs configurés

## 📚 Ressources

- [Variables d'Environnement Flask](https://flask.palletsprojects.com/config/)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html)
- [Docker Environment Variables](https://docs.docker.com/compose/environment-variables/)
