# 🚀 QUICK FIX - LEDs et Buzzer Arduino

## TL;DR - Résumé Rapide

**PROBLÈME:** LEDs et buzzer ne s'allument pas lors de détection caméra  
**CAUSE:** Données de détection jamais envoyées à l'Arduino  
**SOLUTION:** ✅ Code de communication Arduino ajouté!  

---

## 🔧 3 Étapes pour Tester

### Étape 1: Vérifier Installation PySerial
```bash
# Ouvrir PowerShell
.\.venv\Scripts\Activate.ps1

# Vérifier installation
pip list | findstr pyserial

# Si absent → installer:
pip install pyserial
```

### Étape 2: Configurer Port Arduino
```bash
# Voir le port dans Gestionnaire de périphériques
# Exemple: COM3, COM4, COM5...

# Définir la variable d'environnement:
$env:ARDUINO_PORT = "COM3"  # Adapter à votre port
$env:ARDUINO_BAUD = "9600"
```

### Étape 3: Lancer Diagnostic
```bash
# Terminal 1: Lancer le serveur
python run_app.py dev

# Terminal 2: Tester Arduino
python test_arduino_leds.py
```

---

## 🧪 Test API HTTP Rapide

```bash
# Vérifier connexion Arduino:
curl http://localhost:5000/api/arduino/status

# Tester LED Verte (80% compliance):
curl -X POST http://localhost:5000/api/arduino/test-compliance/80

# Tester LED Jaune (70%):
curl -X POST http://localhost:5000/api/arduino/test-compliance/70

# Tester LED Rouge + Buzzer (30%):
curl -X POST http://localhost:5000/api/arduino/test-compliance/30

# Tester données détection complètes:
curl -X POST http://localhost:5000/api/arduino/test-detection \
  -H "Content-Type: application/json" \
  -d '{"helmet":true,"vest":true,"glasses":true,"confidence":85}'
```

---

## 📊 Comportement Attendu

| Compliance | LED | Buzzer | Signification |
|-----------|-----|--------|--------------|
| ≥ 80% | 🟢 VERT | OFF | ✅ SAFE - EPI complet |
| 60-79% | 🟡 JAUNE | OFF | ⚠️ WARNING - EPI partiel |
| < 60% | 🔴 ROUGE | ON | 🚨 DANGER - Pas d'EPI |

---

## 📝 Fichiers Modifiés

- ✅ `app/routes_api.py` → Ajout intégration Arduino au /detect
- ✅ `app/arduino_integration.py` → Déjà correct
- ✅ `scripts/tinkercad_arduino.ino` → Déjà correct

---

## 🆘 Si Ça ne Marche Pas

### Arduino non dans le Gestionnaire de périphériques:
```bash
# 1. Vérifier le câble USB
# 2. Installer le driver: https://arduino.cc/en/guide/windows
# 3. Redémarrer l'ordinateur
```

### Arduino visible mais pas de connexion:
```python
# Trouver le port exact:
python -c "import serial; from serial.tools import list_ports; [print(p.device) for p in list_ports.comports()]"
```

### Arduino connecté mais LEDs n'allument pas:
1. Vérifier Serial Monitor (Arduino IDE):
   - Ouvrir: Tools → Serial Monitor
   - Baud rate: 9600
   - Vous devriez voir: `[STARTUP] EPI Detection Arduino MEGA...`

2. Si rien n'apparaît:
   - Vérifier que le code Arduino est uploadé
   - Vérifier l'alimentation (5V + GND)

---

## 🎯 Checklist Finale

- [ ] PySerial installé
- [ ] Port Arduino configuré (COM3/COM4/etc)
- [ ] Arduino branché et visible dans Gestionnaire de périphériques
- [ ] Code Arduino uploadé
- [ ] Serveur Flask lancé: `python run_app.py dev`
- [ ] Test diagnostic: `python test_arduino_leds.py`
- [ ] LEDs s'allument pendant le test
- [ ] Importer image depuis unified_monitoring.html
- [ ] LEDs changent selon la détection EPI ✅

---

## 🔗 Ressources

- [ARDUINO_LED_BUZZER_DEBUG.md](ARDUINO_LED_BUZZER_DEBUG.md) → Diagnostic détaillé
- [ARDUINO_WIRING_DIAGRAM.md](ARDUINO_WIRING_DIAGRAM.md) → Branchements hardware
- [scripts/tinkercad_arduino.ino](scripts/tinkercad_arduino.ino) → Code Arduino
- [app/arduino_integration.py](app/arduino_integration.py) → Code Python

---

## 💬 Questions Fréquentes

**Q: Quel port Arduino?**  
A: COM3 par défaut, mais peut être COM4, COM5... Vérifier dans Gestionnaire de périphériques sous "Ports (COM et LPT)"

**Q: Pourquoi le buzzer ne sonne pas?**  
A: Le buzzer sonne seulement si compliance < 60%. Tester avec `curl ... test-compliance/30`

**Q: Les LEDs ne changent pas d'état?**  
A: Vérifier branchement physical des LEDs. Voir [ARDUINO_WIRING_DIAGRAM.md](ARDUINO_WIRING_DIAGRAM.md)

**Q: Comment relancer Arduino?**  
A: Débrancher/rebrancher le câble USB

---

Made with ❤️ for EPI Detection System
