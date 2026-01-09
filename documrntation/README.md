# 🛡️ EPI Detection System

Système de détection des Équipements de Protection Individuelle (EPI) utilisant YOLOv5 et Flask.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [API endpoints](#api-endpoints)

## 🎯 Vue d'ensemble

Ce système détecte automatiquement la conformité en matière d'EPI:
- **Casques** (helmet)
- **Gilets de sécurité** (vest)
- **Lunettes** (glasses)
- **Bottes** (boots)
- **Personnes** (person)

## 🚀 Installation

### Prérequis

- Python 3.8+
- CUDA 11.0+ (pour GPU, optionnel)
- 8GB RAM minimum

### Étapes

1. **Cloner le repository**
```bash
git clone <repository-url>
cd EPI-DETECTION-PROJECT
```

2. **Créer un environnement virtuel**
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer l'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

5. **Initialiser la base de données**
```bash
python -c "from app.main_new import app, db; app.app_context().push(); db.create_all()"
```

## ⚙️ Configuration

Éditer le fichier `.env`:

```env
# Mode
ENV=development
DEBUG=True

# Base de données
DATABASE_URI=sqlite:///./data/epi_detection.db

# Détection
CONFIDENCE_THRESHOLD=0.5
IOU_THRESHOLD=0.45

# Notifications
ENABLE_NOTIFICATIONS=True
```

## 🏃 Utilisation

### Lancer l'application

```bash
# Mode développement
python run_app.py dev

# Mode production
python run_app.py prod
```

### Entraîner le modèle

```bash
python run_app.py train
# ou directement
python train.py --epochs 100 --batch-size 16
```

### Utiliser l'API

**Détection sur une image:**
```bash
curl -X POST -F "image=@image.jpg" http://localhost:5000/api/detect
```

**Récupérer les détections:**
```bash
curl http://localhost:5000/api/detections?limit=50
```

**Statistiques:**
```bash
curl http://localhost:5000/api/stats
```

## 📁 Structure du projet

```
.
├── app/
│   ├── __init__.py
│   ├── constants.py        # Énumérations et constantes
│   ├── database.py         # Modèles SQLAlchemy
│   ├── database_new.py     # Modèles améliorés
│   ├── detection.py        # Logique de détection
│   ├── logger.py           # Configuration logging
│   ├── main.py             # Application Flask (ancien)
│   ├── main_new.py         # Application Flask (nouveau)
│   ├── routes_api.py       # API endpoints
│   ├── dashboard.py        # Dashboard routes
│   ├── notifications.py    # Notifications
│   ├── pdf_export.py       # Export PDF
│   ├── tinkercad_sim.py    # Simulation TinkerCad
│   ├── powerbi_export.py   # Export PowerBI
│   ├── utils.py            # Utilitaires
│   └── init.py             # Initialisation
├── config.py               # Configuration globale
├── train.py                # Script d'entraînement
├── dataset/                # Dataset d'entraînement
├── models/                 # Modèles entraînés
├── static/                 # Fichiers statiques
├── templates/              # Templates HTML
├── yolov5/                 # Framework YOLOv5
├── run_app.py              # Point d'entrée
├── requirements.txt        # Dépendances
└── .env.example            # Configuration exemple
```

## 🔌 API Endpoints

### Détection

**POST** `/api/detect`
- Upload une image pour détection
- Retourne: détections, statistiques, ID de détection

**GET** `/api/detections`
- Récupère les détections récentes
- Paramètres: `limit=50&offset=0`

**GET** `/api/detection/<id>`
- Récupère une détection spécifique

### Alertes

**GET** `/api/alerts`
- Récupère les alertes non résolues
- Paramètres: `limit=50&resolved=false`

### Statistiques

**GET** `/api/stats`
- Récupère les statistiques globales (dernières 24h)

**GET** `/api/health`
- Vérifier l'état de l'application

## 🔗 Liens entre modules

- `config.py` → Configuration centralisée utilisée par tous les modules
- `main_new.py` → Crée l'app Flask et enregistre les routes
- `routes_api.py` → Endpoints API utilisant `detection.py` et `database.py`
- `detection.py` → Utilise `constants.py` et `logger.py`
- `database.py` → Modèles SQLAlchemy pour tous les modules

## 📝 Fichiers créés/modifiés

✅ `constants.py` - Énumérations et constantes
✅ `logger.py` - Logging centralisé
✅ `utils.py` - Fonctions utilitaires
✅ `database_new.py` - Modèles améliorés
✅ `routes_api.py` - API endpoints
✅ `main_new.py` - Application Flask restructurée
✅ `run_app.py` - Lanceur d'application
✅ `.env.example` - Configuration exemple

## 🐛 Dépannage

**Problème: Modèle non trouvé**
```bash
# Entraîner d'abord le modèle
python train.py --epochs 50 --batch-size 8
```

**Problème: Port déjà utilisé**
```bash
# Utiliser un autre port
python run_app.py dev --port 5001
```

**Problème: CUDA non disponible**
```bash
# Utiliser CPU (plus lent)
# Vérifier config.py pour voir si GPU est détecté
```

## 📧 Contact & Support

Pour les questions ou issues, consultez la documentation ou contactez l'équipe de développement.

vpython train.py                       
======================================================================
🧠 ENTRAÎNEMENT MODÈLE DE DÉTECTION EPI
======================================================================
Vérification de la structure du dataset...

📊 Statistiques du dataset:
  - Images d'entraînement: 132
  - Images de validation: 132
  - Labels d'entraînement: 128
  - Labels de validation: 128
⚠️  Attention: mismatch images/labels
✓ Fichier data.yaml créé: dataset\data.yaml

📄 Contenu de data.yaml:
----------------------------------------
# Dataset EPI Detection
path: D:\projet\EPI-DETECTION-PROJECT\dataset
train: images/train
val: images/val
test: images/test

# Number of classes
nc: 6

# Class names
names: ['helmet', 'vest', 'glasses', 'person', 'boots', 'class_5']

----------------------------------------
✓ YOLOv5 trouvé localement

============================================================
🚀 DÉMARRAGE DE L'ENTRAÎNEMENT YOLOv5
============================================================
📋 Configuration:
  - Modèle: yolov5s.pt
  - Dataset: dataset\data.yaml
  - Epochs: 100
  - Batch size: 16
  - Image size: 640
  - Device: cpu

⏳ Entraînement en cours (voir runs/train/)
train: weights=yolov5s.pt, cfg=, data=dataset\data.yaml, hyp=yolov5\data\hyps\hyp.scratch-low.yaml, epochs=100, batch_size=16, imgsz=640, rect=False, resume=False, nosave=False, noval=False, noautoanchor=False, noplots=False, evolve=None, evolve_population=yolov5\data\hyps, resume_evolve=None, bucket=, cache=None, image_weights=False, device=cpu, multi_scale=False, single_cls=False, optimizer=SGD, sync_bn=False, workers=8, project=runs/train, name=epi_detection_v1, exist_ok=True, quad=False, cos_lr=False, label_smoothing=0.0, patience=100, freeze=[0], save_period=-1, seed=0, local_rank=-1, entity=None, upload_dataset=False, bbox_interval=-1, artifact_alias=latest, ndjson_console=False, ndjson_file=False        
github: skipping check (offline), for updates see https://github.com/ultralytics/yolov5
YOLOv5  v7.0-450-g781b9d57 Python-3.13.7 torch-2.9.1+cpu CPU

hyperparameters: lr0=0.01, lrf=0.01, momentum=0.937, weight_decay=0.0005, warmup_epochs=3.0, warmup_momentum=0.8, warmup_bias_lr=0.1, box=0.05, cls=0.5, cls_pw=1.0, obj=1.0, obj_pw=1.0, iou_t=0.2, anchor_t=4.0, fl_gamma=0.0, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, degrees=0.0, translate=0.1, scale=0.5, shear=0.0, perspective=0.0, flipud=0.0, fliplr=0.5, mosaic=1.0, mixup=0.0, copy_paste=0.0
Comet: run 'pip install comet_ml' to automatically track and visualize YOLOv5  runs in Comet
TensorBoard: Start with 'tensorboard --logdir runs\train', view at http://localhost:6006/
Overriding model.yaml nc=80 with nc=6

                 from  n    params  module                                  arguments
  0                -1  1      3520  models.common.Conv                      [3, 32, 6, 2, 2]
  1                -1  1     18560  models.common.Conv                      [32, 64, 3, 2]
  2                -1  1     18816  models.common.C3                        [64, 64, 1]
  3                -1  1     73984  models.common.Conv                      [64, 128, 3, 2]
  4                -1  2    115712  models.common.C3                        [128, 128, 2]
  5                -1  1    295424  models.common.Conv                      [128, 256, 3, 2]
  6                -1  3    625152  models.common.C3                        [256, 256, 3]
  7                -1  1   1180672  models.common.Conv                      [256, 512, 3, 2]
  8                -1  1   1182720  models.common.C3                        [512, 512, 1]
  9                -1  1    656896  models.common.SPPF                      [512, 512, 5]
 10                -1  1    131584  models.common.Conv                      [512, 256, 1, 1]
 11                -1  1         0  torch.nn.modules.upsampling.Upsample    [None, 2, 'nearest']
 12           [-1, 6]  1         0  models.common.Concat                    [1] 

 13                -1  1    361984  models.common.C3                        [512, 256, 1, False]
 14                -1  1     33024  models.common.Conv                      [256, 128, 1, 1]
 15                -1  1         0  torch.nn.modules.upsampling.Upsample    [None, 2, 'nearest']
 16           [-1, 4]  1         0  models.common.Concat                    [1] 

 17                -1  1     90880  models.common.C3                        [256, 128, 1, False]
 18                -1  1    147712  models.common.Conv                      [128, 128, 3, 2]
 19          [-1, 14]  1         0  models.common.Concat                    [1] 

 20                -1  1    296448  models.common.C3                        [256, 256, 1, False]
 21                -1  1    590336  models.common.Conv                      [256, 256, 3, 2]
 22          [-1, 10]  1         0  models.common.Concat                    [1] 

 23                -1  1   1182720  models.common.C3                        [512, 512, 1, False]
 24      [17, 20, 23]  1     29667  models.yolo.Detect                      [6, [[10, 13, 16, 30, 33, 23], [30, 61, 62, 45, 59, 119], [116, 90, 156, 198, 373, 326]], [128, 256, 512]]
Model summary: 214 layers, 7035811 parameters, 7035811 gradients, 16.0 GFLOPs

Transferred 343/349 items from yolov5s.pt
optimizer: SGD(lr=0.01) with parameter groups 57 weight(decay=0.0), 60 weight(decay=0.0005), 60 bias
train: Scanning D:\projet\EPI-DETECTION-PROJECT\dataset\labels\train.cache... 1
val: Scanning D:\projet\EPI-DETECTION-PROJECT\dataset\labels\val.cache... 128 i

AutoAnchor: 4.09 anchors/target, 1.000 Best Possible Recall (BPR). Current anchors are a good fit to dataset
Plotting labels to runs\train\epi_detection_v1\labels.jpg... 
D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:362: FutureWarning: `torch.cuda.amp.GradScaler(args...)` is deprecated. Please use `torch.amp.GradScaler('cuda', args...)` instead.
  scaler = torch.cuda.amp.GradScaler(enabled=amp)
Image sizes 640 train, 640 val
Using 4 dataloader workers
Logging results to runs\train\epi_detection_v1
Starting training for 100 epochs...

      Epoch    GPU_mem   box_loss   obj_loss   cls_loss  Instances       Size   
  0%|          | 0/9 [00:00<?, ?it/s]D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
       0/99         0G     0.1193    0.03328    0.05356         47        640: D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
       0/99         0G      0.121    0.03318    0.05532         49        640: D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
       0/99         0G     0.1218     0.0322    0.05539         36        640: D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
       0/99         0G      0.121    0.03172    0.05652         36        640: D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
       0/99         0G      0.121    0.03138     0.0569         40        640: D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
       0/99         0G     0.1196    0.03147    0.05719         46        640: D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
       0/99         0G     0.1179    0.03166    0.05718         42        640: D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
       0/99         0G     0.1176    0.03179    0.05722         47        640: D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
       0/99         0G     0.1125    0.03164     0.0547          9        640: 
                 Class     Images  Instances          P          R      mAP50  WARNING  NMS time limit 2.100s exceeded
                 Class     Images  Instances          P          R      mAP50  WARNING  NMS time limit 2.100s exceeded
                 Class     Images  Instances          P          R      mAP50  WARNING  NMS time limit 2.100s exceeded
                 Class     Images  Instances          P          R      mAP50  
                   all        132        152    0.00239      0.544    0.00669    0.00153

      Epoch    GPU_mem   box_loss   obj_loss   cls_loss  Instances       Size   
  0%|          | 0/9 [00:00<?, ?it/s]D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
       1/99         0G     0.1066    0.03249    0.05822         43        640: D:\projet\EPI-DETECTION-PROJECT\yolov5\train.py:419: FutureWarning: `torch.cuda.amp.autocast(args...)` is deprecated. Please use `torch.amp.autocast('cuda', args...)` instead.
  with torch.cuda.amp.autocast(amp):
