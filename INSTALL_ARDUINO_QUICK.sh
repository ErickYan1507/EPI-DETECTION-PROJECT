#!/bin/bash
# 🚀 INSTALLATION RAPIDE ARDUINO MEGA
# Configuration: Buzzer=9, Red=5, yellow=3, green=3
# Temps estimé: 15 minutes

echo "🤖 Installation Arduino MEGA - Alertes Temps Réel"
echo "=================================================="
echo ""

# Étape 1: PySerial
echo "1️⃣ Installation de PySerial..."
pip install pyserial
echo "✅ PySerial installé"
echo ""

# Étape 2: Lister les ports
echo "2️⃣ Ports disponibles:"
python -m serial.tools.list_ports
echo ""
read -p "Quel est votre port COM? (ex: COM3): " COM_PORT
echo ""

# Étape 3: Instructions Arduino
echo "3️⃣ PROCHAINES ÉTAPES MANUELLES:"
echo "   a) Ouvrir Arduino IDE"
echo "   b) Fichier → Ouvrir"
echo "   c) Sélectionner: scripts/tinkercad_arduino.ino"
echo "   d) Tools → Board → Arduino MEGA or MEGA 2560"
echo "   e) Tools → Port → $COM_PORT"
echo "   f) Sketch → Upload (Ctrl+U)"
echo ""
read -p "✅ Code Arduino chargé? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "⏹️  Rechargez le code Arduino et relancez ce script"
    exit 1
fi
echo ""

# Étape 4: Tests
echo "4️⃣ Lancement des tests..."
echo "   Options:"
echo "   1) Tous les tests"
echo "   2) Mode interactif"
echo "   3) Passer"
echo ""
read -p "Choisissez une option (1-3): " TEST_OPTION

case $TEST_OPTION in
    1)
        python arduino_mega_test.py
        ;;
    2)
        python arduino_mega_test.py
        ;;
    *)
        echo "Tests ignorés"
        ;;
esac

echo ""
echo "=================================="
echo "✅ Installation Complète!"
echo "=================================="
echo ""
echo "Documentation disponible:"
echo "  • ARDUINO_README.md - Point d'entrée"
echo "  • ARDUINO_MEGA_CONFIG.md - Configuration technique"
echo "  • ARDUINO_WIRING_DIAGRAM.md - Schémas branchement"
echo "  • DEPLOYMENT_GUIDE.py - Guide complet"
echo ""
echo "Prochain: Intégrer dans votre code Python"
echo ""
