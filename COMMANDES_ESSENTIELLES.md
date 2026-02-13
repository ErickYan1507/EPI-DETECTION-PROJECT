# ⚡ COMMANDES ESSENTIELLES - COPY-PASTE READY

**Pour:** Déploiement et vérification rapide  
**Date:** 27 janvier 2026

---

## 🚀 COMMANDES DE VÉRIFICATION IMMÉDIATE

### 1️⃣ Vérifier la Base de Données

```bash
cd D:\projet\EPI-DETECTION-PROJECT
python verify_db.py
```

**Attendu:** 
```
ID: 8
Validation Precision: 0.915
Validation Recall: 0.9494
Validation F1-Score: 0.9319
Validation Accuracy: 0.9756
```

### 2️⃣ Vérifier le Fichier JSON

```bash
cd D:\projet\EPI-DETECTION-PROJECT
python -c "import json; d=json.load(open('model_metrics.json')); print(f\"mAP: {d['global_metrics']['mAP_0_5']:.4f}\")"
```

**Attendu:**
```
mAP: 0.9756
```

### 3️⃣ Vérifier les Fichiers Créés

```bash
cd D:\projet\EPI-DETECTION-PROJECT
ls -la *.md | grep -E "(SYNTHESE|QUICK|LIVRABLES|INDEX)"
```

### 4️⃣ Vérifier le Modèle

```bash
cd D:\projet\EPI-DETECTION-PROJECT
ls -la models/best.pt
```

---

## 📊 COMMANDES DE TEST

### Test Détection (si GPU disponible)

```bash
cd D:\projet\EPI-DETECTION-PROJECT
python detect.py --weights models/best.pt --source test_video.mp4 --conf 0.5
```

### Test API (si Flask démarré)

```bash
# Dans un autre terminal
curl -X POST http://localhost:5000/api/detect \
  -F "image=@test_image.jpg" \
  -F "confidence=0.5"
```

---

## 🗂️ FICHIERS À CONSULTER EN PRIORITÉ

### Pour Direction (15 min)

```bash
# 1. Lire
code QUICK_SUMMARY_2MIN.md
code SYNTHESE_FINALE.md

# 2. Vérifier
python verify_db.py

# 3. Approuver -> Déployer
```

### Pour IT/DevOps (1h)

```bash
# 1. Structure
code INDEX_COMPLET_NAVIGATION.md

# 2. Détails
code FINALISATION_RAPPORT.md

# 3. Vérifications
python verify_db.py
python extract_model_metrics.py

# 4. Configuration
code config.py
```

### Pour ML Team (2h)

```bash
# 1. Vue complète
code ANALYSE_METRIQUES_BEST_PT_REELLE.md

# 2. Avant/Après
code COMPARAISON_METRIQUES_REELLES_vs_ESTIMEES.md

# 3. Données
cat model_metrics.json | python -m json.tool
sqlite3 database/epi_detection.db "SELECT * FROM training_results WHERE id=8"
```

---

## 📈 VÉRIFICATION COMPÈTE (5 min)

```bash
#!/bin/bash
# Script de vérification rapide

echo "=== VÉRIFICATION PROJET EPI DETECTION v2.0 ==="
echo ""

# 1. BD
echo "1️⃣  Vérification Base de Données..."
python verify_db.py > /tmp/verify.txt 2>&1
grep "ID: 8" /tmp/verify.txt && echo "   ✅ BD OK" || echo "   ❌ BD problème"

# 2. JSON
echo ""
echo "2️⃣  Vérification JSON..."
test -f model_metrics.json && echo "   ✅ JSON existe" || echo "   ❌ JSON manquant"

# 3. Modèle
echo ""
echo "3️⃣  Vérification Modèle..."
test -f models/best.pt && echo "   ✅ best.pt existe" || echo "   ❌ best.pt manquant"

# 4. Docs
echo ""
echo "4️⃣  Vérification Documentation..."
test -f QUICK_SUMMARY_2MIN.md && echo "   ✅ QUICK_SUMMARY OK"
test -f SYNTHESE_FINALE.md && echo "   ✅ SYNTHESE OK"
test -f LIVRABLES_FINAUX.md && echo "   ✅ LIVRABLES OK"

echo ""
echo "=== ✅ VÉRIFICATION COMPLÈTE ==="
```

---

## 🔄 PIPELINE DE DÉPLOIEMENT

### Phase 1: Validation (Jour 1)

```bash
# 1. Lire résumé
cat QUICK_SUMMARY_2MIN.md

# 2. Vérifier DB
python verify_db.py

# 3. Obtenir approbation
# → Direction valide = Go!
```

### Phase 2: Préparation (Jours 2-3)

```bash
# 1. IT configure infra
# - Serveurs préparés
# - Certificats SSL
# - Monitoring setup

# 2. Test E2E
python detect.py --weights models/best.pt --source test_video.mp4

# 3. Test API
curl http://localhost:5000/api/detect -F "image=@test.jpg"
```

### Phase 3: Déploiement Limité (Jour 4)

```bash
# 1. Zone pilote
# - 1 caméra
# - 1 semaine
# - Logs détaillés

# 2. Monitoring
# - Vérifier détections
# - Collecter feedback

# 3. Analyse
# - Résultats OK? → Go scaling
# - Problèmes? → Ajuster
```

### Phase 4: Production (Jours 5-7)

```bash
# 1. Rollout complet
# - Toutes zones
# - Toutes caméras

# 2. Formation
# - Support user (2h)
# - Documentation utilisateur

# 3. Support 24/7
# - Monitoring continu
# - Alertes actives
# - Review hebdomadaire
```

---

## 🧪 TESTS RAPIDES

### Test 1: BD Connectée

```python
import sqlite3
conn = sqlite3.connect('database/epi_detection.db')
cursor = conn.cursor()
cursor.execute('SELECT val_precision FROM training_results WHERE id=8')
print(cursor.fetchone()[0])  # Doit afficher 0.915
conn.close()
```

### Test 2: JSON Valide

```python
import json
with open('model_metrics.json') as f:
    d = json.load(f)
    assert d['global_metrics']['mAP_0_5'] == 0.9756
    assert 'class_metrics' in d
    print("✅ JSON valide")
```

### Test 3: Modèle Chargeable

```python
from ultralytics import YOLO
model = YOLO('models/best.pt')
# Si pas d'erreur: ✅ OK
```

---

## 📋 CHECKLIST DÉPLOIEMENT

### Pre-Déploiement

```
☐ Lire QUICK_SUMMARY_2MIN.md (2 min)
☐ Exécuter verify_db.py (1 min)
☐ Vérifier fichiers JSON/BD (5 min)
☐ Obtenir approbation Direction (24h)
☐ Configurer monitoring (4h)
☐ Préparer test E2E (2h)
```

### Déploiement Phase 1

```
☐ Tester sur 1 zone (1 jour)
☐ Vérifier détections (8h)
☐ Collecter logs (24h)
☐ Analyser feedback (24h)
```

### Déploiement Phase 2

```
☐ Rollout toutes zones (2 jours)
☐ Former utilisateurs (1 jour)
☐ Activer monitoring complet (4h)
☐ Support 24/7 prêt (asap)
```

---

## 🆘 TROUBLESHOOTING RAPIDE

### Problème: BD manquante

```bash
# Solution
python init_unified_db.py
python insert_metrics_to_db.py
```

### Problème: JSON invalide

```bash
# Régénérer
python extract_model_metrics.py
```

### Problème: Modèle ne charge pas

```bash
# Vérifier fichier
ls -la models/best.pt
# Si manquant: télécharger depuis ...

# Tester
python -c "from ultralytics import YOLO; YOLO('models/best.pt')"
```

### Problème: Détections 0%

```bash
# Vérifier threshold
# Dans config: CONFIDENCE_THRESHOLD = 0.5 (ou 0.2 pour test)

# Vérifier modèle
python detect.py --weights models/best.pt --source test.jpg --verbose
```

---

## 📞 SUPPORT D'URGENCE

### Si Problème Production

```bash
# 1. Vérifier status
python verify_db.py

# 2. Logs applicatif
tail -f logs/app.log

# 3. Contacte ML Team
# Priority: URGENT
```

### Si Besoin Rollback

```bash
# Retour version précédente
# ID 7 contient anciennes métriques (0.65 mAP)
# Mais: Pas recommandé, modèle v2.0 bien meilleur!
```

---

## 🎯 COMMANDES PAR PROFIL

### Direction: Approbation (5 min)

```bash
cat QUICK_SUMMARY_2MIN.md  # Lire
python verify_db.py        # Vérifier
# → Approuver
```

### IT/DevOps: Setup (1h)

```bash
code FINALISATION_RAPPORT.md  # Lire config
python verify_db.py           # Vérifier
# → Configurer monitoring
# → Préparer test E2E
```

### ML: Validation (2h)

```bash
code ANALYSE_METRIQUES_BEST_PT_REELLE.md  # Deep dive
python extract_model_metrics.py           # Voir données
python -c "import json; print(json.load(open('model_metrics.json')))"  # Vérifier
```

### Support: Formation (1h)

```bash
code INDEX_COMPLET_NAVIGATION.md  # Comprendre structure
python verify_db.py                # Savoir vérifier
# → Former utilisateurs finaux
```

---

## 🚀 GO/NO-GO CHECKLIST

### GO Conditions ✅

- [x] Métriques extraites (97.56%)
- [x] BD mise à jour (ID 8)
- [x] Documentation complète
- [x] Scripts testés
- [ ] Approbation métier (à obtenir)
- [ ] Infrastructure prête (à confirmer)

### NO-GO Conditions ❌

- [ ] Métriques manquantes
- [ ] BD vide/corrompue
- [ ] Scripts erreur
- [ ] Métier refuse
- [ ] Infrastructure indisponible

---

**🎯 READY FOR PRODUCTION DEPLOYMENT**

*Exécutez: `python verify_db.py` puis `cat QUICK_SUMMARY_2MIN.md`*
