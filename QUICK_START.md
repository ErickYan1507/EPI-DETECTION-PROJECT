# 🚀 Guide Démarrage Rapide - Détections Réelles avec best.pt

## ⚡ Démarrage en 3 étapes

### 1. Lancer le serveur Flask
```bash
cd d:\projet\EPI-DETECTION-PROJECT
D:\projet\EPI-DETECTION-PROJECT\.venv\Scripts\python.exe app/main.py
```

Vous devriez voir:
```
 * Running on http://127.0.0.1:5000
 * WARNING in app.run(): This is a development server...
```

### 2. Ouvrir le dashboard dans le navigateur
```
http://localhost:5000/unified
```

### 3. Démarrer la webcam et observer les détections réelles
- Cliquer sur le bouton "▶ Démarrer caméra"
- Accepter l'accès à la webcam
- Les détections s'affichent en **TEMPS RÉEL** avec le modèle `best.pt`

---

## 🎥 Ce qui se passe maintenant

**Avant (Simulation):**
- Détections aléatoires avec `Math.random()`
- Métriques fictives (FPS, confiance)
- Pas de rapport avec les images réelles

**Après (Vrai modèle):**
```
Webcam → JavaScript canvas → Base64 → Flask API → 
YOLOv5 (best.pt) → Détections réelles → Dashboard
```

**Exemple de résultat réel:**
```
Personne détectée: 95.6% confiance ✓
├─ Casque: 92.1% confiance
├─ Gilet: 45.3% confiance (faible)
└─ Lunettes: 82.1% confiance

Status: ⚠️ Non-conforme (gilet manquant)
Conformité: 66.7% (2/3 EPI)
```

---

## 🔍 Vérifier que les détections sont RÉELLES

### Via le Dashboard:
1. Mettez-vous devant la caméra
2. Observez les compteurs se mettre à jour **en fonction de votre présence**
3. Testez: enlevez un accessoire (casque, gilet) → détection change

### Via la Console du Navigateur:
```javascript
// Ouvrir F12 → Console
// Voir les requêtes en temps réel
console.log('FPS réel:', document.getElementById('fps-value').textContent)
console.log('Temps inférence:', document.getElementById('inference-time').textContent)
console.log('Confiance:', document.getElementById('confidence-avg').textContent)
```

### Via cURL (test API):
```bash
# Créer une image de test simple
# Puis envoyer à l'API

curl -X POST http://localhost:5000/api/detect \
  -H "Content-Type: application/json" \
  -d '{"image":"data:image/jpeg;base64,/9j/4AAQSkZJRgABA..."}'

# Réponse exemple:
{
  "success": true,
  "detections": [
    {
      "class_name": "person",
      "confidence": 0.956,
      "x1": 120, "y1": 45, "x2": 520, "y2": 620
    }
  ],
  "statistics": {
    "total_persons": 1,
    "with_helmet": 0,
    "with_vest": 0,
    "inference_ms": 42.5,
    "fps": 23.5,
    "compliance_rate": 0.0
  }
}
```

---

## 📊 Données Incluses dans le Système

### Modèle de Production:
- **Fichier:** `models/best.pt`
- **Type:** YOLOv5s (Small)
- **Classes:** helmet, vest, glasses, person, boots
- **Taille:** ~7MB

### Données d'Entraînement:
- **Fichier:** `training_results/training_results.db`
- **Sessions:** 5 (numérotées 001-005)
- **Métriques:** accuracy, loss, fps, inference_time

### Accéder aux données:
```
http://localhost:5000/api/training-results
```

Voir les derniers résultats d'entraînement en JSON.

---

## 🔧 Configuration Rapide

**Si vous avez besoin de changer les seuils:**

Fichier: `config.py`
```python
CONFIDENCE_THRESHOLD = 0.25  # Min confidence to detect
IOU_THRESHOLD = 0.45          # NMS threshold
CLASS_NAMES = ['helmet', 'vest', 'glasses', 'person', 'boots']
```

**Redémarrer le serveur après modification.**

---

## 📱 Accès Multi-Écrans

Le dashboard est accessible depuis:
- 🖥️ **Local:** http://localhost:5000/unified
- 📱 **Réseau interne:** http://[IP-DE-L-ORDINATEUR]:5000/unified

**Exemple:**
```
http://192.168.1.100:5000/unified
```

---

## 🎯 Fonctionnalités Disponibles

✅ **Détections en temps réel**
- Webcam intégrée
- Détections 24/7 tant que caméra active
- Métriques de performance en direct

✅ **Données d'entraînement**
- Historique des 5 sessions
- Comparaison des métriques
- FPS et temps d'inférence

✅ **Alertes**
- ⚠️ Signal audio si non-conforme
- 🔔 Affichage alerte sur le dashboard
- 📊 Comptage des alertes

✅ **Communication Arduino**
- Envoi des données réelles à TinkerCAD
- LED/Buzzer reflète l'état de conformité
- Protocole DETECT et COMPLIANCE

✅ **Thème sombre/clair**
- Toggle en haut à droite
- Sauvegarde de la préférence (localStorage)

---

## ⚠️ Dépannage

### La webcam ne démarre pas
```
❌ getUserMedia not available in insecure context
→ Assurez-vous d'utiliser http://localhost:5000 (pas https)
```

### Les détections ne changent pas
```
❌ API /api/detect ne répond pas
→ Vérifier que le serveur Flask est en cours d'exécution
→ Vérifier les logs Flask pour les erreurs
```

### Les statuts affichent "offline"
```
❌ Caméra non accessible
→ Vérifier les permissions du navigateur
→ Essayer un autre navigateur (Chrome, Edge recommandés)
→ Redémarrer le navigateur
```

### Modèle ne charge pas
```
❌ best.pt not found
→ Vérifier: models/best.pt existe
→ Vérifier le chemin dans config.py
→ Redémarrer Flask
```

---

## 📚 Documentation Complète

Pour une documentation détaillée:
```
IMPLEMENTATION_REAL_DETECTION.md
```

Contient:
- Architecture complète du pipeline
- Exemples de réponses API
- Métriques avant/après
- Prochaines étapes optionnelles

---

## 🎓 Concepts Clés

**YOLOv5:**
- Modèle "You Only Look Once" - v5 (rapide et précis)
- Inférence ~20-50ms sur CPU
- Multi-class detection (5 classes EPI)

**best.pt:**
- "best" = meilleur poids du training
- Format PyTorch (.pt)
- Prêt pour production

**Détections réelles:**
- Analyse réelle de chaque frame
- Confiance proportionnelle à la ressemblance
- Temps d'inférence mesuré en millisecondes

**Conformité:**
- Basée sur les EPI détectés
- Formule: EPI_détectés / nombre_total_personnes
- Alerte si < 100%

---

## 🚀 Status du Système

```
✅ Modèle best.pt                          CHARGÉ
✅ Endpoint /api/detect                    OPÉRATIONNEL  
✅ Pipeline webcam → inférence             ACTIF
✅ Données d'entraînement                  ACCESSIBLE
✅ Communication Arduino                   PRÊTE
✅ Dashboard interface                     FONCTIONNEL

🎯 SYSTÈME PRÊT POUR UTILISATION
```

---

**Bon développement! 🚀**
