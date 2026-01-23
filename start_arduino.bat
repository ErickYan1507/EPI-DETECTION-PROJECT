@echo off
REM Arduino Integration Quick Start Script
REM EPI Detection System v2.0

cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   🤖 EPI DETECTION SYSTEM - ARDUINO INTEGRATION v2.0   ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

echo ✅ Python détecté

REM Vérifier l'environnement virtuel
if not exist .venv (
    echo.
    echo ⚠️  Environnement virtuel non trouvé
    echo Création de l'environnement virtuel...
    python -m venv .venv
)

REM Activer l'environnement virtuel
call .venv\Scripts\activate.bat

echo ✅ Environnement virtuel activé

REM Installer/mettre à jour PySerial
echo.
echo 📦 Vérification des dépendances...
pip install pyserial -q
echo ✅ PySerial installé

REM Afficher le menu
echo.
echo ════════════════════════════════════════════════════════
echo 🎯 CHOISIR UN MODE:
echo ════════════════════════════════════════════════════════
echo.
echo 1️⃣  🚀 Démarrer l'application (Dashboard + API)
echo 2️⃣  🕹️  Ouvrir le Control Panel Arduino
echo 3️⃣  🧪 Lancer les tests Arduino
echo 4️⃣  📡 Monitor série (Arduino)
echo 5️⃣  📚 Ouvrir la documentation
echo 6️⃣  ❌ Quitter
echo.
set /p choice="Sélectionnez une option (1-6): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Démarrage de l'application...
    echo.
    echo 📌 Dashboard:        http://localhost:5000/unified_monitoring.html
    echo 📌 Arduino Panel:    http://localhost:5000/arduino_control_panel.html
    echo 📌 API:             http://localhost:5000/api/physical/arduino/*
    echo.
    python run.py
) else if "%choice%"=="2" (
    echo.
    echo 🕹️  Ouverture du Control Panel Arduino...
    start http://localhost:5000/arduino_control_panel.html
    echo.
    echo ⚠️  Assurez-vous que l'application est lancée (option 1)
    pause
) else if "%choice%"=="3" (
    echo.
    echo 🧪 Lancement des tests Arduino...
    echo.
    python test_arduino_integration.py --test all
    pause
) else if "%choice%"=="4" (
    echo.
    echo 📡 Monitor série Arduino
    echo.
    echo Entrez le port COM (ex: COM3):
    set /p port="Port: "
    python -m serial.tools.miniterm %port% 9600
) else if "%choice%"=="5" (
    echo.
    echo 📚 Ouvrir la documentation...
    echo.
    echo Fichiers disponibles:
    echo   1. ARDUINO_QUICKSTART.md (Guide rapide)
    echo   2. ARDUINO_INTEGRATION_GUIDE.md (Complet)
    echo   3. ARDUINO_IMPLEMENTATION_SUMMARY.md (Résumé)
    echo.
    set /p doc="Choisissez (1-3): "
    if "%doc%"=="1" (
        notepad ARDUINO_QUICKSTART.md
    ) else if "%doc%"=="2" (
        notepad ARDUINO_INTEGRATION_GUIDE.md
    ) else if "%doc%"=="3" (
        notepad ARDUINO_IMPLEMENTATION_SUMMARY.md
    )
) else if "%choice%"=="6" (
    echo.
    echo 👋 Au revoir!
    exit /b 0
) else (
    echo.
    echo ❌ Option invalide
    pause
    goto :menu
)

goto :menu
exit /b 0

:menu
cls
goto :menu
