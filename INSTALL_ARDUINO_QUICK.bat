@echo off
REM 🚀 INSTALLATION RAPIDE ARDUINO MEGA - VERSION WINDOWS
REM Configuration: Buzzer=9, Red=5, yellow=3, green=3
REM Temps estimé: 15 minutes

cls
echo.
echo 🤖 Installation Arduino MEGA - Alertes Temps Réel
echo ===================================================
echo.

REM Étape 1: PySerial
echo 1️⃣ Installation de PySerial...
pip install pyserial
if %ERRORLEVEL% EQU 0 (
    echo ✅ PySerial installé
) else (
    echo ❌ Erreur lors de l'installation
    pause
    exit /b 1
)
echo.

REM Étape 2: Lister les ports
echo 2️⃣ Recherche des ports Arduino disponibles...
echo.
python -m serial.tools.list_ports
echo.
set /p COM_PORT="Quel est votre port COM? (ex: COM3): "
echo (Vous avez sélectionné: %COM_PORT%)
echo.

REM Étape 3: Instructions Arduino
echo 3️⃣ PROCHAINES ÉTAPES MANUELLES:
echo    a) Ouvrir Arduino IDE
echo    b) Fichier --^> Ouvrir
echo    c) Sélectionner: scripts/tinkercad_arduino.ino
echo    d) Tools --^> Board --^> Arduino MEGA or MEGA 2560
echo    e) Tools --^> Port --^> %COM_PORT%
echo    f) Sketch --^> Upload (Ctrl+U)
echo.
set /p CONFIRM="✅ Code Arduino chargé? (y/n): "
if /i NOT "%CONFIRM%"=="y" (
    echo ⏹️ Rechargez le code Arduino et relancez ce script
    pause
    exit /b 1
)
echo.

REM Étape 4: Tests
echo 4️⃣ Lancement des tests...
echo.
echo Options:
echo   1) Tous les tests (recommandé)
echo   2) Mode interactif (manuel)
echo   3) Passer les tests
echo.
set /p TEST_OPTION="Choisissez une option (1-3): "

if "%TEST_OPTION%"=="1" (
    python arduino_mega_test.py
) else if "%TEST_OPTION%"=="2" (
    python arduino_mega_test.py
) else (
    echo Tests ignorés
)

echo.
echo ==================================
echo ✅ Installation Complète!
echo ==================================
echo.
echo Documentation disponible:
echo   • ARDUINO_README.md - Point d'entrée
echo   • ARDUINO_MEGA_CONFIG.md - Configuration technique
echo   • ARDUINO_WIRING_DIAGRAM.md - Schémas branchement
echo   • DEPLOYMENT_GUIDE.py - Guide complet (lisible)
echo.
echo Prochaine étape: Intégrer dans votre code Python
echo.
pause
