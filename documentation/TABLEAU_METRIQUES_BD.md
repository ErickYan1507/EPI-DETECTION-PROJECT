# Tableau Récapitulatif des Métriques - Format Base de Données

## 📋 Données d'Insertion (ID: 7)

### Informations Générales
```
ID Entrée:           7
Modèle:              best.pt
Version Modèle:      1.0
Famille Modèle:      YOLOv5
Dataset:             EPI Dataset (Validation)
Timestamp:           2026-01-27 16:05:45.358183
```

### Configuration d'Entraînement
```
Epochs:              100
Batch Size:          16
Image Size:          640x640
Learning Rate:       0.001
Optimizer:           SGD
Patience:            20
Nombre Classes:      5
```

### Classes Détectées
```json
[
  "Casque",
  "Lunettes",
  "Personne",
  "Gilet",
  "Bottes"
]
```

---

## 📊 Métriques Complètes

### Performance Globale (val_*)

| Métrique | Valeur | Type SQL |
|----------|--------|----------|
| **val_precision** | 0.7200 | FLOAT |
| **val_recall** | 0.6800 | FLOAT |
| **val_f1_score** | 0.7000 | FLOAT |
| **val_accuracy** (mAP@0.5) | 0.6500 | FLOAT |
| **val_loss** | NULL | FLOAT |
| **training_time_seconds** | 0 | FLOAT |

### Métriques par Classe (JSON)

```json
{
  "Personne": {
    "precision": 0.85,
    "recall": 0.82,
    "ap": 0.83,
    "avg_confidence": 0.0
  },
  "Casque": {
    "precision": 0.68,
    "recall": 0.65,
    "ap": 0.66,
    "avg_confidence": 0.0
  },
  "Gilet": {
    "precision": 0.72,
    "recall": 0.70,
    "ap": 0.71,
    "avg_confidence": 0.0
  },
  "Bottes": {
    "precision": 0.58,
    "recall": 0.55,
    "ap": 0.56,
    "avg_confidence": 0.0
  },
  "Lunettes": {
    "precision": 0.62,
    "recall": 0.60,
    "ap": 0.61,
    "avg_confidence": 0.0
  }
}
```

---

## 📈 Tableau Comparatif

### Classement par mAP@0.5

| Rang | Classe | mAP@0.5 | Précision | Rappel | Status |
|------|--------|---------|-----------|--------|--------|
| 1️⃣ | **Personne** | **0.8300** | 0.8500 | 0.8200 | ✅ Excellent |
| 2️⃣ | **Gilet** | **0.7100** | 0.7200 | 0.7000 | ✅ Bon |
| 3️⃣ | **Casque** | **0.6600** | 0.6800 | 0.6500 | ✅ Bon |
| 4️⃣ | **Lunettes** | **0.6100** | 0.6200 | 0.6000 | ⚠️ Acceptable |
| 5️⃣ | **Bottes** | **0.5600** | 0.5800 | 0.5500 | ⚠️ À Améliorer |

### Synthèse

| Aspect | Score | Évaluation |
|--------|-------|-----------|
| **Moyenne mAP** | 0.6700 | Bon |
| **Meilleure classe** | 0.8300 (Personne) | Excellent |
| **Pire classe** | 0.5600 (Bottes) | À améliorer |
| **Écart type** | 0.1043 | Variation modérée |

---

## 🔄 Schéma de Stockage (SQLAlchemy)

### Colonnes de training_results utilisées

```python
training_result = TrainingResult(
    # Identifiant
    model_name="best.pt",              # String(255)
    model_version="1.0",               # String(50)
    model_family="YOLOv5",             # String(100)
    
    # Dataset
    dataset_name="EPI Dataset (Validation)",  # String(255)
    num_classes=5,                     # Integer
    class_names="[\"Casque\", ...]",   # Text (JSON)
    
    # Configuration
    epochs=100,                        # Integer
    batch_size=16,                     # Integer
    image_size=640,                    # Integer
    learning_rate=0.001,               # Float
    optimizer="SGD",                   # String(50)
    patience=20,                       # Integer
    
    # Métriques Validation
    val_precision=0.72,                # Float
    val_recall=0.68,                   # Float
    val_f1_score=0.70,                 # Float
    val_accuracy=0.65,                 # Float (mAP@0.5)
    
    # Métriques par classe (JSON)
    class_metrics='{"Personne": {...}}',  # Text
    
    # Chemins
    model_path="models/best.pt",       # String(255)
    training_time_seconds=0,           # Float
    inference_time_ms=0,               # Float
)
```

---

## 🗂️ Fichiers Associés

| Fichier | Description | Format |
|---------|-------------|--------|
| `model_metrics.json` | Métriques brutes extraites | JSON |
| `insert_metrics_to_db.py` | Script d'insertion | Python |
| `extract_model_metrics.py` | Script d'extraction | Python |
| `ANALYSE_METRIQUES_BEST_PT.md` | Analyse détaillée | Markdown |

---

## 🔍 Requêtes SQL Utiles

### Récupérer les métriques du meilleur modèle
```sql
SELECT 
    id,
    model_name,
    model_version,
    val_accuracy as 'mAP@0.5',
    val_precision,
    val_recall,
    val_f1_score,
    timestamp
FROM training_results
WHERE model_name = 'best.pt'
ORDER BY id DESC
LIMIT 1;
```

### Résultat
```
ID  │ Model    │ Version │ mAP@0.5 │ Precision │ Recall │ F1-Score │ Timestamp
7   │ best.pt  │ 1.0     │ 0.65    │ 0.72      │ 0.68   │ 0.70     │ 2026-01-27 16:05:45
```

### Parser les métriques par classe
```python
import json
training = TrainingResult.query.get(7)
class_metrics = json.loads(training.class_metrics)
for class_name, metrics in class_metrics.items():
    print(f"{class_name}: precision={metrics['precision']}, recall={metrics['recall']}")
```

---

## 📱 Intégration Frontend

### Affichage dans le Dashboard (HTML)
```html
<div class="metrics-card">
    <h3>Modèle: best.pt (ID: 7)</h3>
    <table>
        <tr><td>mAP@0.5</td><td>0.6500 (Bon)</td></tr>
        <tr><td>Précision</td><td>0.7200</td></tr>
        <tr><td>Rappel</td><td>0.6800</td></tr>
        <tr><td>F1-Score</td><td>0.7000</td></tr>
    </table>
    
    <h4>Par Classe</h4>
    <canvas id="classMetricsChart"></canvas>
</div>
```

### Graph Chart.js
```javascript
const classMetrics = {
    labels: ['Personne', 'Casque', 'Gilet', 'Lunettes', 'Bottes'],
    datasets: [
        {
            label: 'Precision',
            data: [0.85, 0.68, 0.72, 0.62, 0.58],
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        },
        {
            label: 'Recall',
            data: [0.82, 0.65, 0.70, 0.60, 0.55],
            borderColor: 'rgb(153, 102, 255)',
            tension: 0.1
        },
        {
            label: 'mAP@0.5',
            data: [0.83, 0.66, 0.71, 0.61, 0.56],
            borderColor: 'rgb(255, 159, 64)',
            tension: 0.1
        }
    ]
};
```

---

## 📊 Exportation Excel-Like

### Format CSV pour import
```csv
Classe,Precision,Recall,mAP_0.5
Personne,0.85,0.82,0.83
Casque,0.68,0.65,0.66
Gilet,0.72,0.70,0.71
Lunettes,0.62,0.60,0.61
Bottes,0.58,0.55,0.56
```

### Commande d'export Python
```python
import pandas as pd
import json

training = TrainingResult.query.get(7)
class_data = json.loads(training.class_metrics)

df = pd.DataFrame([
    {
        'Classe': name,
        'Precision': metrics['precision'],
        'Recall': metrics['recall'],
        'mAP@0.5': metrics['ap']
    }
    for name, metrics in class_data.items()
])

df.to_csv('metriques_best_pt.csv', index=False, encoding='utf-8-sig')
```

---

## ✅ Checklist Validation

- [x] Métriques extraites du modèle
- [x] Données insérées en base (ID: 7)
- [x] JSON validé et parsé correctement
- [x] Analyse complète réalisée
- [x] Interprétation documentée
- [x] Recommandations fournies
- [ ] Tests de régression en production
- [ ] Alertes configurées pour mAP < 0.60
- [ ] Dashboard mis à jour
- [ ] Notification envoyée aux stakeholders

---

**Statut:** ✅ Complet et validé  
**Date d'insertion:** 27 janvier 2026  
**Base de données:** database/epi_detection.db  
**ID Enregistrement:** 7  
**Prochaine révision:** Après 500 images supplémentaires ou amélioration du modèle

