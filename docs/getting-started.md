# Guide de Démarrage

## 📋 Prérequis Système

- **OS:** Windows 10+ / macOS 10.15+ / Linux (Ubuntu 20.04+)
- **Python:** 3.13+
- **RAM:** 4GB minimum (8GB recommandé)
- **GPU:** Optionnel (NVIDIA CUDA pour accélération)
- **Webcam:** USB ou intégrée

## 🔧 Installation

### 1. Cloner le Dépôt

```bash
git clone https://github.com/yourusername/EPI-DETECTION-PROJECT.git
cd EPI-DETECTION-PROJECT
```

### 2. Créer l'Environnement Virtuel

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les Dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🚀 Lancer l'Application

### Option 1: Python Direct

```bash
python app/main.py
```

**Sortie attendue:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Option 2: Docker

```bash
docker-compose up -d
```

## 🌐 Accéder au Dashboard

Ouvrir le navigateur:
```
http://localhost:5000/unified
```

### Éléments du Dashboard

| Élément | Description |
|---------|------------|
| **Flux Webcam** | Vidéo en temps réel (gauche) |
| **Détections** | Boîtes englobantes YOLOv5 (superposées) |
| **Statistiques** | Graphiques en temps réel (droite) |
| **Boutons** | Démarrer/Arrêter caméra |
| **Mode** | Dark/Light toggle |

## 🎥 Tester la Détection

1. Cliquer **"▶ Démarrer caméra"**
2. Accepter les permissions webcam
3. Porter des équipements de sécurité devant la caméra
4. Observer les détections en temps réel

## 📊 Explorer l'API

```bash
# Tester la détection via API
curl -X POST http://localhost:5000/api/detect \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_image"}'
```

## 🔗 Ressources Utiles

- [Architecture Système](architecture/overview.md)
- [Documentation API](api/documentation.md)
- [Dépannage](maintenance/troubleshooting.md)
- [Variables d'Environnement](deployment/configuration.md)

## ⚠️ Problèmes Courants

### Port 5000 Déjà Utilisé
```bash
# Linux/macOS
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Webcam Non Détectée
1. Vérifier les permissions du navigateur
2. Tester avec: `python check_system.py`
3. Redémarrer le navigateur

### Modèle YOLOv5 Manquant
```bash
python -c "from app.detection import EPIDetector; EPIDetector()"
```

## 📚 Prochaines Étapes

- [ ] Lire [Architecture](architecture/overview.md)
- [ ] Configurer [Variables d'Environnement](deployment/configuration.md)
- [ ] Étudier [API Endpoints](api/endpoints.md)
- [ ] Déployer avec [Docker](deployment/docker.md)
