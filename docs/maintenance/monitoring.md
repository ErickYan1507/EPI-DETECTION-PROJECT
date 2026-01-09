# Monitoring et Maintenance

## 📊 Monitoring Application

### Health Check Endpoint

```bash
curl http://localhost:5000/api/health
```

Response:
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "database": "connected",
  "model": "loaded",
  "timestamp": "2026-01-09T10:30:45Z"
}
```

### Métriques en Temps Réel

```bash
# CPU Usage
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%')"

# Memory Usage
python -c "import psutil; print(f'RAM: {psutil.virtual_memory().percent}%')"

# Disk Usage
python -c "import shutil; print(f'Disk: {shutil.disk_usage(\"/\").percent}%')"
```

### Docker Stats

```bash
docker stats epi-detection-app --no-stream
```

## 📈 Logging

### Configuration

```python
# app/logger.py
import logging
import logging.handlers

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Fichier avec rotation
    handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

### Consulter les Logs

```bash
# Dernier 50 lignes
tail -n 50 logs/app.log

# Rechercher erreurs
grep ERROR logs/app.log

# Suivre en temps réel
tail -f logs/app.log
```

### Rotation Logs

Les logs sont automatiquement archivés après 10MB:
```
logs/
├── app.log          # Courant
├── app.log.1        # Archive
├── app.log.2
└── app.log.3
```

## 🔄 Sauvegarde (Backup)

### Automatisé avec Cron (Linux)

```bash
# Éditer crontab
crontab -e

# Ajouter (tous les jours à 2h du matin)
0 2 * * * /usr/bin/python3 /app/backup_script.py
```

Script backup:
```python
# backup_script.py
import shutil
from datetime import datetime

date = datetime.now().strftime('%Y%m%d_%H%M%S')

# Backup BD
shutil.copy(
    'database/epi_detection.db',
    f'backups/db_{date}.db'
)

# Backup logs
shutil.copytree(
    'logs',
    f'backups/logs_{date}',
    dirs_exist_ok=True
)

print(f"Backup créé: {date}")
```

### Sauvegarde Manuelle

```bash
# Créer archive
tar -czf backup_$(date +%Y%m%d).tar.gz \
  database/ logs/ models/best.pt

# Avec cloud (exemple AWS S3)
aws s3 cp backup_$(date +%Y%m%d).tar.gz s3://my-bucket/backups/
```

### Restauration

```bash
# Extraire archive
tar -xzf backup_20260109.tar.gz

# Ou copier fichier unique
cp backups/db_20260109_020000.db database/epi_detection.db
```

## 🔍 Surveillance Proactive

### Alertes par Email (optionnel)

```python
# app/alerts.py
from flask_mail import Mail, Message

mail = Mail()

def send_alert(subject, body):
    msg = Message(
        subject=subject,
        recipients=['admin@example.com'],
        body=body
    )
    mail.send(msg)
```

Utilisation:
```python
if memory_percent > 90:
    send_alert("Alerte Mémoire", f"RAM: {memory_percent}%")
```

### Uptime Monitoring

```bash
# Service systemd (Linux)
sudo systemctl enable epi-detection
sudo systemctl status epi-detection

# Vérifier auto-restart
systemctl show -p RestartForceExitStatus epi-detection
```

## 📊 Métriques de Base de Données

### Taille BD

```bash
# En bytes
ls -lh database/epi_detection.db

# Via SQLite
sqlite3 database/epi_detection.db "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size();"
```

### Nombre de Détections

```bash
sqlite3 database/epi_detection.db "SELECT COUNT(*) FROM detections;"
```

### Nettoyer BD Ancienne

```python
# Supprimer détections > 90 jours
from datetime import datetime, timedelta
from app.database import Detection

cutoff = datetime.utcnow() - timedelta(days=90)
old_detections = Detection.query.filter(Detection.timestamp < cutoff).delete()
db.session.commit()

print(f"Supprimé {old_detections} détections")
```

## 🚀 Optimisation Continue

### Analyser les Performances

```python
# Créer rapport performance
from app.database import Detection, Session
from sqlalchemy import func

# Détections par heure
hourly = db.session.query(
    func.strftime('%H', Detection.timestamp).label('hour'),
    func.count(Detection.id).label('count')
).group_by('hour').all()

for hour, count in hourly:
    print(f"Heure {hour}: {count} détections")
```

### Identifier les Goulots

```bash
# Profiler CPU
python -m cProfile -s cumtime app/main.py > profile.txt

# Vérifier imports lents
python -X importtime app/main.py 2> import_log.txt
```

## 📋 Checklist Maintenance Régulière

### Hebdomadaire
- [ ] Vérifier logs pour erreurs
- [ ] Confirmer health check passant
- [ ] Vérifier espace disque

### Mensuelle
- [ ] Exécuter backup
- [ ] Vérifier taille BD
- [ ] Nettoyer logs anciens
- [ ] Tester restauration backup

### Trimestriellement
- [ ] Mettre à jour dépendances Python
- [ ] Réoptimiser BD (VACUUM)
- [ ] Archiver détections anciennes
- [ ] Analyser métriques usage

## 🔗 Ressources

- [PostgreSQL Monitoring](https://www.postgresql.org/docs/current/monitoring.html)
- [SQLite Best Practices](https://www.sqlite.org/bestpractice.html)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
