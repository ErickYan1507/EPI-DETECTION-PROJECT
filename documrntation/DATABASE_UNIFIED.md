# 🗄️ Base de Données Unifiée - EPI Detection

## Vue d'ensemble

Le projet utilise maintenant une **base de données unifiée** (`app/database_unified.py`) qui consolide tous les domaines:

- ✅ **Training Results** - Résultats d'entraînement YOLOv5
- ✅ **Detections** - Résultats de détection en temps réel  
- ✅ **Alerts** - Alertes et incidents
- ✅ **IoT Sensors & Logs** - Capteurs IoT et simulation TinkerCad
- ✅ **Workers** - Information sur les travailleurs
- ✅ **System Logs** - Logs système

## Configuration

### Variables d'environnement

```bash
# Choisir le type de BD (par défaut: sqlite)
export DB_TYPE=sqlite    # ou "mysql"

# Pour MySQL (optionnel)
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=epi_user
export DB_PASSWORD=votre_mot_de_passe
export DB_NAME=epi_detection_db

# Activer les logs SQL (debug)
export SQLALCHEMY_ECHO=true
```

### SQLite (par défaut - développement)

Aucune configuration requise! La BD est créée automatiquement dans:
```
database/epi_detection.db
```

### MySQL (production)

1. **Installer MySQL Server** (si pas déjà fait)

2. **Créer la base de données:**
```sql
CREATE DATABASE epi_detection_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'epi_user'@'localhost' IDENTIFIED BY 'mot_de_passe_securise';
GRANT ALL PRIVILEGES ON epi_detection_db.* TO 'epi_user'@'localhost';
FLUSH PRIVILEGES;
```

3. **Installer le driver Python:**
```bash
pip install pymysql
# ou
pip install mysql-connector-python
```

4. **Configurer les variables d'environnement**

## Initialisation

### 1. Initialiser la base de données

```bash
python init_unified_db.py
```

Cela va:
- ✅ Créer/vérifier toutes les tables
- ✅ Importer les résultats d'entraînement existants (optionnel)
- ✅ Afficher les statistiques

### 2. Vérifier la connexion

```bash
python -c "from app.database_unified import db; print('✅ BD OK')"
```

## Structure des modèles

### TrainingResult
Stocke les résultats complets d'entraînement YOLOv5:
```python
from app.database_unified import TrainingResult

result = TrainingResult.query.first()
print(result.to_dict())  # Retourne tous les détails
```

**Champs importants:**
- `model_name`, `model_version` - Identifiant du modèle
- `epochs`, `batch_size`, `image_size` - Configuration
- `train_loss`, `val_accuracy`, etc. - Métriques
- `weights_path` - Chemin du fichier de poids
- `class_names` - Noms des classes (JSON)

### Detection
Résultats de détection en temps réel:
```python
from app.database_unified import Detection

# Dernières détections
detections = Detection.query.order_by(Detection.timestamp.desc()).limit(10).all()

for det in detections:
    print(f"Source: {det.source}")  # 'camera', 'image', 'video', 'iot'
    print(f"Conformité: {det.compliance_rate}%")
    print(f"Personnes: {det.total_persons} | Casques: {det.with_helmet}")
```

**Sources possibles:**
- `camera` - Détection en direct caméra
- `image` - Image uploadée
- `video` - Vidéo uploadée
- `iot` - Capteur IoT/TinkerCad

### IoTSensor et IoTDataLog
Gestion des capteurs IoT et simulation TinkerCad:
```python
from app.database_unified import IoTSensor, IoTDataLog

# Récupérer un capteur
sensor = IoTSensor.query.filter_by(sensor_type='tinkercad_sim').first()

# Ses dernières données
logs = sensor.data_logs.order_by(IoTDataLog.timestamp.desc()).limit(100).all()

for log in logs:
    print(f"Mouvement: {log.motion_detected}")
    print(f"Conformité: {log.compliance_level}%")
    print(f"LED: Verte={log.led_green} Rouge={log.led_red}")
```

### Alert
Alertes et incidents:
```python
from app.database_unified import Alert

# Alertes non résolues
unresolved = Alert.query.filter_by(resolved=False).all()

# Marquer comme résolue
alert = Alert.query.get(1)
alert.resolved = True
alert.resolved_at = datetime.utcnow()
db.session.commit()
```

## Intégration avec train.py

Les résultats d'entraînement sont **automatiquement sauvegardés** dans la BD:

```python
from app.db_training_integration import save_training_to_db

# Après un entraînement YOLOv5
training_id = save_training_to_db(
    model_name='YOLOv5s-EPI',
    model_version='2.0',
    dataset_name='dataset',
    training_dir='runs/train/epi_detection_v1',
    epochs=100,
    batch_size=16,
    training_time_seconds=3600
)

print(f"Résultat sauvegardé: ID={training_id}")
```

## API REST

Toutes les routes API utilisent la BD unifiée:

### Détections
```bash
# POST une image
curl -F "image=@photo.jpg" http://localhost:5000/api/detect

# GET les stats
curl http://localhost:5000/api/stats
```

### IoT
```bash
# Démarrer simulation
curl -X POST http://localhost:5000/api/iot/simulation/start

# État de simulation
curl http://localhost:5000/api/iot/simulation/state

# Capteurs
curl http://localhost:5000/api/iot/sensors
```

## Migration depuis l'ancien système

Si vous aviez les anciennes BD:
- `database.py` (SQLAlchemy)
- `database_new.py` (IoT)

L'initialisation va:
1. ✅ Créer les nouvelles tables unifiées
2. ✅ Importer les résultats d'entraînement
3. ⚠️ Les détections/alertes anciennes restent dans l'ancienne BD (optionnel: script de migration)

## Nettoyage des données anciennes

Pour libérer de l'espace, nettoyer les données de plus de 30 jours:

```python
from app.database_unified import clear_old_data, db

with app.app_context():
    cleared = clear_old_data(days=30)
    print(f"Données nettoyées: {cleared}")
```

## Dépannage

### Erreur: "No module named 'pymysql'"
```bash
pip install pymysql
```

### Erreur: "Access denied for user"
Vérifier les crédentiels MySQL:
```bash
mysql -h localhost -u epi_user -p
# Entrer le mot de passe
```

### Erreur: "Table already exists"
Supprimer et réinitialiser:
```python
from app.database_unified import db

with app.app_context():
    db.drop_all()  # ⚠️ Attention: supprime TOUTES les données!
    db.create_all()
```

### BD SQLite verrouillée
Fermer tous les processus accédant au fichier:
```bash
rm database/epi_detection.db  # Supprimer et recréer
python init_unified_db.py
```

## Performance

### SQLite
- **Avantage:** Simple, pas de serveur, parfait pour développement
- **Limitation:** Une seule écriture à la fois
- **Recommandé pour:** < 10k entrées/jour

### MySQL
- **Avantage:** Haute performance, support multi-utilisateurs
- **Limitation:** Nécessite un serveur
- **Recommandé pour:** Production, > 10k entrées/jour

## Fichiers clés

```
app/
├── database_unified.py          # 🆕 BD unifiée avec tous les modèles
├── database.py                  # ⛔ Ancien (deprecated)
├── database_new.py              # ⛔ Ancien (deprecated)
├── db_training_integration.py   # 🆕 Intégration train.py <-> BD
├── main.py                      # ✅ Utilise la BD unifiée
├── routes_api.py                # ✅ Utilise la BD unifiée
└── routes_iot.py                # ✅ Utilise la BD unifiée

config.py                         # ✅ Configuration DB améliorée
init_unified_db.py               # 🆕 Script d'initialisation
```

## Exemple complet

```python
from flask import Flask
from config import config
from app.database_unified import db, TrainingResult, Detection, Alert
from app.db_training_integration import save_training_to_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
db.init_app(app)

with app.app_context():
    # Récupérer un résultat d'entraînement
    latest = TrainingResult.query.order_by(
        TrainingResult.timestamp.desc()
    ).first()
    
    print(f"Modèle: {latest.model_name} v{latest.model_version}")
    print(f"Précision: {latest.val_precision*100:.2f}%")
    print(f"Recall: {latest.val_recall*100:.2f}%")
    print(f"Poids: {latest.weights_path}")
    
    # Récupérer les détections du jour
    from datetime import timedelta
    today = datetime.utcnow().date()
    
    todays_detections = Detection.query.filter(
        Detection.timestamp >= today,
        Detection.timestamp < (today + timedelta(days=1))
    ).all()
    
    print(f"Détections aujourd'hui: {len(todays_detections)}")
    
    # Alertes non résolues
    unresolved = Alert.query.filter_by(resolved=False).count()
    print(f"Alertes en attente: {unresolved}")
```

---

**Dernière mise à jour:** 29 Décembre 2025  
**Base de données:** Unifiée SQLite/MySQL  
**Version:** 2.0
