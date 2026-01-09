# Production Deployment

## 🌐 Préparation Production

### Pre-Deployment Checklist

- [ ] Tester en environnement de staging
- [ ] Revoir les configurations de sécurité
- [ ] Sauvegarder données actuelles
- [ ] Préparer plan de rollback
- [ ] Briefing équipe support

## 🔐 Configuration Sécurité

### Environment Variables

Créer `.env.production`:
```bash
# Security
SECRET_KEY=<random-very-long-string>
FLASK_ENV=production
FLASK_DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/epi_detection

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/epi-detection/app.log

# Performance
WORKERS=8
MAX_CONNECTIONS=20

# API
API_RATE_LIMIT=1000/hour
ENABLE_CORS=False
```

### HTTPS/SSL

```bash
# Avec Certbot (Let's Encrypt)
sudo apt-get install certbot python3-certbot-nginx

# Générer certificat
sudo certbot certonly --standalone -d example.com

# Auto-renew
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/epi-detection

upstream epi_app {
    least_conn;
    server epi-detection-app:5000;
    server epi-detection-app:5001;
    keepalive 32;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name example.com;
    
    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Logs
    access_log /var/log/nginx/epi-detection-access.log;
    error_log /var/log/nginx/epi-detection-error.log;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req zone=api_limit burst=20 nodelay;
    
    # Proxy
    location / {
        proxy_pass http://epi_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API endpoints
    location /api {
        limit_req zone=api_limit burst=50 nodelay;
        proxy_pass http://epi_app;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # Static files
    location /static {
        alias /app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Systemd Service (Linux)

```ini
# /etc/systemd/system/epi-detection.service

[Unit]
Description=EPI Detection Application
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/epi-detection

# Start
ExecStart=/usr/bin/docker-compose -f docker-compose.yml up

# Restart policy
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/epi-detection/.env.production

[Install]
WantedBy=multi-user.target
```

Activation:
```bash
sudo systemctl daemon-reload
sudo systemctl enable epi-detection
sudo systemctl start epi-detection
```

## 📊 Scaling Horizontal

### Docker Compose Multi-instances

```yaml
version: '3.9'

services:
  epi-detection-1:
    build: .
    environment:
      - INSTANCE_ID=1
    ports:
      - "5001:5000"
  
  epi-detection-2:
    build: .
    environment:
      - INSTANCE_ID=2
    ports:
      - "5002:5000"
  
  epi-detection-3:
    build: .
    environment:
      - INSTANCE_ID=3
    ports:
      - "5003:5000"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - epi-detection-1
      - epi-detection-2
      - epi-detection-3
```

### Database Connection Pool

```python
# app/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## 📈 Monitoring Production

### Prometheus Metrics (optionnel)

```python
# app/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

detection_count = Counter(
    'detections_total',
    'Total detections',
    ['class']
)

inference_time = Histogram(
    'inference_duration_seconds',
    'Inference duration'
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active sessions'
)

@app.route('/api/detect', methods=['POST'])
def detect():
    start = time.time()
    # ... detect code ...
    detection_count.labels(class='helmet').inc()
    inference_time.observe(time.time() - start)
```

### Loki Logging (optionnel)

```bash
# docker-compose.yml addons
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"

promtail:
  image: grafana/promtail:latest
  volumes:
    - ./logs:/var/log
    - ./promtail-config.yaml:/etc/promtail/config.yml
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Tests
        run: |
          pip install -r requirements.txt
          pytest tests/
      
      - name: Build Image
        run: docker build -t epi-detection:latest .
      
      - name: Push to Registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag epi-detection:latest ${{ secrets.DOCKER_USERNAME }}/epi-detection:latest
          docker push ${{ secrets.DOCKER_USERNAME }}/epi-detection:latest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          ssh user@production-server << 'EOF'
          cd /opt/epi-detection
          docker-compose pull
          docker-compose up -d
          EOF
```

## 🚨 Alerting

### Health Check Monitoring

```bash
#!/bin/bash
# check_health.sh

HEALTH_ENDPOINT="https://example.com/api/health"
MAX_RETRIES=3

for i in $(seq 1 $MAX_RETRIES); do
  response=$(curl -s $HEALTH_ENDPOINT)
  status=$(echo $response | jq -r '.status')
  
  if [ "$status" == "healthy" ]; then
    echo "✓ Health check passed"
    exit 0
  fi
  
  if [ $i -lt $MAX_RETRIES ]; then
    sleep 10
  fi
done

echo "✗ Health check failed - Alerting..."
# Send alert (Slack, PagerDuty, email, etc.)
curl -X POST https://hooks.slack.com/... -d "EPI Detection Down"
```

Cron:
```bash
*/5 * * * * /opt/epi-detection/check_health.sh
```

## 🔙 Rollback Plan

```bash
#!/bin/bash
# rollback.sh

VERSION=$1
BACKUP_DIR="/backups/epi-detection"

echo "Rolling back to version $VERSION..."

# Arrêter application
docker-compose down

# Restaurer BD depuis backup
cp "$BACKUP_DIR/db_$VERSION.db" database/epi_detection.db

# Relancer version précédente
docker-compose up -d

echo "Rollback complété"
```

Utilisation:
```bash
./rollback.sh 20260109_150000
```

## ✅ Post-Deployment

### Vérifications

```bash
# Health check
curl https://example.com/api/health

# API test
curl -X POST https://example.com/api/detect -d {...}

# Dashboard
open https://example.com/unified

# Logs
docker logs -f epi-detection-app

# Metrics
curl https://example.com/metrics
```

### Documentation

- [ ] Mettre à jour DNS records
- [ ] Documenter configuration production
- [ ] Former l'équipe support
- [ ] Créer runbook opérationnel

## 📞 Support Production

### SLA Guidelines

- **P1 (Critical):** Application down → 15 min response
- **P2 (High):** Fonctionnalité majeure affected → 1h response
- **P3 (Medium):** Bug mineur → 4h response
- **P4 (Low):** Feature request → Backlog

### Runbook Exemple

```markdown
## Incident: Détecteur ne répond plus

### Diagnostique
1. Vérifier health: curl /api/health
2. Vérifier logs: docker logs -f epi-detection-app
3. Vérifier ressources: docker stats

### Resolution Quick
- Redémarrer: docker-compose restart
- Force reload: docker-compose up --force-recreate

### Full Recovery
- Rollback version précédente
- Restaurer BD depuis backup
- Redémarrer services
```

---

**Last Updated:** January 9, 2026
