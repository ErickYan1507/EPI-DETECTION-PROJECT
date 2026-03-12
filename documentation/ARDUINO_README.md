# 🤖 Arduino MEGA - Alertes Temps Réel EPI Detection

## ⚡ Configuration Rapide (5 minutes)

```
Buzzer    → Port 9
LED ROUGE → Port 30 (Danger + 🔊 Buzzer si compliance < 60%)
LED JAUNE → Port 26 (Warning si 60% ≤ compliance ≤ 79%)
LED VERT  → Port 36 (Safe si compliance ≥ 80%)
```

## 📋 Checklist Rapide

- [ ] Arduino MEGA connecté en USB
- [ ] LEDs + Buzzer branchés (voir [ARDUINO_WIRING_DIAGRAM.md](ARDUINO_WIRING_DIAGRAM.md))
- [ ] Code Arduino chargé: `scripts/tinkercad_arduino.ino`
- [ ] PySerial installé: `pip install pyserial`
- [ ] Port COM identifié (voir Gestionnaire Périphériques)

## 🚀 Démarrage Immédiat

### 1️⃣ Charger le Code Arduino
```bash
# Utiliser Arduino IDE
# Fichier → Ouvrir → scripts/tinkercad_arduino.ino
# Sketch → Upload (ou Ctrl+U)
```

### 2️⃣ Tester la Communication
```bash
python arduino_mega_test.py
# Choisir l'option 4 (Tous les tests) ou 5 (Mode interactif)
```

### 3️⃣ Intégrer dans votre Code
```python
from app.arduino_integration import ArduinoController

# Initialiser
arduino = ArduinoController(port='COM3', baudrate=9600)
arduino.connect()

# Envoyer une alerte
arduino.send_compliance_level(85)  # LED Vert s'allume
arduino.send_compliance_level(70)  # LED Jaune s'allume
arduino.send_compliance_level(45)  # LED Rouge + Buzzer

# Fermer
arduino.disconnect()
```

## 📚 Documentation Complète

| Document | Contenu |
|----------|---------|
| [ARDUINO_MEGA_CONFIG.md](ARDUINO_MEGA_CONFIG.md) | Configuration technique détaillée |
| [ARDUINO_WIRING_DIAGRAM.md](ARDUINO_WIRING_DIAGRAM.md) | Schémas de branchement avec diagrams |
| [DEPLOYMENT_GUIDE.py](DEPLOYMENT_GUIDE.py) | Guide de déploiement complet (6 étapes) |

## 🧪 Tests Disponibles

```bash
# Mode automatisé (tous les tests)
python arduino_mega_test.py
→ Choisir option 4

# Mode interactif (contrôle manuel)
python arduino_mega_test.py
→ Choisir option 5

# Depuis Python directement
from test_arduino_integration import *
test_simulation()
test_session_management()
```

## 🔌 Branchement Schématique

```
Arduino MEGA
├─ Pin 36 ──[220Ω]──[LED Vert]──[GND]     ✅ Safe (≥80%)
├─ Pin 26 ──[220Ω]──[LED Jaune]──[GND]    ⚠️ Warning (60-79%)
├─ Pin 30 ──[220Ω]──[LED Rouge]──[GND]    🚨 Danger (<60%)
└─ Pin 9 ─────[Buzzer+]──[GND]            🔊 Alerte sonore
```

Voir [ARDUINO_WIRING_DIAGRAM.md](ARDUINO_WIRING_DIAGRAM.md) pour le schéma complet.

## 🎯 Protocole de Communication

### Host → Arduino
```
C<niveau>                                    # Compliance level (0-100)
Exemple: C85                                 # Envoie 85%

DETECT:helmet=<0|1>,vest=<0|1>,glasses=<0|1>,confidence=<0-100>
Exemple: DETECT:helmet=1,vest=0,glasses=1,confidence=92
```

### Arduino → Host
```
[STATUS] ✅ SAFE (Compliance: 85%) - LED: VERT
[STATUS] ⚠️ WARNING (Compliance: 65%) - LED: JAUNE
[STATUS] 🚨 DANGER (Compliance: 45%) - LED: ROUGE + BUZZER
```

## 🔍 Dépannage Rapide

### Arduino ne s'affiche pas
```bash
# 1. Vérifier les ports disponibles
python -m serial.tools.list_ports

# 2. Vérifier dans Gestionnaire Périphériques Windows
# Ou ls /dev/tty* sur Linux/Mac

# 3. Tenter redémarrage Arduino
```

### LEDs ne s'allument pas
```
✓ Vérifier polarité (longue broche = +)
✓ Vérifier résistance 220Ω présente
✓ Vérifier GND commun
✓ Tester LED isolément avec batterie 5V
```

### Pas de son du buzzer
```
✓ Vérifier polarité (⊕ en haut, ⊖ en bas)
✓ Tester isolément avec batterie 5V
✓ Vérifier pilotage au port 9 (PWM)
✓ Passer en buzzer actif si possible
```

## 📊 Table d'États

| Compliance | LED | Buzzer | État |
|-----------|-----|--------|------|
| ≥ 80% | 🟢 VERT | ❌ | ✅ SAFE |
| 60-79% | 🟡 JAUNE | ❌ | ⚠️ WARNING |
| < 60% | 🔴 ROUGE | ✅ | 🚨 DANGER |

## 💡 Cas d'Usage Courants

### 1️⃣ Alerter sur conformité
```python
arduino.send_compliance_level(compliance_percentage)
# Arduino ajuste LEDs et buzzer automatiquement
```

### 2️⃣ Alerter sur détection EPI
```python
arduino.send_detection_data(
    helmet=person_has_helmet,
    vest=person_has_vest,
    glasses=person_has_glasses,
    confidence=detection_confidence
)
# Arduino calcule conformité et ajuste alertes
```

### 3️⃣ Boucle d'alerte en temps réel
```python
import time

arduino.connect()
while True:
    # Votre détection
    compliance = calculate_epi_compliance()
    
    # Alerter Arduino
    arduino.send_compliance_level(compliance)
    
    time.sleep(0.5)  # Mise à jour 2 fois/seconde
```

## 📞 Support

Pour des problèmes:
1. Consulter [ARDUINO_WIRING_DIAGRAM.md](ARDUINO_WIRING_DIAGRAM.md) section Troubleshooting
2. Consulter [DEPLOYMENT_GUIDE.py](DEPLOYMENT_GUIDE.py) section Dépannage
3. Lancer les tests: `python arduino_mega_test.py`

## ✅ Modifications Apportées

- ✅ Code Arduino MEGA v2.1 (scripts/tinkercad_arduino.ino)
- ✅ Support LED Jaune (3 couleurs: VERT/JAUNE/ROUGE)
- ✅ Buzzer sur port 9 (PWM)
- ✅ Configuration optimisée pour Arduino MEGA
- ✅ Scripts de test complets
- ✅ Documentation technique complète
- ✅ Guide de déploiement 6 étapes

## 🎓 Prochaines Étapes

1. **Charger le code Arduino** (scripts/tinkercad_arduino.ino)
2. **Tester le hardware** (arduino_mega_test.py)
3. **Intégrer dans l'application** (voir documentation)
4. **Déployer en production** (DEPLOYMENT_GUIDE.py)

---

**Version**: 2.1  
**Date**: Février 2026  
**Statut**: ✅ Prêt pour production
