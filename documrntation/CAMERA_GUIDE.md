# Guide d'Utilisation - Détection Caméra en Temps Réel

## Vue d'ensemble

La détection en temps réel via webcam a été intégrée à votre système EPI Detection. Vous pouvez maintenant capturer et analyser des vidéos live avec détection automatique des EPI.

## Comment ça marche

### Architecture

- **Backend**: Routes Flask intégrées dans `app/main.py`
- **Frontend**: Page web `templates/camera.html` avec interface intuitive
- **Streaming**: Flux MJPEG pour visualisation en temps réel
- **Détection**: Utilise le modèle YOLOv5 existant avec statistiques en direct

### Fonctionnalités principales

1. **Démarrage/Arrêt de la caméra**
   - Cliquez sur "Démarrer" pour activer votre webcam
   - Cliquez sur "Arrêter" pour arrêter la capture

2. **Flux vidéo en direct**
   - Affichage MJPEG du flux caméra
   - Boîtes de détection en temps réel
   - Affichage des statistiques de conformité

3. **Statistiques live**
   - Taux de conformité (%)
   - Nombre de personnes détectées
   - Nombre d'EPI par type (casques, gilets, lunettes)
   - Niveau d'alerte (OK, ATTENTION, CRITIQUE)

4. **Capture de frames**
   - Bouton "Capturer" pour télécharger des captures d'écran
   - Sauvegarde automatique en JPEG

5. **Historique des détections**
   - Log des détections récentes
   - Horodatage de chaque détection
   - Affichage du nom de l'EPI et de la confiance

## Routes API disponibles

### POST `/api/camera/start`
Démarre la capture webcam

**Payload:**
```json
{
  "camera_index": 0
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Caméra démarrée"
}
```

### POST `/api/camera/stop`
Arrête la capture webcam

**Réponse:**
```json
{
  "success": true,
  "message": "Caméra arrêtée"
}
```

### GET `/api/camera/stream`
Stream MJPEG continu

**Utilisation:**
```html
<img src="/api/camera/stream">
```

### GET `/api/camera/frame`
Récupère le dernier frame traité en JPEG

### GET `/api/camera/detect`
Récupère les détections et statistiques du frame actuel

**Réponse:**
```json
{
  "detections": [
    {
      "class": "helmet",
      "confidence": 0.95,
      "bbox": [100, 50, 150, 120],
      "color": [0, 255, 0]
    }
  ],
  "statistics": {
    "total_persons": 2,
    "with_helmet": 2,
    "with_vest": 1,
    "with_glasses": 0,
    "with_boots": 0,
    "compliance_rate": 100.0,
    "compliance_level": "excellent",
    "alert_type": "safe"
  },
  "detection_id": 42
}
```

## Utilisation

### Interface Web

1. Accédez à: `http://localhost:5000/camera`
2. Cliquez sur **"Démarrer"** pour activer la webcam
3. Le flux apparaîtra en direct avec les détections
4. Observez les statistiques en temps réel sur le panneau droit
5. Cliquez sur **"Capturer"** pour télécharger une capture
6. Cliquez sur **"Arrêter"** pour fermer la webcam

### Intégration Programmée

```python
import requests

# Démarrer la caméra
requests.post('http://localhost:5000/api/camera/start', 
              json={'camera_index': 0})

# Obtenir les détections
response = requests.get('http://localhost:5000/api/camera/detect')
data = response.json()
print(f"Conformité: {data['statistics']['compliance_rate']}%")

# Arrêter la caméra
requests.post('http://localhost:5000/api/camera/stop')
```

## Configuration

### Indices de caméra

- `0`: Webcam par défaut
- `1`, `2`, etc.: Caméras additionnelles (si disponibles)

Pour découvrir les caméras disponibles:

```python
import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Caméra {i}: disponible")
        cap.release()
    else:
        print(f"Caméra {i}: non disponible")
```

### Paramètres de qualité

Les paramètres de streaming sont configurés dans `app/main.py`:

```python
camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)    # Largeur
camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)    # Hauteur
camera_capture.set(cv2.CAP_PROP_FPS, 30)             # Frames par seconde
```

Ajustez ces valeurs selon vos besoins de performance/qualité.

## Données sauvegardées

Chaque détection effectuée via la caméra est automatiquement sauvegardée dans la base de données:

- Image source: `camera_live`
- Statistiques: personnes, EPI détectés, taux de conformité
- Timestamp: date/heure de la détection
- Type d'alerte: safe, warning, danger

Ces données sont ensuite disponibles dans:
- Le dashboard `/dashboard`
- L'API `/api/stats`
- Les exports PDF/CSV

## Dépannage

### La caméra ne démarre pas
- Vérifiez que votre webcam est connectée et fonctionnelle
- Vérifiez que les permissions d'accès webcam sont accordées
- Essayez un redémarrage de l'application

### Le flux vidéo est lent
- Réduisez la résolution (1280x720 → 640x480)
- Réduisez la qualité JPEG (80 → 60)
- Vérifiez la charge CPU

### Les détections sont peu précises
- Améliorez l'éclairage
- Positionnez la caméra correctement
- Consultez `models/best.pt` pour ajuster le modèle

## Notes

- Le streaming MJPEG peut consommer beaucoup de bande passante
- Les détections sont traitées en temps réel (latence ~100-300ms)
- Les données sont persistantes en base de données
- Compatible avec les systèmes multi-caméra (à développer)

## Voir aussi

- `/dashboard` - Vue d'ensemble des détections
- `/realtime` - Monitoring en temps réel
- `/api/stats` - Statistiques globales
