# RAPPORT FINAL D'ANALYSE DU PROJET EPI-DETECTION

Date d'audit: 2026-02-27  
Projet: EPI-DETECTION-PROJECT  
Type: Audit technique global (code, architecture, securite, exploitation, qualite)

## Introduction

Ce document presente une analyse technique detaillee du projet EPI Detection, avec une lecture orientee:
- architecture logicielle et coherence technique,
- qualite de code et maintenabilite,
- securite applicative et risques operationnels,
- adequation avec un cadre de memoire M2 (canevas thematique).

## Methodologie d'analyse

Analyse realisee sur le depot local, en priorite sur les zones a impact fort:
- backend principal Flask + routes API + services transverses,
- modeles de donnees unifies (SQLite/MySQL),
- points d'entree d'execution (run scripts, Docker),
- couverture de tests et structure du projet,
- hygiene DevOps (fichiers generes, secrets, volumetrie).

Limite explicite: le depot contient plusieurs milliers de fichiers (notamment images/uploads et .venv), donc l'analyse detaillee ligne-a-ligne de 100% des fichiers n'est pas realiste en un seul passage. L'audit cible les composants critiques et les signaux systemiques representatifs.

---

## PARTIE 1 - PRESENTATION GENERALE

### Chapitre 1 - Presentation globale du systeme

Le projet implemente un systeme de detection EPI base sur YOLOv5 avec interface web Flask, notifications, administration, statistiques et integration Arduino.

Fonctions metier majeures observees:
- detection EPI par image/base64 et camera,
- suivi de conformite (helmet, vest, glasses, boots, person),
- alerting et notifications email,
- dashboard web + exports,
- gestion admin CRUD de tables metier,
- base unifiee (SQLite/MySQL) et synchronisation.

### Chapitre 2 - Inventaire technique du depot

Indicateurs de volumetrie:
- `app/`: 144 fichiers
- `tests/`: 88 fichiers
- `templates/`: 22 fichiers
- `documentation/`: 290 fichiers
- `static/`: 6730 fichiers (majoritairement assets/uploads)

Volume code (estimation):
- `app/`: ~19 009 lignes (sources texte principales)
- `tests/`: ~4 633 lignes
- `templates/`: ~9 992 lignes

Conclusion inventaire:
- Le projet est riche fonctionnellement.
- La volumetrie runtime (uploads/images/logs) est tres elevee dans le workspace.
- Le perimetre "produit" et le perimetre "donnees d'execution" sont melanges.

### Chapitre 3 - Objectif et resultat attendu du projet

Objectif principal du systeme:
- monitorer la conformite EPI en quasi temps reel,
- tracer en base les evenements et metriques,
- exposer un pilotage operationnel via dashboard/alertes.

Resultat attendu pour un niveau M2/production:
- plateforme robuste, securisee, deploiement reproductible,
- gouvernance claire du code (entrypoint unique, configuration stable),
- qualite exploitable long terme (tests fiables, logs, CI/CD).

---

## PARTIE 2 - ANALYSE ET CONCEPTION

### Chapitre 4 - Etat de l'art applique au projet

Positionnement technique observe:
- Stack coherente pour un POC avance/proto industriel: Flask + OpenCV + PyTorch/YOLOv5 + SQLAlchemy.
- Presence de modules avances: multi-model ensemble, attendance, IoT/Arduino, notifications centrees DB.

Forces:
- Couverture fonctionnelle large,
- efforts de modularisation via blueprints,
- support multi-bases et exports.

Faiblesses structurelles:
- plusieurs chemins d'execution concurrents,
- dette d'integration entre documentation, Docker et code reel,
- securite encore partiellement "mode dev".

### Chapitre 5 - Analyse de l'existant

#### 5.1 Architecture applicative

Observations cles:
- Deux implementations serveur principales coexistent: `app/main.py` et `app/main_new.py`.
- Points d'entree multiples: `run.py`, `run_app.py`, execution directe de `app/main.py` ou `app/main_new.py`.
- `run_app.py` pointe `app.main_new`, tandis que la doc et d'autres scripts pointent `app/main.py`.

Impact:
- Risque de derive fonctionnelle (comportements differents selon la commande de lancement).
- Difficulte de debug et de reproductibilite.

#### 5.2 Configuration et donnees

Constats:
- `config.py` charge `.env.email` explicitement.
- Presence de variables DB/SMTP et de nombreux scripts de migration/sync.
- Base unifiee riche (`app/database_unified.py`) avec modeles detection, alertes, admin, attendance, notifications.

Points positifs:
- Schema metier relativement complet,
- SQLAlchemy bien present,
- support SQLite/MySQL clair au niveau configuration.

Points de vigilance:
- stockage de `sender_password` en clair dans la table configuration notifications.
- logique de config dispersee (env, fallback hardcodes, scripts divers).

#### 5.3 Qualite logicielle

Signaux positifs:
- base de tests importante (88 fichiers dans `tests/`),
- separation partielle des responsabilites (routes/services/models).

Signaux faibles / dette technique:
- `app/main.py` monolithique (environ 2914 lignes),
- duplication de logique entre modules historiques et nouveaux,
- documentation tres abondante mais heterogene et parfois desynchronisee.

### Chapitre 6 - Conception / coherence interne

Diagnostic de coherence:
- La conception metier est ambitieuse et globalement bien pensee.
- Le principal frein n'est pas le manque de fonctionnalites, mais la gouvernance technique:
  - multiplicite des versions de flux,
  - artefacts runtime melanges au code,
  - conventions non stabilisees (lancement, docs, packaging).

---

## PARTIE 3 - MISE EN OEUVRE ET RESULTATS

### Chapitre 7 - Implementation (audit technique)

### 7.1 Constat general

Le projet est operationnel sur de nombreux volets mais il est en "etat evolutif" plutot qu'en "etat stabilise production".

### 7.2 Findings critiques (ordre de severite)

1. Secrets et credentials par defaut
- `app/main.py` definit une `SECRET_KEY` hardcodee.
- `app/routes_admin.py` cree un admin par defaut avec mot de passe fallback (`Admin@1234`) si aucun admin n'existe.
- Risque: compromission session/admin en environnement expose.

2. Stockage mot de passe SMTP en clair
- Le modele notifications conserve `sender_password` en base (champ texte).
- Risque: fuite de credentials email en cas d'acces DB/log dump.

3. CORS permissif global
- `CORS(app, resources={r"/api/*": {"origins": "*"}})` dans `app/main_new.py`.
- `CORS(app)` dans `app/main.py`.
- Risque: surface d'abus API si endpoint sensible non authentifie.

4. Docker non reproductible en l'etat
- `Dockerfile` fait `COPY requirements.txt`, mais aucun `requirements.txt` a la racine (uniquement `documentation/requirements.txt`).
- Le healthcheck Docker pointe `/health` alors que l'API expose `/api/health`.
- Risque: build/healthcheck KO en CI/deploiement.

5. Multiples entrypoints et derive de version
- coexistence `main.py` vs `main_new.py` + scripts multiples.
- Risque: comportements differents selon l'operateur et la doc suivie.

### 7.3 Findings majeurs (P1)

1. Repo tres encombre par donnees runtime
- presence massive d'uploads images/videos et logs dans l'arborescence de travail.
- impact: performance Git, bruit de review, risque de commit accidentel.

2. Documentation surabondante et peu normalisee
- tres grand nombre de fichiers markdown et txt, avec contenus redondants/archives.
- impact: difficultes de navigation pour un nouveau mainteneur.

3. Monolithe applicatif central
- `app/main.py` concentre beaucoup de responsabilites (init app, sockets, camera, sync, routes annexes).
- impact: testabilite reduite, dette de maintenance.

### 7.4 Findings moyens (P2)

1. Incoherences d'encodage visibles dans certaines sorties/logs (mojibake probable).
2. Multiplication de scripts de diagnostic/fix ponctuels, signe d'exploitation reactive.
3. Difference entre discours "production ready" et pre-requis techniques reels (stabilisation a finaliser).

### Chapitre 8 - Resultats de l'audit

Synthese:
- Maturite fonctionnelle: elevee
- Maturite architecture/industrialisation: moyenne
- Maturite securite: moyenne a faible (selon exposition reseau)
- Maturite DevOps/reproductibilite: moyenne

Verdict global:
- Le projet est solide pour demonstration avancee / pilote terrain.
- Un passage "hardening + normalisation" est necessaire avant qualification production stricte.

### Chapitre 9 - Evaluation et suggestions

#### 9.1 Evaluation comparee (qualitative)

Par rapport a une solution industrialisee standard, le projet presente:
- un excellent niveau de fonctionnalites metier,
- mais un niveau de standardisation inferieur sur securite, deployment deterministe, et gouvernance du code.

#### 9.2 Contributions academiques et professionnelles

Contributions techniques notables:
- integration IA + vision + web + IoT,
- modelisation metier et persistence multi-domaines,
- capacite d'observabilite et de reporting.

Valeur academique:
- tres bon terrain pour un memoire M2 orientee systeme intelligent applique.

#### 9.3 Limitations et perspectives

Limitations principales:
- securite applicative partiellement en mode development,
- architecture d'execution duale,
- dette documentaire et organisationnelle.

Perspectives:
- convergence vers un seul entrypoint,
- externalisation stricte des secrets,
- pipeline CI/CD avec tests automatiques et quality gates,
- nettoyage des artefacts runtime hors depot.

---

## Plan d'actions priorise (30/60/90 jours)

### Priorite immediate (J+0 a J+7)

1. Securite
- retirer SECRET_KEY hardcodee, imposer variable env obligatoire.
- supprimer credentials admin par defaut en production.
- chiffrer ou externaliser `sender_password` (vault/env secure store).

2. Deployment
- ajouter un `requirements.txt` racine reel (ou corriger Dockerfile vers chemin valide).
- corriger healthcheck Docker vers `/api/health`.

3. Gouvernance lancement
- declarer un entrypoint unique officiel (ex: `run.py --mode run` ou `app/main.py`).

### Court terme (Semaine 2 a 4)

1. Refactoring
- decouper `app/main.py` en modules d'initialisation (app factory, sockets, camera, integrations).

2. Tests
- classer tests par niveau (`unit`, `integration`, `e2e`) et fiabiliser la suite minimale CI.

3. Hygiene repo
- exclure/archiver runtime artifacts (uploads/logs volumineux) hors zone versionnee.

### Moyen terme (M+2 a M+3)

1. Hardening web
- renforcer authn/authz sur endpoints sensibles,
- restreindre CORS a domaines de confiance.

2. Observabilite
- standardiser logs structures + indicateurs de sante.

3. Documentation ciblee
- garder un "README principal" + "runbook ops" + "architecture"; archiver le reste.

---

## Conclusion

Le projet EPI-DETECTION est techniquement riche, ambitieux et deja tres avance fonctionnellement. La valeur metier est claire. Le principal enjeu n'est plus l'ajout de fonctionnalites, mais la stabilisation d'une base d'exploitation professionnelle: securite, reproductibilite, simplification de l'architecture de demarrage et hygiene du depot.

En suivant le plan d'actions priorise ci-dessus, le projet peut passer rapidement d'un excellent prototype integre a une plateforme fiable et defendable en contexte production et memoire M2.

---

## Annexes - Elements factuels utilises

Fichiers references principaux:
- `config.py`
- `app/main.py`
- `app/main_new.py`
- `run.py`
- `run_app.py`
- `app/routes_api.py`
- `app/routes_admin.py`
- `app/routes_notifications_center.py`
- `app/database_unified.py`
- `app/detection.py`
- `Dockerfile`
- `docker-compose.yml`
- `.gitignore`
- `pytest.ini`
- `documentation/README.md`

Template memoire integre:
- `C:\Users\ANDRIANAVALONA\Documents\canevas-INFO-M2-Thematique.docx` (structure des parties/chapitres adaptee)
