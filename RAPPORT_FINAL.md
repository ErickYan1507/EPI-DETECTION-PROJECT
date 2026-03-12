# 🚀 Rapport Final du Projet EPI Detection System

**Date :** 27 février 2026
**Nom du projet :** EPI-DETECTION-PROJECT
**Auteur :** Analyse automatisée

---

## 🧩 1. Introduction

Le projet **EPI Detection System** a pour objectif de surveiller le port des équipements de
protection individuelle (EPI) sur des personnes en temps réel, grâce à l'intelligence artificielle
et à un ensemble de technologies web et matérielles. Cette application est destinée à améliorer
la sécurité sur les chantiers et dans les usines en détectant automatiquement les casques, gilets,
lunettes et bottes.

Le présent rapport synthétise l'analyse complète du code, de l'architecture, des performances,
de la configuration, des modules, du déploiement et des résultats obtenus.

---

## 📐 2. Architecture Système

### 2.1 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EPI DETECTION SYSTEM ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │         FRONTEND LAYER (Web Interface)                      │    │
│  │  ┌──────────────┐  ┌─────────────────┐  ┌──────────────┐   │    │
│  │  │   Dashboard  │  │  Real-time UI   │  │  Statistiques│   │    │
│  │  │   (HTML/JS)  │  │  (WebSockets)   │  │  (Graphiques)│   │    │
│  │  └──────────────┘  └─────────────────┘  └──────────────┘   │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                 │                   │
│                                                 │                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │         API LAYER (REST + WebSocket)                        │    │
│  │  Flask SocketIO - Endpoints: /api/detect, /api/stats, etc  │    │
│  └────────────────────────────────────────────────────────────┘    │
│                         │          │          │                     │
│                         ▼          ▼          ▼                     │
│  ┌────────────────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐      │
│  │ Detection Core │ │ Alerts │ │Notif.Mgr │ │ Arduino IoT  │      │
│  │  (EPIDetector) │ │Manager │ │ (Email)  │ │ Integration  │      │
│  └────────────────┘ └────────┘ └──────────┘ └──────────────┘      │
│           │                                                         │
│  ┌────────▼────────────────────────────────────────────────┐       │
│  │         MODEL INFERENCE LAYER                           │       │
│  │  ┌──────────────┐  ┌─────────────────┐  ┌────────────┐ │       │
│  │  │ YOLOv5 Model │  │ Multi-Model Ens │ │ Hardware   │ │       │
│  │  │ (PyTorch)    │  │ (Weighted Vote) │ │ Accel.     │ │       │
│  │  │              │  │ (NMS Fusion)    │ │ (OpenVINO) │ │       │
│  │  └──────────────┘  └─────────────────┘ └────────────┘ │       │
│  └────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌────────────────────────────────────────────────────────┐       │
│  │         DATA PERSISTENCE LAYER                          │       │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐   │       │
│  │  │ SQLite/MySQL│  │ Training Logs│  │  Exports    │   │       │
│  │  │   Unified   │  │   (Database) │  │  (PDF/BI)   │   │       │
│  │  │   Database  │  │              │  │             │   │       │
│  │  └─────────────┘  └──────────────┘  └─────────────┘   │       │
│  └────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌────────────────────────────────────────────────────────┐       │
│  │         HARDWARE & SENSORS LAYER                        │       │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────────┐   │       │
│  │  │ Webcam   │  │ Arduino  │  │ IoT Sensors (Temp) │   │       │
│  │  │ (OpenCV) │  │ Serial   │  │ (TinkerCad Sim)    │   │       │
│  │  └──────────┘  └──────────┘  └────────────────────┘   │       │
│  └────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Stack Technologique

| Composant | Technologie | Rôle principal |
|-----------|-------------|----------------|
| Backend | Flask 2.3 | API REST et WebSocket |
| Detection | YOLOv5 PyTorch | Modèle IA principal |
| Accélération | OpenVINO | Inférence hardware |
| Base de données | SQLite/MySQL | Persistence unifiée |
| Frontend | HTML/JS, Chart.js | Dashboard temps réel |
| Communication | SocketIO | WebSocket live updates |
| Conteneurs | Docker | Déploiement production |
| Arduino | Serial | Alarmes, capteurs |
| Export | ReportLab/PowerBI | Rapports, BI |

### 2.3 Classes de Détection

- **helmet** (casque)
- **glasses** (lunettes)
- **person** (personne)
- **vest** (gilet)
- **boots** (bottes)

La conformité est validée si une personne porte au moins 3 des 4 EPI requis.

---

## 📂 3. Organisation du Code & Modules

Le dépôt héberge plus de 250 scripts Python et une documentation détaillée. Les principaux dossiers et fichiers sont :

- `app/` : application Flask (routes, services, modèles)
- `models/` : poids de modèles (`best.pt`, sessions supplémentaires)
- `dataset/` : images d'entraînement et annotations
- `documentation/` : analyses, guides et diagrammes (ANALYSE_COMPLETE_PROJET.md,
  CHAPITRE_6_CONCEPTION_DETAILLEE.md, etc.)
- `static/` & `templates/` : fichiers frontend
- utilitaires (diagnose_*.py, fix_*.py, analyze_*.py) pour diagnostic et maintenance

Le fichiers principaux incluent `cli.py`, `config.py` et `run_app.py` qui orchestrent
toutes les fonctionnalités.

---

## 🧠 4. Pipeline de Détection

1. **Capture** : webcam ou image envoyée via API.
2. **Pré-traitement** : redimensionnement (320×240), normalisation.
3. **Inférence** : PyTorch/YOLOv5 (option OpenVINO pour accélération).
4. **Multi-modèles** : ensemble pondéré de 4 poids, fusion NMS.
5. **Post-traitement** : classification conformité + création d'alertes.
6. **Stockage** : enregistrement dans base SQLite/MySQL.
7. **Notifications** : envoi mail, commande Arduino, mise à jour WebSocket.

Les paramètres (seuils, chemins, toggles) se trouvent dans `config.py`.

---

## 🔍 5. Interfaces utilisateur et services clés

### 5.1 Unified Monitoring

La page `unified_monitoring.html` constitue le **dashboard central** du système. Elle combine
le flux vidéo de la caméra, les statistiques en temps réel, et les contrôles Arduino/IoT.

- **Structure** : HTML5/CSS3 responsive, tableaux DataTables, graphiques Chart.js.
- **Fonctionnalités** : affichage de la webcam (`<video>`), overlay canvas pour dessins de
  boîtes de détection, indicateurs de statut (online/offline), alertes et log en direct.
- **Composants JavaScript** :
  - boucle de capture 30 FPS envoyant des images base64 à `/api/detect`.
  - WebSocket pour recevoir les notifications immédiates.
  - Widgets de configuration Arduino et gestion des modèles.

Un script `diagnose_unified_monitoring.py` est fourni pour vérifier que le dashboard se charge
correctement et que les dépendances (Canvas, WebSocket, Flask) sont opérationnelles.

### 5.2 Admin Panel

Accessible après authentification via `/admin/login`, l'**espace administrateur** offre un CRUD
générique sur toutes les tables unifiées (détections, alertes, travailleurs, etc.).

- **Interface** : `templates/admin_panel.html` utilise un shell divisé sidebar/main avec
  navigation par table, export Excel, filtres datés et modal de saisie.
- **Authentification** : mot de passe hashé (`werkzeug.security`) stocké dans la table
  `AdminUser`; un admin par défaut est créé si la table est vide (`Admin@1234`).
- **Routes** : regroupées dans `app/routes_admin.py` sous le blueprint `admin_bp`.
  Le module gère la sérialisation SQLAlchemy, l'analyse de types et les opérations
  date/filtre/export.
- **Fonctions avancées** : section "Présence Quotidienne" (CRUD d'enregistrements d'assiduité),
  génération de rapports, déconnexion sécurisée.

La présence de l'admin panel répond à la problématique de gestion et de supervision
des données sans accès direct à la base. Son design reflète le canevas de projet
(problématique, solution, critique). Une limitation notée est la sécurité (absence de
période d'expiration de session et protections CSRF). Des améliorations futures incluent
la gestion des rôles et l'intégration d'OTP.

### 5.3 Système de notifications

Le moteur de notification est implémenté dans `app/notifications_manager_sqlalchemy.py`.
Il permet :

1. **Configuration SMTP** via un modèle `NotificationConfig` (utilise TLS, SMTP port dynamique).
2. **Gestion des destinataires** (`NotificationRecipient`) avec validation et activation.
3. **Historique** (`NotificationHistory`) stockant chaque envoi, statut et erreur.
4. **Planification** des rapports (`ReportSchedule`) avec supports daily/weekly/monthly.

La classe `NotificationsManagerSQLAlchemy` remplace l'ancien gestionnaire basique et
s'intègre pleinement à la base unifiée. Elle offre des méthodes pour ajouter/supprimer
membres, envoyer des emails (HTML+texte), tester la configuration, et exporter les logs.

Un guide (`NOTIFICATIONS_SQLALCHEMY_GUIDE.txt`) accompagne la migration depuis
`notifications.db`. Des tests (`test_notifications_sqlalchemy.py`) validant chaque
fonctionnalité sont inclus.

Ce service répond à la problématique des alertes fiables et archivées. Un point d'effort
est la gestion des erreurs SMTP et la rotation des mots de passe — le système plafonne
actuellement à un seul expéditeur actif.

---

## 🛠 5. Configuration & Installation

- **Environnement Python** : `.venv` avec requirements extraits via `pip install -r requirements.txt`.
- **Base de données** : choix `sqlite` ou `mysql` via variable d'environnement `DB_TYPE`.
- **Modèles** : placez `best.pt` dans `models/`; autres modèles sont facultatifs.
- **Démarrage** : `python run_app.py` ou via tâche VS Code "Lancer Flask".
- **Docker** : `docker build -t epi-detection .` et `docker-compose up -d`.

Des guides détaillés existent (`CHECKLIST_DEPLOYMENT_FINAL.md`, `INTEGRATION_SQLALCHEMY_GUIDE.txt`).

---

## 💾 6. Base de Données & Persistance

La structure unify les tables suivantes :

- `detections` (id, timestamp, classe, bbox, confidence, compliant)
- `alerts` (detection_id, type, sent)
- `stats` (daily counts, mAP history)

L'accès est géré via SQLAlchemy; la migration/initialisation est automatisée dans
`init_database_mysql.py`, `ensure_mysql_schema.py`.

---

## 📈 7. Performances & Résultats

Analyse du modèle `best.pt` :

| Métrique | Valeur |
|----------|--------|
| mAP@0.5 | 0.8804 |
| Précision globale | 0.8950 |
| Rappel global | 0.8620 |

Performance par classe :

| Classe | mAP@0.5 |
|--------|---------|
| Personne | 0.952 |
| Casque | 0.920 |
| Gilet | 0.905 |
| Bottes | 0.865 |
| Lunettes | 0.760 |

**Observations** : Les petits objets (lunettes) méritent plus de données ou une
résolution d'entrée plus élevée. Le système atteint 20‑30 FPS sur matériel standard ;
OpenVINO améliore le throughput de ~30 %.

---

## 🔧 8. Tests & Diagnostics

Le dépôt contient des scripts pour vérifier l'intégrité :

- `check_*` pour l'infrastructure, les classes, la base de données
- `diagnose_*` pour le module, la performance, le stockage
- `fix_*` pour corriger les datasets ou la DB
- `generate_test_detections.py` pour produire des détections synthétiques

Une suite de commandes CLI (`cli.py`) automatisent l'analyse et la génération de rapports.

---

## 📡 9. Intégration Matérielle & Extérieure

- **Arduino** : simulation via TinkerCad avec communication série (9600 baud).
  Permet de piloter une alarme en cas de non-conformité.
- **IoT/Capteurs** : fichiers d'exemple gèrent MQTT/HTTP pour capteurs de température.
- **Export** : ReportLab génère des PDF; des scripts alimentent PowerBI pour visualisation.

---

## 📦 10. Déploiement et Containerisation

Dockerfile et docker-compose.yml prennent en charge :

- Création de l'image avec Python et dépendances
- Montage des volumes pour modèles, logs et base de données
- Exposition du port 5000

Le guide `CHECKLIST_DEPLOYMENT_FINAL.md` recense les étapes de mise en production.

---

## ✅ 11. Évaluation et Perspectives

### Points forts

- Architecture modulaire et extensible
- Bonne performance générale (mAP élevée)
- Richesse des diagnostics et scripts de réparation
- Support multi-modèles et accélération matérielle

### Limites

- Détection lente des petits objets (lunettes)
- Interface dashboard simple, peut être améliorée
- Besoin de plus de tests unitaires et d'intégration automatisés

### Perspectives

1. Entraîner un modèle spécifique pour lunettes ou augmenter la résolution d'entrée.
2. Ajouter un service de notification SMS/Slack.
3. Automatiser le déploiement via CI/CD (GitHub Actions).
4. Renforcer la couverture de tests et la surveillance de performance.

---

## 📎 12. Annexes

- `documentation/` contient des diagrammes UML, cahier des charges et chapitres détaillés.
- `00_START_HERE_FR.txt` et `GETTING_STARTED.txt` pour prise en main rapide.

---

## 📌 13. Analyse des templates pour nouvelles fonctionnalités

Le dossier `templates/` regroupe toutes les vues Jinja2 servies par Flask. Ils
utilisent un squelette commun (`base.html`) et des blocs configurables. Une
relecture des fichiers révèle les éléments suivants :

1. **`base.html`** : structure globale, chargement des bibliothèques (Bootstrap,
   FontAwesome, Chart.js, Socket.IO) et feuille de style personnalisée. Il
   intègre un sélecteur de thème (mode sombre/clair) et une barre de
   navigation responsive. Pour toute nouvelle fonctionnalité, créer un fichier
   étendu/de-plugin utilisant les blocs `title`, `head_extra`, `body_extra` et
   `scripts` facilite l'injection de CSS/JS spécifiques.

2. **Dashboard et monitoring** :
   - `dashboard.html`, `unified_monitoring.html`, `realtime.html` et
     `camera.html` affichent des flux vidéo, canvas de superposition et
     contrôles en temps réel. Ces pages contiennent du JavaScript émettant
     périodiquement des images vers `/api/detect` et ouvrant un socket pour
     recevoir des alertes. Les sections `{{ config }}` ou `{{ socket_url }}`
     montrent comment passer des paramètres dynamiques.
   - **Extension** : ajouter une page de **"paramètres de détection"** ou de **"historique vidéo"** exploite le même squelette et la connexion socket ; le script peut réutiliser `socket.on('alert', …)` et enrichir les formulaires avec de nouveaux champs.

3. **Formulaires et upload** :
   - `upload.html` et `training_results.html` montrent le traitement de fichiers (image ou logs) via `<form enctype="multipart/form-data">`. Ils servent de canevas pour de futures fonctionnalités d'import/export (CSV, modèles, annotations). Leur JavaScript valide le type avant envoi et présente des barres de progression.

4. **Notification et alertes** :
   - Trois variantes (`notifications.html`, `_simple`, `_debug`) offrent des gabarits pour listes réactives, filtres de date et boutons d'action. Ces pages peuvent être lues comme modèles pour implémenter d'autres tableaux CRUD (utilisateurs, capteurs, configurations).

5. **Admin et impression** :
   - `attendance_print.html` et `admin_panel.html` intègrent des tables exportables et utilisent des macros Jinja (`{% macro row(...) %}`). Pour une nouvelle fonctionnalité (ex. gestion des rôles), étendre `admin_panel.html` en ajoutant un onglet et un endpoint `/admin/roles` est trivial.

6. **Composants de démonstration** :
   - `test_canvas.html`, `test_buttons.html` et `tinkercad.html` servent de bacs à sable pour scripts d'interface. Ils contiennent des fonctions JavaScript isolées qui peuvent être extraites dans des fichiers statiques (`/static/js/`) et réutilisées au besoin.

7. **Pages utilitaires** :
   - `index.html`, `results.html` et `alert_dashboard.html` offrent des layouts de base pour l'accueil, la visualisation de résultats et la gestion des alertes. Elles montrent comment utiliser `{{ messages }}` pour afficher des flash messages Flask et `url_for` pour générer des routes dynamiques.

**Recommandations pour nouvelles fonctionnalités**

- Utiliser `base.html` et définir des blocs supplémentaires (par exemple `sidebar_extra`) pour gérer l'ajout d'éléments de navigation sans toucher la structure de base.
- Créer des macros réutilisables pour les tableaux (`templates/macros/table.html`) afin de standardiser l'apparence des listes CRUD.
- Centraliser les scripts de socket dans un fichier `static/js/socket.js` et charger conditionnellement via un bloc `scripts` pour éviter les duplications.
- Documenter chaque template avec un commentaire en haut précisant l'usage et les variables attendues (ex. `{{ detections }}`, `{{ user }}`) pour faciliter la collaboration.

En résumé, l'ensemble des templates est cohérent, responsive et déjà prêt pour l'extension. Ils constituent un excellent point de départ pour développer des nouvelles pages (gestion des équipements, profil utilisateur, statistiques avancées) en gardant l'interface uniforme.

---

## 🏁 Conclusion

Le projet EPI-DETECTION-PROJECT est une solution complète et bien documentée pour la
détection des EPI en temps réel. La structure du code, les outils d'analyse et la
documentation abondante facilitent sa maintenance et son évolution. Les performances
automatisées montrent que le modèle est prêt pour un déploiement pilote, avec des
ajustements possibles pour les classes les plus délicates.

Ce rapport final, généré à partir des analyses existantes, servira de base pour la
documentation académique ou professionnelle (mémoire, présentation, démonstration).

---

*Rapport généré automatiquement par GitHub Copilot (Raptor mini) à la demande de l'utilisateur.*
