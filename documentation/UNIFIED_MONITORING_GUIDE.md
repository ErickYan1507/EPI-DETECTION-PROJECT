# 🎯 GUIDE COMPLET - UNIFIED MONITORING DETECTION

## Problème Identifié et Corrigé ✅

**Problème**: La détection ne fonctionnait pas sur le dashboard **unified_monitoring** même avec la caméra activée.

**Cause Root**: Les variables globales `multi_detector` et `detector` n'étaient pas accessibles dans le thread de la caméra (`_run()`) faute de déclaration `global`.

**Solution Appliquée**: Ajout de `global multi_detector, detector` au début de la fonction `_run()` dans `app/main.py` (ligne 125).

---

## Lancer le Système

### 1️⃣ **Démarrer Flask**

```bash
# Option 1: Lancer normalement
python app/main.py

# Option 2: Avec le fichier run_app.py
python run_app.py

# Option 3: Mode développement (-dev)
python run_app.py dev
```

Attendez que vous voyiez ce message:
```
[2026-02-20 XX:XX:XX] epi_detection - INFO - ✅ MultiModelDetector initialisé: 1 modèles disponibles
[2026-02-20 XX:XX:XX] epi_detection - INFO - 🌐 Accédez à l'application via le navigateur:
   → http://127.0.0.1:5000
```

### 2️⃣ **Accéder à Unified Monitoring**

Naviguer vers:
```
http://localhost:5000/unified_monitoring.html
```

### 3️⃣ **Activer la Caméra**

1. Sur le dashboard, cliquer sur **"Démarrer Caméra"** (bouton rouge)
2. Attendre 3-5 secondes pour que le flux vidéo s'affiche
3. Les détections devraient apparaître automatiquement avec:
   - **Boîtes de détection** autour des personnes
   - **Statistiques en temps réel** (casque, gilet, lunettes)
   - **Conformité %** 
   - **Au ors d'alerte** si nécessaire

---

## 🔍 Dépannage

### La caméra n'apparaît pas

```python
# Test de connectivité caméra
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

Essayer un index différent:
```python
python -c "
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f'Caméra trouvée à index {i}')
        cap.release()
"
```

### Aucune détection visible

1. Vérifier les logs Flask pour les erreurs
2. Vérifier que `models/best.pt` existe
3. Tester la détection sur image:
   ```
   http://localhost:5000/upload
   ```

### Erreur "MultiModelDetector not initialized"

Assurez-vous que le détecteur est initialisé au démarrage:
1. Vérifier que `python app/main.py` lance sans erreur
2. Attendre le message "✅ MultiModelDetector initialisé"
3. Redémarrer Flask si nécessaire

---

## 📊 Structure du Système

```
app/main.py
├── Initialise MultiModelDetector (ligne 413-420)
├── CameraManager (_run thread) 
│   ├── Démarre caméra via /api/camera/start
│   ├── Lit frames en temps réel
│   └── Applique détection avec global multi_detector
├── Routes API
│   ├── /api/camera/start - Démarre caméra
│   ├── /api/camera/stream - Flux vidéo
│   ├── /api/camera/detect - Résultats détection
│   └── /api/camera/frame - Frame actuel
└── WebSocket
    └── Envoie mises à jour temps réel

templates/unified_monitoring.html
└── Affiche:
    - Flux caméra en direct
    - Détections temps réel
    - Statistiques
    - Alertes
```

---

## ✅ Vérification Complète

```bash
# 1. Vérifier les modèles
ls models/      # Doit voir: best.pt

# 2. Vérifier la configuration
python -c "from config import config; print(f'MODELS_FOLDER={config.MODELS_FOLDER}')"

# 3. Tester les détecteurs
python test_detector_init.py

# 4. Lancer Flask
python app/main.py

# 5. Ouvrir le navigateur
# http://localhost:5000/unified_monitoring.html
```

---

## 📝 Notes Importantes

- La détection utilise **CPU** (visible "YOLOv5 ... CPU" dans les logs)
- Chaque frame prend ~500-1000ms (1-2 FPS en temps réel)
- Pour GPU: installer `torch[cuda]` et modifier config
- MultiModelDetector supporte plusieurs modèles (actuellement: 1)

---

## 🚀 Prochaines Étapes

Pour **améliorer les performances**:

1. **Plus de modèles** → Placer `.pt` dans `models/`
2. **Mode ensemble** → Modifier config ou utiliser l'API `?use_ensemble=true`
3. **GPU** → Installer CUDA et pytorch avec GPU
4. **Frame Skip** → Augmenter `config.FRAME_SKIP` (sauter frames)

---

## 💬 Questions Fréquentes

**P: Pourquoi "Aucun détecteur disponible"?**
R: Le détecteur n'a pas pu se charger au démarrage. Vérifier les logs Flask pour les erreurs.

**P: Comment ajouter plusieurs modèles?**
R: Placer les `.pt` dans le dossier `models/` et redémarrer Flask.

**P: Peut-on detecter en offline?**
R: Oui! YOLOv5 local est utilisé (dossier `yolov5/`).

**P: Comment tester sans caméra?**
R: Utiliser `/upload` pour tester sur images.
