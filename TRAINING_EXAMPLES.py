#!/usr/bin/env python3
"""
Exemples d'utilisation du train.py optimisé
Copiez-collez les commandes selon vos besoins
"""

# ═══════════════════════════════════════════════════════════
# 1️⃣ ENTRAÎNEMENT RAPIDE (RECOMMANDÉ)
# ═══════════════════════════════════════════════════════════
"""
Description: Entraînement rapide pour démarrer
Temps: 5-10 minutes (GPU) | 15-20 minutes (CPU)
Qualité: Bonne pour test
Espace: 100 MB

Commande:
"""
# python train.py --epochs 50 --batch-size 8

# ═══════════════════════════════════════════════════════════
# 2️⃣ ENTRAÎNEMENT STANDARD
# ═══════════════════════════════════════════════════════════
"""
Description: Entraînement équilibré (par défaut)
Temps: 10-20 minutes (GPU) | 30-45 minutes (CPU)
Qualité: Excellent
Espace: 100 MB

Commande:
"""
# python train.py --epochs 100 --batch-size 16

# ═══════════════════════════════════════════════════════════
# 3️⃣ ENTRAÎNEMENT QUALITÉ
# ═══════════════════════════════════════════════════════════
"""
Description: Meilleur modèle (plus long)
Temps: 30-60 minutes (GPU)
Qualité: Maximum
Espace: 100 MB

Commande:
"""
# python train.py --epochs 200 --batch-size 8 --img-size 800

# ═══════════════════════════════════════════════════════════
# 4️⃣ ENTRAÎNEMENT TEST (ULTRA-RAPIDE)
# ═══════════════════════════════════════════════════════════
"""
Description: Test rapide des optimisations
Temps: 2-5 minutes
Qualité: Faible (test seulement)
Espace: 100 MB

Commande:
"""
# python train.py --epochs 10 --batch-size 4 --img-size 416

# ═══════════════════════════════════════════════════════════
# 5️⃣ ENTRAÎNEMENTS MULTIPLES
# ═══════════════════════════════════════════════════════════
"""
Description: 3 entraînements successifs rapides
Temps: 15-30 minutes total
Résultat: 3 models/best.pt (remplacé chaque fois)
Usage: Comparer différentes seed/initialisation

Commande:
"""
# python train.py --num-trainings 3 --epochs 50 --batch-size 8

# ═══════════════════════════════════════════════════════════
# 6️⃣ AVEC DATASET PERSONNALISÉ
# ═══════════════════════════════════════════════════════════
"""
Description: Entraîner avec dataset spécifique
Dataset: Doit avoir structure images/train, images/val, labels/

Commande:
"""
# python train.py --dataset /chemin/vers/dataset --epochs 100 --batch-size 16

# ═══════════════════════════════════════════════════════════
# 7️⃣ GPU ULTRA-RAPIDE (Batch gros)
# ═══════════════════════════════════════════════════════════
"""
Description: Exploiter pleinement le GPU
Risque: Peut nécessiter GPU haute performance
Temps: 3-5 minutes (GPU rapide)
Qualité: Réduite (img_size=416)

Commande:
"""
# python train.py --epochs 50 --batch-size 32 --img-size 416

# ═══════════════════════════════════════════════════════════
# 8️⃣ CPU SEUL (Peu de mémoire)
# ═══════════════════════════════════════════════════════════
"""
Description: Entraînement CPU optimisé
Restriction: Petit batch_size
Temps: 30-45 minutes
Qualité: Bonne mais lent

Commande:
"""
# python train.py --epochs 50 --batch-size 4 --img-size 416

# ═══════════════════════════════════════════════════════════
# 9️⃣ AVEC POIDS PRE-ENTRAÎNÉS PERSONNALISÉS
# ═══════════════════════════════════════════════════════════
"""
Description: Utiliser des poids YOLOv5 différents
Options: yolov5n, yolov5s (petit), yolov5m (moyen), yolov5l (gros)

Commande pour version gros:
"""
# python train.py --weights yolov5l.pt --epochs 100 --batch-size 8

# Commande pour version très petite:
# python train.py --weights yolov5n.pt --epochs 50 --batch-size 16

# ═══════════════════════════════════════════════════════════
# 🔟 AVEC NOM DE RUN PERSONNALISÉ
# ═══════════════════════════════════════════════════════════
"""
Description: Donner un nom à votre entraînement
Utilité: Identifier le run dans runs/train/

Commande:
"""
# python train.py --run-name mon_modele_v1 --epochs 50

# ═══════════════════════════════════════════════════════════
# VARIANTES AVANCÉES
# ═══════════════════════════════════════════════════════════

# Image size réduite (plus rapide mais moins précis)
# python train.py --epochs 100 --batch-size 16 --img-size 320

# Image size augmentée (plus précis mais plus lent)
# python train.py --epochs 100 --batch-size 8 --img-size 896

# Avec toutes les classes
# python train.py --classes helmet vest glasses person boots --epochs 100

# Avec noms de classes personnalisés
# python train.py --classes hard_hat safety_vest goggles worker safety_boots --epochs 100

# ═══════════════════════════════════════════════════════════
# VÉRIFICATION APRÈS ENTRAÎNEMENT
# ═══════════════════════════════════════════════════════════

"""
1. Vérifier que le modèle existe:
   ls -lh models/best.pt
   
2. Vérifier qu'un seul fichier est créé:
   ls models/ | grep .pt | wc -l  # Devrait afficher 1
   
3. Voir l'historique complet:
   ls runs/train/
   
4. Tester le modèle:
   python detect.py --weights models/best.pt --source test.jpg
"""

# ═══════════════════════════════════════════════════════════
# UTILISATION EN CODE PYTHON
# ═══════════════════════════════════════════════════════════

"""
Exemple d'utilisation du modèle créé:

from yolov5 import YOLOv5

# Charger le modèle
model = YOLOv5('models/best.pt')

# Prédire sur une image
results = model.predict('image.jpg')

# Afficher les résultats
results.print()

# Accéder aux détections
for pred in results.pred:
    for box in pred:
        print(f"Classe: {box[5]}, Confiance: {box[4]}")
"""

# ═══════════════════════════════════════════════════════════
# COMMANDES POWERSHELL (Windows)
# ═══════════════════════════════════════════════════════════

"""
# Rapide
.\quick_train_optimized.ps1 -epochs 50 -batch 8

# Mode prédéfini
.\quick_train_optimized.ps1 -mode fast
.\quick_train_optimized.ps1 -mode quality
.\quick_train_optimized.ps1 -mode multi
"""

# ═══════════════════════════════════════════════════════════
# COMMANDES BATCH (Windows)
# ═══════════════════════════════════════════════════════════

"""
# Rapide
quick_train.bat 50 8

# Standard
quick_train.bat 100 16
"""

# ═══════════════════════════════════════════════════════════
# MONITORING EN TEMPS RÉEL
# ═══════════════════════════════════════════════════════════

"""
Dans un autre terminal:

# TensorBoard
tensorboard --logdir runs/train/

# Puis ouvrir: http://localhost:6006
"""

# ═══════════════════════════════════════════════════════════
# TROUBLESHOOTING RAPIDE
# ═══════════════════════════════════════════════════════════

"""
❌ ERREUR: Out of memory
   ✅ Solution: --batch-size 4 ou --img-size 416

❌ ERREUR: Entraînement très lent
   ✅ Solution: augmenter --workers ou réduire --img-size

❌ ERREUR: Dataset non trouvé
   ✅ Solution: Créer dataset/images/train/, dataset/images/val/

❌ ERREUR: Modèles multiples créés
   ✅ Solution: C'est normal! Garder models/best.pt

❌ ERREUR: YOLOv5 non trouvé
   ✅ Solution: train.py le télécharge automatiquement
"""

# ═══════════════════════════════════════════════════════════
# COMMANDES UTILES
# ═══════════════════════════════════════════════════════════

"""
# Voir le help
python train.py --help

# Compter les fichiers models
ls models/ | wc -l

# Supprimer les anciens entraînements
rm -rf runs/train/*

# Nettoyer les modèles
rm models/*

# Voir la structure dataset
tree dataset/
ou
ls -R dataset/
"""

# ═══════════════════════════════════════════════════════════
# RÉSUMÉ RAPIDE
# ═══════════════════════════════════════════════════════════

"""
DÉMARRAGE RAPIDE:
  python train.py --epochs 50

PRODUCTION:
  python train.py --epochs 100 --batch-size 16

MEILLEUR MODÈLE:
  python train.py --epochs 200 --batch-size 8 --img-size 800

TEST:
  python train.py --epochs 10 --batch-size 4
"""
