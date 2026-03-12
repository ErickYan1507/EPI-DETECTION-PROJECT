# 📐 Diagrammes d'Architecture du Projet EPI-DETECTION

## Table des Matières
1. [Diagramme de Paquetage (Package)](#1-diagramme-de-paquetage)
2. [Architecture Matérielle](#2-architecture-matérielle)
3. [Architecture Logicielle](#3-architecture-logicielle)
4. [Diagrammes Complémentaires](#4-diagrammes-complémentaires)

---

## 1. Diagramme de Paquetage

### 📦 Vue Générale des Modules

```mermaid
graph TB
    subgraph "EPI-DETECTION-PROJECT"
        subgraph "PRESENTATION[Couche Présentation]"
            WEB[Templates Web]
            DASH[Unified Monitoring.html]
            ARDUINO_UI[Arduino Control Panel.html]
            UI_STATIC[Assets Statiques]
        end
        
        subgraph "APPLICATION[Couche Application/Métier]"
            FLASK[Flask Backend]
            API_ROUTES[API Routes]
            DETECT_ENGINE[Detection Engine]
            ARDUINO_INT[Arduino Integration]
            MODEL_MGR[Model Manager]
            DB_MGR[Database Manager]
        end
        
        subgraph "DATA[Couche Données]"
            MODELS[Modèles YOLOv5]
            DATASET[Dataset EPI]
            DATABASE[Base de Données]
            CACHE[Cache/Logs]
        end
        
        subgraph "DEVICES[Périphériques Physiques]"
            ARDUINO[Arduino TinkerCAD]
            SENSORS[Capteurs]
            LEDS[LEDs]
            BUZZER[Buzzer]
        end
    end
    
    DASH --> WEB
    ARDUINO_UI --> WEB
    UI_STATIC --> WEB
    WEB --> FLASK
    FLASK --> API_ROUTES
    API_ROUTES --> DETECT_ENGINE
    API_ROUTES --> ARDUINO_INT
    DETECT_ENGINE --> MODEL_MGR
    DETECT_ENGINE --> DB_MGR
    MODEL_MGR --> MODELS
    DETECT_ENGINE --> DATASET
    DB_MGR --> DATABASE
    FLASK --> CACHE
    ARDUINO_INT --> ARDUINO
    ARDUINO --> SENSORS
    ARDUINO --> LEDS
    ARDUINO --> BUZZER
    
    style PRESENTATION fill:#e1f5ff
    style APPLICATION fill:#fff3e0
    style DATA fill:#f3e5f5
    style DEVICES fill:#e8f5e9
```

### 📋 Interprétation du Diagramme de Paquetage

**Couche Présentation (Bleu):**
- **Templates Web:** Fichiers HTML (unified_monitoring.html, arduino_control_panel.html)
- **Assets Statiques:** CSS, JavaScript, images stockés dans le dossier `static/`
- **Rôle:** Interface utilisateur pour visualiser les détections et contrôler Arduino

**Couche Application/Métier (Orange):**
- **Flask Backend:** Serveur web Python avec framework Flask
- **API Routes:** Points d'accès REST pour les opérations
- **Detection Engine:** Moteur de détection utilisant YOLOv5
- **Arduino Integration:** Module de communication avec Arduino
- **Model Manager:** Gestion des modèles de ML (chargement, versioning)
- **Database Manager:** Gestion des opérations de base de données
- **Rôle:** Traitement métier, orchestration des services

**Couche Données (Violet):**
- **Modèles YOLOv5:** Fichiers .pt (best.pt, session_003-005.pt)
- **Dataset EPI:** Images d'entraînement et validation
- **Base de Données:** SQLite ou MySQL pour stocker les détections
- **Cache/Logs:** Fichiers log et cache temporaire
- **Rôle:** Persistance et stockage des données

**Périphériques Physiques (Vert):**
- **Arduino TinkerCAD:** Microcontrôleur simulé
- **Composants:** Capteurs de température/humidité, motion
- **Actuateurs:** LEDs (vert/rouge) et buzzer d'alerte
- **Rôle:** Retour physique et collecte de données environnementales

---

## 2. Architecture Matérielle

### 🔌 Schéma Complet du Système Matériel

```mermaid
graph TB
    subgraph "SENSORS[🎯 Capteurs - Entrées]"
        DHT22["🌡️ DHT22<br/>Pin D4<br/>Temp: -40°C à +80°C<br/>Humidité: 0-100%<br/>Freq: 2s"]
        PIR["👁️ Capteur PIR<br/>Pin D2<br/>Détecte Mouvement<br/>Portée: 5-7m<br/>Délai: 2-3s"]
        CAM["📷 Webcam USB<br/>Résolution: 1280x720<br/>Format: MJPEG/YUV"]
    end
    
    subgraph "ARDUINO_CORE[⚙️ Microcontrôleur Arduino UNO]"
        CPU["ATmega328P<br/>16 MHz - 2KB RAM<br/>32KB Flash"]
        GPIO["GPIO Pins<br/>D2, D4, D11, D12, D13"]
        UART["UART Serial<br/>9600 baud<br/>Format: 8N1"]
    end
    
    subgraph "OUTPUTS[🎬 Actuateurs - Sorties]"
        LED_G["🟢 LED Verte<br/>Pin D11<br/>2V forward<br/>20mA"]
        LED_R["🔴 LED Rouge<br/>Pin D12<br/>2V forward<br/>20mA"]
        BUZZ["🔊 Buzzer<br/>Pin D13<br/>2-5kHz<br/>30mA @ 5V"]
    end
    
    subgraph "COMM[🌐 Communication Série]"
        USB["🔗 USB/Serial Cable<br/>COM3<br/>Bidirectionnelle"]
    end
    
    subgraph "SERVER[💻 Serveur PC]"
        PYBACK["🐍 Backend Flask<br/>App.py<br/>Port: 5000"]
        MYDB["💾 Database<br/>SQLite/MySQL<br/>Détections & Capteurs"]
    end
    
    DHT22 -->|Données| GPIO
    PIR -->|Signal| GPIO
    CAM -->|Flux Vidéo| PYBACK
    
    GPIO -->|Traitement| CPU
    CPU -->|UART Serial| UART
    UART -->|USB 9600 baud| USB
    USB -->|Données Capteurs| PYBACK
    
    PYBACK -->|Conformité| USB
    USB -->|Commandes| UART
    UART -->|GPIO Contrôle| GPIO
    
    GPIO -->|Power| LED_G
    GPIO -->|Power| LED_R
    GPIO -->|Power| BUZZ
    
    PYBACK -->|Persistance| MYDB
    
    style SENSORS fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style ARDUINO_CORE fill:#fff3e0,stroke:#f57f17,stroke-width:2px
    style OUTPUTS fill:#ffebee,stroke:#c62828,stroke-width:2px
    style COMM fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    style SERVER fill:#e1f5ff,stroke:#0277bd,stroke-width:2px
```

### 📋 Détails Techniques

**Capteurs (Entrées):**
- DHT22: Température/Humidité via Pin D4 (I2C), lecture toutes les 2 secondes
- PIR: Détecteur mouvement Pin D2, signal HIGH lors détection, portée 5-7m
- Webcam USB: Flux vidéo direct au PC Python (1280x720 MJPEG)

**Microcontrôleur Arduino:**
- CPU: ATmega328P 16MHz avec 2KB RAM et 32KB Flash
- GPIO: 14 pins numériques + 6 pins analogiques
- Communication: UART Série 9600 baud via USB (CH340 ou FT232)
- Alimentation: USB 5V, courant moyen 40mA

**Actuateurs (Sorties):**
- LED Verte (Pin D11): Indique conformité ≥80% (SAFE)
- LED Rouge (Pin D12): Indique conformité <80% (WARNING/DANGER)
- Buzzer Piezo (Pin D13): Alerte sonore 2-5kHz quand danger détecté

**Communication Série:**
- Protocole: UART/Serial 9600 baud 8N1 (8 bits, pas de parité, 1 stop)
- Câble: USB vers Mini-B (Arduino) - COM3 typiquement
- Flux: Arduino → Python (capteurs), Python → Arduino (commandes)

**Serveur PC:**
- Backend Flask Python sur port 5000
- Base de données SQLite ou MySQL
- Reçoit images webcam, envoie conformité (C85), stocke historique

### 🎯 Interprétation de l'Architecture Matérielle

**Couche de Capteurs:**
- **DHT22:** Collecte température/humidité toutes les 2 secondes
- **Capteur PIR:** Détecte mouvements dans la zone surveillée
- **Webcam:** Capture flux vidéo pour détection EPI
- Tous les capteurs envoient leurs données à Arduino en continu

**Microcontrôleur Arduino:**
- **Rôle central:** Collecte des capteurs et contrôle des actuateurs
- **Communication:** Via UART sériel au PC (9600 baud)
- **Traitement local:** Temps réel pour réactivité immédiate
- **Pin mapping:** Configuration GPIO pour chaque capteur/actuateur

**Actuateurs:**
- **LEDs:** Signalisation visuelle (vert=sûr, rouge=danger)
- **Buzzer:** Alerte sonore en cas de non-conformité EPI
- Réagissent aux commandes du backend Python

**Flux Bidirectionnel:**
- Arduino → Python: Données de capteurs
- Python → Arduino: Commandes conformité et contrôle

---

## 3. Architecture Logicielle

### 🏗️ Architecture Complète en Couches

```mermaid
graph TB
    subgraph "TIER1[🌐 Tier 1: Présentation - Frontend]"
        USER["👤 Utilisateur"]
        BROWSER["🌐 Navigateur Web<br/>HTTP/WebSocket"]
        DASHBOARD["📊 Unified Monitoring<br/>Dashboard Principal"]
        PANEL["🎛️ Arduino Control Panel<br/>Contrôle Temps Réel"]
    end
    
    subgraph "TIER2[🐍 Tier 2: Application - Flask Backend]"
        MAIN["📌 Flask App<br/>app.py - Initialisation"]
        API["🔌 API Routes<br/>app/routes_*.py"]
        LOGIC["⚙️ Logique Métier<br/>Controllers & Services"]
    end
    
    subgraph "TIER3[⚡ Tier 3: Services Métier]"
        DETECT["🔍 Detection Service<br/>YOLOv5 Multi-Model<br/>+ NMS + Agrégation"]
        ARDUINO_SVC["🎛️ Arduino Service<br/>Serial Communication<br/>9600 baud UART"]
        DB_SVC["💾 Database Service<br/>SQLAlchemy ORM<br/>CRUD Operations"]
        MODEL_SVC["🤖 Model Management<br/>Load, Cache, Version<br/>GPU Acceleration"]
    end
    
    subgraph "TIER4[📦 Tier 4: Infrastructure - Données]"
        MODELS["📤 Modèles ML<br/>best.pt<br/>session_003-005.pt"]
        DATABASE["🗄️ Base de Données<br/>SQLite ou MySQL"]
        FILES["📁 Système Fichiers<br/>Dataset, Logs, Cache"]
        HARDWARE["🔌 Hardware Interface<br/>Serial Port COM3"]
    end
    
    USER -->|Interagit| BROWSER
    BROWSER -->|HTTP/WS| DASHBOARD
    BROWSER -->|HTTP/WS| PANEL
    
    DASHBOARD -->|Requêtes| API
    PANEL -->|Requêtes| API
    
    API -->|Reçoit| MAIN
    MAIN -->|Délègue| LOGIC
    
    LOGIC -->|Utilise| DETECT
    LOGIC -->|Utilise| ARDUINO_SVC
    LOGIC -->|Utilise| DB_SVC
    LOGIC -->|Utilise| MODEL_SVC
    
    DETECT -->|Charge| MODELS
    DETECT -->|Persiste| DATABASE
    
    DB_SVC -->|CRUD| DATABASE
    MODEL_SVC -->|Manage| MODELS
    ARDUINO_SVC -->|Serial| HARDWARE
    
    MODEL_SVC -->|Logs| FILES
    DETECT -->|Cache| FILES
    
    DASHBOARD -->|Affiche| USER
    PANEL -->|Affiche| USER
    
    style TIER1 fill:#e1f5ff,stroke:#0277bd,stroke-width:3px
    style TIER2 fill:#fff3e0,stroke:#f57f17,stroke-width:3px
    style TIER3 fill:#f3e5f5,stroke:#6a1b9a,stroke-width:3px
    style TIER4 fill:#e8f5e9,stroke:#00695c,stroke-width:3px
```

### 📋 Couches et Responsabilités

**Tier 1 - Présentation (Interface Utilisateur):**
- **Dashboard Principal:** Affichage temps réel détections YOLOv5, historique
- **Panel Arduino:** Visualisation capteurs (temp/humidité/mouvement), contrôle LEDs/Buzzer
- **Navigateur:** HTTP/WebSocket pour communication asynchrone
- **Rôle:** Présenter données et recevoir commandes utilisateur

**Tier 2 - Application (Flask Backend):**
- **Main App:** Point d'entrée, initialisation Flask, enregistrement routes
- **API Routes:** Points d'accès REST (/api/detect, /api/arduino/*, /api/stats/*)
- **Logique Métier:** Orchestration entre services, validation données, gestion workflow
- **Rôle:** Recevoir requêtes frontend, coordonner services, retourner résultats

**Tier 3 - Services (Logique Métier Spécialisée):**
- **Detection Service:** YOLOv5 inference multi-modèles, NMS, calcul conformité EPI
- **Arduino Service:** Gestion connexion sérielle, parsing données capteurs, envoi commandes
- **Database Service:** Opérations CRUD via SQLAlchemy, transactions
- **Model Management:** Chargement/déchargement modèles, cache, versioning
- **Rôle:** Implémenter logique spécialisée pour chaque domaine

**Tier 4 - Infrastructure (Ressources Externes):**
- **Modèles ML:** Fichiers .pt pré-entraînés (best.pt, session_*.pt)
- **Base de Données:** SQLite ou MySQL, tables détections/capteurs/modèles
- **Système Fichiers:** Dataset images, logs, cache temporaire
- **Interface Matériel:** Accès serial port COM3 pour Arduino
- **Rôle:** Fournir ressources et persistance aux services

### 🔄 Flux d'Exécution: Détection d'EPI

```
1. User → Upload image
      ↓
2. Frontend → POST /api/detect (image binary)
      ↓
3. Flask → Réception & prétraitement
      ↓
4. Detection Service → YOLOv5 inference (4 modèles)
      ↓
5. NMS & Agrégation → Union/Weighted voting
      ↓
6. Classification → Helmet/Vest/Glasses/Boots/Person
      ↓
7. Calcul Conformité → Score % et état (SAFE/WARNING/DANGER)
      ↓
8. DB Service → Sauvegarde détections en BD
      ↓
9. Arduino Service → Envoi conformité à Arduino (C85)
      ↓
10. Arduino → Activation LED verte/rouge + Buzzer si danger
      ↓
11. Flask → Retour JSON (detections, confidence, conformity)
      ↓
12. Frontend → Affichage results, visualisation dashboard
      ↓
13. User → Voir résultats avec bounding boxes colorées
```

### 🎯 Interprétation de l'Architecture Logicielle

---

## 4. Diagrammes Complémentaires

### 🔄 Protocole de Communication Arduino-Python

```mermaid
stateDiagram-v2
    [*] --> DISCONNECTED: Initial State
    
    DISCONNECTED --> CONNECTING: User Click "Connect"
    CONNECTING --> CONNECTED: Port Trouvé & Ouvert
    CONNECTING --> DISCONNECTED: Port Non Trouvé
    
    CONNECTED --> MONITORING: Setup Arduino Réussi
    
    MONITORING --> MONITORING: Arduino envoie [SENSOR]
    MONITORING --> MONITORING: Python reçoit temp/humidity
    MONITORING --> MONITORING: Python traite YOLOv5
    MONITORING --> MONITORING: Python envoie C85
    MONITORING --> MONITORING: Arduino active LED/Buzzer
    
    MONITORING --> DISCONNECTING: User Click "Disconnect"
    DISCONNECTING --> DISCONNECTED: Port Fermé
    
    CONNECTED --> ERROR: Erreur Serial/Timeout
    ERROR --> DISCONNECTED: Reset & Retry
```

### 📊 Classification et Conformité EPI

```mermaid
graph TD
    IMG["📷 Image"]
    
    IMG --> YOLO["🤖 YOLOv5 Detection"]
    
    YOLO --> HELMET{Casque<br/>Détecté?}
    YOLO --> VEST{Gilet<br/>Détecté?}
    YOLO --> GLASSES{Lunettes<br/>Détectées?}
    
    HELMET -->|✓ OUI| H_OK["Helmet ✓"]
    HELMET -->|✗ NON| H_FAIL["Helmet ✗"]
    
    VEST -->|✓ OUI| V_OK["Vest ✓"]
    VEST -->|✗ NON| V_FAIL["Vest ✗"]
    
    GLASSES -->|✓ OUI| G_OK["Glasses ✓"]
    GLASSES -->|✗ NON| G_FAIL["Glasses ✗"]
    
    H_OK --> CALC["Score = (Items_Présents/3) × 100"]
    H_FAIL --> CALC
    V_OK --> CALC
    V_FAIL --> CALC
    G_OK --> CALC
    G_FAIL --> CALC
    
    CALC --> SCORE["Score %"]
    
    SCORE --> CHECK{Score ≥ 80%?}
    
    CHECK -->|✅ OUI| SAFE["🟢 SAFE<br/>LED Verte"]
    CHECK -->|⚠️ 60-79%| WARNING["🟡 WARNING<br/>LED Rouge"]
    CHECK -->|❌ <60%| DANGER["🔴 DANGER<br/>LED + Buzzer"]
    
    SAFE --> SEND["Envoyer à Arduino"]
    WARNING --> SEND
    DANGER --> SEND
    
    style SAFE fill:#c8e6c9
    style WARNING fill:#fff9c4
    style DANGER fill:#ffcdd2
    style YOLO fill:#f3e5f5
    style SEND fill:#e1f5ff
```

### 🔐 Sécurité et Persistance des Données

```mermaid
graph LR
    USER["👤 User"]
    
    USER -->|1. Upload| APP["Flask API"]
    APP -->|2. Validate| AUTH["Authentification<br/>JWT Token"]
    AUTH -->|3. OK| PROCESS["Traitement<br/>YOLOv5"]
    AUTH -->|✗ FAIL| REJECT["Rejeté"]
    
    PROCESS -->|4. Save| DB["Base de Données<br/>Detection_results"]
    DB -->|5. Log| LOGS["Logs Files<br/>audit.log"]
    PROCESS -->|6. Cache| CACHE["Cache<br/>Recent results"]
    
    CACHE -->|7. Return| APP
    APP -->|8. Response| USER
    
    style AUTH fill:#f3e5f5
    style DB fill:#e8f5e9
    style LOGS fill:#fff3e0
    style CACHE fill:#ffebee
```

### ⚡ Performance et Optimisations

```mermaid
graph TB
    INPUT["Image Input"]
    
    INPUT --> PREPROCESS["Prétraitement<br/>Resize 640×640"]
    PREPROCESS --> MODELS["Multi-Model Ensemble<br/>• best.pt<br/>• session_003.pt<br/>• session_004.pt<br/>• session_005.pt"]
    MODELS --> NMS["NMS Filtering<br/>IOU Threshold: 0.65<br/>Confidence: 0.2"]
    NMS --> AGGREGATE["Agrégation Résultats<br/>Weighted Voting"]
    AGGREGATE --> CLASSIFY["Classification EPI<br/>5 classes"]
    CLASSIFY --> CALC["Calcul Conformité"]
    CALC --> OUTPUT["📤 Résultats"]
    
    OUTPUT --> STAT1["Temps GPU: ~200ms"]
    OUTPUT --> STAT2["Temps CPU: ~1500ms"]
    OUTPUT --> STAT3["Throughput: 5 img/s"]
    
    style INPUT fill:#e1f5ff
    style PREPROCESS fill:#fff3e0
    style MODELS fill:#f3e5f5
    style NMS fill:#e8f5e9
    style AGGREGATE fill:#fff9c4
    style CLASSIFY fill:#ffebee
    style CALC fill:#f1f8e9
    style OUTPUT fill:#e0f2f1
    style STAT1 fill:#c8e6c9
    style STAT2 fill:#ffcdd2
    style STAT3 fill:#ffecb3
```

---

## 📝 Résumé Complet des Architectures

### 🔌 Architecture Matérielle - Points Clés
✅ **Capteurs:** DHT22 (temp/humidité), PIR (mouvement), Webcam USB  
✅ **Microcontrôleur:** Arduino UNO ATmega328P 16MHz  
✅ **Actuateurs:** LEDs (vert/rouge), Buzzer piezo  
✅ **Communication:** UART Série 9600 baud via USB COM3  
✅ **Flux:** Bidirectionnel capteurs → Arduino → PC, PC → Arduino → Actuateurs  

**Rôle:** Collecte de données environnementales et retour physique (visuel/sonore)

---

### 🏗️ Architecture Logicielle - Points Clés
✅ **Tier 1 - Présentation:** Dashboard web + Control Panel Arduino  
✅ **Tier 2 - Application:** Flask + Routes API REST  
✅ **Tier 3 - Services:** Detection (YOLOv5), Arduino (Serial), Database (SQLAlchemy), Model Manager  
✅ **Tier 4 - Infrastructure:** Modèles ML, Base de données, Fichiers, Hardware  
✅ **Flux:** User → Frontend → API → Services → Infrastructure → Response  

**Rôle:** Orchestration des détections, persistance et retour physique

---

### 📦 Diagramme de Paquetage - Points Clés
✅ **Couche Présentation:** Templates HTML, Assets CSS/JS  
✅ **Couche Application:** Flask, Routes, Logique Métier  
✅ **Couche Données:** Modèles YOLOv5, Dataset, BD, Logs  
✅ **Périphériques:** Arduino + Capteurs/Actuateurs  
✅ **Interdépendances:** Bien structurées par couches  

**Rôle:** Vue modulaire et organisée du système complet

---

### 🎯 Cas d'Usage Principaux

#### 1️⃣ **Détection d'EPI (Cas Nominal)**
```
Utilisateur Upload Image
        ↓
Flask reçoit POST /api/detect
        ↓
YOLOv5 détecte EPI (Helmet, Vest, Glasses)
        ↓
Calcul conformité (score %)
        ↓
Sauvegarde en BD
        ↓
Envoi conformité à Arduino (C85)
        ↓
Arduino active LEDs/Buzzer
        ↓
Frontend affiche résultats
        ↓
User voit bounding boxes colorées + score
```

#### 2️⃣ **Monitoring Arduino Temps Réel**
```
Arduino DHT22 lit temp/humidité
        ↓
Arduino PIR détecte mouvement
        ↓
Arduino envoie [SENSOR] temp=25.5,humidity=60
        ↓
Python reçoit via Serial
        ↓
Sauvegarde en BD
        ↓
Frontend met à jour dashboard
        ↓
User voit capteurs en temps réel
```

#### 3️⃣ **Alerte Conformité**
```
Score conformité < 60%
        ↓
Status: DANGER
        ↓
Python envoie C20 (20% conformité)
        ↓
Arduino active LED rouge
        ↓
Arduino active Buzzer 2kHz
        ↓
User entend alerte sonore
```

---

## 🔗 Relations entre Architectures

```
                    ┌─────────────────────────────────┐
                    │   Architecture Matérielle       │
                    │  (Capteurs → Arduino ↔ PC)     │
                    └──────────────┬──────────────────┘
                                   │ Serial Port COM3
                                   ↓
        ┌──────────────────────────────────────────────────────┐
        │       Architecture Logicielle (Tiers 1-4)            │
        │  ┌───────────────┐  ┌──────────────────────────┐    │
        │  │   Frontend    │  │  Détection YOLOv5 +      │    │
        │  │  Dashboard    │  │  Arduino Integration +    │    │
        │  │  Arduino Panel│  │  Database Management     │    │
        │  └───────────────┘  └──────────────────────────┘    │
        └──────────────────────────────────────────────────────┘
                                   ↓
        ┌──────────────────────────────────────────────────────┐
        │       Diagramme de Paquetage                         │
        │  (Organisation logique de tous les modules)          │
        │  • Présentation | Application | Données | Devices   │
        └──────────────────────────────────────────────────────┘
```

---

## 📊 Tableau Récapitulatif Complet

| Aspect | Détails |
|--------|---------|
| **Microcontrôleur** | Arduino UNO ATmega328P, 16MHz, 2KB RAM |
| **Capteurs** | DHT22 (I2C), PIR (GPIO D2), Webcam USB |
| **Actuateurs** | LED Verte (D11), LED Rouge (D12), Buzzer (D13) |
| **Communication** | UART 9600 baud 8N1 via USB COM3 |
| **Backend** | Python Flask port 5000 |
| **Modèles** | YOLOv5 best.pt + 3 sessions, GPU-enabled |
| **Base de Données** | SQLite par défaut, MySQL optionnel |
| **Frontend** | HTML5 Dashboard + Control Panel |
| **Classes EPI** | Helmet, Vest, Glasses, Boots, Person |
| **Conformité** | Score % : ≥80% SAFE, 60-79% WARNING, <60% DANGER |
| **Temps Inference** | ~200ms GPU / ~1500ms CPU par image |
| **Throughput** | 5 img/s GPU / 0.67 img/s CPU |

---
