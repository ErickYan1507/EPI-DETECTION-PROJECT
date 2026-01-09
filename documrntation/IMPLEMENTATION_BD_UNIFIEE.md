# 📊 SYNTHÈSE - Base de Données Unifiée EPI Detection

**Date:** 29 Décembre 2025  
**Statut:** ✅ COMPLET  
**Testée:** SQLite + MySQL  

---

## 🎯 Objectif Atteint

Créer une base de données **unifiée** qui consolide tous les domaines du projet EPI Detection:
- ✅ Training Results (résultats YOLOv5)
- ✅ Detections (détections temps réel)
- ✅ Alerts (alertes)
- ✅ IoT/TinkerCad (capteurs + simulation)
- ✅ Workers (travailleurs)
- ✅ System Logs (logs système)

---

## 📁 Fichiers Créés/Modifiés

### Fichiers CRÉÉS (Nouveaux)
```
✨ app/database_unified.py           - BD unifiée complète (422 lignes)
✨ app/db_training_integration.py    - Intégration train.py <-> BD
✨ init_unified_db.py                - Script d'initialisation
✨ reset_db.py                        - Reset simple (suppression + création)
✨ force_reset_db.py                 - Reset forcé (drop_all + create_all)
✨ test_database.py                  - Tests CRUD complets
✨ DATABASE_UNIFIED.md               - Documentation complète
```

### Fichiers MODIFIÉS (Importants)
```
📝 app/main.py                       - Utilise database_unified
📝 app/routes_api.py                 - Utilise database_unified
📝 app/routes_iot.py                 - Utilise database_unified
📝 config.py                          - Configuration BD améliorée
```

### Fichiers ANCIENS (Déprécié)
```
⛔ app/database.py                   - Ancien modèle (non utilisé)
⛔ app/database_new.py               - Ancien modèle IoT (non utilisé)
```

---

## 🗄️ Architecture BD Unifiée

### Modèles (7 au total)

#### 1. **TrainingResult** - Entraînement YOLOv5
```python
- id, timestamp, model_name, model_version, model_family
- dataset_name, num_classes, class_names
- epochs, batch_size, image_size, learning_rate
- train_loss, val_accuracy, test_precision (métriques)
- class_metrics, confusion_matrix (JSON)
- weights_path, model_path, training_log_path
- training_time_seconds, inference_time_ms, fps
- status ('training', 'completed', 'failed')
```

#### 2. **Detection** - Détections temps réel
```python
- id, timestamp, training_result_id (lien au modèle)
- source ('camera', 'image', 'video', 'iot')
- image_path, video_path, camera_id, sensor_id
- total_persons, with_helmet, with_vest, with_glasses, with_boots
- compliance_rate, compliance_level, alert_type
- raw_data (JSON), inference_time_ms
```

#### 3. **Alert** - Alertes et incidents
```python
- id, timestamp, detection_id
- type, message, severity ('low', 'medium', 'high', 'critical')
- resolved, resolved_at, resolution_notes
- data (JSON)
```

#### 4. **IoTSensor** - Capteurs IoT/TinkerCad
```python
- id, sensor_id (unique), sensor_name
- sensor_type ('tinkercad_sim', 'arduino', 'mqtt')
- location, description, status ('active', 'inactive', 'error')
- last_data (JSON), last_update
- config_data (JSON)
```

#### 5. **IoTDataLog** - Logs capteurs
```python
- id, sensor_id (FK), timestamp
- motion_detected, compliance_level
- led_green, led_red, buzzer_active, worker_present
- raw_data (JSON)
```

#### 6. **Worker** - Travailleurs
```python
- id, name, badge_id (unique)
- department, role
- last_detection, compliance_score
- is_active, created_at, updated_at
```

#### 7. **SystemLog** - Logs système
```python
- id, timestamp, level, message, source
- exception_info (traceback complet si erreur)
```

---

## 🚀 Démarrage Rapide

### 1️⃣ Réinitialiser la BD (Important!)
```bash
python force_reset_db.py  # Supprime TOUTES les tables et recrée
```

### 2️⃣ Tester la BD
```bash
python test_database.py   # Teste connexion + CRUD sur tous les modèles
```

### 3️⃣ Lancer l'app
```bash
python run_app.py
```

### 4️⃣ (Optionnel) Importer les résultats d'entraînement existants
```bash
python init_unified_db.py  # Guide interactif
# ou directement
python -c "from app.db_training_integration import import_all_training_results_to_db; import_all_training_results_to_db()"
```

---

## 🔧 Configuration BD

### SQLite (Défaut - Développement)
```python
# Automatique - aucune config nécessaire
# Fichier: database/epi_detection.db
```

### MySQL (Production)
```bash
# 1. Définir les variables d'environnement
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=epi_user
export DB_PASSWORD=votre_motdepasse
export DB_NAME=epi_detection_db

# 2. Créer la BD MySQL
mysql -u root -p <<EOF
CREATE DATABASE epi_detection_db CHARACTER SET utf8mb4;
CREATE USER 'epi_user'@'localhost' IDENTIFIED BY 'votre_motdepasse';
GRANT ALL PRIVILEGES ON epi_detection_db.* TO 'epi_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# 3. Installer le driver
pip install pymysql  # ou mysql-connector-python

# 4. Initialiser
python force_reset_db.py
```

---

## 📊 Tests Validés

```
✅ Connexion BD
✅ Création tables
✅ TrainingResult CRUD
✅ Detection CRUD
✅ IoTSensor CRUD
✅ IoTDataLog CRUD
✅ Worker CRUD
✅ Alert CRUD
✅ SystemLog CRUD
✅ Relations (1-to-many)
✅ JSON serialization
```

---

## 💡 Exemple d'Utilisation

```python
from flask import Flask
from config import config
from app.database_unified import db, TrainingResult, Detection, Alert

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
db.init_app(app)

with app.app_context():
    # Récupérer le dernier modèle entraîné
    latest_model = TrainingResult.query.order_by(
        TrainingResult.timestamp.desc()
    ).first()
    
    if latest_model:
        print(f"Modèle: {latest_model.model_name}")
        print(f"Précision: {latest_model.val_precision*100:.2f}%")
        print(f"Poids: {latest_model.weights_path}")
        
        # Récupérer les détections avec ce modèle
        detections = Detection.query.filter_by(
            training_result_id=latest_model.id
        ).all()
        print(f"Détections: {len(detections)}")
```

---

## 🔄 Intégration avec train.py

Les résultats d'entraînement YOLOv5 sont **automatiquement sauvegardés** dans la BD:

```python
from app.db_training_integration import save_training_to_db

# Après un entraînement
save_training_to_db(
    model_name='YOLOv5s-EPI',
    model_version='2.0',
    dataset_name='dataset',
    training_dir='runs/train/epi_detection_v1',
    epochs=100,
    batch_size=16,
    training_time_seconds=3600
)
```

---

## 🎁 Fonctionnalités Bonus

### 1. Nettoyage automatique
```python
from app.database_unified import clear_old_data

# Supprimer les données > 30 jours
clear_old_data(days=30)
```

### 2. Export JSON
```python
result = TrainingResult.query.first()
json_data = result.to_dict()  # Sérialisation complète
```

### 3. API REST intégrée
```bash
# Détections
curl http://localhost:5000/api/detect -F "image=@photo.jpg"

# IoT
curl http://localhost:5000/api/iot/sensors
curl -X POST http://localhost:5000/api/iot/simulation/start

# Stats
curl http://localhost:5000/api/stats
```

---

## ⚠️ Points Importants

### Migration depuis l'ancien système
- ✅ Les nouvelles tables coexistent avec les anciennes (aucun impact)
- ✅ Les données anciennes restent (dans `database.db`)
- ⚠️ L'app utilise uniquement la BD unifiée
- 💡 Possibilité de créer des scripts de migration si nécessaire

### Performance
- **SQLite:** Recommandé pour < 10k entrées/jour
- **MySQL:** Recommandé pour production (>  10k entrées/jour)

### Sécurité
- ✅ SQLAlchemy ORM (prévention SQL injection)
- ✅ Pool de connexions pour MySQL
- ✅ Connexions timeouts
- ⚠️ À faire: SSL pour MySQL en production

---

## 📋 Checklist Utilisation

- [ ] Exécuter `python force_reset_db.py` une fois
- [ ] Vérifier avec `python test_database.py`
- [ ] Vérifier l'app avec `python run_app.py`
- [ ] Accéder à http://localhost:5000
- [ ] Importer les résultats d'entraînement si nécessaire
- [ ] Utiliser les nouveaux modèles dans le code

---

## 📚 Documentation

Voir **[DATABASE_UNIFIED.md](DATABASE_UNIFIED.md)** pour:
- Configuration détaillée
- API REST complète
- Exemples avancés
- Dépannage
- Migration données

---

**Résumé:** La BD unifiée est prête à être utilisée en production avec support complet pour SQLite (développement) et MySQL (production). Tous les tests passent. ✅

