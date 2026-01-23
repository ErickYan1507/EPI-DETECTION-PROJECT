# 📋 RESTRUCTURATION DU PROJET EPI DETECTION

## ✅ Fichiers créés/modifiés

### Fichiers de configuration et support
- ✅ `config.py` - Configuration centrale (améliorée)
- ✅ `.env.example` - Variables d'environnement
- ✅ `test_config.py` - Configuration de test
- ✅ `requirements.txt` - Dépendances Python

### Fichiers app/
- ✅ `app/constants.py` - Énumérations et constantes
- ✅ `app/logger.py` - Logging centralisé
- ✅ `app/utils.py` - Fonctions utilitaires
- ✅ `app/database_new.py` - Modèles améliorés avec relations
- ✅ `app/detection.py` - Détecteur EPI (modifié pour utiliser nouveaux modules)
- ✅ `app/routes_api.py` - Endpoints API REST
- ✅ `app/init.py` - Initialisation des composants
- ✅ `app/main_new.py` - Application Flask restructurée

### Fichiers scripts et CLI
- ✅ `run_app.py` - Lanceur principal de l'application
- ✅ `cli.py` - Interface en ligne de commande
- ✅ `init.py` - Script d'initialisation du projet

### Documentation
- ✅ `README.md` - Documentation complète
- ✅ `RESTRUCTURATION.md` - Ce fichier

## 🔗 Liens entre modules

### Hiérarchie des imports

```
config.py
    ↓
app/constants.py, app/logger.py, app/utils.py
    ↓
app/detection.py, app/database_new.py
    ↓
app/routes_api.py, app/dashboard.py
    ↓
app/main_new.py
    ↓
run_app.py / cli.py
```

### Flux de données

1. **Configuration**: `config.py` → utilisé par tous les modules
2. **Logging**: `logger.py` → utilisé par `detection.py`, `routes_api.py`
3. **Utils**: `utils.py` → utilisé par `routes_api.py`, `init.py`
4. **Constants**: `constants.py` → utilisé par `detection.py`, `routes_api.py`
5. **Database**: `database_new.py` → relations avec `routes_api.py`, `dashboard.py`
6. **Detection**: `detection.py` → utilisé par `routes_api.py`
7. **Routes**: `routes_api.py`, `dashboard.py` → enregistrées dans `main_new.py`
8. **App**: `main_new.py` → lancée par `run_app.py`

## 🎯 Fonctionnalités

### API REST
- `POST /api/detect` - Détecter les EPI sur une image
- `GET /api/detections` - Récupérer les détections
- `GET /api/alerts` - Récupérer les alertes
- `GET /api/stats` - Statistiques globales
- `GET /api/health` - Vérifier l'état

### CLI
```bash
python cli.py init-db              # Initialiser la BDD
python cli.py drop-db              # Supprimer la BDD
python cli.py show-stats           # Afficher les stats
python cli.py add-worker            # Ajouter un travailleur
python cli.py list-workers          # Lister les travailleurs
python cli.py show-recent-alerts    # Alertes récentes
python cli.py cleanup --days 30     # Nettoyer les anciennes données
python cli.py export-stats          # Exporter en CSV
```

### Scripts
```bash
python init.py                      # Initialiser le projet
python run_app.py dev              # Lancer en dev
python run_app.py prod             # Lancer en prod
python run_app.py train            # Entraîner le modèle
python train.py --epochs 100       # Entraînement avec paramètres
```

## 📊 Structure améliorée

### Avant
- Configuration fragmentée
- Modèles de données basiques
- Pas de logging centralisé
- Imports circulaires possibles
- Pas de CLI

### Après
- Configuration centralisée et hiérarchisée
- Modèles enrichis avec relations et méthodes
- Logging structuré et configurable
- Imports organisés et linéaires
- CLI complète pour administration

## 🚀 Usage

### Initialisation (première fois)
```bash
python init.py
python train.py --epochs 50 --batch-size 8
```

### Lancer l'application
```bash
# Développement
python run_app.py dev

# Production
python run_app.py prod

# Ou avec gunicorn
gunicorn --worker-class eventlet -w 1 app.main_new:app
```

### Utiliser l'API
```bash
# Détecter
curl -X POST -F "image=@test.jpg" http://localhost:5000/api/detect

# Récupérer les détections
curl http://localhost:5000/api/detections?limit=10

# Voir les stats
curl http://localhost:5000/api/stats

# Voir les alertes
curl http://localhost:5000/api/alerts
```

## 🔐 Améliorations de sécurité

1. Configuration par environnement (dev/prod/test)
2. Secrets gérés via `.env`
3. Validation des fichiers uploadés
4. Logging sécurisé
5. CORS configuré correctement
6. MaxContentLength limité

## 📈 Prochaines étapes recommandées

1. ✅ Lancer `python init.py`
2. ✅ Entraîner le modèle: `python train.py`
3. ✅ Tester l'API: `python run_app.py dev`
4. ✅ Ajouter des travailleurs: `python cli.py add-worker`
5. ✅ Configurer les notifications (si nécessaire)
6. ✅ Déployer en production avec gunicorn

## 📝 Notes

- Les fichiers anciens (`main.py`, `database.py`) sont conservés pour compatibilité
- Les nouveaux fichiers (_new) peuvent être renommés après transition
- Ajouter `PYTHONPATH=.` si les imports ne fonctionnent pas
- Utiliser `.env` pour toutes les configurations sensibles

## 🆘 Support

Pour toute question, vérifier:
1. Le fichier `.env` est correctement configuré
2. La base de données est initialisée: `python cli.py init-db`
3. Les logs: vérifier le dossier `logs/`
4. La santé de l'app: `curl http://localhost:5000/api/health`
