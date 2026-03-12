# 🔍 DIAGNOSTIC: Boîtes Colorées Non Affichées

## ✅ Ce qui a été corrigé

1. **CSS du Canvas** - Ajouté `width: 100% !important` et `height: 100% !important`
2. **Dimensions JavaScript** - Arrondies avec `Math.round()`
3. **Inline HTML** - Enlevé les dimensions pour éviter conflit avec CSS

## 🧪 Comment Diagnostiquer le Problème

### Étape 1: Tester le Canvas Basique

Accédez à: **`http://localhost:5000/test_canvas`**

Cliquez sur **"Test 1: Canvas Basique"**

Vous devriez voir:
- ✅ Un rectangle vert (200×150)
- ✅ Un cercle rouge (r=50)

**Si vous ne voyez rien → Problème canvas/navigateur**

### Étape 2: Tester le Dessin de Boîtes

Cliquez sur **"Test 2: Canvas avec Boîtes Colorées"**

Vous devriez voir:
- ✅ 5 boîtes colorées
- ✅ Labels avec emojis
- ✅ Numéros (#1-#5)

**Si vous ne voyez rien → Bug dans `drawDetections()`**

### Étape 3: Vérifier les Dimensions

Cliquez sur **"Test 3: Dimensions Canvas"**

Vous devriez voir:
- ✅ Dimensions du container DOM
- ✅ Dimensions du canvas CSS
- ✅ Dimensions du canvas pixels
- ✅ 4 coins rouges marquant les limites

**Les coins doivent être aux 4 angles du cadre noir**

**Si les coins sont manquants ou à mauvaise place → Problème de synchronisation**

### Étape 4: Tester l'API /api/detect

Cliquez sur **"Test 4: API /api/detect"**

Vous devriez voir:
- ✅ `Success: true`
- ✅ Nombre de détections
- ✅ Détails de chaque détection

**Si erreur 404 ou 500 → L'API ne fonctionne pas**

**Si erreur de connexion → Le serveur Flask n'est pas démarré**

## 🚨 Problèmes Possibles et Solutions

### Problème 1: "Canvas not found!"
```
❌ Test 1 échoue avec "Canvas not found!"
```

**Cause:** L'élément `<canvas id="overlay-canvas">` n'existe pas dans le HTML

**Solution:**
```html
<!-- Vérifier que ce code existe dans unified_monitoring.html ligne ~695 -->
<canvas id="overlay-canvas" style="position:absolute; left:0; top:0; pointer-events:none;"></canvas>
```

---

### Problème 2: Canvas présent mais rien n'apparaît
```
✅ Test 1 trouve le canvas
✅ Dimensions OK
❌ Mais aucun dessin visible
```

**Cause:** Problème de contexte 2D ou CSS de positionnement

**Solutions à vérifier:**

1. **Z-index du canvas parent:**
```css
.camera-feed {
    position: relative;  /* ← IMPORTANT! */
}

.camera-feed #overlay-canvas {
    position: absolute;
    z-index: 10;        /* ← Doit être > que la vidéo */
}
```

2. **CSS du canvas complet:**
```css
.camera-feed #overlay-canvas {
    position: absolute;
    left: 0;
    top: 0;
    width: 100% !important;
    height: 100% !important;
    z-index: 10;
    pointer-events: none;
    border: 1px solid red;  /* ← Temporaire pour debug */
}
```

---

### Problème 3: Canvas visible (bordure rouge) mais rien dessiné
```
✅ Test 1 & 3 OK
❌ Mais aucune boîte colorée
```

**Cause:** Fonction `drawDetections()` ne s'exécute pas ou `detections` est vide

**Solutions à vérifier:**

1. **Les détections arrivent-elles?** Ouvrez la console (F12):
```javascript
// Tapez dans la console:
console.log(detections);  // Doit montrer un array
```

2. **La fonction est-elle appelée?** Cherchez dans la console:
```
// Recherchez cette ligne (cherchez "Détection réussie"):
console.log('Détection réussie:', { detections: X, persons: Y, ... });
```

3. **Format des données correct?** Vérifiez que chaque détection a:
```javascript
{
    class_name: "helmet",      // ou "class"
    bbox: [x1, y1, x2, y2],   // ou "box" ou "bbox_xyxy"
    confidence: 0.95           // ou "conf"
}
```

---

### Problème 4: Canvas dessiné mais positions incorrectes
```
✅ Boîtes colorées visibles
❌ Mais au mauvais endroit (décalage)
```

**Cause:** Problème de ratio d'aspect vidéo/canvas

**Solution:** Vérifier les calculs dans `drawDetections()`:
```javascript
const videoWidth = video.videoWidth;
const videoHeight = video.videoHeight;
const canvasWidth = canvas.width;
const canvasHeight = canvas.height;

// Les dimensions vidéo doivent être > 0
if (videoWidth === 0 || videoHeight === 0) {
    console.error('Vidéo dimensions non prêtes');
    return;
}

// Le ratio doit être cohérent
const videoAspect = videoWidth / videoHeight;
const canvasAspect = canvasWidth / canvasHeight;
console.log(`Ratio vidéo: ${videoAspect}, Canvas: ${canvasAspect}`);
```

---

### Problème 5: Erreur API "/api/detect"
```
❌ Test 4: Erreur 404 ou 500
```

**Cause 1:** Serveur Flask n'est pas démarré
**Solution:** Démarrez avec `python app/main.py`

**Cause 2:** L'endpoint `/api/detect` n'existe pas
**Solution:** Vérifiez que `app/routes_api.py` contient la route

**Cause 3:** Image invalide ou API timeout
**Solution:** Vérifiez les logs Flask pour les erreurs

---

## 📋 Checklist de Diagnostic

Exécutez cette checklist dans cet ordre:

- [ ] **Test 1 (Canvas Basique)** - Voir rectangle vert + cercle rouge?
- [ ] **Test 2 (Boîtes Colorées)** - Voir 5 boîtes numérotées?
- [ ] **Test 3 (Dimensions)** - Voir 4 coins rouges aux limites?
- [ ] **Test 4 (API Détection)** - Voir `Success: true`?
- [ ] **Console F12** - Chercher "Détection réussie" messages?
- [ ] **Unified Monitoring** - Clic "Démarrer Webcam" → Voir boîtes?

## 🎯 Arborescence de Diagnostic

```
Canvas Basique Visible?
├─ NON → Z-index ou CSS manquant
│   └─ Vérifier .camera-feed { position: relative; }
│   └─ Vérifier #overlay-canvas { z-index: 10; }
│
└─ OUI → Boîtes colorées dessinées?
    ├─ NON → API ne retourne pas de détections
    │   └─ Tester Test 4 (API Détection)
    │   └─ Vérifier logs Flask
    │   └─ Vérifier format des détections
    │
    └─ OUI → Positions incorrectes?
        ├─ NON → ✅ SUCCÈS!
        │
        └─ OUI → Problème ratio d'aspect
            └─ Vérifier calcul offset/scale
            └─ Vérifier videoWidth/Height !== 0
```

## 🛠️ Code Debug à Ajouter

Dans `drawDetections()`, ajoutez avant `detections.forEach()`:

```javascript
console.log('drawDetections() appelée avec:', {
    detectionsCount: detections.length,
    canvasSize: `${canvas.width}x${canvas.height}`,
    videoSize: `${video.videoWidth}x${video.videoHeight}`,
    canvasBounds: canvas.getBoundingClientRect()
});

// Vérifier que le canvas peut être dessiné
const testCtx = canvas.getContext('2d');
if (!testCtx) {
    console.error('Impossible d\'obtenir le contexte 2D!');
    return;
}

// Vérifier que les dimensions sont valides
if (canvas.width === 0 || canvas.height === 0) {
    console.error('Canvas dimensions invalides:', canvas.width, canvas.height);
    return;
}

console.log('✅ Canvas prêt à dessiner');
```

## 📞 Cas Spécifiques

### Cas A: "✓ En attente de détections..." affiche mais pas de boîtes
```
= Les détections sont NULL ou []
= L'API retourne success: true mais detections: []
= OU la fonction drawDetections() n'est pas appelée
```

**Debug:**
```javascript
// À la fin de simulateDetections():
console.log('Avant drawDetections():', {
    detectionsCount: detections.length,
    firstDetection: detections[0]
});
```

### Cas B: Console erreur "Cannot read property 'bbox' of undefined"
```
= Le format des données est incorrect
= Les détections n'ont pas la structure attendue
```

**Debug:**
```javascript
// Dans drawDetections():
detections.forEach((det, idx) => {
    console.log(`Detection ${idx}:`, det);
    const bbox = det.bbox || det.box || det.bbox_xyxy;
    if (!bbox) {
        console.error(`Detection ${idx} n'a pas de bbox!`, det);
    }
});
```

### Cas C: Boîtes visibles mais avec des artefacts (flicker, distortion)
```
= Canvas dimensions changent trop souvent
= Dimensions float au lieu d'entiers
= Ratio d'aspect non géré correctement
```

**Debug:**
```javascript
// Log tous les 5 appels:
if (idx % 5 === 0) {
    console.log('Canvas dimensions:', canvas.width, canvas.height);
}
```

## ✅ Après Diagnostic

Une fois que vous avez identifié le problème:

1. **Communiquez les résultats des 4 tests**
2. **Partagez les logs de la console (F12)**
3. **Décrivez ce que vous voyez/ne voyez pas**

Exemple:
```
Test 1: ✅ Rect vert + cercle rouge visible
Test 2: ❌ Aucune boîte, canvas noir
Test 3: ✅ Coins rouges aux limites  
Test 4: ✅ API détection ok, 3 objets détectés

Console: [14:35:22] Détection réussie: { detections: 3, ... }

Conclusion: Les boîtes ne s'affichent pas alors que l'API fonctionne!
```

---

**Cette page de test: `http://localhost:5000/test_canvas`**

**Date:** 31 Janvier 2026  
**Status:** 🔍 Diagnostic en cours

