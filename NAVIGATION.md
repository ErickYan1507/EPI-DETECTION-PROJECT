# 🗺️ Carte de Navigation du Projet

Bienvenue dans le **EPI Detection System**! Ce document vous aide à naviguer rapidement vers ce que vous cherchez.

---

## 👤 Vous êtes...

### 🚀 Nouvel Utilisateur / Débutant

Commencez ici en 5 minutes:

1. **[README.md](README.md)** - Vue d'ensemble projet
2. **[docs/getting-started.md](docs/getting-started.md)** - Installation & utilisation
3. **Lancez:** `python app/main.py`
4. **Accédez:** http://localhost:5000/unified

**Temps estimé:** 5 minutes ✨

---

### 💻 Développeur / Ingénieur

Comprendre l'architecture:

1. **[docs/architecture/overview.md](docs/architecture/overview.md)** - Vue d'ensemble système
2. **[docs/architecture/backend.md](docs/architecture/backend.md)** - Code Flask
3. **[docs/architecture/frontend.md](docs/architecture/frontend.md)** - Code JavaScript
4. **[docs/api/documentation.md](docs/api/documentation.md)** - API REST endpoints

**Fichiers clés:**
- Backend: `app/main.py`, `app/detection.py`, `app/routes_api.py`
- Frontend: `templates/unified_monitoring.html`
- Config: `config.py`, `.env`

**Temps estimé:** 30 minutes 🔧

---

### 🚢 DevOps / Opérations

Déployer en production:

1. **[docs/deployment/docker.md](docs/deployment/docker.md)** - Containerisation
2. **[docs/deployment/production.md](docs/deployment/production.md)** - Production ready
3. **[docs/deployment/configuration.md](docs/deployment/configuration.md)** - Variables env
4. **[docs/maintenance/monitoring.md](docs/maintenance/monitoring.md)** - Monitoring

**Commandes clés:**
```bash
docker-compose up -d
docker logs -f epi-detection-app
docker exec -it epi-detection-app bash
```

**Temps estimé:** 20 minutes ⚙️

---

### 🔧 Maintenance / Support

Diagnostiquer et réparer:

1. **[docs/maintenance/troubleshooting.md](docs/maintenance/troubleshooting.md)** - Dépannage
2. **[docs/maintenance/monitoring.md](docs/maintenance/monitoring.md)** - Logs & alertes
3. **[check_system.py](check_system.py)** - Script diagnostic

**Problèmes courants:**
- Webcam pas détectée → [Troubleshooting](docs/maintenance/troubleshooting.md#2-webcam-non-détectée)
- Port en usage → [Troubleshooting](docs/maintenance/troubleshooting.md#1-port-5000-déjà-utilisé)
- Modèle manquant → [Troubleshooting](docs/maintenance/troubleshooting.md#3-modèle-yolov5-manquant)

**Temps estimé:** Variable 🆘

---

### 📊 Gestionnaire / Manager

Comprendre le projet:

1. **[RAPPORT_FINAL.md](RAPPORT_FINAL.md)** - État complet du projet
2. **[README.md](README.md)** - Résumé exécutif
3. **[docs/about.md](docs/about.md)** - À propos & roadmap

**Points clés:**
- ✅ Tous les objectifs réalisés
- 📈 Performances: 92% accuracy, 30 FPS
- 🐳 Production-ready avec Docker
- 📚 Documentation complète

**Temps estimé:** 15 minutes 👔

---

### 👨‍🔬 Chercheur / ML Engineer

Améliorer le modèle:

1. **[docs/architecture/backend.md](docs/architecture/backend.md#-détecteur-yolov5---detectionpy)** - YOLOv5 intégré
2. **[app/detection.py](app/detection.py)** - Code détecteur
3. **[train.py](train.py)** - Script d'entraînement
4. **[models/best.pt](models/best.pt)** - Modèle courant

**Tâches courantes:**
- Ré-entraîner modèle: `python train.py`
- Tester inférence: `python test_real_detection.py`
- Analyser performance: `python benchmark_performance.py`

**Temps estimé:** 1-2 heures 🧠

---

## 📁 Structure Fichiers Rapide

```
EPI-DETECTION-PROJECT/
│
├── 📄 README.md                    ← COMMENCEZ ICI
├── 📄 RAPPORT_FINAL.md             ← État du projet
│
├── 🐍 app/
│   ├── main.py                     ← Serveur Flask (point d'entrée)
│   ├── detection.py                ← YOLOv5 intégré
│   ├── routes_api.py               ← API endpoints
│   └── database.py                 ← BD & ORM
│
├── 🎨 templates/
│   └── unified_monitoring.html      ← Dashboard web
│
├── 🐳 Dockerfile                   ← Containerisation
├── 🐳 docker-compose.yml           ← Orchestration
│
├── 📚 docs/
│   ├── index.md                    ← Documentation accueil
│   ├── getting-started.md          ← Guide démarrage
│   ├── architecture/               ← Architecture
│   ├── api/                        ← API documentation
│   ├── deployment/                 ← Déploiement
│   └── maintenance/                ← Maintenance
│
├── 🧪 tests/
│   └── test_*.py                   ← Tests unitaires
│
├── 🤖 models/
│   └── best.pt                     ← Modèle YOLOv5 (production)
│
├── ⚙️ config.py                     ← Configuration
├── ⚙️ .env.example                 ← Variables d'environnement
├── ⚙️ .gitignore                   ← Git exclusions
│
└── 📋 mkdocs.yml                   ← Config MkDocs
```

---

## 🔗 Navigation par Sujet

### Configuration
- [.env.example](.env.example) - Template variables
- [config.py](config.py) - Config application
- [docs/deployment/configuration.md](docs/deployment/configuration.md) - Guide config

### Installation & Démarrage
- [Getting Started](docs/getting-started.md) - Tuto installation
- [Docker Guide](docs/deployment/docker.md) - Déploiement container
- [Production Guide](docs/deployment/production.md) - Production setup

### API & Utilisation
- [API Documentation](docs/api/documentation.md) - Endpoints REST
- [Frontend Architecture](docs/architecture/frontend.md) - UI/UX
- [Backend Architecture](docs/architecture/backend.md) - Server logic

### Déploiement & Opérations
- [Docker Deployment](docs/deployment/docker.md) - Containers
- [Production Deployment](docs/deployment/production.md) - Production
- [Monitoring](docs/maintenance/monitoring.md) - Logs & alertes
- [Troubleshooting](docs/maintenance/troubleshooting.md) - Dépannage

### Modèle ML
- [YOLOv5 Detection](docs/architecture/backend.md#-détecteur-yolov5---detectionpy) - Détecteur
- [Training](train.py) - Entraîner modèle
- [Benchmark](benchmark_performance.py) - Performance

### Documentation
- [Architecture Overview](docs/architecture/overview.md) - Vue d'ensemble
- [About Project](docs/about.md) - À propos & roadmap
- [Final Report](RAPPORT_FINAL.md) - État final

---

## 🎯 Objectifs Courants

### "Je veux démarrer l'application"
```bash
1. pip install -r requirements.txt
2. python app/main.py
3. http://localhost:5000/unified
```
👉 Voir: [Getting Started](docs/getting-started.md)

### "Je veux l'API en production"
```bash
1. docker-compose up -d
2. Configure .env.production
3. Setup Nginx + SSL
```
👉 Voir: [Production Deployment](docs/deployment/production.md)

### "L'app ne fonctionne pas"
```bash
1. Lancer: python check_system.py
2. Vérifier les logs
3. Consulter troubleshooting
```
👉 Voir: [Troubleshooting](docs/maintenance/troubleshooting.md)

### "Je veux comprendre l'architecture"
```bash
1. Lire: Architecture Overview
2. Explorer: Backend & Frontend
3. Tester: API endpoints
```
👉 Voir: [Architecture](docs/architecture/overview.md)

### "Je veux ré-entraîner le modèle"
```bash
1. Préparer dataset
2. Lancer: python train.py
3. Mettre à jour: models/best.pt
```
👉 Voir: [train.py](train.py)

---

## 📞 Aide & Support

### Documentation Locale
- Voir [docs/](docs/) pour toute la documentation
- Générer site local: `mkdocs serve`
- Puis ouvrir: http://localhost:8000

### Diagnostic Complet
```bash
python check_system.py
python diagnose.py
```

### Questions Courantes
👉 [Troubleshooting Guide](docs/maintenance/troubleshooting.md)

### Code Issues
👉 [GitHub Issues](../../issues) (à remplir)

### Discussions
👉 [GitHub Discussions](../../discussions) (à créer)

---

## ⚡ Quick Command Reference

```bash
# Development
python app/main.py                 # Lancer serveur
pytest tests/                      # Lancer tests
mkdocs serve                       # Docs locales

# Docker
docker-compose up -d               # Démarrer
docker-compose logs -f             # Logs
docker-compose down                # Arrêter

# Diagnostic
python check_system.py             # Diagnostic système
python diagnose.py                 # Diagnostic complet
python test_api_detection.py       # Test API

# Training
python train.py                    # Entraîner modèle
python benchmark_performance.py    # Benchmark
```

---

## 🗂️ Index Complet

| Document | Audience | Temps |
|----------|----------|-------|
| [README.md](README.md) | Tous | 5 min |
| [Getting Started](docs/getting-started.md) | Utilisateurs | 5 min |
| [Architecture Overview](docs/architecture/overview.md) | Devs | 15 min |
| [Backend](docs/architecture/backend.md) | Devs Python | 20 min |
| [Frontend](docs/architecture/frontend.md) | Devs JS | 20 min |
| [API Docs](docs/api/documentation.md) | Intégrateurs | 10 min |
| [Docker](docs/deployment/docker.md) | DevOps | 15 min |
| [Production](docs/deployment/production.md) | DevOps | 30 min |
| [Configuration](docs/deployment/configuration.md) | Opérations | 10 min |
| [Monitoring](docs/maintenance/monitoring.md) | Ops/Support | 15 min |
| [Troubleshooting](docs/maintenance/troubleshooting.md) | Support | Variable |
| [About](docs/about.md) | Managers | 15 min |
| [Final Report](RAPPORT_FINAL.md) | Managers | 20 min |

---

## 🎓 Parcours d'Apprentissage

### Chemin Utilisateur
1. README → Getting Started → Dashboard → API Docs → ✅

### Chemin Développeur
1. README → Architecture → Backend → Frontend → Code → ✅

### Chemin DevOps
1. README → Docker → Production → Monitoring → ✅

### Chemin Maintenance
1. README → Troubleshooting → Monitoring → Maintenance → ✅

---

## 💡 Bonnes Pratiques

1. **Toujours lire README.md en premier** 📖
2. **Consulter docs/ avant de coder** 📚
3. **Tester localement avant production** 🧪
4. **Vérifier check_system.py si problème** 🔍
5. **Mettre à jour .env avant de lancer** ⚙️

---

**Besoin d'aide?** 👉 [Troubleshooting](docs/maintenance/troubleshooting.md)

**Prêt à démarrer?** 👉 [Getting Started](docs/getting-started.md)

---

*Dernière mise à jour: 9 Janvier 2026*
