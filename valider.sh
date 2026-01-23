#!/bin/bash

# Validation rapide du projet EPI-DETECTION
# Usage: ./valider.sh

clear

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║           EPI-DETECTION PROJECT - VALIDATION RAPIDE                    ║"
echo "║                      10 janvier 2026                                   ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

echo "🔍 Lancement du test rapide..."
echo ""

python quicktest.py

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ VALIDATION RÉUSSIE                               ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Fichiers créés et validés:"
    echo "  ✅ EPI_CLASS_CONFIG.py       - Configuration centrale"
    echo "  ✅ training_optimizer.py      - Optimisation entraînement"
    echo "  ✅ cleanup_models.py          - Nettoyage des modèles"
    echo "  ✅ repair_project.py          - Diagnostic complet"
    echo "  ✅ quicktest.py               - Test rapide"
    echo ""
    echo "Prochaines étapes:"
    echo "  1. python cleanup_models.py -y          (Nettoyer les modèles)"
    echo "  2. python GUIDE_REPARATION.py          (Lire le guide complet)"
    echo "  3. Créer train_optimized.py            (Voir GUIDE_REPARATION.py)"
    echo "  4. python run_app.py                   (Lancer l'application)"
    echo ""
    echo "Documentation:"
    echo "  📋 FICHIERS_CREES.txt                  (Fichiers créés)"
    echo "  📖 GUIDE_REPARATION.py                 (Guide d'utilisation)"
    echo "  📊 RESUME_COMPLET_CORRECTIONS.md       (Résumé technique)"
    echo "  📈 AVANT_APRES_COMPARAISON.txt         (Améliorations)"
    echo "  ✅ REPARATION_VALIDEE.txt              (Certification)"
    echo ""
else
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║                    ❌ ERREUR - VALIDATION ÉCHOUÉE                      ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Actions recommandées:"
    echo "  1. Vérifier les erreurs ci-dessus"
    echo "  2. Exécuter: python repair_project.py"
    echo "  3. Consulter: repair_report.json"
    echo ""
    exit 1
fi
