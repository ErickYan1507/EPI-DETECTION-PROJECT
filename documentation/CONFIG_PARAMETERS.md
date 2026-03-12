# 🔧 Configuration Arduino - Paramètres Modifiables

## 📋 Configuration Hardware (À ADAPTER à votre système)

### Port de Connexion
```
Port par défaut: COM3
```

**Pour trouver votre port:**
```bash
# Windows
Gestionnaire de Périphériques → Ports COM

# Linux/Mac
python -m serial.tools.list_ports
ou
ls /dev/tty*
```

---

## 🔌 Configuration des Pins (NE PAS MODIFIER - Arduino MEGA)

```python
# Pins Arduino MEGA v2.1 (FINAL)
BUZZER_PIN = 9      # 🔊 Buzzer (PWM)
RED_LED_PIN = 30    # 🔴 LED Rouge (Danger + Buzzer)
YELLOW_LED_PIN = 26 # 🟡 LED Jaune (Warning)
GREEN_LED_PIN = 36  # 🟢 LED Vert (Safe)
```

---

## ⚙️ Paramètres Ajustables

### Baudrate (Vitesse Série)
```python
# Actuellement: 9600 baud
# Ne pas changer sauf si nécessaire
# Arduino supporté: 9600 uniquement
BAUDRATE = 9600
```

### Seuils de Conformité
```python
# Ces seuils PEUVENT être modifiés dans le code Arduino

HIGH_COMPLIANCE_THRESHOLD = 80    # ≥ 80%  → LED VERT
MEDIUM_COMPLIANCE_THRESHOLD = 60  # 60-79% → LED JAUNE
# < 60%                            → LED ROUGE + BUZZER
```

### Fréquence Buzzer
```python
# Fréquence son: 1500 Hz (actuel)
# Durée: 500 ms
# Pause: 300 ms
# (À modifier dans tinkercad_arduino.ino si besoin)
```

---

## 🐍 Configuration Python Rapide

### Avant de lancer le script:

```bash
# 1. Identifier le port COM
python -m serial.tools.list_ports

# 2. Modifier si nécessaire dans le code:
# arduino = ArduinoController(port='COM3')  # Remplacer COM3

# 3. Tester
python arduino_mega_test.py
```

---

## 📝 Fichiers à Modifier si Nécessaire

### 1️⃣ Pour changer le port COM pour les tests:
**Fichier**: `arduino_mega_test.py`
```python
# Ligne ~60
port = input("\nPort COM par défaut? (appuyez sur Entrée pour COM3): ").strip() or 'COM3'
# ↑ Remplacer 'COM3' par votre port
```

### 2️⃣ Pour changer le port COM dans l'application:
**Fichier**: `app/arduino_integration.py`
```python
# Ligne ~23
def __init__(self, port: str = 'COM3', baudrate: int = 9600, timeout: int = 2):
    # ↑ Remplacer 'COM3' par votre port
```

### 3️⃣ Pour changer seuils LED dans Arduino:
**Fichier**: `scripts/tinkercad_arduino.ino`
```ino
// Lignes ~34-35
const int HIGH_COMPLIANCE_THRESHOLD = 80;
const int MEDIUM_COMPLIANCE_THRESHOLD = 60;
// Vous pouvez modifier ces valeurs
```

---

## ✅ Vérification de Configuration

```bash
# 1. Vérifier port
python -m serial.tools.list_ports

# 2. Vérifier PySerial
python -c "import serial; print('PySerial OK')"

# 3. Vérifier communication
python arduino_mega_test.py
# Option 4 ou 5
```

---

## 🎯 Configuration Par Système

### Windows
```bash
# Port détecté dans: Gestionnaire de Périphériques
# Format: COM3, COM4, COM5, etc.
# Utiliser: port='COM3'
```

### Linux (Ubuntu/Raspberry Pi)
```bash
# Port détecté: /dev/ttyUSB0 ou /dev/ttyACM0
# Utiliser: port='/dev/ttyUSB0'
```

### macOS
```bash
# Port détecté: /dev/cu.usbserial-* ou /dev/tty.usbserial-*
# Utiliser: port='/dev/cu.usbserial-14110'
```

---

## 🔄 Configuration Complète Depuis Python

```python
from app.arduino_integration import ArduinoController

# 1. Créer le contrôleur avec VOTRE port
arduino = ArduinoController(
    port='COM3',        # ← Remplacer par votre port
    baudrate=9600,      # ← Vitesse (laisser 9600)
    timeout=2           # ← Délai d'attente (2 secondes)
)

# 2. Établir la connexion
if arduino.connect():
    print("✅ Connecté!")
    
    # 3. Envoyer commandes
    arduino.send_compliance_level(85)  # LED VERT
    arduino.send_compliance_level(70)  # LED JAUNE
    arduino.send_compliance_level(45)  # LED ROUGE + BUZZER
    
    # 4. Fermer
    arduino.disconnect()
else:
    print("❌ Connexion échouée - vérifier port COM")
```

---

## 📊 Tableau Récapitulatif

| Paramètre | Valeur | Modifiable | Note |
|-----------|--------|-----------|------|
| Port COM | COM3 | ✅ YES | Adapter à votre système |
| Baudrate | 9600 | ❌ NON | Arduino supporté: 9600 |
| Buzzer Pin | 9 | ❌ NON | Arduino MEGA configuration |
| Red LED Pin | 30 | ❌ NON | Arduino MEGA configuration |
| Yellow LED Pin | 26 | ❌ NON | Arduino MEGA configuration |
| Green LED Pin | 36 | ❌ NON | Arduino MEGA configuration |
| High Threshold | 80% | ✅ YES | Seuil LED Vert |
| Medium Threshold | 60% | ✅ YES | Seuil LED Jaune |
| Buzzer Freq | 1500 Hz | ✅ YES | Frequency du son alarm |

---

## 🆘 Configuration Correcte vs Incorrecte

### ❌ INCORRECT:
```python
# Port erroné
arduino = ArduinoController(port='COM1')  # Si Arduino est sur COM3

# Baudrate erroné
arduino = ArduinoController(port='COM3', baudrate=115200)  # Arduino attend 9600
```

### ✅ CORRECT:
```python
# Port correct
arduino = ArduinoController(port='COM3')

# Baudrate standard (ne pas changer)
arduino = ArduinoController(port='COM3', baudrate=9600)
```

---

## 🚀 Configuration Finale Recommandée

**AVANT production:**
```bash
# 1. Identifier le port
python -m serial.tools.list_ports
# Résultat: "COM3 - Arduino MEGA"

# 2. Changer dans le code si nécessaire
# arduino = ArduinoController(port='COM3')

# 3. Lancer les tests
python arduino_mega_test.py
# Tous les tests doivent passer

# 4. Valider hardware
# LEDs s'allument correctement
# Buzzer sonne quand compliance < 60%
```

---

## 📞 Besoin d'Aide ?

Consultez:
- `TROUBLESHOOTING_QUICK.txt` - Dépannage rapide
- `ARDUINO_MEGA_CONFIG.md` - Configuration complète
- `DEPLOYMENT_GUIDE.py` - Guide détaillé

Version: 2.1
Date: Février 2026
