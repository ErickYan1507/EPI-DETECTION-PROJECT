# EPI Detection System

**Système de détection d'Équipements de Protection Individuelle en temps réel utilisant YOLOv5**

![Status](https://img.shields.io/badge/Status-Production-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Vue d'ensemble

Le **EPI Detection System** est une application web complète permettant la détection en temps réel des équipements de protection individuelle (casques, gilets de sécurité, lunettes, etc.) via webcam, avec :

- ✅ Dashboard interactif en temps réel
- ✅ API REST documentée
- ✅ Alertes configurables
- ✅ Exports de données (PDF, Power BI)
- ✅ Modèle YOLOv5 (92%+ précision)
- ✅ Communication Arduino
- ✅ Base de données SQLite

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.13+
- Docker & Docker Compose (optionnel)
- Webcam

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/EPI-DETECTION-PROJECT.git
cd EPI-DETECTION-PROJECT

# Créer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app/main.py
```

### Accès au Dashboard
```
http://localhost:5000/unified
```

## 🐳 Docker

```bash
# Démarrer avec Docker Compose
docker-compose up -d

# Accéder à l'application
http://localhost:5000
```

## 📚 Documentation

- [Guide de Démarrage](getting-started.md)
- [Architecture](architecture/overview.md)
- [API Documentation](api/documentation.md)
- [Déploiement](deployment/docker.md)

## 📊 Caractéristiques Principales

### 1. Détection en Temps Réel
- Modèle YOLOv5 optimisé
- Inférence 20-50ms par image
- Support multiprocesseur

### 2. Dashboard Interactif
- Flux vidéo webcam
- Graphiques en temps réel
- Statistiques détaillées
- Mode sombre/clair

### 3. API REST
- Routes documentées `/api/detect`, `/api/stats`
- JSON structuré
- Authentification JWT (optionnel)

### 4. Alertes & Notifications
- Configuration flexible
- Communication Arduino
- Email & SMS (futur)

### 5. Base de Données
- SQLite pour le développement
- Support PostgreSQL (production)
- Export SQL

## 📁 Structure du Projet

```
EPI-DETECTION-PROJECT/
├── app/                    # Application Flask
│   ├── main.py            # Point d'entrée
│   ├── detection.py       # Logique détection YOLOv5
│   ├── routes_api.py      # Endpoints API
│   └── database.py        # Gestion BD
├── models/                # Modèles ML
│   └── best.pt           # Modèle YOLOv5 (production)
├── templates/            # Frontend HTML/CSS/JS
│   └── unified_monitoring.html
├── static/              # Assets (images, CSS)
├── docs/                # Documentation MkDocs
├── Dockerfile           # Conteneurisation
└── docker-compose.yml   # Orchestration
```

## 🔧 Configuration

Voir [Configuration](deployment/configuration.md) pour les variables d'environnement.

## 📈 Performances

| Métrique | Valeur |
|----------|--------|
| Précision | 92%+ |
| Inférence | 20-50ms |
| FPS | 20-30 |
| Latence Totale | ~100ms |
| Modèle Taille | 7MB |

## 🤝 Contribution

Les contributions sont bienvenues ! Veuillez consulter [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE)

## 📞 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/EPI-DETECTION-PROJECT/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/EPI-DETECTION-PROJECT/discussions)

---

**Version:** 1.0.0 | **Dernière mise à jour:** Janvier 2026
