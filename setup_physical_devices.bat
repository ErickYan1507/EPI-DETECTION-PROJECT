@echo off
REM Batch file for Windows to setup physical devices
REM Script de configuration des périphériques physiques pour Windows

cls
echo.
echo ========================================================
echo  [EPI DETECTION] Installation Peripheriques Physiques
echo ========================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Python n'est pas installe ou non accessible
    echo          Installez Python 3.8+ depuis python.org
    pause
    exit /b 1
)

echo [OK] Python detecte
echo.

REM Show menu
echo Que voulez-vous faire?
echo.
echo  1. Installer les dependances (menu interactif)
echo  2. Valider l'installation
echo  3. Lancer le dashboard (besoin d'un serveur actif)
echo  4. Lire le guide rapide
echo  5. Ouvrir l'index des fichiers
echo  6. Quitter
echo.

set /p choice="Votre choix (1-6): "

if "%choice%"=="1" (
    echo.
    echo Lancement de l'installation...
    echo.
    python install_physical_devices.py
    pause
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Validation de l'installation...
    echo.
    python validate_physical_devices.py
    pause
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Ouverture du dashboard...
    echo Assurez-vous que le serveur est lance
    echo.
    timeout /t 2
    start http://localhost:5000/unified_monitoring.html
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Ouverture du guide rapide...
    echo.
    timeout /t 1
    if exist QUICK_START_PHYSICAL_DEVICES.md (
        start QUICK_START_PHYSICAL_DEVICES.md
    ) else (
        echo [ERREUR] Fichier guide non trouve
    )
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Ouverture de l'index...
    echo.
    timeout /t 1
    if exist PHYSICAL_DEVICES_INDEX.md (
        start PHYSICAL_DEVICES_INDEX.md
    ) else (
        echo [ERREUR] Fichier index non trouve
    )
    goto end
)

if "%choice%"=="6" (
    echo.
    echo Quitter
    echo.
    goto end
)

echo [ERREUR] Choix invalide
pause
goto menu

:end
echo.
echo ========================================================
echo  Fin du script
echo ========================================================
echo.
