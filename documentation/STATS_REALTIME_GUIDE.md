# 📊 Guide: Statistiques en Temps Réel

## ✅ Problème Résolu

**AVANT**: Dashboard.html et Home n'affichaient pas les statistiques en direct
- ❌ `/api/stats` n'existait pas
- ❌ `/api/chart/*` endpoints manquaient
- ❌ `/api/realtime` n'existait pas
- ❌ Les données affichées étaient statiques (hardcoded)

**APRÈS**: Tous les endpoints créés, statistiques mises à jour en temps réel

---

## 📋 Architecture des Endpoints Créés

### 1. **`GET /api/stats`** - Statistiques Globales
Récupère les stats globales en direct (5s de fraîcheur)

**Réponse:**
```json
{
  "compliance_rate": 85.5,          // Taux de conformité (%)
  "total_persons": 24,              // Nombre total de personnes
  "with_helmet": 23,                // Avec casque
  "with_vest": 20,                  // Avec gilet
  "with_glasses": 18,               // Avec lunettes
  "with_boots": 15,                 // Avec chaussures
  "alerts": 3,                      // Alertes non résolues
  "detections_today": 156,          // Total détections aujourd'hui
  "timestamp": "2025-12-30T...",
  "status": "success"
}
```

**Utilisé par:**
- `dashboard.html` → KPI Cards (taux conformité, personnes, alertes, etc.)
- `index.html` → Statistiques en Direct section

**Fréquence de rafraîchissement:**
- Dashboard: 5 secondes (quasi en temps réel)
- Home: 5 secondes

---

### 2. **`GET /api/chart/hourly`** - Détections par Heure

Graphique "Détections par Heure" sur les 24 dernières heures

**Réponse:**
```json
{
  "hours": ["00h", "01h", "02h", ...],
  "detections": [5, 8, 12, 15, ...],
  "compliance": [78, 82, 85, ...],
  "status": "success"
}
```

**Utilisé par:**
- `dashboard.html` → Graphique "Détections par Heure"

---

### 3. **`GET /api/chart/epi`** - Répartition EPI

Données pour camembert "Répartition EPI (Casques, Gilets, Lunettes)"

**Réponse:**
```json
{
  "helmets": 68,
  "vests": 45,
  "glasses": 32,
  "boots": 28,
  "status": "success"
}
```

**Utilisé par:**
- `dashboard.html` → Graphique "EPI Détectés" (camembert)

---

### 4. **`GET /api/chart/alerts`** - Alertes par Sévérité

Données pour doughnut "Alertes par Sévérité"

**Réponse:**
```json
{
  "high": 5,      // Critique
  "medium": 12,   // Moyen
  "low": 8,       // Bas
  "status": "success"
}
```

**Utilisé par:**
- `dashboard.html` → Graphique "Alertes par Sévérité"

---

### 5. **`GET /api/chart/cumulative`** - Données Cumulatives

Données pour graphique surface "Cumul Détections"

**Réponse:**
```json
{
  "labels": ["01/01", "02/01", "03/01", ...],
  "data": [50, 120, 180, 260, ...],
  "status": "success"
}
```

**Utilisé par:**
- `dashboard.html` → Graphique "Cumul Détections"

---

### 6. **`GET /api/realtime`** - Détections Temps Réel

Dernières 10 détections pour affichage en tableau

**Réponse:**
```json
{
  "timestamps": ["14:32:15", "14:31:42", "14:30:58", ...],
  "persons": [24, 18, 21, ...],
  "helmets": [23, 17, 20, ...],
  "vests": [20, 15, 18, ...],
  "glasses": [18, 12, 16, ...],
  "boots": [15, 10, 14, ...],
  "compliance_rates": [85.5, 78.2, 92.1, ...],
  "status": "success"
}
```

**Utilisé par:**
- `dashboard.html` → Table "Détections Récentes" (10 dernières)

**Fréquence:** Mise à jour tous les 3 secondes

---

### 7. **`GET /api/stats/training`** - Dernier Entraînement

Statistiques du dernier modèle entraîné

**Réponse:**
```json
{
  "model_name": "helmet_detection_v3",
  "model_version": "3.1",
  "epochs": 100,
  "batch_size": 32,
  "image_size": 640,
  "precision": 0.95,
  "recall": 0.92,
  "f1_score": 0.93,
  "accuracy": 0.91,
  "training_time": 3600.5,
  "fps": 45.2,
  "timestamp": "2025-12-30T10:15:00",
  "status": "success"
}
```

---

### 8. **`GET /api/stats/uploads`** - Statistiques Uploads

Nombre de fichiers uploadés et taille

**Réponse:**
```json
{
  "total_files": 245,
  "total_size_mb": 1234.56,
  "image_count": 180,
  "video_count": 65,
  "status": "success"
}
```

---

### 9. **`GET /api/stats/live`** - Statistiques en Direct (Polling)

Stats actualisées à chaque appel (WebSocket-like)

**Réponse:**
```json
{
  "latest_detection_time": "2025-12-30T14:32:15",
  "detections_last_hour": 45,
  "unresolved_alerts": 3,
  "current_time": "2025-12-30T14:35:20",
  "status": "success"
}
```

---

## 🔄 Flux de Données

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCES DE DONNÉES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Database_Unified (SQLite/MySQL)                              │
│  ├── Detection (détections en temps réel)                     │
│  ├── Alert (alertes)                                          │
│  ├── TrainingResult (résultats d'entraînement)                │
│  └── Uploads (fichiers uploadés)                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│              API ENDPOINTS (app/routes_stats.py)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  /api/stats          → KPI Cards (compliance, persons, etc.)  │
│  /api/realtime       → Table détections (10 dernières)        │
│  /api/chart/hourly   → Graphique par heure                    │
│  /api/chart/epi      → Camembert EPI                          │
│  /api/chart/alerts   → Doughnut alertes                       │
│  /api/chart/cumulative → Surface cumulé                       │
│  /api/stats/training → Stats entraînement                     │
│  /api/stats/uploads  → Stats fichiers                         │
│  /api/stats/live     → Stats actualisées                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│           PAGES HTML (templates)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  dashboard.html                                               │
│  ├── KPI Cards (refreshData() every 5s)                       │
│  ├── 6 Charts (initCharts() every 5s)                         │
│  └── Détections Table (loadDetections() every 3s)             │
│                                                                 │
│  index.html (HOME)                                            │
│  └── Stats Section (updateLiveStats() every 5s)               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Configuration Intégrée

### 1. **app/main.py**
```python
from app.routes_stats import stats_bp

app.register_blueprint(stats_bp)  # Enregistrer les endpoints
```

### 2. **app/routes_stats.py**
- 9 endpoints créés et testés
- Gestion d'erreurs avec try/except
- Formatage JSON cohérent
- Récupération données depuis database_unified

### 3. **templates/dashboard.html**
```javascript
// Refresh stats toutes les 5 secondes
setInterval(refreshData, 5000);

// Reload détections toutes les 3 secondes
setInterval(loadDetections, 3000);
```

### 4. **templates/index.html**
```javascript
// Update live stats toutes les 5 secondes
setInterval(updateLiveStats, 5000);
```

---

## 📊 Cycle de Rafraîchissement

| Élément | Endpoint | Fréquence | Page |
|---------|----------|-----------|------|
| **KPI Cards** | `/api/stats` | 5s | dashboard, index |
| **Détections Table** | `/api/realtime` | 3s | dashboard |
| **Hourly Chart** | `/api/chart/hourly` | 5s | dashboard |
| **EPI Chart** | `/api/chart/epi` | 5s | dashboard |
| **Alerts Chart** | `/api/chart/alerts` | 5s | dashboard |
| **Cumulative Chart** | `/api/chart/cumulative` | 5s | dashboard |

---

## ✨ Améliorations Apportées

### Avant
```
❌ Pas d'endpoints /api/stats
❌ Pas de graphiques alimentés en direct
❌ Données hardcoded (valeurs fixes)
❌ Refresh toutes les 30 secondes
```

### Après
```
✅ 9 endpoints créés pour statistiques en direct
✅ Tous les graphiques alimentés par DB
✅ Données réelles de training.py, uploads, detect.py
✅ Refresh 3-5 secondes (temps quasi-réel)
✅ Gestion d'erreurs et fallback
✅ Format JSON standardisé
✅ Pas de dépendance fichier - tout en BD
```

---

## 🧪 Tests Rapides

### 1. Vérifier les endpoints
```bash
# Stats globales
curl http://localhost:5000/api/stats

# Détections temps réel
curl http://localhost:5000/api/realtime

# Graphique horaire
curl http://localhost:5000/api/chart/hourly

# EPI
curl http://localhost:5000/api/chart/epi

# Alertes
curl http://localhost:5000/api/chart/alerts

# Cumulatif
curl http://localhost:5000/api/chart/cumulative
```

### 2. Vérifier les pages
```bash
# Dashboard
http://localhost:5000/dashboard

# Home
http://localhost:5000/
```

### 3. Vérifier dans console navigateur
```javascript
// Ouvrir F12 → Console
fetch('/api/stats').then(r => r.json()).then(d => console.log(d))
```

---

## 📁 Fichiers Modifiés

| Fichier | Modifications |
|---------|---|
| `app/routes_stats.py` | **CRÉÉ** - 400+ lignes, 9 endpoints |
| `app/main.py` | +2 lignes (import + register_blueprint) |
| `templates/dashboard.html` | Changé rafraîchissement de 30s → 5s, 10s → 3s |
| `templates/index.html` | Script améloré pour récupérer les 4 données |

---

## 🎯 Objectifs Atteints

✅ **Objectif 1**: Dashboard affiche les stats d'aujourd'hui en direct  
✅ **Objectif 2**: Home affiche stats en direct (compliance, personnes, helmets, alerts)  
✅ **Objectif 3**: Données proviennent de training.py (database_unified)  
✅ **Objectif 4**: Données proviennent des uploads (statistiques fichiers)  
✅ **Objectif 5**: Données proviennent de detect.py (database_unified)  
✅ **Objectif 6**: Temps quasi-réel (3-5 secondes max)  
✅ **Objectif 7**: Pas de dépendances statiques, tout dynamique via API  

---

## 🔐 Sécurité & Performance

✅ Endpoints en lecture seule (GET)  
✅ Gestion d'erreurs avec try/except  
✅ Cache implicite via base de données  
✅ Pas de surcharge API (5s+ d'intervalle)  
✅ JSON responses standardisées  
✅ Fallback gracieux en cas d'erreur  

---

## 📞 Support

Si les données ne s'affichent pas:
1. Vérifier que l'app est lancée: `python run_app.py`
2. Vérifier la console navigateur (F12)
3. Vérifier les logs Flask pour erreurs
4. Vérifier que database_unified a des données (Training, Detection, etc.)

