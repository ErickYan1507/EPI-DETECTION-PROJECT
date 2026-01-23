@echo off
REM 🚀 Démarrage rapide d'entraînement optimisé
REM Utilisation: quick_train.bat [epochs] [batch_size]

setlocal enabledelayedexpansion

set epochs=50
set batch=8
set imgsize=640

if not "%1"=="" set epochs=%1
if not "%2"=="" set batch=%2

cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║    🚀 ENTRAÎNEMENT OPTIMISÉ - DÉMARRAGE RAPIDE            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📋 Configuration:
echo   - Epochs: !epochs!
echo   - Batch Size: !batch!
echo   - Image Size: !imgsize!
echo.

REM Vérifier dataset
if not exist "dataset\images\train" (
    echo ⚠️  Dataset non trouvé!
    echo.
    echo Créez la structure:
    echo   dataset\images\train\
    echo   dataset\images\val\
    echo   dataset\labels\train\
    echo   dataset\labels\val\
    echo.
    pause
)

echo 🚀 Démarrage de l'entraînement...
echo ═════════════════════════════════════════════════════════════

python train.py --epochs !epochs! --batch-size !batch! --img-size !imgsize!

echo.
echo ═════════════════════════════════════════════════════════════
echo ✅ ENTRAÎNEMENT TERMINÉ
echo.

if exist "models\best.pt" (
    echo 📊 Résultat:
    echo   ✓ Modèle sauvegardé: models\best.pt
    echo.
    echo 🎯 Utilisation:
    echo   python detect.py --weights models\best.pt --source image.jpg
) else (
    echo ❌ Erreur: Modèle non créé
)

echo.
pause
