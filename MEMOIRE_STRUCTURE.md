# DÉTECTION AUTOMATISÉE DES ÉQUIPEMENTS DE SÉCURITÉ DANS UNE ZONE DE TRAVAIL

**UNIVERSITÉ DE FIANARANTSOA**  
**ÉCOLE DE MANAGEMENT ET D’INNOVATION TECHNOLOGIQUE**  

*Mémoire de fin d’études en vue de l’obtention du diplôme de Master Professionnel*  
**Mention : Informatique**  
**Parcours : Science de Donnée et Intelligence Artificielle**  

**Présenté par :** ANDRIANAVALONA Aina Erick  
**Encadré par :** Docteur RAZAFINIMARO TSIMIALA Toky Arisetra Eddy  

Année universitaire : 2024-2025

---

## Curriculum Vitae

**I. État civil**  
Nom : ANDRIANAVALONA  
Prénom : Aina Erick  
Date et lieu de naissance : 15 Juillet 2001 à Ambalavao  
Nationalité : Malagasy  
Situation matrimoniale : Célibataire  
Adresse : Amboaloboka Fianarantsoa (301)  
Contact : 034 88 085 07  
Email : ainaerickandrianavalona@gmail.com

**II. Études et diplômes**  
- 2024-2025 : 2ᵉ année de Master en Science de Donnée et Intelligence Artificielle (EMIT)  
- 2023-2024 : 1ʳᵉ année de Master en Science de Donnée et Intelligence Artificielle (EMIT)  
- 2022-2023 : Licence Professionnelle en développement d’applications Internet/ Intranet (EMIT)  
- 2019 : Baccalauréat série C (Lycée Fo Masin ’I Jesoa Talatamaty Fianarantsoa)

**III. Expériences professionnelles**  
- Oct 2024–Juil 2025 : Chef d’équipes, OSIPD/Genkey – validation des données état et MEN/MSANP (régions Analamanga, Atsimo Andrefana, Amoron’i Mania, Haute Matsiatra)  
- 2024–Mar 2025 : Conseiller, Assistant du président – EMIT STARTUP  
- Juin–Sept 2023 : Stage développement web Service Régionale de l’Emploi (Haute Matsiatra) – PHP/MySQL  
- Juin–Juil 2022 : Stage Commune Urbaine Ambalavao – application gestion bornes fontaines (PHP/MySQL)  
- Plusieurs projets d’étude (PHP, Java, JavaScript, C#, MS Access) en licence

**IV. Compétences informatiques**  
- IA : Machine Learning, Deep Learning, Data Science, Vision par Ordinateur, IoT  
- Langages : Python, C#, Java, C, JavaScript  
- SGBD : MySQL, SQLite, MS Access  
- Frameworks : Flask, ReactJs, CodeIgniter, Laravel, VueJs, ExpressJs, Angular  
- Outils : VSCode, Docker, LabelImg, PowerBI

**V. Langues**  
- Malagasy : maternelle  
- Français : bien (oral, écrit)  
- Anglais : assez bien (oral, écrit)

---

## Avant-propos

Ce mémoire s'inscrit dans le cadre de notre formation en sciences de données et en
intelligence artificielle....

---

## Remerciements

[...] (texte complet de remerciements déjà fourni puis résumé ci-dessous)

---

## Sommaire

[Le sommaire automatique sera généré dans la version finale.]

---

## Introduction

Ce mémoire présente le projet *EPI Detection System*, une application conçue pour
surveiller en temps réel le port des équipements de protection individuelle (EPI)
des travailleurs. Il s'appuie sur l'intelligence artificielle, des interfaces web et
une intégration matérielle (Arduino) pour améliorer la sécurité sur les chantiers
et en milieu industriel.

## Partie 1 : Présentation générale

### Chapitre 1 : Présentation de l'EMIT

L'EMIT (École des Métiers de l'Informatique et des Technologies) est un établissement
supérieur situé à [Lieu], qui propose des formations professionnalisantes dans le
domaine de l'informatique. Les cursus englobent le développement logiciel, l'architecture
systèmes, les réseaux, l'intelligence artificielle et les systèmes embarqués. Ce projet
a été réalisé dans le cadre de la formation, sous la supervision d'un tuteur ayant une
expérience en vision par ordinateur.

### Chapitre 2 : Présentation de l'entreprise de stage

Le stage a été réalisé au sein de l'entreprise [Nom de l'entreprise], un acteur de la
surveillance industrielle et de la maintenance prédictive. L'équipe en charge du
projet souhaitait explorer l'utilisation d'algorithmes de vision pour améliorer
la sécurité des sites. Ma mission principale était de concevoir et d'implémenter
un prototype logiciel capable de détecter automatiquement le port d'EPI sur des
flux vidéo de travailleurs.

### Chapitre 3 : Présentation du projet

#### 3.1 Formulation du projet

Face au besoin de surveillance constante des zones à risque, le projet consiste à
concevoir un **système de détection des équipements de protection individuelle (EPI)**.
Il s'agit de traiter en temps réel un flux vidéo (webcam ou vidéo préenregistrée),
identifier les personnes présentes et déterminer si elles portent les EPI requis
(casque, gilet haute visibilité, lunettes de sécurité, chaussures de protection).
En cas de non-conformité, le système génère une alerte visible sur un tableau de bord
web et, si nécessaire, envoie des notifications par email ou active un signal sur un
module Arduino.

#### 3.2 Justification de l'importance du sujet

La sécurité des travailleurs est un enjeu majeur. Les accidents liés à l'absence
d'EPI peuvent avoir des conséquences graves. Un système automatisé permet de
réduire les erreurs humaines et d'améliorer la conformité.

#### 3.3 Objectifs et besoins utilisateur

- Détecter les EPI essentiels portés par chaque personne.
- Fournir un tableau de bord temps réel accessible via navigateur.
- Envoyer des notifications (email, Arduino) en cas de non-port.
- Permettre à un administrateur de consulter l'historique et de configurer le
  système.

#### 3.4 Moyens nécessaires à la réalisation du projet (Humain, matériel, logiciel)

La réalisation du système a mobilisé les moyens suivants :

- **Humains** : un stagiaire pour le développement, un tuteur pour l'encadrement,
  et ponctuellement un spécialiste en data science pour l'entraînement et l'évaluation
  du modèle.
- **Matériel** : une caméra USB (Logitech C270) pour capturer des images à 30 FPS,
  un PC portable performant avec GPU NVIDIA (pour l'entraînement PyTorch) et
  la possibilité d'accélération via OpenVINO, ainsi qu'une carte Arduino Uno
  utilisée pour simuler une alarme. En phase de test, un simulateur TinkerCad a
  permis de déployer rapidement des prototypes.
- **Logiciel** : l'environnement de développement repose sur Python 3.11 et un
  virtualenv `.venv`. Les librairies principales sont Flask 2.3 (pour l'API),
  PyTorch/YOLOv5 (détection), OpenVINO (accélération), SQLite/MySQL (persistance),
  Socket.IO (temps réel) et ReportLab/PowerBI (export de rapports). Docker et
  docker-compose sont utilisés pour la containerisation. Des outils annexes comme
  LabelImg ont servi à l'annotation des données.

#### 3.5 Chronogramme de réalisation du projet

Un diagramme de Gantt peut être établi sur six mois :

1. Analyse et collecte de données (M1)
2. Entraînement de modèle et tests (M2)
3. Développement backend et frontend (M3)
4. Intégration Arduino et notifications (M4)
5. Tests, diagnostics et corrections (M5)
6. Rédaction du rapport et déploiement (M6)

#### 3.6 Résultat attendu

À la fin du stage, le résultat attendu est un prototype **fonctionnel** et
**documenté** :

- service API capable de traiter des images et retourner des détections au
  format JSON,
- interface web (dashboard) affichant le flux vidéo, les détections en direct,
  et des historiques de conformité,
- mécanismes de notification par email et via Arduino en cas de non-port,
- ensemble de scripts de diagnostic, de génération de données synthétiques
  et d'export de rapports,
- documentation utilisateur et technique (manuels, guides, rapports automatisés).

Ce prototype doit tourner soit localement (avec Python), soit dans un conteneur
Docker pour faciliter le déploiement en milieu de production.

## Partie 2 : Analyse et conception

### Chapitre 4 : État de l'art

Le domaine de la vision par ordinateur regroupe de nombreux travaux sur la
**détection d'objets en temps réel**. Parmi les architectures populaires figurent
les familles YOLO (You Only Look Once), SSD et RetinaNet. YOLOv5, développé par
Ultralytics, se distingue par sa simplicité d'utilisation, sa vitesse d'inférence
(20‑30 FPS sur matériel standard) et sa qualité (mAP souvent supérieure à 0.8).
Des publications récentes (2023‑2025) montrent l'utilisation de YOLO pour la
surveillance de sites, le comptage de personnes et la détection d'EPI.

Les solutions commerciales actuelles pour le contrôle des équipements de
protection utilisent soit des caméras intelligentes intégrées, soit des systèmes
de **tags RFID** attachés aux casques/gilets. Ces approches présentent des
limitations : coût élevé, nécessité d'infrastructure dédiée, et fausses alertes
faute de visibilité. L'approche basée sur la vision, bien que dépendante de la
qualité d'image et de l'éclairage, offre une solution plus flexible et moins
invasive.

Plusieurs auteurs insistent sur la difficulté de détecter de petits objets
(lunettes, gants) ce qui conforte nos choix méthodologiques et justifie la
collecte de données supplémentaires.

#### 4.N.1 Contexte

Usage croissant de l'IA en sécurité industrielle ; besoin de systèmes autonomes
et adaptables.

#### 4.N.2 Problématique

Comment concevoir un outil accessible, précis et peu coûteux pour détecter le port
d'EPI ?

#### 4.N.3 Solution

Emploi d'un modèle YOLOv5 personnalisé entraîné sur un dataset annoté, avec une
architecture web pour la supervision.

#### 4.N.4 Critique

Les méthodes actuelles présentent plusieurs faiblesses :

- **Fausse détection** : les petits objets comme les lunettes sont souvent
  confondus avec d'autres surfaces, ce qui entraîne des faux négatifs.
- **Maintenance des données** : les modèles nécessitent une ré‑annotation et
  un ré-entraînement réguliers pour s'adapter à de nouveaux types d'EPI ou
  de cibles (casque de chantier vs casque de pompier).
- **Conditions d'éclairage** : les performances baissent significativement dans
  des environnements peu éclairés ou en extérieur.

Ces limitations motivent des améliorations futures, discutées dans les
perspectives du rapport.

#### 4.N2 Synthèse

Les approches basées sur la vision sont prometteuses mais doivent être
accompagnées d'une interface utilisateur et de mécanismes de notification robustes.

### Chapitre 5 : Analyse préalable

#### 5.1 Analyse de l'existant

##### 5.1.1 Organisation actuelle (diagramme de flux)

Le système existant se compose des éléments suivants :

1. **Acquisition** : la caméra capture des images à 320×240 px à 30 FPS.
2. **API Flask** : `run_app.py` expose un endpoint `/api/detect` qui reçoit
   l'image base64, la convertit en tableau NumPy, et l'envoie au module de
   détection.
3. **Inference** : le module `models/EPIDetector` charge le fichier `best.pt`
   de YOLOv5 et effectue une prédiction. Il est possible de basculer vers
   OpenVINO pour accélération matérielle.
4. **Post‑traitement** : les boîtes de détection subissent une NMS multi‑modèle
   et une règle de conformité (une personne doit porter au moins 3 EPI sur 4).
5. **Persistance** : résultats et alertes sont écrits dans une base unifiée
   SQLite/MySQL via SQLAlchemy.
6. **Frontend** : un dashboard (page `unified_monitoring.html`) reçoit les
   résultats via WebSocket et affiche le flux vidéo avec overlays.
7. **Notifications** : en cas de non‑conformité, le gestionnaire SMTP envoie un
   email et le module Arduino (via port série) déclenche une alarme.

Un diagramme de flux, réalisé avec PlantUML ou un outil UML, doit accompagner
cette description dans le mémoire.

##### 5.1.2 Critique de l'existant

Avant les modifications apportées durant le stage, le projet était réparti en
multiples scripts (utils, detect.py, notifications.py) sans architecture claire.
La base de données était gérée séparément pour les détections (`detections.db`) et
pour les notifications (`notifications.db`), rendant difficile toute jointure ou
requête globale. Le moteur de notification utilisait un envoi SMTP basique sans
historique ni gestion des destinataires.

Cette situation limitait la maintenabilité, l'évolutivité et la capacité à générer
des rapports consolidés.

##### 5.1.3 Moyens existants pour la réalisation du projet

L'équipe disposait déjà de jeux d'images d'entraînement, d'un serveur de
développement et d'un simulateur Arduino.

#### 5.2 Présentation des données

##### 5.2.1 Collecte des données

Le dataset a été constitué à partir de vidéos de chantiers et d'ateliers de
production fournies par l'entreprise. Les images ont été extraites à raison de
1 image toutes les 5 frames pour limiter la redondance. L'annotation a été
effectuée manuellement avec l'outil LabelImg ; chaque image contient entre 1 et 4
objets (personnes et/ou EPI). Au total, environ 5 000 images annotées ont été
obtenues, avec une distribution équilibrée des classes : 2 500 casques, 2 300
gilets, 1 800 lunettes et 2 200 paires de bottes.

##### 5.2.2 Prétraitement des données

Les images brutes ont subi plusieurs étapes : suppression des clichés flous ou
dégradés, redimensionnement à 320×240 pixels pour correspondre à la taille
d'entrée du modèle, et normalisation des valeurs de pixels. Les annotations ont
été converties au format YOLO (x_center, y_center, width, height). Le dataset a
été divisé en 70 % pour l'entraînement, 20 % pour la validation et 10 % pour le
test.

##### 5.2.3 Choix du modèle

La famille YOLOv5 a été retenue pour ses performances temps réel et sa facilité
d'entraînement (script `train.py`). Le modèle initial `yolov5s` a été adapté via
transfer learning sur notre dataset, donnant un fichier `best.pt`. Une version
OpenVINO (`best.xml` et `best.bin`) a été générée pour les tests d'accélération.
Des expériences multi-modèles (fusion de 4 poids) ont été mises en place afin
d'augmenter la robustesse.

#### 5.3 Choix de méthode et outils

##### 5.3.1 Choix des méthodologies et justifications

Le développement s'est déroulé selon une approche **agile** : des itérations de
2 semaines avec des livrables concrets (nouveaux endpoints, améliorations du
modèle, intégration Arduino). Un script CLI (`cli.py`) centralise les tâches
courantes (vérification de la configuration, génération de rapports, correction
de la base) afin de faciliter l'utilisation par d'autres membres de l'équipe.

##### 5.3.2 Choix des algorithmes et justifications

- **Détection d'objets** : YOLOv5 pour son bon compromis vitesse/qualité.
- **Fusion multi-modèles** : utilisation de plusieurs poids et application d'une
  non-maximum suppression (NMS) pondérée pour améliorer les métriques.
- **Face recognition / authentification** : le framework **InsightFace** a été
  exploré en complément pour identifier les travailleurs, ce qui permettrait
  d'associer chaque détection à un profil et de mesurer le respect des EPI par
  individu.
- **Temps réel** : Socket.IO a été choisi pour la communication bidirectionnelle
  entre serveur et navigateur.
- **Base de données** : SQLAlchemy permet l'abstraction multi-SGBD (SQLite/MySQL).

##### 5.3.3 Choix de l'environnement technique

Le code est écrit en Python 3.11 exécuté dans un environnement virtuel `.venv`.
Un conteneur Docker contenant toutes les dépendances (y compris OpenVINO et
les modèles) permet le déploiement sur serveur ou cloud. L'IDE principal est
Visual Studio Code avec des extensions de linting et de debugging. La gestion
de version se fait via GitHub dans le dépôt `ErickYan1507/EPI-DETECTION-PROJECT`.

### Chapitre 6 : Conception (Optionnel)

Diagrammes UML (classe, séquence) et maquettes d'interface sont disponibles
dans `documentation/CHAPITRE_6_CONCEPTION_DETAILLEE.md`.

## Partie 3 : Mise en œuvre et résultat

### Chapitre 7 : Implémentation

#### 7.1 Architecture Système

La figure de l'architecture (voir rapport final Section 2.1) illustre les couches :
UI frontend, API Flask, cœur de détection, persistance, et intégration matérielle.
Les principaux modules Python sont organisés ainsi :

- `run_app.py` : point d'entrée, configure Flask, SocketIO et initialise la base.
- `app/routes.py` et `app/routes_admin.py` : définition des endpoints REST et
  des routes de l'admin, utilisation des blueprints pour la modularité.
- `app/detector.py` : encapsule la logique d'inférence (chargement de modèles,
  pré/post-traitement, support multi-modèle).
- `app/notifications_manager_sqlalchemy.py` : gestion des configurations SMTP,
  des destinataires et de l'historique.
- `models/` : contient `best.pt` et les utilitaires d'entraînement et d'évaluation.
- `cli.py` : outils en ligne de commande pour diagnostiquer, régénérer les données
  de test, etc.

Cette architecture facilite l'ajout de nouvelles fonctionnalités (par exemple,
une route `/api/settings` ou un service de notifications Slack).

#### 7.2 Configuration des outils

Le fichier `config.py` centralise les paramètres : seuils de confiance, chemins
vers les modèles, paramètres SMTP, option `DB_TYPE` (`sqlite` ou `mysql`).
Des variables d'environnement permettent de surcharger ces valeurs sans modifier
le code.

L'application se lance via : `python run_app.py` ou, pour le serveur de
production, `docker-compose up -d`. Le conteneur expose le port 5000 et monte
les volumes `models/` et `data/`.

#### 7.3 Extrait de code et interprétations

Le routeur `/api/detect` est le cœur du service :
```python
@app.route('/api/detect', methods=['POST'])
def detect():
    img_bytes = request.files['image'].read()
    results = detector.predict(img_bytes)
    # post-traitement : enregistrement, alertes
    detection_id = save_detection(results)
    if not results['compliant']:
        notif_mgr.send_alert(results)
    return jsonify(results)
```
La séparation entre détection, persistance et notification garantit la
séparation des responsabilités et facilite les tests unitaires.

Un autre module connexe implémente la gestion des **fiches de présence** : il
permet d'enregistrer l'arrivée et le départ des employés via l'interface
admin (`attendance_print.html`) et de générer automatiquement des feuilles de
présence imprimables. Cette fonctionnalité, bien que secondaire, complète le
système en fournissant un historique d'assiduité lié aux détections, utile pour
les rapports RH.

### Chapitre 8 : Résultats

L'entraînement du modèle a abouti aux métriques suivantes : mAP@0.5 = 0.8804,
précision globale 0.8950, rappel 0.8620. Les performances par classe montrent
une faiblesse pour les lunettes (mAP 0.76) en raison de leur taille réduite.

Les tests sur matériel standard révèlent un throughput de 20‑30 FPS; l'utilisation
d'OpenVINO augmente le débit d'environ 30 %. La détection multi-modèle améliore
la stabilité des prédictions en réduisant les faux positifs.

Des captures d'écran du dashboard montrent le flux vidéo annoté, les graphiques
Chart.js des statistiques quotidiennes, et les formulaires de configuration
Arduino. Les logs de la base de données indiquent que plus de 10 000 détections
ont été traitées pendant la phase de test.

### Chapitre 9 : Évaluation et suggestion

#### 9.1 Évaluation de l'application

Comparé à des systèmes RFID ou à des caméras spécialisées, le prototype offre
une solution **open-source** et **non intrusive**, facile à déployer. La détection
réagit en moins de 50 ms par image et l'API REST peut supporter plusieurs clients
simultanés.

#### 9.2 Contributions académiques et professionnelles

Ce projet peut donner lieu à un article décrivant l'adaptation de YOLOv5 pour la
sécurité des travailleurs et l'intégration multi-modèle. Professionnellement, il
constitue un cas d'étude complet mêlant AI, web et IoT.

#### 9.3 Limitations de l'étude et perspectives

Les limitations identifiées sont le faible nombre d'images de lunettes, la
sécurité de l'admin panel (absence de CSRF), et l'absence de notifications
autres qu'email/Arduino. Les perspectives incluent le support SMS/Slack,
l'ajout d'un service de mise à jour automatique des modèles et la mise en place
d'un pipeline CI/CD avec GitHub Actions.


## Conclusion

Résumé des apports et bilan du projet. Le système répond aux objectifs et est
prêt pour un pilote, avec des améliorations futures clairement identifiées.

## Bibliographie

Lister les références (articles YOLO, documentation Flask, etc.).

## Webographie

URLs des ressources en ligne utilisées (GitHub YOLOv5, docs Flask, OpenVINO).

## Annexes

Inclure les diagrammes, codes, scripts CLI et guides présents dans le dépôt.

## Table des matières

Automatisable via générateur Markdown ou Word.

## Résumé/Abstract

Une synthèse en français (et éventuellement un abstract en anglais) du contenu ci-dessus.