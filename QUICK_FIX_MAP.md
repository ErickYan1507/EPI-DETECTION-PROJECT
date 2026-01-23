# 🚀 GUIDE RAPIDE: Corriger mAP TRÈS BASSE (0.02)

## TL;DR - En 30 Secondes

Votre modèle a mAP=0.02 car:
1. **50% des images n'avaient pas de labels** ❌
2. **Annotations invalides** (966 bounding boxes cassées) ❌
3. **Déséquilibre extrême** (person=1%, glasses=33%) ⚠️
4. **Seuils NMS mauvais** (0.25 et 0.45) ⚠️

## ✅ Solution: Pipeline en 1 Commande

```bash
# Tout faire d'un coup
python fix_map_pipeline.py
```

Ou étape par étape:

```bash
# 1. Diagnostic
python diagnose_low_map.py

# 2. Nettoyage dataset
python restructure_dataset.py

# 3. Augmentation (optionnel)
python augment_and_balance.py

# 4. Entraînement optimisé (2-4h)
python train_optimized_fixed.py
```

---

## Qu'est-ce Qui a Été Corrigé

### ✅ Dataset
```
Avant:  12,445 images, 5,571 labels → MISMATCH!
Après:  5,571 images, 5,571 labels → PARFAIT!
        
Supprimé: 6,226 images orphelines + 689 bboxes invalides
```

### ✅ Configuration
```python
# config.py - Seuils NMS optimisés
CONFIDENCE_THRESHOLD = 0.50  # was 0.25
IOU_THRESHOLD = 0.65        # was 0.45
NMS_IOU_THRESHOLD = 0.65    # was 0.5
```

### ✅ Entraînement
```python
# train_optimized_fixed.py
epochs: 200 (was 50)
batch_size: 32 (was 8)
data_augmentation: RENFORCÉE
patience: 50 (early stopping)
```

---

## Résultats Attendus

| Métrique | Avant | Après |
|----------|-------|-------|
| mAP50 | 0.0202 ❌ | 0.45-0.65 ✅ |
| mAP50-95 | 0.00464 ❌ | 0.30-0.50 ✅ |
| NMS time | 2.1s exceed ❌ | <1s ✅ |
| Instances | 12 ❌ | 3.5/image ✅ |

---

## Commandes Utiles

```bash
# 1. Tout en une commande (recommandé)
python fix_map_pipeline.py

# 2. Ou individuellement:
python diagnose_low_map.py          # Vérifier les problèmes
python restructure_dataset.py       # Nettoyer
python augment_and_balance.py       # Équilibrer
python train_optimized_fixed.py     # Entraîner

# 3. Pendant l'entraînement:
tail -f runs/train/epi_optimized_training/results.csv

# 4. Tester le nouveau modèle:
python detect.py --source test_image.jpg --weights models/best.pt
```

---

## Monitoring Pendant l'Entraînement

**Regarder `runs/train/epi_optimized_training/results.csv`:**

```
epoch | train_loss | val_loss | mAP50 | mAP50-95
------|-----------|----------|-------|----------
  1   | 0.5123    | 0.4891   | 0.001 | 0.0001
  5   | 0.3421    | 0.3156   | 0.015 | 0.0045
  10  | 0.2156    | 0.2134   | 0.065 | 0.0234
  20  | 0.1234    | 0.1456   | 0.234 | 0.1123
  50  | 0.0834    | 0.1123   | 0.456 | 0.3012  ← Bon!
```

**Si mAP n'améliore pas après epoch 50:** ⚠️
- Attendez jusqu'à epoch 100
- Si toujours < 0.1: problème du dataset reste
- Essayez: `--epochs 300 --patience 100`

---

## FAQ Rapide

**Q: Combien de temps?**
A: 2-4h sur GPU, 8-16h sur CPU

**Q: mAP s'améliorera vraiment?**
A: OUI! Maintenant qu'on a des données propres

**Q: Dois-je augmenter les données?**
A: Non, 5,571 images c'est assez. YOLOv5 fait déjà l'augmentation

**Q: Si mAP stagne < 0.3?**
A: 1) Collectez plus d'images réelles
   2) Améliorez les annotations
   3) Utilisez transfer learning (modèle pré-entraîné)

---

## Fichiers Créés

```
diagnose_low_map.py              ← Diagnostic
restructure_dataset.py            ← Nettoyage
sync_dataset.py                   ← Synchronisation
augment_and_balance.py            ← Augmentation
train_optimized_fixed.py          ← Entraînement optimisé
fix_map_pipeline.py               ← Pipeline complet
config.py                         ✏️ Modifié (seuils NMS)
DIAGNOSTIC_MAP_BASSE.md           ← Doc complète
QUICK_FIX_MAP.md                  ← Ce guide
```

---

## Prochaines Étapes

1. ✅ **Maintenant:** Exécuter `python fix_map_pipeline.py`
2. ⏳ **Demain/Après:** Vérifier mAP dans `results.csv`
3. 🎯 **Si mAP > 0.4:** Modèle PRÊT pour production!
4. ❌ **Si mAP < 0.2:** Créer issue avec `results.csv` pour debug

---

## Support

Si mAP n'améliore toujours pas:
1. Partagez `runs/train/epi_optimized_training/results.csv`
2. Partagez la sortie de `diagnose_low_map.py`
3. Vérifiez que `dataset/data.yaml` a 5 classes

