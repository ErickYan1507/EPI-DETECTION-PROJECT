# 🚀 COMMANDES PRÊTES À COPIER-COLLER

## OPTION 1: ULTRA-RAPIDE (RECOMMANDÉ) - 20-30 min/epoch

### Étape 1: Redimensionner dataset (2-3 minutes)
```powershell
python optimize_training_speed.py --resize --size 416 --dataset dataset
```

### Étape 2: Entraîner avec optimisations
```powershell
python train.py --dataset dataset --epochs 50 --batch-size 48 --img-size 416
```

**Résultat:** ~17-25 heures pour 50 epochs (1 jour!)

---

## OPTION 2: RAPIDE SANS REDIMENSIONNER - 45-60 min/epoch

### Directement entraîner (pas de prétraitement)
```powershell
python train.py --dataset dataset --epochs 50 --batch-size 32 --img-size 416
```

**Résultat:** ~37-50 heures pour 50 epochs (2 jours)

---

## OPTION 3: SCRIPT AUTOMATISÉ (PowerShell)

### Tout en un
```powershell
.\quick_train_ultra_fast.ps1
```

Le script demande si redimensionner puis gère tout automatiquement.

---

## OPTION 4: APRÈS ENTRAÎNEMENT - Affinage haute résolution (optionnel)

Si vous voulez meilleure précision en 640×640:

```powershell
python train.py --dataset dataset --epochs 20 --batch-size 24 --img-size 640 --weights models/best.pt
```

**Note:** Transfer learning sur le modèle pré-entraîné (converge vite)

---

## TEST RAPIDE MODÈLE

Après entraînement:
```powershell
python test_api_detection.py --model models/best.pt
```

---

## AFFICHAGE GUIDE D'OPTIMISATION

Pour revoir les détails:
```powershell
python optimize_training_speed.py --guide
```

---

## DÉPANNAGE

### OutOfMemory?
```powershell
# Le script auto-réduit, mais vous pouvez forcer batch 16:
python train.py --dataset dataset --epochs 50 --batch-size 16 --img-size 416
```

### Vérifier GPU disponible:
```powershell
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
```

### Vérifier RAM disponible:
```powershell
python -c "import psutil; mem = psutil.virtual_memory(); print(f'Total: {mem.total/1e9:.1f}GB, Available: {mem.available/1e9:.1f}GB, Used: {mem.percent}%')"
```

---

## RÉSUMÉ GAINS

| Métrique | Avant | Après | Gain |
|----------|-------|-------|------|
| Temps/epoch | 3:00h | 20-30min | **85%** ⚡ |
| 50 epochs | 150h | 17-25h | **85%** ⚡ |
| 100 epochs | 300h | 34-50h | **85%** ⚡ |
| Jours | 12.5 | **1-2** | **10x plus rapide** 🚀 |

---

## FICHIERS CRÉÉS/MODIFIÉS

### Nouveaux fichiers:
- ✅ `optimize_training_speed.py` - Script redimensionnement
- ✅ `quick_train_ultra_fast.ps1` - Automation PowerShell
- ✅ `quick_train_ultra_fast.sh` - Automation Bash
- ✅ `SPEED_OPTIMIZATION_GUIDE.md` - Documentation détaillée
- ✅ `OPTIMIZATION_APPLIED.txt` - Explications techniques
- ✅ `START_OPTIMIZED_TRAINING.txt` - Commandes détaillées
- ✅ `COPY_PASTE_COMMANDS.md` - Ce fichier

### Fichiers modifiés:
- 📝 `train.py` - Paramètres optimisés par défaut

---

## ⏱️ ESTIMATIONS DE TEMPS

### Avec redimensionnement (Ultra-rapide):
```
Redimensionner: 2-3 min
50 epochs: 17-25 heures  
Total: ~17-26 heures (1 jour)
```

### Sans redimensionner (Rapide):
```
50 epochs: 37-50 heures
Total: ~37-50 heures (2 jours)
```

### Affinage 640×640 (optionnel):
```
20 epochs: 15-30 heures
Total: ~15-30 heures (1 jour)
```

---

## VÉRIFICATION PRE-LANCEMENT

Avant de lancer, copier-coller dans PowerShell:

```powershell
# Vérifier GPU
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"

# Vérifier dataset
Get-ChildItem dataset/images/train | Measure-Object | Select-Object Count

# Vérifier data.yaml
Test-Path dataset/data.yaml
```

Tous les verts? C'est parti! 🚀

---

## 📚 DOCUMENTATION COMPLÈTE

Pour plus de détails:
- [SPEED_OPTIMIZATION_GUIDE.md](SPEED_OPTIMIZATION_GUIDE.md)
- [OPTIMIZATION_APPLIED.txt](OPTIMIZATION_APPLIED.txt)
- [START_OPTIMIZED_TRAINING.txt](START_OPTIMIZED_TRAINING.txt)

---

## 🎯 COMMANDE DÉFINITIVE

```powershell
# ULTRA-RAPIDE (RECOMMANDÉ):
python optimize_training_speed.py --resize --size 416 --dataset dataset; python train.py --dataset dataset --epochs 50 --batch-size 48 --img-size 416

# Ou split en deux:
python optimize_training_speed.py --resize --size 416 --dataset dataset
python train.py --dataset dataset --epochs 50 --batch-size 48 --img-size 416
```

À vous de jouer! 🚀✨
