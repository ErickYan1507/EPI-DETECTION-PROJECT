# Déploiement Docker

## 📦 Build l'Image

```bash
# Build standard
docker build -t epi-detection:latest .

# Build avec tags de version
docker build -t epi-detection:1.0.0 \
             -t epi-detection:latest .

# Build sur ARM (Raspberry Pi)
docker buildx build --platform linux/arm64 \
  -t epi-detection:latest .
```

## 🚀 Lancer avec Docker Compose

### Démarrage
```bash
# Mode production
docker-compose up -d

# Avec logs
docker-compose up

# Rebuild l'image
docker-compose up --build
```

### Arrêt
```bash
# Arrêt propre
docker-compose down

# Supprimer les volumes aussi
docker-compose down -v
```

### Logs
```bash
# Voir les logs
docker-compose logs -f epi-detection-app

# Dernier 100 lignes
docker-compose logs --tail=100 epi-detection-app
```

## 🔧 Configuration

### Variables d'Environnement

Créer `.env`:
```bash
FLASK_ENV=production
DATABASE_URL=sqlite:////app/database/epi_detection.db
LOG_LEVEL=INFO
MAX_WORKERS=4
CONFIDENCE_THRESHOLD=0.25
```

Référencer dans `docker-compose.yml`:
```yaml
environment:
  - FLASK_ENV=${FLASK_ENV}
  - DATABASE_URL=${DATABASE_URL}
```

### Volumes

| Volume | Host | Container | Usage |
|--------|------|-----------|-------|
| models | `./models` | `/app/models` | Modèles YOLOv5 |
| database | `./database` | `/app/database` | SQLite DB |
| logs | `./logs` | `/app/logs` | Logs application |
| exports | `./exports` | `/app/exports` | PDF/Excel exports |

## 🌐 Networking

### Accès Local
```bash
http://localhost:5000
```

### Exposer sur Réseau
Modifier `docker-compose.yml`:
```yaml
ports:
  - "0.0.0.0:5000:5000"  # Accessible depuis n'importe quelle interface
```

### Avec Reverse Proxy (Nginx)
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - epi-detection-app
```

## 🔍 Monitoring

### Health Check
```bash
# Via curl
curl http://localhost:5000/health

# Via docker
docker ps  # HEALTHCHECK status
docker inspect epi-detection-app
```

### Métriques
```bash
# CPU/Memory usage
docker stats epi-detection-app

# Événements
docker events --filter container=epi-detection-app
```

## 🛠️ Maintenance

### Sauvegarder les Données
```bash
# Backup base de données
docker cp epi-detection-app:/app/database/epi_detection.db \
  ./backup/epi_detection_$(date +%Y%m%d).db

# Backup logs
docker cp epi-detection-app:/app/logs ./backup/logs_$(date +%Y%m%d)
```

### Restaurer les Données
```bash
docker cp ./backup/epi_detection.db \
  epi-detection-app:/app/database/epi_detection.db
```

### Nettoyer les Ressources
```bash
# Containers arrêtés
docker container prune

# Images non utilisées
docker image prune

# Volumes orphelins
docker volume prune

# Tout
docker system prune -a
```

## 📊 Performance Tuning

### Resources Limits
```yaml
epi-detection-app:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 1G
```

### Restart Policy
```yaml
restart_policy:
  condition: on-failure
  delay: 5s
  max_attempts: 5
  window: 60s
```

## 🐛 Dépannage

### Container N'Existe Pas
```bash
docker-compose down
docker system prune
docker-compose up --build
```

### Port Déjà Utilisé
```bash
# Trouver le processus
lsof -i :5000
# Ou changer le port
docker-compose.yml: ports: ["5001:5000"]
```

### Modèle Manquant
```bash
# Vérifier le volume
docker exec epi-detection-app ls -la /app/models

# Copier le modèle
docker cp ./models/best.pt epi-detection-app:/app/models/
```

### Erreur de Permission
```bash
# Changer les permissions de volume
sudo chown -R 1000:1000 ./models ./database ./logs
```

## 🚢 Déploiement Production

### Avec Kubernetes (Optionnel)
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: epi-detection
spec:
  replicas: 3
  selector:
    matchLabels:
      app: epi-detection
  template:
    metadata:
      labels:
        app: epi-detection
    spec:
      containers:
      - name: app
        image: epi-detection:1.0.0
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: production
```

Déployer:
```bash
kubectl apply -f deployment.yaml
```

### Avec Docker Swarm
```bash
docker swarm init
docker stack deploy -c docker-compose.yml epi-detection
```

## 📝 Checklist Déploiement

- [ ] Image buildée et testée localement
- [ ] Variables d'environnement configurées
- [ ] Volumes créés et montés
- [ ] Healthcheck fonctionne
- [ ] Ports corrects exposés
- [ ] Logs visibles
- [ ] Backup stratégie en place
- [ ] Monitoring configuré
