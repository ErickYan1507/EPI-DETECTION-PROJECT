# PARTIE 1 : PRESENTATION GENERALE

## CHAPITRE 3 : PRESENTATION DU PROJET

### 3.1 Formulation du projet

Le projet "EPI-DETECTION-PROJECT" a pour but de développer un système automatisé de détection du port des Équipements de Protection Individuelle (EPI) en milieu professionnel. En s'appuyant sur des techniques de vision par ordinateur et de deep learning, l'application analyse des flux vidéo ou des images pour identifier en temps réel si les personnes présentes dans une zone définie portent correctement les équipements requis (casques, gilets, etc.).

Le système est conçu pour être une application web complète, offrant non seulement la détection, but aussi une interface de visualisation, un système de notification et des capacités d'export de rapports.

### 3.2 Justification de l’importance du sujet

La sécurité sur le lieu de travail est une priorité absolue dans de nombreux secteurs industriels (construction, manufacture, etc.). Le non-respect du port des EPI est une cause majeure d'accidents, entraînant des blessures graves, voire mortelles.

La surveillance manuelle est souvent inefficace, coûteuse et sujette à l'erreur humaine. Un système de détection automatisé permet d'assurer une surveillance continue et objective, 24/7. Il aide les entreprises à :
-   **Prévenir les accidents** en identifiant les situations à risque en temps réel.
-   **Renforcer la culture de la sécurité** en responsabilisant le personnel.
-   **Garantir la conformité** avec les réglementations de sécurité en vigueur.
-   **Optimiser les processus de contrôle** en allégeant la charge des superviseurs de sécurité.

Ce projet répond donc à un besoin critique d'amélioration de la sécurité et de l'efficacité opérationnelle.

### 3.3 Objectifs et besoins utilisateur

L'objectif principal est de créer un système fiable et performant pour la détection d'EPI. Les sous-objectifs et besoins utilisateurs identifiés sont :

-   **Détection en temps réel :** Analyser un flux vidéo (ex: caméra de surveillance) pour identifier instantanément le port ou non-port des EPI.
-   **Tableau de bord (Dashboard) :** Fournir une interface web (`dashboard.py`) pour visualiser les statistiques de détection, les événements récents et l'état général du système.
-   **Système de notifications :** Alerter les responsables de sécurité en cas de non-conformité détectée, via un système de notifications (`notifications.py`).
-   **Stockage des données :** Enregistrer les incidents de non-conformité dans une base de données (`database.py`, `mysql-connector-python`) pour analyse ultérieure.
-   **Rapports et Exports :** Permettre aux utilisateurs d'exporter les données et les statistiques, notamment sous forme de PDF (`pdf_export.py`, `reportlab`) et potentiellement vers des outils de BI comme PowerBI (`powerbi_export.py`).
-   **Accessibilité via API :** Exposer les fonctionnalités de détection via une API REST (`routes_api.py`) pour une intégration potentielle avec d'autres systèmes.

### 3.4 Moyens nécessaire à la réalisation du projet

#### Moyens Humains
-   **Chef de Projet / Développeur Principal :** Pour la coordination, le développement du backend et l'intégration des différents modules.
-   **Spécialiste en Deep Learning / Vision par Ordinateur :** Pour le choix, l'entraînement (si nécessaire) et l'optimisation du modèle de détection d'objets.

#### Moyens Matériels
-   **Poste de développement :** Un ordinateur performant pour le codage et les tests.
-   **Serveur de déploiement (ou service Cloud) :** Pour héberger l'application web et le modèle de détection.
-   **GPU (Carte Graphique) :** Fortement recommandé pour l'inférence du modèle de deep learning (YOLOv5) afin d'assurer des performances en temps réel.
-   **Caméras IP :** Pour la capture des flux vidéo en conditions réelles.

#### Moyens Logiciels
L'analyse du fichier `requirements.txt` révèle l'environnement technique suivant :
-   **Langage de programmation :** Python
-   **Framework Backend :** Flask (`flask`, `flask-socketio`, `gunicorn`, `eventlet`) pour le serveur web et la communication en temps réel.
-   **Deep Learning & Vision par Ordinateur :**
    -   `torch`, `torchvision` : Framework de deep learning (Pytorch).
    -   `yolov5` : Le modèle pré-entraîné utilisé pour la détection d'objets.
    -   `opencv-python` : Bibliothèque pour le traitement d'images et de vidéos.
-   **Base de données :**
    -   `flask-sqlalchemy` : ORM pour la gestion de la base de données.
    -   `mysql-connector-python` : Connecteur pour une base de données MySQL.
-   **Manipulation de données :** `numpy`, `pandas`.
-   **Génération de rapports :** `reportlab` pour les exports PDF.
-   **Tests :** `pytest`.

### 3.5 Chronogramme de réalisation du projet

Un diagramme de Gantt formel est recommandé pour un suivi détaillé. Ci-dessous, une proposition de chronogramme simplifié sous forme de tableau.

| Phase | Tâches Principales | Durée Estimée |
| :--- | :--- | :--- |
| **1. Analyse & Conception** | - État de l'art sur la détection d'EPI<br>- Collecte et préparation du jeu de données<br>- Conception de l'architecture système | 2 semaines |
| **2. Développement Backend** | - Mise en place du serveur Flask<br>- Intégration du modèle YOLOv5<br>- Développement du module de détection | 3 semaines |
| **3. Développement Frontend**| - Création du tableau de bord<br>- Mise en place de la visualisation temps réel | 2 semaines |
| **4. Fonctionnalités & DB** | - Développement de la gestion base de données<br>- Implémentation des notifications et exports | 2 semaines |
| **5. Tests & Intégration** | - Tests unitaires et d'intégration<br>- Déploiement sur un serveur de test | 1 semaine |
| **6. Déploiement & Finalisation**| - Déploiement en production<br>- Rédaction de la documentation finale | 1 semaine |

### 3.6 Résultat attendu

Le résultat final attendu est une application web fonctionnelle, robuste et performante, capable de :
1.  Analyser un flux vidéo en direct depuis une caméra.
2.  Détecter avec une bonne précision le port correct ou incorrect d'équipements de protection individuelle.
3.  Afficher les détections en temps réel sur une interface web claire et intuitive.
4.  Enregistrer les événements de non-conformité dans une base de données.
5.  Générer des alertes pour les superviseurs.
6.  Fournir des statistiques et des rapports exportables pour l'analyse des tendances de sécurité.

L'application doit être un outil clé en main pour améliorer la sécurité et la conformité sur un site industriel.

---

# PARTIE 2 : ANALYSE ET CONCEPTION

## CHAPITRE 4 : ETAT DE L’ART

Ce chapitre dresse un panorama des approches existantes pour la détection d'objets, en se concentrant sur les méthodes pertinentes pour l'identification en temps réel d'Équipements de Protection Individuelle (EPI).

### 4.1 La détection d'objets pour la sécurité au travail

#### 4.1.1 Contexte
L'avènement du deep learning a révolutionné le domaine de la vision par ordinateur. La détection d'objets, qui consiste à identifier et localiser des instances d'objets dans des images ou des vidéos, est passée de méthodes traditionnelles (basées par exemple sur les caractéristiques HOG ou les classifieurs en cascade de Haar) à des approches neuronales beaucoup plus performantes et robustes. Ce progrès technologique a ouvert la voie à des applications à fort impact sociétal, notamment dans le domaine de la sécurité industrielle.

#### 4.1.2 Problématique
La détection d'EPI en milieu réel présente plusieurs défis techniques :
- **Rapidité :** Le système doit fonctionner en temps réel pour permettre des alertes immédiates.
- **Robustesse :** Il doit être performant dans des conditions d'éclairage variables, avec des occultations partielles (ex: un travailleur partiellement caché par une machine) et des angles de vue divers.
- **Précision :** Le système doit distinguer avec précision les différents types d'EPI (casque, gilet, masque, etc.) et ne pas générer de fausses alarmes.
- **Variété :** Les EPI existent dans de nombreuses formes, couleurs et tailles, et le système doit pouvoir tous les généraliser.

#### 4.1.3 Solutions Existantes
Les solutions modernes de détection d'objets basées sur le deep learning se divisent principalement en deux familles.

**1. Les détecteurs en deux étapes (Two-Stage Detectors)**

*   **Principe :** Ces méthodes, initiées par la famille d'algorithmes R-CNN (Regions with CNN features), décomposent la détection en deux étapes. D'abord, un mécanisme génère des "propositions de régions" où un objet est susceptible de se trouver. Ensuite, un classifieur évalue chacune de ces régions.
*   **Exemple notable :** L'algorithme **Faster R-CNN** (Ren, He, Girshick, & Sun, 2015) a marqué une étape clé en introduisant un "Region Proposal Network" (RPN) qui partage les couches de convolution avec le réseau de détection, rendant la génération de propositions beaucoup plus rapide.
*   **Avantages :** Ils atteignent généralement la meilleure précision de détection.
*   **Inconvénients :** La séparation en deux étapes les rend plus lents et plus complexes à entraîner, ce qui peut être un frein pour les applications nécessitant une très haute vitesse.

**2. Les détecteurs en une étape (One-Stage Detectors)**

*   **Principe :** Ces approches traitent la détection comme un problème de régression unique. Le réseau analyse l'image en une seule passe ("you only look once") pour prédire simultanément les boîtes englobantes (bounding boxes) et les probabilités de classe pour tous les objets.
*   **Exemple notable :** La famille d'algorithmes **YOLO (You Only Look Once)**, introduite par Redmon et al. (2015), est l'pionnière de cette approche. Elle est réputée pour son incroyable rapidité, ce qui la rend idéale pour la détection en temps réel. Le projet actuel utilise **YOLOv5**, une itération plus recente et performante de cette famille (bien que non publiée par les auteurs originaux, elle est largement adoptée par la communauté pour ses performances et sa facilité d'utilisation).
*   **Avantages :** Extrêmement rapides, capables d'analyser des flux vidéo en temps réel. Architecture plus simple.
*   **Inconvénients :** Peuvent parfois avoir une précision légèrement inférieure à celle des détecteurs en deux étapes, en particulier pour les objets très petits.

#### 4.1.4 Critique et Synthèse

Le choix entre ces deux familles d'approches dépend du compromis recherché entre précision et vitesse.

| Approche | Auteurs Clés | Vitesse | Précision | Idéal pour... |
| :--- | :--- | :--- | :--- | :--- |
| **Faster R-CNN** | Girshick, Ren, He | Lente | Très Haute | Analyse d'images médicales, compétition de recherche où la précision prime. |
| **YOLO** | Redmon, Farhadi | Très Rapide | Haute | Véhicules autonomes, surveillance vidéo, applications temps réel comme la détection d'EPI. |

Pour un projet de détection d'EPI, la capacité à analyser un flux vidéo en direct et à générer des alertes instantanées est un critère non négociable. La vitesse est donc le facteur prédominant. Les détecteurs en une étape, et en particulier la famille YOLO, représentent l'état de l'art pour ce type d'application.

Le choix de **YOLOv5** pour ce projet est donc tout à fait justifié. Il offre un excellent équilibre entre vitesse et précision, tout en bénéficiant d'une large communauté d'utilisateurs et d'un écosystème d'outils qui facilitent son entraînement et son déploiement.

---

## CHAPITRE 5 : ANALYSE PREALABLE

Ce chapitre détaille l'analyse menée avant le développement du système, incluant l'étude du processus existant, la présentation des données utilisées et la justification des choix méthodologiques et techniques.

### 5.1 Analyse de l’existant

#### 5.1.1 Organisation actuelle et diagramme de flux
Avant l'implémentation de ce projet, le processus de surveillance du port des EPI reposait entièrement sur une supervision humaine. L'organisation typique est la suivante :

1.  **Patrouille :** Un ou plusieurs responsables de la sécurité (HSE) effectuent des rondes régulières sur le site (chantier, usine, etc.).
2.  **Observation :** Le responsable observe visuellement les travailleurs pour vérifier s'ils portent correctement leurs équipements (casque, gilet, chaussures de sécurité, etc.).
3.  **Intervention :** En cas de non-conformité, le responsable intervient directement auprès de la personne concernée pour lui rappeler les règles.
4.  **Rapport :** Les incidents peuvent être consignés manuellement dans un registre ou un rapport journalier, qui est ensuite analysé périodiquement pour identifier des tendances.

Ce flux peut être décrit comme un processus manuel, séquentiel et réactif.

#### 5.1.2 Critique de l’existant
Le système de surveillance manuelle, bien qu'essentiel, présente des limites significatives qui justifient la recherche d'une solution automatisée :

-   **Non-exhaustivité :** Il est impossible pour les superviseurs de surveiller toutes les zones et toutes les personnes en permanence.
-   **Coût élevé :** La mobilisation de personnel dédié à la surveillance représente un coût salarial important.
-   **Subjectivité et erreur humaine :** La fatigue, le manque d'attention ou une appréciation personnelle peuvent conduire à des oublis ou à des erreurs de jugement.
-   **Manque de données centralisées :** Les rapports manuels sont difficiles à agréger et à analyser de manière statistique pour obtenir une vue d'ensemble fiable et en temps réel.
-   **Caractère réactif :** L'intervention a lieu après la constatation de la faute, et non au moment précis où elle se produit, ce qui peut retarder la correction.

#### 5.1.3 Moyen existant pour la réalisation du projet
Le projet a été initié en s'appuyant principalement sur les ressources suivantes :
-   **Logiciels Open Source :** Le projet est entièrement construit sur des technologies ouvertes et gratuites (Python, Flask, YOLOv5), ce qui a considérablement réduit les coûts de développement.
-   **Jeux de données publics :** Des jeux de données d'images existants ont probablement servi de base pour constituer le jeu de données final.
-   **Expertise technique :** Les compétences en développement logiciel et en intelligence artificielle du développeur ont été le principal moteur de la réalisation.

### 5.2 Présentation des données

La performance d'un modèle de deep learning est intrinsèquement liée à la qualité et à la quantité des données d'entraînement.

#### 5.2.1 Collecte des données
Le projet utilise un jeu de données personnalisé, comme l'indique la structure du dossier `/dataset`. Ce dossier contient les images brutes (`raw_images`) et les images préparées (`images/train`, `images/val`, `images/test`). La constitution de ce jeu de données a probablement impliqué :
-   La collecte d'images provenant de diverses sources (banques d'images, chantiers, etc.).
-   La capture de vidéos et l'extraction d'images (frames) pour représenter des scénarios réels.

#### 5.2.2 Prétraitement et Annotation des données
Le prétraitement a consisté en une étape cruciale : **l'annotation**. Chaque image du jeu de données a été annotée manuellement. Ce processus consiste à dessiner des boîtes englobantes (bounding boxes) autour de chaque objet d'intérêt et à lui assigner une classe.

Le fichier `dataset/data.yaml` nous informe sur la nature de ces classes :
-   **Nombre de classes :** 6
-   **Noms des classes :** `helmet` (casque), `vest` (gilet), `glasses` (lunettes), `person` (personne), `boots` (chaussures), et `class_5` (une classe non spécifiée ou en cours de définition).

La présence d'un dossier `labels` contenant un fichier texte par image (au format YOLO) confirme que cette annotation a été réalisée et constitue le "ground truth" (la vérité terrain) pour l'entraînement du modèle.

#### 5.2.3 Choix du modèle
Le modèle choisi pour ce projet est **YOLOv5**. Plus précisément, la présence du fichier `yolov5s.pt` dans le répertoire racine suggère l'utilisation de la version "small" du modèle.

Ce choix est justifié par plusieurs facteurs clés :
-   **Performance en temps réel :** Comme discuté dans l'état de l'art, YOLO est la référence pour la détection à haute vitesse.
-   **Excellent compromis :** La version YOLOv5s offre un très bon équilibre entre vitesse d'inférence, qui est cruciale pour l'analyse de flux vidéo, et une précision de détection élevée.
-   **Facilité d'utilisation :** L'écosystème YOLOv5 fournit des scripts et des outils qui simplifient grandement les phases d'entraînement, de validation et d'inférence.

### 5.3 Choix de méthode et outils

#### 5.3.1 Choix des méthodologies et justifications
Une **méthodologie de développement hybride** a probablement été adoptée.
-   Une approche **en cascade (Waterfall)** pour la phase initiale de planification : définition des objectifs globaux, analyse des besoins et conception générale de l'architecture.
-   Une approche **Agile** pour les phases de développement, de test et de déploiement. Le travail a été découpé en modules fonctionnels (backend, détection, base de données, frontend), qui ont pu être développés et testés de manière itérative. Cette flexibilité permet d'intégrer facilement de nouvelles fonctionnalités ou de corriger des problèmes au fur et à mesure.

#### 5.3.2 Choix des algorithmes et justifications
L'algorithme principal est **YOLOv5**. La justification a déjà été établie : il représente l'état de l'art pour la détection d'objets en temps réel, ce qui est une exigence fondamentale du projet. Le choix de cet algorithme conditionne une grande partie de l'architecture technique.

#### 5.3.3 Choix de l’environnement technique et justifications
Chaque composant de la stack logicielle a été choisi pour sa pertinence et son efficacité :

-   **Python :** Langage de prédilection pour l'intelligence artificielle et le développement web backend, bénéficiant d'un immense écosystème de bibliothèques.
-   **PyTorch & YOLOv5 :** PyTorch offre une grande flexibilité pour la recherche et le développement en deep learning. YOLOv5, bâti sur PyTorch, fournit une implémentation optimisée et facile à utiliser d'un modèle de pointe.
-   **Flask :** Framework web minimaliste et léger, parfait pour créer des API REST et des applications web sans la complexité de frameworks plus lourds. Sa simplicité est un atout pour un projet où le cœur de la complexité réside dans le modèle de vision par ordinateur.
-   **OpenCV :** Bibliothèque incontournable pour toutes les manipulations de flux vidéo et d'images (lecture de caméra, redimensionnement, dessin des boîtes de détection, etc.).
-   **MySQL :** Système de gestion de base de données relationnelle robuste, éprouvé et largement utilisé, idéal pour stocker de manière structurée les données sur les événements de détection.
---
