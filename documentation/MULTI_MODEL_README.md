# Système Multi-Modèles EPI Detection

## Vue d'ensemble

Le système multi-modèles permet d'utiliser **tous les modèles entraînés** disponibles dans le dossier `models/` pour améliorer la précision et la robustesse de la détection EPI. Au lieu d'utiliser un seul modèle (best.pt), le système peut combiner les prédictions de plusieurs modèles pour obtenir de meilleurs résultats.

## Modèles Disponibles

Le système charge automatiquement tous les fichiers `.pt` du dossier `models/`:
- `best.pt` - Modèle principal (poids: 1.0)
- `epi_detection_session_003.pt` (poids: 0.8)
- `epi_detection_session_004.pt` (poids: 0.9)
- `epi_detection_session_005.pt` (poids: 0.85)

## Modes de Fonctionnement

### Mode Single
- **Utilisation**: Un seul modèle (best.pt par défaut)
- **Avantages**: Performance maximale, temps d'inférence rapide
- **Utilisation recommandée**: Caméra en temps réel, vidéos

### Mode Ensemble
- **Utilisation**: Tous les modèles disponibles avec agrégation des résultats
- **Avantages**: Meilleure précision, réduction des faux positifs/négatifs
- **Utilisation recommandée**: Upload d'images, analyse approfondie

## Stratégies d'Agrégation

### 1. Weighted Voting (Par défaut)
- Combine les détections avec vote pondéré
- Nécessite un minimum de votes (MIN_ENSEMBLE_VOTES)
- Moyenne les boîtes englobantes et confidences

### 2. Union NMS
- Combine toutes les détections
- Applique NMS (Non-Maximum Suppression) pour éliminer les duplicatas

### 3. Average
- Calcule la moyenne des confidences pour détections similaires

## Configuration

### Fichier `config.py`

```python
# Activer/désactiver le système multi-modèles
MULTI_MODEL_ENABLED = True

# Stratégie d'agrégation
ENSEMBLE_STRATEGY = 'weighted_voting'  # ou 'union_nms', 'average'

# Poids des modèles
MODEL_WEIGHTS = {
    'best.pt': 1.0,
    'epi_detection_session_003.pt': 0.8,
    'epi_detection_session_004.pt': 0.9,
    'epi_detection_session_005.pt': 0.85
}

# Seuil IoU pour NMS
NMS_IOU_THRESHOLD = 0.5

# Votes minimum requis (weighted_voting)
MIN_ENSEMBLE_VOTES = 2

# Mode ensemble par défaut
DEFAULT_USE_ENSEMBLE = True

# Utiliser ensemble pour caméra (impact performance)
USE_ENSEMBLE_FOR_CAMERA = False
```

### Variables d'environnement

```bash
# Activer multi-modèles
export MULTI_MODEL_ENABLED=True

# Choisir stratégie
export ENSEMBLE_STRATEGY=weighted_voting
```

## Utilisation

### Dans le code Python

```python
from app.multi_model_detector import MultiModelDetector

# Initialiser le détecteur
detector = MultiModelDetector(use_ensemble=True)

# Détection en mode ensemble
detections, stats = detector.detect(image, use_ensemble=True)

# Détection en mode single
detections, stats = detector.detect(image, use_ensemble=False)

# Obtenir la liste des modèles
models = detector.get_model_list()

# Changer le mode
detector.set_ensemble_mode(True)
```

### Via l'API REST

#### Détection avec mode sélectionnable
```bash
# Mode ensemble (par défaut)
curl -X POST http://localhost:5000/api/detect \
  -F "image=@test.jpg" \
  -F "use_ensemble=true"

# Mode single
curl -X POST http://localhost:5000/api/detect \
  -F "image=@test.jpg" \
  -F "use_ensemble=false"
```

#### Liste des modèles
```bash
curl http://localhost:5000/api/models/list
```

#### Changer le mode
```bash
curl -X POST http://localhost:5000/api/models/mode \
  -H "Content-Type: application/json" \
  -d '{"use_ensemble": true}'
```

#### Comparer les modèles
```bash
curl -X POST http://localhost:5000/api/models/compare \
  -F "image=@test.jpg"
```

### Dans l'interface web (unified_monitoring.html)

1. Ouvrir `http://localhost:5000/unified`
2. Dans la barre de statut en haut, sélectionner le mode:
   - **Ensemble (Multi-Modèles)**: Utilise tous les modèles
   - **Single (best.pt)**: Utilise uniquement best.pt

## Traçabilité

Chaque détection est enregistrée en base de données avec les métadonnées suivantes:

- `model_used`: Nom du/des modèle(s) utilisé(s)
- `ensemble_mode`: Boolean indiquant si le mode ensemble était activé
- `model_votes`: JSON contenant les votes de chaque modèle
- `aggregation_method`: Méthode d'agrégation utilisée

### Migration de la base de données

Pour ajouter les colonnes de traçabilité:

```bash
python migrate_add_model_tracking.py
```

## Tests

### Script de test complet

```bash
python test_multi_model.py
```

Tests effectués:
1. Liste des modèles disponibles
2. Mode Single (best.pt uniquement)
3. Mode Ensemble (tous les modèles)
4. Comparaison des performances

### Script detect.py

Le script `detect.py` supporte déjà les multi-modèles:

```bash
# Utiliser tous les modèles
python detect.py --image test.jpg

# Utiliser un modèle spécifique
python detect.py --image test.jpg --model models/best.pt
```

## Performance

### Temps d'inférence typiques

| Mode | Temps (CPU) | Temps (GPU) |
|------|-------------|-------------|
| Single | ~100ms | ~30ms |
| Ensemble (4 modèles) | ~400ms | ~120ms |

### Recommandations

- **Caméra en temps réel**: Mode Single (USE_ENSEMBLE_FOR_CAMERA=False)
- **Upload d'images**: Mode Ensemble (meilleure précision)
- **Traitement vidéo**: Mode Single (performance)
- **Analyse approfondie**: Mode Ensemble avec comparaison

## Optimisations

### Mémoire
- Utiliser lazy loading pour charger les modèles à la demande
- Mode CPU pour modèles secondaires si GPU limité

### Performance
- Ajuster MIN_ENSEMBLE_VOTES pour compromis précision/rappel
- Utiliser NMS_IOU_THRESHOLD adapté à vos besoins

## Dépannage

### Erreur: "Aucun modèle .pt trouvé"
- Vérifier que le dossier `models/` contient des fichiers .pt
- Vérifier les permissions de lecture

### Erreur mémoire GPU
- Réduire le nombre de modèles
- Désactiver ENABLE_HALF_PRECISION
- Utiliser USE_ENSEMBLE_FOR_CAMERA=False

### Performance lente
- Utiliser mode Single pour temps réel
- Vérifier MULTI_MODEL_ENABLED=True
- Optimiser MODEL_WEIGHTS

## Intégration dans les Projets

Le système multi-modèles est intégré dans:

✅ **app/main.py** - Application Flask principale
- CameraManager utilise mode configurable
- process_image() utilise mode ensemble pour uploads
- process_video() utilise mode single pour performance

✅ **app/routes_api.py** - API REST
- Endpoint `/api/detect` avec paramètre `use_ensemble`
- Nouveaux endpoints pour gestion multi-modèles

✅ **detect.py** - Script CLI
- Support natif multi-modèles

✅ **templates/unified_monitoring.html** - Interface web
- Sélecteur de mode dans la barre de statut
- Détection temps réel avec mode choisi

✅ **Base de données** - Traçabilité
- Colonnes ajoutées pour métadonnées multi-modèles

## Support

Pour toute question ou problème:
1. Vérifier les logs dans `logs/app.log`
2. Tester avec `test_multi_model.py`
3. Vérifier la configuration dans `config.py`

## Contribution

Pour ajouter un nouveau modèle:
1. Copier le fichier `.pt` dans `models/`
2. Ajouter l'entrée dans `MODEL_WEIGHTS` (config.py)
3. Redémarrer l'application