# 🧪 TEST RAPIDE - UNIFIED MONITORING

## ⚡ 5 Minutes pour Tester

### Étape 1: Lancer Flask (1 min)
```bash
python app/main.py
```

**Cherchez ce message WARNING:**
```
✅ MultiModelDetector initialisé: 1 modèles disponibles
```

### Étape 2: Ouvrir le Dashboard (30 sec)
Naviguer dans votre navigateur:
```
http://localhost:5000/unified_monitoring.html
```

### Étape 3: Démarrer la Caméra (30 sec)
Cliquer sur le bouton rouge **"Démarrer Caméra"** en haut à gauche

### Étape 4: Observer les Détections (3 min)
- Vous devez voir un **flux vidéo en direct**
- Les **boîtes de détection** autour des personnes
- Les **statistiques en bas** (casque, gilet, etc)
- Le **pourcentage de conformité**

---

## ✅ Checklist de Succès

- [ ] Flask démarre sans erreur
- [ ] "MultiModelDetector initialisé" apparaît dans les logs
- [ ] Le dashboard charge en HTML
- [ ] Cliquer "Démarrer Caméra" active le flux
- [ ] Les images s'affichent à l'écran
- [ ] Les boîtes de détection s'affichent autour des personnes
- [ ] Les statistiques "Personnes: X" s'actualisent

---

## ❌ Si Ça Ne Marche Pas

### Problème #1: Flask ne démarre pas
```
❌ ModuleNotFoundError: No module named 'app'
```
→ Assurez-vous que vous êtes dans le dossier du projet:
```bash
cd d:\projet\EPI-DETECTION-PROJECT
python app/main.py
```

### Problème #2: Caméra n'apparaît pas
```
⚠️ "No frame available" ou flux noir
```
→ Tester la caméra:
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

Si "FAIL", essayer un index différent dans le code:
```python
# Dans unified_monitoring.html, chercher:
fetch('/api/camera/start', {
    method: 'POST',
    body: JSON.stringify({ camera_index: 0 })  # Try 1, 2, etc
})
```

### Problème #3: Détections ne s'affichent pas
```
✅ Caméra marche mais pas de boîtes de détection
```
→ Vérifier les logs Flask pour erreur de détecteur:
```bash
# Dans les logs Flask, chercher:
"ERROR" ou "Erreur détection"
```

Si "Aucun détecteur disponible", redémarrer Flask:
1. Arrêter Flask (Ctrl+C)
2. Attendre 2 secondes
3. Relancer: `python app/main.py`

### Problème #4: Performance très lente
```
⏱️ Détection prend 5+ secondes par frame
```
→ Normal sur CPU! Pour CPU lent:
1. Augmenter `FRAME_SKIP` dans `config.py`
2. Ou utiliser GPU (installer torch[cuda])

---

## 🔧 Test Déconnecté (Sans Caméra)

Si vous n'avez pas de caméra:

### Tester via Upload d'Image
1. Allez à: `http://localhost:5000/upload`
2. Choisissez une image avec des gens
3. Cliquez "Détecter"
4. Vous verrez les détections

### Tester via API
```bash
# Terminal 1: Lancer Flask
python app/main.py

# Terminal 2: Faire une détection
curl -X POST -F "image=@test_image.jpg" \
  http://localhost:5000/api/detect
```

---

## 🎬 Commandes Utiles

```bash
# Voir tous les logs
python app/main.py 2>&1 | grep -E "(Error|OK|✅|❌)"

# Tester juste le détecteur
python -c "
from app.multi_model_detector import MultiModelDetector
md = MultiModelDetector(use_ensemble=False)
print(f'{len(md.models)} model(s) loaded')
"

# Lister caméras
python -c "
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f'Camera {i}: Available')
        cap.release()
"

# Vérifier la structure
ls -la models/          # Voir best.pt
ls -la app/            # Voir les fichiers app
```

---

## 📊 Résultats Attendus

Une fois que ça marche, vous devriez voir:

```
UNIFIED MONITORING DASHBOARD
════════════════════════════════════

📷 Flux Caméra: [Vidéo en direct]

📊 Détections:
   • Personnes: 2
   • Avec Casque: 1
   • Avec Gilet: 2
   • Avec Lunettes: 0
   
   Conformité: 66%
   Alerte: ⚠️ ATTENTION (manque équipement)

⏱️ Performance:
   • FPS: 1.2
   • Temps/détection: 820ms
```

---

## 💡 Tips Utiles

1. **FPS lent?** Normal sur CPU à ~1-2 images/sec
2. **Détections mal placées?** Améliorer l'entraînement du modèle
3. **Faux positifs?** Ajuster seuils dans config ou API
4. **Besoin de multi-caméra?** Modifier le UI et API

---

## ✨ C'est Prêt!

Le bug a été fixé! La détection fonctionne maintenant correctement dans unified_monitoring.

Testez et profitez! 🚀
