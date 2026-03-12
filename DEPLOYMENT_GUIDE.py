#!/usr/bin/env python3
"""
🚀 Guide de Déploiement Complet - Arduino MEGA Alertes Temps Réel
EPI Detection System - Real-time Alerts
"""

DEPLOYMENT_GUIDE = """
╔════════════════════════════════════════════════════════════════════════════╗
║                     🤖 ARDUINO MEGA - GUIDE COMPLET                        ║
║           Configuration pour Alertes Temps Réel - EPI Detection            ║
╚════════════════════════════════════════════════════════════════════════════╝

## 📋 INFORMATIONS TECHNIQUES

Configuration Matérielle:
├─ Microcontrôleur: Arduino MEGA 2560
├─ Buzzer: Port 9 (PWM)
├─ LED Rouge (Danger): Port 30
├─ LED Jaune (Warning): Port 26
├─ LED Vert (Safe): Port 36
└─ Vitesse Série: 9600 baud

Système d'Alertes:
├─ Compliance ≥ 80%     → LED VERT seule (Safe)
├─ Compliance 60-79%    → LED JAUNE seule (Warning)
└─ Compliance < 60%     → LED ROUGE + BUZZER (Danger)


## 🛠️ ÉTAPE 1: Préparation du Matériel

### Composants Nécessaires:
┌─ Arduino MEGA 2560
├─ Buzzer Actif 5V
├─ LED Vert (avec résistance 220Ω)
├─ LED Jaune (avec résistance 220Ω)
├─ LED Rouge (avec résistance 220Ω)
├─ Résistances 220Ω (×3 pour LEDs)
├─ Câble USB Arduino
└─ Alimentation externe 5V (optionnel mais recommandé)

### Vérification avant Installation:
[ ] Arduino reconnu sur le portail de communication PC
[ ] LEDs fonctionnent individuellement (test avec batterie)
[ ] Buzzer produit du son (test avec batterie)
[ ] Câble USB en bon état


## 📱 ÉTAPE 2: Installation du Code Arduino

### 2.1 Télécharger l'IDE Arduino
```
Aller sur: https://www.arduino.cc/en/software
Télécharger et installer "Arduino IDE"
```

### 2.2 Charger le Code Arduino MEGA
```
Fichier à charger: scripts/tinkercad_arduino.ino

Procédure:
1. Ouvrir "scripts/tinkercad_arduino.ino" dans Arduino IDE
2. Connecter Arduino MEGA par USB
3. Sélectionner: Tools → Board → "Arduino MEGA or MEGA 2560"
4. Sélectionner: Tools → Port → "COM3" (ou votre port)
5. Cliquer: Sketch → Upload (ou Ctrl+U)
6. Attendre "Done uploading"
```

### 2.3 Vérifier l'Envoi
```
Arduino IDE → Tools → Serial Monitor
Doit voir:
[STARTUP] EPI Detection Arduino MEGA Controller v2.1
[INFO] System ready - waiting for commands
[INFO] Configuration: Buzzer=9, Red=30, yellow=3, green=3
```


## 🔌 ÉTAPE 3: Installation du Branchement Physique

### 3.1 Schéma de Branchement Simplifié
```
Arduino MEGA:
Pin 36 --[220Ω]--[LED Vert]--[GND]
Pin 26 --[220Ω]--[LED Jaune]--[GND]
Pin 30 --[220Ω]--[LED Rouge]--[GND]
Pin 9 -----[Buzzer+]--[GND]

Voir le fichier: ARDUINO_WIRING_DIAGRAM.md pour schéma complet
```

### 3.2 Installation Physique
```
1. Éteindre Arduino
2. Brancheter les composants selon le schéma
3. Vérifier polarité LEDs et buzzer
4. Double-vérifier connexions GND
5. Réalimenter Arduino
```

### 3.3 Test Hardware
```
Arduino ID → Tools → Serial Monitor (9600 baud)

Envoyer: C85
Résultat attendu: LED VERT s'allume

Envoyer: C70
Résultat attendu: LED JAUNE s'allume

Envoyer: C45
Résultat attendu: LED ROUGE + BUZZER
```


## 💻 ÉTAPE 4: Installation Python

### 4.1 Installer PySerial
```bash
pip install pyserial
```

### 4.2 Tester la Communication
```bash
# Lister les ports disponibles
python -m serial.tools.list_ports

# Vous devriez voir quelque chose comme:
# /dev/ttyUSB0 - Arduino MEGA 2560 (device)
# COM3 - Arduino MEGA 2560 (device)
```

### 4.3 Trouver le Port COM Correct
```bash
# Windows: Gestionnaire des Périphériques
# Chercher: "Arduino MEGA" ou "Ports COM"

# Linux/Mac:
ls /dev/tty*
```


## 🧪 ÉTAPE 5: Tests de Fonctionnement

### 5.1 Test Automatisé
```bash
python arduino_mega_test.py

Choisir option: 4 (Tous les tests)
Cela lance:
- Séquence de démarrage
- Tests de niveaux (Safe/Warning/Danger)
- Tests de détection EPI
```

### 5.2 Mode Interactif
```bash
python arduino_mega_test.py

Choisir option: 5 (Contrôle interactif)
Vous pouvez:
- Envoyer des niveaux de conformité (0-100)
- Simuler des détections EPI
- Tester les réactions du système
```

### 5.3 Tests Individuels
```bash
# Test 1: Startup
python arduino_mega_test.py → Choisir 1

# Test 2: Conformité
python arduino_mega_test.py  → Choisir 2

# Test 3: Détection
python arduino_mega_test.py → Choisir 3
```


## ⚙️ ÉTAPE 6: Intégration dans l'Application EPI

### 6.1 Configuration au Démarrage

Avant de lancer l'application Flask:

```python
# Dans votre code de démarrage (ex: run_app.py, main initiation)

from app.arduino_integration import ArduinoController

# Initialiser le contrôleur
arduino = ArduinoController(port='COM3', baudrate=9600)
arduino.connect()

# Enregistrer un callback pour les alertes
def on_alert(level):
    arduino.send_compliance_level(level)

arduino.register_callback(on_alert)
```

### 6.2 Envoi d'Alertes Détection

Depuis votre système de détection EPI:

```python
from app.arduino_integration import ArduinoController

arduino = ArduinoController(port='COM3', baudrate=9600)
arduino.connect()

# Après une détection
arduino.send_detection_data(
    helmet=detect_helmet,
    vest=detect_vest,
    glasses=detect_glasses,
    confidence=confidence_score
)
```

### 6.3 Alertes Basées sur Conformité

```python
# Envoyer le niveau de conformité calculé
compliance_level = calculate_compliance()
arduino.send_compliance_level(compliance_level)

# Arduino gère automatiquement:
# - LEDs (rouge/jaune/vert)
# - Buzzer si < 60%
```


## 📊 RAPPEL: États des LEDs

┌─────────────────────────────────────────────────────┐
│ NIVEAU DE CONFORMITÉ │ ÉTAT                         │
├─────────────────────┼──────────────────────────────┤
│ ≥ 80%               │ 🟢 LED VERT                  │
│ 60-79%              │ 🟡 LED JAUNE                 │
│ < 60%               │ 🔴 LED ROUGE + 🔊 BUZZER    │
└─────────────────────────────────────────────────────┘

Signification:
🟢 VERT   = ✅ SAFE (Conforme)
🟡 JAUNE  = ⚠️ WARNING (À risque)
🔴 ROUGE  = 🚨 DANGER (Non-conforme)


## 🔧 DÉPANNAGE

### Arduino ne trouve pas le port série
```
Solution 1: Installer driver CH340
Solution 2: Vérifier câble USB
Solution 3: Redémarrer Arduino
Solution 4: Tester un autre port USB
```

### LEDs ne s'allument pas
```
Solution 1: Vérifier polarité (longue broche = +)
Solution 2: Tester LED isolément avec batterie
Solution 3: Vérifier résistance 220Ω
Solution 4: Vérifier GND commun
```

### Buzzer ne sonne pas
```
Solution 1: Vérifier polarité
Solution 2: Tester buzzer isolément
Solution 3: Vérifier alimentation 5V sur pin 9
Solution 4: Passer en buzzer actif si buzzer passif
```

### Communication série instable
```
Solution 1: Réduire distance entre PC et Arduino (câble court)
Solution 2: Minimiser interférences wifi 2.4GHz
Solution 3: Ajouter condensateur 100µF entre 5V et GND
Solution 4: Vérifier vitesse 9600 baud
```


## 📁 FICHIERS MODIFIÉS/CRÉÉS

Fichiers Arduino:
├─ scripts/tinkercad_arduino.ino (MODIFIÉ - Nouvelle config)
├─ ARDUINO_MEGA_CONFIG.md (CRÉÉ - Documentation)
└─ ARDUINO_WIRING_DIAGRAM.md (CRÉÉ - Schéma branchement)

Fichiers Python:
├─ app/arduino_integration.py (Compatible - Pas changement d'API)
├─ arduino_mega_test.py (CRÉÉ - Script test)
└─ Ce fichier: DEPLOYMENT_GUIDE.md

Configuration Existante:
├─ test_arduino_integration.py (Compatible)
└─ arduino_control_panel.html (À mettre à jour si nécessaire)


## ✅ CHECKLIST FINALE

Avant production:
[ ] Arduino MEGA flashé avec code v2.1
[ ] Tous les composants branchés correctement
[ ] Port COM identifié et testé
[ ] PySerial installé (pip install pyserial)
[ ] Communication série testée (9600 baud)
[ ] LEDs s'allument correctement
[ ] Buzzer sonne correctement
[ ] Tests automatisés passent
[ ] Tests manuels valident states
[ ] Intégration dans main app testée
[ ] Alertes en temps réel fonctionnent

Production:
[ ] Documentation mise en place
[ ] Instructions de déploiement disponibles
[ ] Support technique formé
[ ] Maintenance routine planifiée


## 📞 ASSISTANCE TECHNIQUE

Erreurs Courants:
1. "Port not found" → Vérifier COM dans Gestionnaire Périphériques
2. "Permission denied" → Redémarrer IDE Arduino
3. "Upload timeout" → Vérifier câble, tester autre port USB
4. "Serial communication error" → Fermer Serial Monitor, voir PySerial


## 📚 DOCUMENTATION SUPPLÉMENTAIRE

- ARDUINO_MEGA_CONFIG.md → Configuration détaillée
- ARDUINO_WIRING_DIAGRAM.md → Schémas de branchement
- test_arduino_integration.py → Tests unitaires
- arduino_mega_test.py → Tests complets

"""

if __name__ == '__main__':
    print(DEPLOYMENT_GUIDE)
    
    # Optionnel: Sauvegarder en fichier
    with open('DEPLOYMENT_GUIDE_OUTPUT.txt', 'w', encoding='utf-8') as f:
        f.write(DEPLOYMENT_GUIDE)
    print("\n✅ Guide sauvegardé dans: DEPLOYMENT_GUIDE_OUTPUT.txt")
