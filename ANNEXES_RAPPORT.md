# ANNEXES DU RAPPORT - EPI DETECTION PROJECT

**Document Complet des Annexes pour Rapport de Projet**

---

## Table des Matières

1. [Configuration Système Détaillée](#1-configuration-système-détaillée)
2. [Structure Complète de la Base de Données](#2-structure-complète-de-la-base-de-données)
3. [Guide d'Installation et de Déploiement](#3-guide-dinstallation-et-de-déploiement)
4. [Documentation Technique de l'API](#4-documentation-technique-de-lapi)
5. [Questionnaire Utilisateur et Résultats](#5-questionnaire-utilisateur-et-résultats-complets)
6. [Diagramme de Gantt Détaillé](#6-diagramme-de-gantt-détaillé)
7. [Fichiers de Configuration (Exemples)](#7-fichiers-de-configuration-exemples)

---

## 1. Configuration Système Détaillée

### 1.1 Prérequis Système

#### Matériel Minimum Requis
```
- Processeur: Intel i5 ou équivalent (x64)
- RAM: 8 GB minimum (16 GB recommandé)
- Disque Dur: 20 GB libre (SSD recommandé)
- GPU (optionnel): NVIDIA CUDA compute capability 3.5+ pour accélération
```

#### Système d'Exploitation Supporté
```
- Windows 10/11 (x64)
- Linux (Ubuntu 20.04 LTS ou supérieur)
- macOS 10.13+ (avec ARM64 support)
```

### 1.2 Configuration Logicielle

#### Stack Technologique

| Composant | Version | Rôle |
|-----------|---------|------|
| **Python** | 3.8 - 3.11 | Langage principal |
| **PyTorch** | 1.13+ | Framework deep learning |
| **YOLOv5** | v6.2+ | Modèle de détection d'objets |
| **Flask** | 2.0+ | Framework web backend |
| **SQLAlchemy** | 1.4+ | ORM base de données |
| **OpenCV** | 4.5+ | Traitement d'images |
| **NumPy** | 1.20+ | Calcul scientifique |
| **Pandas** | 1.1+ | Analyse de données |
| **PyMySQL** | 1.0+ | Driver MySQL (optionnel) |
| **MySQL** | 5.7 ou 8.0 | Base de données (optionnel) |

#### Variables d'Environnement

```ini
# Base de Données
DB_TYPE=sqlite                    # 'sqlite' ou 'mysql'
DB_HOST=localhost                 # Hôte MySQL
DB_PORT=3306                      # Port MySQL
DB_USER=epi_user                  # Utilisateur MySQL
DB_PASSWORD=                       # Mot de passe MySQL
DB_NAME=epi_detection_db          # Nom base de données

# Flask
FLASK_ENV=development             # 'development' ou 'production'
FLASK_DEBUG=0                      # 0 ou 1
SECRET_KEY=your-secret-key        # Clé secrète pour sessions

# Logging
SQLALCHEMY_ECHO=False             # Echo requêtes SQL
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR

# Performance
ENSEMBLE_STRATEGY=weighted_voting # 'union_nms', 'weighted_voting', 'average'
USE_ENSEMBLE_FOR_CAMERA=False     # Pour performance temps réel
```

### 1.3 Architecture d'Application

```
EPI-DETECTION-PROJECT/
├── app/
│   ├── main.py                    # Point d'entrée Flask
│   ├── database_unified.py        # Modèles SQLAlchemy
│   ├── routes*.py                 # Routes API
│   └── [autres modules]
├── models/
│   └── best.pt                    # Modèle YOLOv5 entraîné
├── dataset/
│   ├── images/
│   └── labels/
├── database/
│   └── epi_detection.db          # Base SQLite (développement)
├── static/
│   ├── uploads/
│   └── [ressources web]
├── templates/
│   └── [fichiers HTML/JS]
├── logs/
│   └── [fichiers de log]
├── config.py                      # Configuration globale
└── requirements.txt               # Dépendances Python
```

### 1.4 Configuration Réseau

```
API Web
├── Backend Flask: http://127.0.0.1:5000
├── API REST: http://127.0.0.1:5000/api/
├── Dashboard Unified: http://127.0.0.1:5000/unified
└── Monitoring: http://127.0.0.1:5000/monitoring

Endpoints Clés:
├── POST /api/detect - Détection d'image
├── POST /api/detect_video - Détection vidéo
├── GET /api/training_results - Résultats entraînement
├── GET /api/detections - Historique détections
└── GET /api/alerts - Alertes système
```

### 1.5 Configuration des Classes EPI

```python
# Classes détectées (5 classes obligatoires)
CLASS_NAMES = [
    'helmet',    # Casque de sécurité
    'glasses',   # Lunettes de protection
    'person',    # Personne (travailleur)
    'vest',      # Gilet de sécurité
    'boots'      # Chaussures de sécurité
]

# Couleurs d'affichage des détections
CLASS_COLORS = {
    'helmet': (0, 255, 0),     # Vert
    'glasses': (0, 0, 255),    # Bleu
    'person': (255, 255, 0),   # Jaune
    'vest': (255, 0, 0),       # Rouge
    'boots': (255, 165, 0)     # Orange
}

# Seuils de détection (optimisés)
CONFIDENCE_THRESHOLD = 0.5      # Seuil confiance (50%)
IOU_THRESHOLD = 0.65            # Seuil IoU pour NMS (65%)
NMS_IOU_THRESHOLD = 0.65        # NMS ensemble (65%)
```

### 1.6 Paramètres YOLOv5

```
Model: YOLOv5 Small (s) - meilleur équilibre vitesse/précision

Entraînement:
├── Epochs: 100
├── Batch Size: 32
├── Image Size: 640×640
├── Optimizer: SGD (momentum=0.937)
├── Learning Rate: 0.01
├── Augmentation: Mosaic, AutoAugment, HSV
└── Patience (Early Stopping): 50

Inférence:
├── Max Detections: 300
├── Confidence Threshold: 0.50
├── NMS IOU: 0.65
└── Inference Time: ~50-100ms (CPU), ~20-30ms (GPU)
```

---

## 2. Structure Complète de la Base de Données

### 2.1 Schéma MySQL Détaillé

#### Table: `training_results`

```sql
CREATE TABLE training_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Identifiant du modèle
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(50),
    model_family VARCHAR(50) DEFAULT 'YOLOv5',
    model_path VARCHAR(255),
    
    -- Dataset
    dataset_name VARCHAR(255),
    dataset_size INT,
    num_classes INT DEFAULT 5,
    class_names LONGTEXT,  -- JSON format
    
    -- Configuration entraînement
    epochs INT,
    batch_size INT,
    image_size INT,
    learning_rate FLOAT,
    optimizer VARCHAR(50),
    loss_function VARCHAR(100),
    patience INT,
    
    -- Métriques entraînement
    train_loss FLOAT,
    train_accuracy FLOAT,
    train_precision FLOAT,
    train_recall FLOAT,
    train_f1_score FLOAT,
    
    -- Métriques validation
    val_loss FLOAT,
    val_accuracy FLOAT,
    val_precision FLOAT,
    val_recall FLOAT,
    val_f1_score FLOAT,
    
    -- Métriques test
    test_loss FLOAT,
    test_accuracy FLOAT,
    test_precision FLOAT,
    test_recall FLOAT,
    test_f1_score FLOAT,
    
    -- Données détaillées (JSON)
    class_metrics LONGTEXT,
    confusion_matrix LONGTEXT,
    epoch_losses LONGTEXT,
    
    -- Performance
    training_time_seconds INT,
    inference_time_ms FLOAT,
    fps FLOAT,
    gpu_memory_mb FLOAT,
    
    -- Artifacts
    metrics_plot_path VARCHAR(255),
    confusion_matrix_plot_path VARCHAR(255),
    training_log_path VARCHAR(255),
    
    -- Métadonnées
    status VARCHAR(20) DEFAULT 'completed',
    notes LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_timestamp (timestamp),
    INDEX idx_model_name (model_name),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### Table: `detections`

```sql
CREATE TABLE detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    training_result_id INT,
    
    -- Source de détection
    source VARCHAR(50) NOT NULL,  -- 'webcam', 'file', 'video', 'iot'
    image_path VARCHAR(255),
    video_path VARCHAR(255),
    camera_id INT,
    sensor_id INT,
    
    -- Résultats détection
    total_persons INT DEFAULT 0,
    with_helmet INT DEFAULT 0,
    with_vest INT DEFAULT 0,
    with_glasses INT DEFAULT 0,
    with_boots INT DEFAULT 0,
    
    -- Conformité
    compliance_rate FLOAT DEFAULT 0.0,
    compliance_level VARCHAR(20),  -- 'compliant', 'partial', 'non_compliant'
    alert_type VARCHAR(20),
    
    -- Données détection (JSON)
    raw_data LONGTEXT,
    
    -- Performance
    inference_time_ms FLOAT,
    
    -- Modèle utilisé
    model_used VARCHAR(255) DEFAULT 'best.pt',
    ensemble_mode BOOLEAN DEFAULT FALSE,
    model_votes LONGTEXT,  -- JSON
    aggregation_method VARCHAR(50),
    
    -- Métadonnées
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (training_result_id) REFERENCES training_results(id) ON DELETE SET NULL,
    FOREIGN KEY (sensor_id) REFERENCES iot_sensors(id) ON DELETE SET NULL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_source (source),
    INDEX idx_compliance_level (compliance_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### Table: `alerts`

```sql
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    detection_id INT,
    
    -- Type d'alerte
    type VARCHAR(50) NOT NULL,           -- 'missing_epi', 'low_confidence', 'system_error'
    message VARCHAR(500) NOT NULL,
    severity VARCHAR(20) NOT NULL,       -- 'info', 'warning', 'critical'
    
    -- Résolution
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME,
    resolution_notes VARCHAR(500),
    
    -- Données
    data LONGTEXT,  -- JSON
    
    -- Métadonnées
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (detection_id) REFERENCES detections(id) ON DELETE SET NULL,
    INDEX idx_severity (severity),
    INDEX idx_resolved (resolved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### Table: `iot_sensors`

```sql
CREATE TABLE iot_sensors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL UNIQUE,
    sensor_name VARCHAR(255) NOT NULL,
    sensor_type VARCHAR(50),  -- 'motion', 'temperature', 'humidity', etc.
    location VARCHAR(255),
    description LONGTEXT,
    
    status VARCHAR(20) DEFAULT 'active',
    last_data LONGTEXT,  -- JSON
    last_update DATETIME,
    config_data LONGTEXT,  -- JSON
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_sensor_id (sensor_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### Table: `iot_data_logs`

```sql
CREATE TABLE iot_data_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    motion_detected BOOLEAN DEFAULT FALSE,
    compliance_level FLOAT,
    led_green BOOLEAN,
    led_red BOOLEAN,
    buzzer_active BOOLEAN,
    worker_present BOOLEAN,
    
    raw_data LONGTEXT,  -- JSON
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sensor_id) REFERENCES iot_sensors(id) ON DELETE CASCADE,
    INDEX idx_sensor_id (sensor_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 2.2 Diagramme Entité-Relation

```
┌─────────────────────────┐
│  training_results       │
├─────────────────────────┤
│ id (PK)                 │
│ model_name              │
│ model_version           │
│ dataset_name            │
│ epochs, batch_size      │
│ train/val metrics       │
│ test metrics            │
│ created_at              │
└─────────────┬───────────┘
              │
              │ (1..N)
              │
┌─────────────▼───────────┐         ┌──────────────────┐
│     detections          │────────▶│  iot_sensors     │
├─────────────────────────┤  (N..1) ├──────────────────┤
│ id (PK)                 │         │ id (PK)          │
│ timestamp               │         │ sensor_id        │
│ source                  │         │ sensor_name      │
│ training_result_id (FK) │         │ sensor_type      │
│ total_persons           │         │ location         │
│ compliance_rate         │         │ status           │
│ raw_data (JSON)         │         │ created_at       │
└─────────────┬───────────┘         └──────────────────┘
              │                              │
              │ (1..N)                       │ (1..N)
              │                              │
              └──────────────────┬───────────┘
                                 │
                    ┌────────────▼──────────┐
                    │  iot_data_logs       │
                    ├──────────────────────┤
                    │ id (PK)              │
                    │ sensor_id (FK)       │
                    │ timestamp            │
                    │ motion_detected      │
                    │ compliance_level     │
                    │ led_green/red        │
                    │ buzzer_active        │
                    │ created_at           │
                    └──────────────────────┘

┌─────────────────────────┐
│      alerts             │
├─────────────────────────┤
│ id (PK)                 │
│ detection_id (FK)       │
│ type                    │
│ message                 │
│ severity                │
│ resolved                │
│ created_at              │
└─────────────────────────┘
```

### 2.3 Stratégie de Sauvegarde et Maintenance

```
Sauvegarde Automatique:
├── Fréquence: Quotidienne à minuit
├── Format: SQL dump compressé
├── Rétention: 30 jours minimum
└── Destination: /database/backups/

Nettoyage des Données:
├── Détections: Archivage après 90 jours
├── Logs IoT: Compression après 30 jours
├── Alertes résolues: Archivage après 60 jours
└── Training results: Conservées indéfiniment

Index Optimization:
├── Fréquence: Hebdomadaire
├── Analyse table: ANALYZE TABLE
└── Défragmentation: OPTIMIZE TABLE
```

---

## 3. Guide d'Installation et de Déploiement

### 3.1 Installation Locale (Développement)

#### Étape 1: Cloner le Repository

```bash
git clone https://github.com/ErickYan1507/EPI-DETECTION-PROJECT.git
cd EPI-DETECTION-PROJECT
```

#### Étape 2: Créer un Environnement Virtuel Python

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

#### Étape 3: Installer les Dépendances

```bash
# Installer PyTorch CPU (rapide)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Ou PyTorch GPU (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Installer les autres dépendances
pip install -r requirements.txt
```

#### Étape 4: Initialiser la Base de Données

```bash
# SQLite (par défaut, aucune configuration nécessaire)
python init.py

# Ou MySQL (si configuré)
set DB_TYPE=mysql
set DB_HOST=localhost
set DB_USER=epi_user
set DB_PASSWORD=your_password
set DB_NAME=epi_detection_db
python init_unified_db.py
```

#### Étape 5: Lancer l'Application

```bash
python app/main.py
```

Accéder à: `http://localhost:5000/unified`

### 3.2 Installation avec Docker

#### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    git wget curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers
COPY . /app/

# Installer PyTorch et dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 5000

# Commande de démarrage
CMD ["python", "app/main.py"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  # Application Flask
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DB_TYPE=mysql
      - DB_HOST=mysql_db
      - DB_USER=epi_user
      - DB_PASSWORD=epi_secure_password
      - DB_NAME=epi_detection_db
    depends_on:
      - mysql_db
    volumes:
      - ./models:/app/models
      - ./database:/app/database
      - ./logs:/app/logs
    networks:
      - epi_network

  # Base de données MySQL
  mysql_db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=epi_detection_db
      - MYSQL_USER=epi_user
      - MYSQL_PASSWORD=epi_secure_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/epi_detection_mysql_schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "3306:3306"
    networks:
      - epi_network

  # phpMyAdmin (optionnel - gestion BD)
  phpmyadmin:
    image: phpmyadmin
    environment:
      - PMA_HOST=mysql_db
      - PMA_USER=epi_user
      - PMA_PASSWORD=epi_secure_password
    ports:
      - "8080:80"
    depends_on:
      - mysql_db
    networks:
      - epi_network

volumes:
  mysql_data:

networks:
  epi_network:
    driver: bridge
```

#### Lancer avec Docker Compose

```bash
# Démarrer les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f app

# Arrêter les services
docker-compose down
```

### 3.3 Déploiement en Production

#### Checklist de Sécurité

- [ ] Désactiver DEBUG mode (`FLASK_DEBUG=0`)
- [ ] Générer `SECRET_KEY` sécurisé (32+ caractères aléatoires)
- [ ] Utiliser HTTPS/SSL (Let's Encrypt)
- [ ] Configurer CORS approprié
- [ ] Limiter les uploads de fichiers (max 50MB)
- [ ] Mettre en place rate limiting (10 req/sec par IP)
- [ ] Activer l'authentification API (tokens JWT)
- [ ] Mettre en place un firewall
- [ ] Activer les logs d'audit
- [ ] Configurer backups automatiques
- [ ] Mettre à jour régulièrement les dépendances

#### Configuration Gunicorn (Production WSGI)

```bash
# Installation
pip install gunicorn

# Lancer avec Gunicorn
gunicorn --workers=4 --threads=2 --worker-class=gthread \
  --bind=0.0.0.0:5000 \
  --timeout=120 \
  --access-logfile=/var/log/epi-app/access.log \
  --error-logfile=/var/log/epi-app/error.log \
  'app.main:app'
```

#### Configuration Nginx (Reverse Proxy)

```nginx
upstream epi_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Rediriger vers HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy
    location / {
        proxy_pass http://epi_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
    
    # Static files
    location /static/ {
        alias /var/www/epi-app/static/;
        expires 30d;
    }
}
```

---

## 4. Documentation Technique de l'API

### 4.1 Points de Terminaison (Endpoints)

#### 1. Détection d'Image

**Endpoint:** `POST /api/detect`

```bash
curl -X POST http://localhost:5000/api/detect \
  -H "Content-Type: multipart/form-data" \
  -F "image=@test_image.jpg" \
  -F "confidence=0.5"
```

**Paramètres:**
- `image` (file, required): Fichier image (PNG, JPG, JPEG)
- `confidence` (float, optional): Seuil de confiance (0-1, défaut: 0.5)
- `use_ensemble` (boolean, optional): Utiliser multi-modèles (défaut: false)

**Réponse (200 OK):**
```json
{
  "status": "success",
  "detection_id": 12345,
  "timestamp": "2026-01-26T10:30:45.123Z",
  "inference_time_ms": 85.5,
  "detections": [
    {
      "class": "helmet",
      "confidence": 0.92,
      "bbox": [100, 50, 200, 150],
      "area": 15000
    },
    {
      "class": "person",
      "confidence": 0.95,
      "bbox": [80, 40, 220, 250],
      "area": 27200
    }
  ],
  "summary": {
    "total_persons": 1,
    "with_helmet": 1,
    "with_vest": 0,
    "with_glasses": 1,
    "with_boots": 1,
    "compliance_rate": 0.75,
    "compliance_level": "partial"
  }
}
```

#### 2. Détection Vidéo

**Endpoint:** `POST /api/detect_video`

```bash
curl -X POST http://localhost:5000/api/detect_video \
  -H "Content-Type: multipart/form-data" \
  -F "video=@test_video.mp4" \
  -F "max_frames=100"
```

**Paramètres:**
- `video` (file, required): Fichier vidéo (MP4, AVI, MOV)
- `max_frames` (int, optional): Nombre max de frames (défaut: 300)
- `sample_rate` (int, optional): Traiter 1 frame tous les N frames (défaut: 5)

**Réponse (200 OK):**
```json
{
  "status": "success",
  "video_id": "vid_67890",
  "total_frames": 100,
  "processed_frames": 20,
  "alerts": 3,
  "avg_compliance_rate": 0.78,
  "frame_results": [
    {
      "frame_number": 0,
      "timestamp_sec": 0.0,
      "detections_count": 2,
      "compliance_level": "compliant",
      "alert": null
    },
    {
      "frame_number": 25,
      "timestamp_sec": 1.0,
      "detections_count": 1,
      "compliance_level": "non_compliant",
      "alert": "missing_vest"
    }
  ]
}
```

#### 3. Résultats d'Entraînement

**Endpoint:** `GET /api/training_results`

```bash
curl http://localhost:5000/api/training_results?limit=10&offset=0
```

**Paramètres:**
- `limit` (int, optional): Nombre de résultats par page (défaut: 10)
- `offset` (int, optional): Décalage (défaut: 0)
- `model_name` (string, optional): Filtrer par modèle
- `status` (string, optional): Filtrer par statut

**Réponse (200 OK):**
```json
{
  "status": "success",
  "total_count": 15,
  "results": [
    {
      "id": 1,
      "model_name": "best.pt",
      "model_version": "v1.0",
      "dataset_name": "EPI_Dataset_2025",
      "epochs": 100,
      "batch_size": 32,
      "val_accuracy": 0.92,
      "val_precision": 0.89,
      "val_recall": 0.91,
      "val_f1_score": 0.90,
      "inference_time_ms": 62.5,
      "fps": 16.0,
      "training_time_seconds": 4500,
      "created_at": "2026-01-15T09:30:00Z",
      "status": "completed"
    }
  ]
}
```

#### 4. Historique des Détections

**Endpoint:** `GET /api/detections`

```bash
curl "http://localhost:5000/api/detections?start_date=2026-01-20&end_date=2026-01-26&source=webcam"
```

**Paramètres:**
- `start_date` (string, optional): Date début (YYYY-MM-DD)
- `end_date` (string, optional): Date fin (YYYY-MM-DD)
- `source` (string, optional): Source (webcam, file, video, iot)
- `compliance_level` (string, optional): compliant, partial, non_compliant
- `limit` (int, optional): Nombre max résultats (défaut: 50)

**Réponse (200 OK):**
```json
{
  "status": "success",
  "total_count": 42,
  "detections": [
    {
      "id": 12345,
      "timestamp": "2026-01-26T10:30:45Z",
      "source": "webcam",
      "total_persons": 2,
      "with_helmet": 2,
      "with_vest": 1,
      "compliance_rate": 0.75,
      "compliance_level": "partial",
      "inference_time_ms": 85.5,
      "model_used": "best.pt",
      "alert_type": "missing_vest"
    }
  ]
}
```

#### 5. Alertes Système

**Endpoint:** `GET /api/alerts`

```bash
curl "http://localhost:5000/api/alerts?severity=critical&resolved=false"
```

**Paramètres:**
- `severity` (string, optional): info, warning, critical
- `resolved` (boolean, optional): Alertes résolues ou non
- `limit` (int, optional): Nombre max (défaut: 20)

**Réponse (200 OK):**
```json
{
  "status": "success",
  "total_count": 3,
  "alerts": [
    {
      "id": 99,
      "timestamp": "2026-01-26T14:25:30Z",
      "type": "missing_epi",
      "message": "Worker without safety vest detected",
      "severity": "critical",
      "detection_id": 12345,
      "resolved": false
    }
  ]
}
```

#### 6. Modèles Disponibles

**Endpoint:** `GET /api/models`

```bash
curl http://localhost:5000/api/models
```

**Réponse (200 OK):**
```json
{
  "status": "success",
  "models": [
    {
      "name": "best.pt",
      "type": "yolov5s",
      "size_mb": 25.5,
      "input_size": 640,
      "num_classes": 5,
      "class_names": ["helmet", "glasses", "person", "vest", "boots"],
      "is_active": true,
      "created_date": "2026-01-01T00:00:00Z"
    }
  ],
  "ensemble_enabled": false
}
```

### 4.2 Codes d'Erreur HTTP

```
200 OK               - Requête réussie
400 Bad Request      - Paramètres invalides
401 Unauthorized     - Authentication requise
403 Forbidden        - Accès refusé
404 Not Found        - Ressource non trouvée
413 Payload Too Large - Fichier trop volumineux (>50MB)
429 Too Many Requests - Rate limit dépassé
500 Internal Error    - Erreur serveur
503 Service Unavailable - Service en maintenance
```

### 4.3 Authentification

#### Avec JWT Token

```python
# Générer un token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Utiliser le token
curl -H "Authorization: Bearer eyJhbGc..." \
  http://localhost:5000/api/detections
```

### 4.4 Exemples avec Python

```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

# 1. Détection d'image
def detect_image(image_path):
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {'confidence': 0.5}
        response = requests.post(f"{BASE_URL}/detect", files=files, data=data)
    return response.json()

# 2. Obtenir les alertes critiques
def get_critical_alerts():
    params = {
        'severity': 'critical',
        'resolved': False,
        'limit': 20
    }
    response = requests.get(f"{BASE_URL}/alerts", params=params)
    return response.json()

# 3. Obtenir les statistiques du jour
def get_daily_statistics():
    today = datetime.now().date()
    params = {
        'start_date': str(today),
        'end_date': str(today),
        'limit': 1000
    }
    response = requests.get(f"{BASE_URL}/detections", params=params)
    data = response.json()
    
    if data['status'] == 'success':
        detections = data['detections']
        total_persons = sum(d['total_persons'] for d in detections)
        non_compliant = sum(1 for d in detections if d['compliance_level'] == 'non_compliant')
        avg_compliance = sum(d['compliance_rate'] for d in detections) / len(detections) if detections else 0
        
        return {
            'total_detections': len(detections),
            'total_persons_detected': total_persons,
            'non_compliant_count': non_compliant,
            'average_compliance_rate': avg_compliance
        }

# Utilisation
result = detect_image('sample_image.jpg')
print(json.dumps(result, indent=2))
```

---

## 5. Questionnaire Utilisateur et Résultats Complets

### 5.1 Questionnaire de Satisfaction

#### Questionnaire (A remplir par les utilisateurs)

**Contexte:** Vous utilisez le système EPI Detection depuis [durée]. Veuillez répondre honnêtement aux questions suivantes pour nous aider à améliorer le système.

---

**Section 1: Facilité d'Utilisation**

1. **Facilité d'installation**
   - [ ] Très facile
   - [ ] Facile
   - [ ] Neutre
   - [ ] Difficile
   - [ ] Très difficile

2. **Interface web (dashboard)**
   - [ ] Très intuitive
   - [ ] Intuitive
   - [ ] Acceptable
   - [ ] Peu intuitive
   - [ ] Confuse

3. **Configuration initiale**
   - [ ] Très simple (<15 min)
   - [ ] Simple (15-30 min)
   - [ ] Modéré (30-60 min)
   - [ ] Complexe (1-2h)
   - [ ] Très complexe (>2h)

**Section 2: Performance et Précision**

4. **Précision des détections**
   - [ ] Excellente (95%+)
   - [ ] Très bonne (90-95%)
   - [ ] Bonne (80-90%)
   - [ ] Acceptable (70-80%)
   - [ ] Insuffisante (<70%)

5. **Vitesse de détection en temps réel**
   - [ ] Très rapide (<50ms)
   - [ ] Rapide (50-100ms)
   - [ ] Acceptable (100-200ms)
   - [ ] Lent (200-500ms)
   - [ ] Très lent (>500ms)

6. **Stabilité du système**
   - [ ] Très stable (>99% uptime)
   - [ ] Stable (95-99% uptime)
   - [ ] Acceptable (90-95% uptime)
   - [ ] Instable (<90% uptime)

**Section 3: Fonctionnalités**

7. **Classes EPI détectées adéquates**
   - [ ] Tout à fait d'accord
   - [ ] D'accord
   - [ ] Neutre
   - [ ] Pas d'accord
   - [ ] Pas du tout d'accord

8. **Alertes et notifications utiles**
   - [ ] Très utiles
   - [ ] Utiles
   - [ ] Peu utiles
   - [ ] Pas utiles

9. **Rapports et statistiques suffisants**
   - [ ] Oui, complètement
   - [ ] Oui, largement
   - [ ] Moyennement
   - [ ] Non, insuffisants
   - [ ] Non, très insuffisants

**Section 4: Support et Documentation**

10. **Qualité de la documentation**
    - [ ] Excellente
    - [ ] Bonne
    - [ ] Acceptable
    - [ ] Insuffisante
    - [ ] Très insuffisante

11. **Disponibilité du support technique**
    - [ ] Très disponible
    - [ ] Disponible
    - [ ] Moyennement disponible
    - [ ] Peu disponible
    - [ ] Indisponible

**Section 5: Recommandations et Améliorations**

12. **Recommanderiez-vous ce système?**
    - [ ] Certainement
    - [ ] Probablement
    - [ ] Peut-être
    - [ ] Probablement pas
    - [ ] Certainement pas

13. **Quelles améliorations demandez-vous?** (texte libre)
    ```
    [Espace pour réponse]
    ```

14. **Quelles fonctionnalités manquent?** (texte libre)
    ```
    [Espace pour réponse]
    ```

15. **Commentaires généraux** (texte libre)
    ```
    [Espace pour réponse]
    ```

---

### 5.2 Résultats Agrégés (Exemple)

**Enquête auprès de 25 utilisateurs (Janvier 2026)**

```
SECTION 1: FACILITÉ D'UTILISATION
================================

Q1: Facilité d'installation
├─ Très facile: 40% (10)
├─ Facile: 40% (10)
├─ Neutre: 16% (4)
├─ Difficile: 4% (1)
└─ Très difficile: 0%

Q2: Interface web
├─ Très intuitive: 48% (12)
├─ Intuitive: 40% (10)
├─ Acceptable: 12% (3)
└─ Note moyenne: 4.36/5

Q3: Configuration initiale
├─ Très simple (<15 min): 28% (7)
├─ Simple (15-30 min): 56% (14)
├─ Modéré (30-60 min): 16% (4)
└─ Durée moyenne: 28 minutes


SECTION 2: PERFORMANCE
=====================

Q4: Précision des détections
├─ Excellente (95%+): 32% (8)
├─ Très bonne (90-95%): 44% (11)
├─ Bonne (80-90%): 20% (5)
├─ Acceptable (70-80%): 4% (1)
└─ Note moyenne: 4.04/5

Q5: Vitesse temps réel
├─ Très rapide (<50ms): 24% (6)
├─ Rapide (50-100ms): 52% (13)
├─ Acceptable (100-200ms): 24% (6)
└─ Note moyenne: 4.0/5

Q6: Stabilité système
├─ Très stable (>99% uptime): 36% (9)
├─ Stable (95-99% uptime): 48% (12)
├─ Acceptable (90-95% uptime): 16% (4)
└─ Note moyenne: 4.2/5


SECTION 3: FONCTIONNALITÉS
=========================

Q7: Classes EPI adéquates
├─ Tout à fait d'accord: 52% (13)
├─ D'accord: 40% (10)
├─ Neutre: 8% (2)
└─ Note moyenne: 4.44/5

Q8: Alertes utiles
├─ Très utiles: 48% (12)
├─ Utiles: 44% (11)
├─ Peu utiles: 8% (2)
└─ Note moyenne: 4.4/5

Q9: Rapports suffisants
├─ Oui, complètement: 40% (10)
├─ Oui, largement: 36% (9)
├─ Moyennement: 20% (5)
├─ Non, insuffisants: 4% (1)
└─ Note moyenne: 4.12/5


SECTION 4: SUPPORT
==================

Q10: Qualité documentation
├─ Excellente: 44% (11)
├─ Bonne: 40% (10)
├─ Acceptable: 12% (3)
├─ Insuffisante: 4% (1)
└─ Note moyenne: 4.24/5

Q11: Support technique
├─ Très disponible: 32% (8)
├─ Disponible: 48% (12)
├─ Moyennement: 16% (4)
├─ Peu disponible: 4% (1)
└─ Note moyenne: 4.08/5


SECTION 5: RECOMMANDATIONS
===========================

Q12: Recommanderiez-vous?
├─ Certainement: 56% (14)
├─ Probablement: 32% (8)
├─ Peut-être: 12% (3)
├─ Probablement pas: 0%
├─ Certainement pas: 0%
└─ Net Promoter Score: +44%


THÈMES COMMUNS AMÉLIORATIONS
=============================

Améliorations demandées:
├─ Mobile app (28% - 7 utilisateurs)
├─ Export PDF rapports (24% - 6 utilisateurs)
├─ API webhooks (20% - 5 utilisateurs)
├─ Historique détaillé par personne (20% - 5 utilisateurs)
└─ Intégration SSO/LDAP (16% - 4 utilisateurs)

Fonctionnalités manquantes:
├─ Machine learning adaptatif (32% - 8 utilisateurs)
├─ Détection faciale pour identification (28% - 7 utilisateurs)
├─ Zone d'alerte géographique (24% - 6 utilisateurs)
├─ Prédictions analytics (20% - 5 utilisateurs)
└─ Support multi-langue (16% - 4 utilisateurs)


STATISTIQUES GLOBALES
====================

Score de satisfaction global: 4.15/5 ⭐⭐⭐⭐

Taux de recommandation: 88% (22/25)

Taux de satisfaction:
├─ Très satisfait (4-5): 76% (19)
├─ Satisfait (3-4): 16% (4)
├─ Neutre: 8% (2)
└─ Insatisfait: 0%

NPS (Net Promoter Score): +44% (excellent)
```

---

## 6. Diagramme de Gantt Détaillé

### 6.1 Planification du Projet (6 mois)

```
PHASE 1: PRÉPARATION & ANALYSE (Semaine 1-4)
═════════════════════════════════════════════

├─ Recherche & Analyse des besoins      [████████░░░░░░░░░░░░] 1-2
├─ Collecte et préparation dataset       [░░████████░░░░░░░░░░] 2-4
├─ Configuration environnement dev       [░░░░████████░░░░░░░░] 3-4
└─ Mise en place infrastructure          [░░░░░░██████░░░░░░░░] 4


PHASE 2: DÉVELOPPEMENT MODÈLE (Semaine 5-12)
═════════════════════════════════════════════

├─ Data augmentation & preprocessing     [████████░░░░░░░░░░░░] 5-6
├─ Training modèle YOLOv5 (v1)          [░░████████████░░░░░░] 6-9
├─ Validation & tuning hyperparamètres   [░░░░░░░░████████░░░░] 8-10
├─ Optimisation performance              [░░░░░░░░░░░░██████░░] 10-12
└─ Tests robustesse & edge cases         [░░░░░░░░░░░░░░██████] 11-12


PHASE 3: DÉVELOPPEMENT BACKEND (Semaine 8-14)
═════════════════════════════════════════════

├─ Architecture Flask & API design       [░░░░████████░░░░░░░░] 8-10
├─ Intégration modèle YOLOv5            [░░░░░░░░████████░░░░] 9-11
├─ Base de données (SQLite/MySQL)        [░░░░░░░░░░██████░░░░] 10-12
├─ Routes API REST complètes             [░░░░░░░░░░░░████████] 12-14
└─ Authentification & sécurité           [░░░░░░░░░░░░░░██████] 13-14


PHASE 4: DÉVELOPPEMENT FRONTEND (Semaine 10-16)
════════════════════════════════════════════════

├─ Dashboard HTML/CSS/JS                 [░░░░░░░░░░████████░░] 10-12
├─ Capture webcam en temps réel          [░░░░░░░░░░░░██████░░] 11-13
├─ Visualisation détections              [░░░░░░░░░░░░░░██████] 12-14
├─ Graphiques & statistiques             [░░░░░░░░░░░░░░░░████] 14-16
└─ Responsive design & UX                [░░░░░░░░░░░░░░░░░░██] 15-16


PHASE 5: INTÉGRATION & TESTS (Semaine 13-18)
═════════════════════════════════════════════

├─ Tests unitaires backend               [░░░░░░░░░░░░░░░░████] 13-14
├─ Tests intégration API                 [░░░░░░░░░░░░░░░░░███] 14-15
├─ Tests e2e interface                   [░░░░░░░░░░░░░░░░░░██] 15-16
├─ Tests performance & charge            [░░░░░░░░░░░░░░░░░░██] 16-17
└─ Correction bugs critiques             [░░░░░░░░░░░░░░░░░░░░] 17-18


PHASE 6: DÉPLOIEMENT & FINALISATION (Semaine 18-24)
═════════════════════════════════════════════════════

├─ Setup production (Docker/Nginx)       [░░░░░░░░░░░░░░░░░░██] 18-19
├─ Sécurité production (SSL, firewall)   [░░░░░░░░░░░░░░░░░░░░] 19-20
├─ Formation utilisateurs                [░░░░░░░░░░░░░░░░░░░░] 20-21
├─ Documentation & guides                [░░░░░░░░░░░░░░░░░░░░] 21-22
├─ Déploiement prod                      [░░░░░░░░░░░░░░░░░░░░] 22-23
└─ Monitoring & support continu          [░░░░░░░░░░░░░░░░░░░░] 23-24


LÉGENDE:
████ = Tâche en cours/complétée
░░░░ = Tâche future
```

### 6.2 Dépendances et Jalons Critiques

```
Dépendances Critiques:
━━━━━━━━━━━━━━━━━━━━━━

Dataset collecté & validé
    └─→ Entraînement modèle ✓
          ├─→ Optimisation performance ✓
          └─→ Tests validation ✓
               └─→ Intégration backend ✓
                    └─→ Tests intégration
                         └─→ Déploiement production


Jalons Clés (Milestones):
═════════════════════════

Semaine 6: [▓▓▓▓▓▓░░░░] Dataset & env prêt          (25%)
Semaine 9: [▓▓▓▓▓▓▓▓▓░] Modèle v1 entraîné          (37%)
Semaine 12: [▓▓▓▓▓▓▓▓▓▓] Modèle optimisé             (50%)
Semaine 14: [▓▓▓▓▓▓▓▓▓▓] Backend API complet         (58%)
Semaine 16: [▓▓▓▓▓▓▓▓▓▓] Frontend terminé            (67%)
Semaine 18: [▓▓▓▓▓▓▓▓▓▓] Tests complétés             (75%)
Semaine 20: [▓▓▓▓▓▓▓▓▓▓] Production prête            (83%)
Semaine 24: [▓▓▓▓▓▓▓▓▓▓] Projet terminé              (100%)


Ressources Allouées par Phase:
═════════════════════════════

Phase 1 (Préparation):          1 lead + 1 data engineer = 2 personnes
Phase 2 (Modèle ML):            1 ML engineer + 1 data scientist = 2 personnes
Phase 3 (Backend):              2 backend developers = 2 personnes
Phase 4 (Frontend):             1 full-stack + 1 frontend = 2 personnes
Phase 5 (Tests):                1 QA engineer + 2 developers = 3 personnes
Phase 6 (Déploiement):          1 DevOps + 1 support = 2 personnes

Total ressources: 6-8 personnes
```

---

## 7. Fichiers de Configuration (Exemples)

### 7.1 config.py - Configuration Principale

```python
"""
Configuration application EPI Detection
"""
import os
from urllib.parse import quote_plus

class Config:
    """Configuration de base"""
    
    # ========== CHEMINS ==========
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_PATH = os.path.join(BASE_DIR, 'dataset')
    MODELS_FOLDER = os.path.join(BASE_DIR, 'models')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')
    TRAINING_RESULTS_FOLDER = os.path.join(BASE_DIR, 'runs', 'train')
    
    # ========== CLASSES EPI ==========
    CLASS_NAMES = ['helmet', 'glasses', 'person', 'vest', 'boots']
    CLASS_COLORS = {
        'helmet': (0, 255, 0),     # Vert
        'glasses': (0, 0, 255),    # Bleu
        'person': (255, 255, 0),   # Jaune
        'vest': (255, 0, 0),       # Rouge
        'boots': (255, 165, 0)     # Orange
    }
    
    # ========== SEUILS DÉTECTION ==========
    CONFIDENCE_THRESHOLD = 0.5
    IOU_THRESHOLD = 0.65
    NMS_IOU_THRESHOLD = 0.65
    
    # ========== MULTI-MODÈLES ==========
    MULTI_MODEL_ENABLED = False
    ENSEMBLE_STRATEGY = os.getenv('ENSEMBLE_STRATEGY', 'weighted_voting')
    MODEL_WEIGHTS = {
        'best.pt': 1.0,
        'model_v2.pt': 0.9,
        'model_v3.pt': 0.85
    }
    
    # ========== BASE DE DONNÉES ==========
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()
    
    if DB_TYPE == 'mysql':
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = int(os.getenv('DB_PORT', 3306))
        DB_USER = os.getenv('DB_USER', 'epi_user')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DB_NAME = os.getenv('DB_NAME', 'epi_detection_db')
        DATABASE_URI = f'mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    else:
        DB_PATH = os.path.join(BASE_DIR, 'database', 'epi_detection.db')
        DATABASE_URI = f'sqlite:///{DB_PATH}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    if DB_TYPE == 'mysql':
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 10,
            'pool_recycle': 3600,
            'pool_pre_ping': True,
            'max_overflow': 20
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {'timeout': 30}
        }
    
    # ========== FLASK ==========
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    
    # ========== CAMÉRA ==========
    CAMERA_FRAME_WIDTH = 320
    CAMERA_FRAME_HEIGHT = 240
    CAMERA_FPS = 5
    
    # ========== NOTIFICATIONS ==========
    ENABLE_NOTIFICATIONS = True
    NOTIFICATION_INTERVAL = 30

class DevelopmentConfig(Config):
    """Configuration développement"""
    DEBUG = True
    FLASK_DEBUG = 1

class ProductionConfig(Config):
    """Configuration production"""
    DEBUG = False
    FLASK_DEBUG = 0
    PREFERRED_URL_SCHEME = 'https'

class TestingConfig(Config):
    """Configuration tests"""
    TESTING = True
    DB_TYPE = 'sqlite'
    DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### 7.2 .env - Variables d'Environnement

```bash
# FLASK
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-super-secret-key-change-in-production

# DATABASE
DB_TYPE=sqlite
# DB_TYPE=mysql  # Décommenter pour MySQL

# MySQL (optionnel)
DB_HOST=localhost
DB_PORT=3306
DB_USER=epi_user
DB_PASSWORD=secure_password
DB_NAME=epi_detection_db

# SQLALCHEMY
SQLALCHEMY_ECHO=False
SQLALCHEMY_TRACK_MODIFICATIONS=False

# LOGGING
LOG_LEVEL=INFO

# DETECTIONS
CONFIDENCE_THRESHOLD=0.5
IOU_THRESHOLD=0.65

# ENSEMBLE
ENSEMBLE_STRATEGY=weighted_voting
USE_ENSEMBLE_FOR_CAMERA=False

# API
MAX_UPLOAD_SIZE=52428800  # 50MB
NOTIFICATION_INTERVAL=30

# SECURITY (Production)
# HTTPS_ONLY=True
# CORS_ORIGINS=https://yourdomain.com
```

### 7.3 docker-compose.yml - Configuration Docker

```yaml
version: '3.8'

services:
  # Flask Application
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: epi-detection-app
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DB_TYPE=mysql
      - DB_HOST=mysql_db
      - DB_USER=epi_user
      - DB_PASSWORD=epi_secure_password
      - DB_NAME=epi_detection_db
    depends_on:
      - mysql_db
    volumes:
      - ./models:/app/models:ro
      - ./logs:/app/logs
      - ./database:/app/database
      - ./static/uploads:/app/static/uploads
    networks:
      - epi_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # MySQL Database
  mysql_db:
    image: mysql:8.0
    container_name: epi-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=root_secure_password
      - MYSQL_DATABASE=epi_detection_db
      - MYSQL_USER=epi_user
      - MYSQL_PASSWORD=epi_secure_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/epi_detection_mysql_schema.sql:/docker-entrypoint-initdb.d/schema.sql:ro
    networks:
      - epi_network
    restart: unless-stopped

  # phpMyAdmin (Administration BD)
  phpmyadmin:
    image: phpmyadmin:5.2
    container_name: epi-phpmyadmin
    environment:
      - PMA_HOST=mysql_db
      - PMA_USER=epi_user
      - PMA_PASSWORD=epi_secure_password
      - PMA_PORT=3306
    ports:
      - "8080:80"
    depends_on:
      - mysql_db
    networks:
      - epi_network
    restart: unless-stopped

volumes:
  mysql_data:
    driver: local

networks:
  epi_network:
    driver: bridge
```

### 7.4 nginx.conf - Configuration Reverse Proxy

```nginx
# Configuration Nginx pour EPI Detection

upstream epi_backend {
    server app:5000;
}

# Redirection HTTP → HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Logging
    access_log /var/log/nginx/epi-access.log combined;
    error_log /var/log/nginx/epi-error.log warn;
    
    # Upload size limit
    client_max_body_size 50M;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    gzip_min_length 1000;
    
    # API Proxy
    location /api/ {
        proxy_pass http://epi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }
    
    # Application proxy
    location / {
        proxy_pass http://epi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files (with caching)
    location /static/ {
        alias /var/www/epi-app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 7.5 requirements.txt - Dépendances Python

```
# Deep Learning & Computer Vision
torch==2.0.1
torchvision==0.15.2
yolov5==7.0.13
opencv-python==4.8.0.74
pillow==9.5.0
numpy==1.24.3

# Web Framework
flask==2.3.2
flask-cors==4.0.0
flask-sqlalchemy==3.0.5

# Database
sqlalchemy==2.0.19
pymysql==1.1.0
alembic==1.11.1

# Data Processing
pandas==2.0.3
scikit-learn==1.3.0
scikit-image==0.21.0

# API & Utilities
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.0.2

# Monitoring & Logging
gunicorn==21.2.0
python-dateutil==2.8.2

# Testing
pytest==7.4.0
pytest-cov==4.1.0

# Development (optionnel)
black==23.7.0
flake8==6.0.0
pylint==2.17.5
```

### 7.6 pytest.ini - Configuration Tests

```ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=html
    --cov-report=term-missing

markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    slow: Slow tests (deselect with '-m "not slow"')
    cuda: Requires GPU/CUDA
```

---

## Résumé des Annexes

Ce document fournit une documentation complète pour:

1. **Configuration système** - Spécifications matérielles, logicielles et d'architecture
2. **Base de données** - Schéma complet, relations entités, stratégies sauvegarde
3. **Installation & Déploiement** - Procédures locales, Docker, production
4. **API technique** - Endpoints détaillés, exemples, codes d'erreur
5. **Enquête utilisateurs** - Questionnaire complet et résultats agrégés
6. **Planification** - Diagramme Gantt détaillé sur 6 mois
7. **Configuration** - Fichiers config, env, Docker, Nginx, requirements

**Document Généré:** 26 janvier 2026
**Version:** 1.0
**Statut:** Complet et prêt pour rapport final
