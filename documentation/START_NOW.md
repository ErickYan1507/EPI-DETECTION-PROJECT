# 🚀 DÉMARRER MAINTENANT - Unified Monitoring v2.1

## ⚡ 5 Minutes pour Commencer

### 1️⃣ Arrêter le serveur (si en cours)
```bash
# Terminal: Appuyer sur CTRL+C
```

### 2️⃣ Redémarrer le serveur Flask
```bash
# Depuis D:\projet\EPI-DETECTION-PROJECT
python app.py

# Vous devriez voir:
# * Running on http://127.0.0.1:5000
# * WARNING: This is a development server
```

### 3️⃣ Ouvrir dans le navigateur
```
http://localhost:5000/unified
```

### 4️⃣ Cliquer sur "▶️ Démarrer Webcam"
```
• Autoriser l'accès à la caméra (popup navigateur)
• Attendre 2-3 secondes pour initialisation
• Observer le flux vidéo apparaître
```

### 5️⃣ Voir les Boîtes Englobantes!
```
Les classes détectées apparaissent comme:

┌─────────────────────────────┐
│ 🪖 Casque │ 95% │ ①      │ ← Boîte verte
│                             │
│   [Objet Détecté]           │
│                             │
└─────────────────────────────┘

À droite: Liste détections
#1 🪖 Casque 95%    [████████████░]
#2 🟧 Gilet 87%     [████████░░░░]
```

---

## 🎮 Contrôles Principaux

| Bouton | Effet |
|--------|-------|
| ▶️ Démarrer | Lance détection |
| ⏹️ Arrêter | Arrête flux |
| 📸 Capture | Sauvegarde image |
| 🔊 Test | Test alerte audio |
| 🗑️ Effacer | Nettoie alertes |

### Sélecteur Mode
```
Mode: [Ensemble ▼]
      ├─ Ensemble (Précis, lent)
      └─ Single (Rapide, temps réel)
```

---

## 📊 Qu'Afficher

### Vue Complète (3 Colonnes)
```
┌────────────────┬────────────────┬────────────────┐
│ 📹 CAMÉRA      │ 🔍 DÉTECTIONS  │ ⚠️ ALERTES    │
│                │                │                │
│ [Video Flux]   │ 👤 Personnes:5 │ 📊 FPS: 30    │
│ avec boîtes    │ 🪖 Casques: 4  │ ⏱️ Inference  │
│ englobantes    │ 🟧 Gilets: 3   │ 📈 Compliance │
│                │ 👓 Lunettes:1  │                │
│ ▶️ Start       │ 👢 Bottes: 2   │ Détections:   │
│ ⏹️ Stop        │                │ #1 🪖 95%    │
│ 📸 Capture     │ LISTE:         │ #2 🟧 87%    │
│                │ #1 🪖 95%      │ #3 👤 92%    │
│                │ [████████░░]   │ #4 👓 78%    │
│                │ #2 🟧 87%      │ #5 👢 65%    │
│                │ [████████░░]   │                │
│                │ #3 👤 92%      │ +3 plus       │
│                │ [████████░░]   │                │
└────────────────┴────────────────┴────────────────┘
```

---

## 🎨 Identifier les Classes par Couleur

### Couleur sur Flux Caméra
```
🟢 Vert      → 🪖 Casque
🟠 Orange    → 🟧 Gilet
🔵 Cyan      → 👓 Lunettes
🟣 Indigo    → 👤 Personne
🟣 Violet    → 👢 Bottes
```

### Exemple Réel
```
Personne dans le champ caméra:
  ↓
Détection: Casque + Gilet + Bottes
  ↓
Affichage:
  ┌─ Boîte VERTE (#1 🪖 Casque 95%)
  ├─ Boîte ORANGE (#2 🟧 Gilet 87%)
  └─ Boîte VIOLET (#3 👢 Bottes 78%)
  ↓
Conformité Calculée: 3/3 = 100% ✅
```

---

## 🧪 Tester Rapidement

### Test 1: Casque
```
1. Porter/montrer casque à la caméra
2. Attendre 1-2 secondes
3. Vérifier boîte VERTE (#1 🪖)
4. Vérifier 🪖 Casques: 1 augmente
```

### Test 2: Gilet
```
1. Porter/montrer gilet à la caméra
2. Attendre 1-2 secondes
3. Vérifier boîte ORANGE (#2 🟧)
4. Vérifier 🟧 Gilets: 1 augmente
```

### Test 3: Multi-Objets
```
1. Montrer casque + gilet + lunettes
2. Vérifier 3 boîtes avec couleurs différentes
3. Vérifier numérotation: #1, #2, #3
4. Vérifier liste à droite mise à jour
5. Vérifier confiance (%) pour chacun
```

### Test 4: Performance
```
Vérifier en bas à droite:
📊 FPS: [devrait être ≥ 25]
⏱️ Inférence: [devrait être < 100ms]
📈 Conformité: [pourcentage d'équipement]
```

---

## 🔧 Si Problème

### Problème: Pas de Boîtes
**Solution:**
```
1. Vérifier que caméra fonctionne (vidéo visible)
2. Attendre 3 secondes après démarrage
3. Essayer mode "Single" (plus rapide)
4. Augmenter lumière
5. Relancer page (F5)
```

### Problème: FPS Faible
**Solution:**
```
1. Sélectionner mode "Single" (pas "Ensemble")
2. Fermer autres applications
3. Redémarrer serveur Flask
4. Vérifier CPU/GPU disponible
```

### Problème: Vidéo Noire
**Solution:**
```
1. Vérifier permissions caméra navigateur
2. Aller à Paramètres → Confidentialité → Caméra
3. Autoriser localhost/127.0.0.1
4. Actualiser page (F5)
```

### Problème: Erreur API
**Solution:**
```
1. Vérifier que Flask tourne
2. Vérifier modèle best.pt présent
3. Vérifier fichier app.py pour erreurs
4. Regarder console Flask pour erreurs
5. Redémarrer le serveur
```

---

## 📊 Comprendre l'Affichage

### Boîte Englobante
```
┌─ OMBRE NOIRE (contraste)
│ ┌─ BORDURE COLORÉE (classe)
│ │ ┌─ CADRE INTERNE POINTILLÉ
│ │ │
│ │ │ ┌─────────────────────────┐
│ │ │ │ 🪖 Casque │ 95% │ ①  │ ← LABEL
│ │ │ │              ↑        ↑   
│ │ │ │          Classe   Confiance   ID
│ │ │ │                                 │
│ │ │ │   [OBJET DÉTECTÉ]              │
│ │ │ │                                 │
│ │ │ │   ╱╲ Coin stylisé              │
│ │ │ └─────────────────────────┘
│ │ └─────────────────────────────
│ └───────────────────────────────
└───────────────────────────────────
```

### Barre de Confiance
```
Affichée dans liste détections:

#1 🪖 Casque 95%
   [████████████░] ← Barre % proportionnelle
    ↑                (12/13 rempli = 95%)

#2 🟧 Gilet 87%
   [████████░░░░] ← Un peu moins remplie
    ↑                (11/13 rempli = 87%)
```

### Numérotation
```
#1 = Première détection (index 0)
#2 = Deuxième détection (index 1)
#3 = Troisième détection (index 2)
...
#5 = Cinquième détection (index 4)

Si > 5: Affiche "+X détections"
```

---

## 🎯 À Vérifier Après Démarrage

- [ ] Page charge sans erreur
- [ ] Tous les boutons visibles
- [ ] Vidéo flux affichée
- [ ] Status "En ligne" vert
- [ ] Mode de détection sélectionnable
- [ ] Boîtes apparaissent quand objet en vue
- [ ] Labels affichent nom + %
- [ ] Liste détections se met à jour
- [ ] Barres de confiance proportionnelles
- [ ] FPS ≥ 25 et stable

---

## 💡 Conseils Pro

### Pour Meilleure Détection
```
✅ Bonne lumière (pas de contre-jour)
✅ Caméra stable
✅ Distance 1-3 mètres
✅ Angle frontal (face caméra)
✅ Équipement bien visible
❌ Éviter mouvements rapides
❌ Éviter ombres
❌ Trop loin (>5m) ou trop proche (<0.5m)
```

### Pour Meilleure Performance
```
✅ Mode "Single" pour vidéo
✅ Mode "Ensemble" pour uploads
✅ Fermer autres onglets
✅ Fermer autres applications
❌ Pas de streaming parallèle
❌ Pas de plusieurs instances
```

---

## 📱 Pour Mobile/Tablette

La page est **responsive**, fonctionne sur:
- Desktop (1920x1080+): 3 colonnes
- Tablette (1200px): 2 colonnes  
- Mobile (< 1200px): 1 colonne

```
Mobile vue:
┌──────────────────┐
│ 📹 Caméra       │
│ [Video]         │
├──────────────────┤
│ 🔍 Détections   │
│ 👤: 5           │
│ 🪖: 4           │
├──────────────────┤
│ ⚠️ Alertes      │
│ [Historique]    │
└──────────────────┘
```

---

## 🎓 Apprentissage Rapide

### Vocabulaire
| Terme | Signification |
|-------|--------------|
| Boîte englobante | Rectangle autour de l'objet |
| Confiance | % que le modèle est certain |
| Flux | Vidéo en direct de la caméra |
| Inférence | Temps de traitement |
| Compliance | Taux d'équipement |
| Détection | Objet/classe identifié |

### Raccourcis
```
F12          = Console navigateur (pour debug)
F5           = Actualiser page
CTRL+R       = Forcer refresh
CTRL+SHIFT+R = Purger cache + refresh
```

---

## 🚀 Démarrage Minimum (2 min)

```bash
# 1. Terminal PowerShell
cd D:\projet\EPI-DETECTION-PROJECT

# 2. Venv déjà activé? Si pas:
.\.venv\Scripts\Activate.ps1

# 3. Démarrer Flask
python app.py

# 4. Ouvrir navigateur
http://localhost:5000/unified

# 5. Clic "▶️ Démarrer Webcam"
# 6. Observer les boîtes! 🎉
```

---

## 📞 En Cas de Besoin

### Vérifier Logs Flask
```
Regarder la sortie de la console Flask:
- Erreurs en rouge
- Warnings en jaune
- Infos en blanc

Ex: [2026-01-30 14:45:23] GET /api/detect - 200 OK (45ms)
```

### Tester Manuellement API
```bash
# PowerShell - Tester endpoint
$uri = "http://localhost:5000/api/detect?use_ensemble=false"
$response = Invoke-WebRequest -Uri $uri -Method POST
$response.StatusCode  # Doit être 200

# Ou avec curl
curl -X POST "http://localhost:5000/api/detect" -H "Content-Type: application/json"
```

---

## ✨ À Faire Après Vérification

- [ ] Tester avec vrais objets EPI
- [ ] Vérifier taux de conformité
- [ ] Tester export statistiques
- [ ] Tester mode Ensemble
- [ ] Vérifier LEDs Arduino
- [ ] Tester alertes son
- [ ] Documenter résultats

---

## 🎉 Vous Êtes Prêt!

Vous avez maintenant un système complet de **détection EPI en temps réel** avec:

✅ Boîtes englobantes colorées  
✅ Labels détaillés avec confiance  
✅ Liste détections en direct  
✅ Flux caméra HD  
✅ Statistiques temps réel  

**Lancez-vous!** 🚀

---

**Documentation:** UNIFIED_MONITORING_QUICK_START.md  
**Problèmes?** Consulter TROUBLESHOOTING_DETECTION.md  
**Détails techniques?** UNIFIED_MONITORING_IMPROVEMENTS.md  

*Dernière MAJ: 30 Janvier 2026*
