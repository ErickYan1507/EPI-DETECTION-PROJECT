# Guide de Dépannage - Détection Non Fonctionnelle

## Problème: unified_monitoring.html ne détecte pas les personnes

### Étapes de Diagnostic

#### 1. Vérifier que le serveur fonctionne

```bash
# Démarrer le serveur
python run_app.py

# Vérifier dans les logs
# Doit afficher: "MultiModelDetector initialisé: X modèles"
```

#### 2. Tester l'API directement

```bash
# Test 1: Health check
python test_api_detection.py

# OU avec curl
curl http://localhost:5000/api/health
```

**Résultat attendu:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "multi_model_enabled": true,
  "models_loaded": 4,
  "ensemble_mode": true
}
```

#### 3. Tester avec la page de test

1. Ouvrir: http://localhost:5000/test-detection
2. Cliquer "Tester /api/health"
3. Cliquer "Démarrer Webcam"
4. Cliquer "Détecter"

Vérifier les logs dans la section "Logs Console"

#### 4. Vérifier la console du navigateur

1. Ouvrir http://localhost:5000/unified
2. Appuyer sur F12 (Developer Tools)
3. Aller dans l'onglet "Console"
4. Démarrer la webcam
5. Chercher les erreurs en rouge

### Problèmes Courants et Solutions

#### Erreur: "Aucun modèle .pt trouvé"

**Cause:** Le dossier `models/` est vide ou les modèles ne sont pas au bon endroit.

**Solution:**
```bash
# Vérifier le contenu du dossier models/
ls -la models/

# Doit contenir au minimum:
# - best.pt
# - epi_detection_session_003.pt (optionnel)
# - epi_detection_session_004.pt (optionnel)
# - epi_detection_session_005.pt (optionnel)
```

Si les modèles sont manquants:
1. Entraîner un modèle: `python train.py`
2. OU copier un modèle pré-entraîné dans `models/best.pt`

#### Erreur: "Détecteur non initialisé"

**Cause:** Le détecteur n'a pas pu se charger au démarrage.

**Solution:**
```bash
# Vérifier les logs au démarrage
python run_app.py 2>&1 | grep -i "detect"

# Doit afficher:
# "Initialisation du MultiModelDetector..."
# "MultiModelDetector initialisé: X modèles"
```

Si l'erreur persiste:
- Vérifier que PyTorch est installé: `pip install torch`
- Vérifier que YOLOv5 est accessible: `pip install ultralytics`

#### Erreur: "Video dimensions not ready yet"

**Cause:** La webcam n'est pas encore prête ou n'a pas les permissions.

**Solution:**
1. Autoriser l'accès à la webcam dans le navigateur
2. Attendre 2-3 secondes après le démarrage de la webcam
3. Vérifier que la webcam fonctionne: http://localhost:5000/test-detection

#### Erreur: "Erreur API détection: 400" ou "500"

**Cause:** Format de l'image invalide ou erreur backend.

**Solution:**
1. Vérifier les logs serveur Flask
2. Tester avec curl:
```bash
# Créer une image de test base64
python -c "import cv2, base64; img=cv2.imread('aa.jpg'); _, buf=cv2.imencode('.jpg', img); print(f'data:image/jpeg;base64,{base64.b64encode(buf).decode()}')" > test_image.txt

# Tester l'API
curl -X POST http://localhost:5000/api/detect \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$(cat test_image.txt)\"}"
```

#### Détections = 0 (personnes non détectées)

**Cause:** Le modèle ne détecte rien dans l'image.

**Diagnostic:**
1. Tester avec une image connue:
```bash
python detect.py --image images/aa.jpg
```

2. Vérifier la qualité de l'image:
   - Éclairage suffisant?
   - Personnes visibles et de face?
   - Distance appropriée (pas trop loin)?

3. Vérifier les seuils de confiance:
```python
# Dans config.py
CONFIDENCE_THRESHOLD = 0.25  # Essayer 0.1 pour tester
```

4. Tester le modèle:
```bash
python test_multi_model.py
```

#### Erreur: "Failed to fetch" ou "Network error"

**Cause:** Le serveur Flask n'est pas accessible.

**Solution:**
1. Vérifier que le serveur est démarré: `netstat -an | grep 5000`
2. Vérifier le pare-feu
3. Essayer: http://127.0.0.1:5000 au lieu de localhost

#### Performances lentes (>5 secondes par détection)

**Cause:** Mode ensemble activé sans GPU.

**Solution:**
```python
# Dans config.py
USE_ENSEMBLE_FOR_CAMERA = False  # Utiliser single pour caméra
MULTI_MODEL_ENABLED = True  # Garder activé pour uploads

# OU désactiver half precision
ENABLE_HALF_PRECISION = False
```

### Vérifications Supplémentaires

#### Vérifier la configuration

```python
# Dans config.py
print(f"MULTI_MODEL_ENABLED: {config.MULTI_MODEL_ENABLED}")
print(f"MODELS_FOLDER: {config.MODELS_FOLDER}")
print(f"USE_ENSEMBLE_FOR_CAMERA: {config.USE_ENSEMBLE_FOR_CAMERA}")
```

#### Vérifier les dépendances

```bash
pip list | grep -E "(torch|opencv|ultralytics|flask)"

# Doit afficher:
# torch                1.x.x
# opencv-python        4.x.x
# Flask                2.x.x ou 3.x.x
```

#### Tester manuellement la détection

```python
# test_manual.py
from app.multi_model_detector import MultiModelDetector
import cv2

detector = MultiModelDetector(use_ensemble=False)
image = cv2.imread('aa.jpg')
detections, stats = detector.detect(image)

print(f"Détections: {len(detections)}")
print(f"Personnes: {stats['total_persons']}")
print(f"Casques: {stats['with_helmet']}")
```

### Logs Utiles à Vérifier

```bash
# Logs Flask
tail -f logs/app.log

# Chercher:
# - "MultiModelDetector initialisé"
# - "Détection réussie" ou "Erreur détection"
# - "Modèle chargé"
```

### Contact Support

Si le problème persiste après ces étapes:

1. Exécuter le diagnostic complet:
```bash
python test_api_detection.py > diagnostic.txt 2>&1
python test_multi_model.py >> diagnostic.txt 2>&1
```

2. Collecter les informations:
   - Version Python: `python --version`
   - Logs serveur: `tail -100 logs/app.log`
   - Configuration: `cat config.py`

3. Partager le fichier diagnostic.txt

### Checklist Rapide

- [ ] Serveur Flask démarré (`python run_app.py`)
- [ ] Au moins un modèle dans `models/` (ex: `best.pt`)
- [ ] API health répond: `curl http://localhost:5000/api/health`
- [ ] Page test fonctionne: http://localhost:5000/test-detection
- [ ] Webcam autorisée dans le navigateur
- [ ] Console navigateur (F12) sans erreurs rouges
- [ ] Test manuel avec `python test_api_detection.py` réussi

### Solution Rapide (Reset)

Si rien ne fonctionne, réinitialiser:

```bash
# 1. Arrêter le serveur
pkill -f run_app.py

# 2. Supprimer les caches
rm -rf __pycache__ app/__pycache__

# 3. Redémarrer proprement
python run_app.py

# 4. Tester immédiatement
python test_api_detection.py
```