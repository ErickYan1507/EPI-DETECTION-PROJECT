#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUIDE RAPIDE - Commandes essentielles apres les corrections
"""

print("""
╔════════════════════════════════════════════════════════════════════╗
║         GUIDE RAPIDE - EPI DETECTION SYSTEM CORRECTIONS             ║
╚════════════════════════════════════════════════════════════════════╝

=== ÉTAPE 1: REDÉMARRER L'APPLICATION ===

Ouvrir un terminal et exécuter:
    cd D:\\projet\\EPI-DETECTION-PROJECT
    python app/main.py

L'application démarre sur: http://localhost:5000


=== ÉTAPE 2: TESTER LES CORRECTIONS ===

A. UPLOADS (Double-clic fix):
   URL: http://localhost:5000/upload
   Test: 
   1. Charger une image
   2. Cliquer une seule fois sur "Analyze Now"
   3. Attendre les résultats
   ✓ Doit voir les détections

B. TRAINING RESULTS (Dates):
   URL: http://localhost:5000/training-results
   Test:
   1. Vérifier que les dates s'affichent (JJ/MM/AAAA)
   2. Vérifier que les graphiques se chargent
   3. Cliquer sur un résultat pour voir les détails
   ✓ Les dates ne doivent pas afficher "Invalid Date"

C. UNIFIED MONITORING (Détection):
   URL: http://localhost:5000/unified_monitoring.html
   Test:
   1. Cliquer sur "Start Camera"
   2. Attendre les détections
   3. Vérifier les statistiques
   ✓ Doit voir les détections et les stats mises à jour


=== ÉTAPE 3: VÉRIFIER LES LOGS ===

Ouvrir un nouveau terminal et exécuter:
    cd D:\\projet\\EPI-DETECTION-PROJECT
    python -c "
import subprocess
import time
import os

log_file = 'logs/app.log'
if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        lines = f.readlines()
        for line in lines[-50:]:  # Dernières 50 lignes
            print(line.rstrip())
"

Chercher les messages:
    ✓ "MultiModelDetector initialisé"
    ✓ "Modèle chargé: best.pt"
    ✓ "Det: X détections" (sans erreurs)


=== ÉTAPE 4: DIAGNOSTICS (SI PROBLÈMES) ===

Vérifier l'état du système:
    python fix_detection_issues.py

Vérifier/corriger la base de données:
    python fix_database.py

Tester les corrections appliquées:
    python test_simple.py


=== FICHIERS CLÉS MODIFIÉS ===

templates/upload.html
    ✓ Ajout flag 'isProcessing' pour double-clic
    ✓ Meilleure gestion des erreurs

templates/training_results.html
    ✓ Fonction formatDate() pour dates invalides
    ✓ Gestion d'erreurs pour timestamps

app/main.py (process_image)
    ✓ Utilisation du détecteur global
    ✓ Activation du mode ensemble

app/main.py (process_video)
    ✓ Meilleure gestion du détecteur
    ✓ Performance optimisée

config.py
    ✓ MULTI_MODEL_ENABLED = True
    ✓ DEFAULT_USE_ENSEMBLE = True
    ✓ MODEL_WEIGHTS avec best.pt = 1.0


=== CONFIGURATIONS IMPORTANTES ===

Base de données:
    DB_TYPE: sqlite (ou mysql si configuré)
    DATABASE_URI: sqlite:///database/epi_detection.db

Modèles:
    MODELS_FOLDER: models/
    MODEL_PATH: models/best.pt
    MULTI_MODEL_ENABLED: True (tous les modèles)
    DEFAULT_USE_ENSEMBLE: True (uploads)
    USE_ENSEMBLE_FOR_CAMERA: False (performance)

Détection:
    CONFIDENCE_THRESHOLD: 0.5
    IOU_THRESHOLD: 0.65
    MAX_DETECTIONS: 100


=== DÉPANNAGE RAPIDE ===

Problème: "Aucun modèle trouvé"
Solution: Vérifier que models/best.pt existe
    ls models/best.pt

Problème: "Invalid Date" dans training results
Solution: Base de données a besoin de correction
    python fix_database.py

Problème: Doubles uploads
Solution: Vider le cache navigateur (Ctrl+Shift+Delete)

Problème: Port 5000 déjà utilisé
Solution: Tuer le processus et redémarrer
    netstat -ano | findstr :5000
    taskkill /PID <PID> /F


=== PERFORMANCE ATTENDUE ===

Upload image: < 2 secondes
Upload vidéo: < 30 secondes (pour 100 frames)
Détection temps réel: 5-10 FPS (dépend du hardware)
API latency: < 200ms


=== CONTACT & DOCUMENTATION ===

Documentation complète:
    - CORRECTIONS_README.md
    - CORRECTIONS_SUMMARY.md
    - CORRECTIONS_APPLIED.py

Scripts:
    - fix_detection_issues.py (diagnostic)
    - fix_database.py (BD check/fix)
    - test_simple.py (tests)

═══════════════════════════════════════════════════════════════════════════

✓ Vous êtes prêt! Lancez l'application et testez les corrections.
✓ Si vous avez des problèmes, exécutez les scripts de diagnostic.
✓ Pour plus d'infos, lisez la documentation incluse.

═══════════════════════════════════════════════════════════════════════════
""")
