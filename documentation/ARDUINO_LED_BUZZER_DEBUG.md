# 🔴 Diagnostic: LEDs et Buzzer ne s'allument pas

## Résumé du Problème
Les LEDs (rouge/jaune/vert) et le buzzer ne s'allument pas lors de la détection sur la caméra en unified monitoring.

## Cause Identifiée
✅ **CORRIGÉE:** Le système Python n'envoyait PAS les données de détection à l'Arduino!

### Avant (BROKEN):
```
Caméra détecte EPI → Python stocke en BD → Frontend affiche
                                          ❌ Arduino jamais contacté!
```

### Après (FIXED):
```
Caméra détecte EPI → Python stocke en BD → Python envoie à Arduino
                    ✅ Arduino contrôle LEDs/Buzzer!
```

---

## Checklist Diagnostic

### 1️⃣ Vérifier la Connection Arduino Physique

```bash
# Sur Windows - Vérifier les ports COM disponibles
# Aller dans: Gestionnaire de périphériques → Ports (COM et LPT)
# Vous devriez voir: "Arduino Mega 2560" ou similar sur COM3, COM4, etc.
```

**⚠️ Si pas d'Arduino visible:**
- Branchez le câble USB Arduino
- Installez le driver: https://arduino.cc/en/guide/windows
- Redémarrez l'ordinateur
- Vérifiez à nouveau

### 2️⃣ Vérifier l'Installation PySerial

```bash
# Ouvrir une terminal PowerShell dans le repo
.venv/Scripts/Activate.ps1

# Vérifier installation
pip list | findstr pyserial

# Si pas installé:
pip install pyserial
```

### 3️⃣ Vérifier le Port Arduino

Le port par défaut est **COM3**, mais peut être **COM4, COM5**, etc.

```bash
# Voir le port réel (depuis PowerShell):
$ports = Get-Content HKLM:\HARDWARE\DEVICEMAP\SERIALCOMM -ErrorAction SilentlyContinue
$ports

# Exemple de résultat:
# Device0 : COM3
```

### 4️⃣ Configuration du Port

Trois méthodes pour configurer le port Arduino:

**Méthode A: Variable d'Environnement (Recommandé)**
```bash
# Windows PowerShell:
$env:ARDUINO_PORT = "COM3"
$env:ARDUINO_BAUD = "9600"

# Puis lancer l'app:
python run_app.py dev
```

**Méthode B: Fichier .env** (Créer ce fichier à la racine):
```
ARDUINO_PORT=COM3
ARDUINO_BAUD=9600
```

**Méthode C: Modifier le code** (app/main_new.py):
```python
port = os.getenv('ARDUINO_PORT', 'COM3')  # Remplacer COM3 si besoin
```

### 5️⃣ Tester la Connexion Arduino

```bash
# Test de communication basique
python test_arduino_integration.py

# Devrait afficher:
# ✅ Arduino connecté sur COM3
# ou
# ❌ Arduino not found on COM3
```

### 6️⃣ Test Détection → Arduino

```bash
# Lancer le serveur:
python run_app.py dev

# Dans un autre terminal, tester:
curl -X POST http://localhost:5000/api/detect \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/jpeg;base64,..."}'

# Vérifier les logs pour: "✅ Arduino reçoit détection:"
```

---

## Codes de Réponse Arduino

### Format Envoyé au Arduino:
```
DETECT:helmet=1,vest=1,glasses=0,confidence=85
```

### LEDs Contrôlées par Arduino:
| Level | LED | Buzzer | Situation |
|-------|-----|--------|-----------|
| ≥ 80% | 🟢 VERT | Silence | ✅ SAFE (EPI complet et confiance haute) |
| 60-79% | 🟡 JAUNE | Silence | ⚠️ WARNING (EPI partiel) |
| < 60% | 🔴 ROUGE | 🔊 ON | 🚨 DANGER (Peu/pas d'EPI) |

---

## Logs à Vérifier

### Serveur Flask (app/main_new.py):
```
[INFO] Démarrage connexion Arduino sur COM3@9600
[INFO] Arduino initialisé et connecté
```

### Lors de la Détection (app/routes_api.py):
```
✅ Arduino reçoit détection: H=True, V=True, G=False, Conf=85%
```

### Arduino Serial Monitor (Arduino IDE):
```
[STARTUP] EPI Detection Arduino MEGA Controller v2.1
[DETECT] Helmet:✓ Vest:✓ Glasses:✗ Confidence:85%
[STATUS] 🟢 SAFE (Compliance: 85%) - LED: VERT
```

---

## Si Ça ne Marche Toujours Pas

### A. Arduino ne se connecte pas:
```bash
# Vérifier le port exact:
python -c "import serial; print([p.device for p in serial.tools.list_ports.comports()])"

# Résultat attendu: ['COM3', 'COM4', ...]
```

### B. Arduino connecté mais pas de réponse:
1. Vérifier que le code Arduino est uploadé (voir `scripts/tinkercad_arduino.ino`)
2. Vérifier les pins:
   - RED_LED: Pin 30
   - YELLOW_LED: Pin 26
   - GREEN_LED: Pin 36
   - BUZZER: Pin 9
3. Ouvrir Serial Monitor (Arduino IDE) et vérifier les messages

### C. Détection ne s'envoie pas à Arduino:
```bash
# Vérifier les logs:
tail -f logs/app.log | findstr Arduino

# Devrait contenir:
# "Arduino reçoit détection:"
```

### D. LEDs reçoivent le signal mais ne s'allument pas:
1. Vérifier les branchements (voir ARDUINO_WIRING_DIAGRAM.md)
2. Vérifier l'alimentation externe (vérifier 5V et GND)
3. Tester avec Arduino IDE directly:
   ```cpp
   digitalWrite(RED_LED_PIN, HIGH);
   delay(1000);
   digitalWrite(RED_LED_PIN, LOW);
   ```

---

## Code Arduino Clé

Les LEDs sont contrôlées par la fonction `setSystemStatus()` dans `scripts/tinkercad_arduino.ino`:

```cpp
void setSystemStatus(int level, bool startup) {
  level = constrain(level, 0, 100);
  
  // Turn off all LEDs first
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(YELLOW_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  noTone(BUZZER_PIN);
  
  if (level >= 80) {
    // ✅ SAFE - Green LED
    digitalWrite(GREEN_LED_PIN, HIGH);
  } 
  else if (level >= 60) {
    // ⚠️ WARNING - Yellow LED
    digitalWrite(YELLOW_LED_PIN, HIGH);
  } 
  else {
    // 🚨 DANGER - Red LED + buzzer
    digitalWrite(RED_LED_PIN, HIGH);
    tone(BUZZER_PIN, 1500, 500);
  }
}
```

---

## Quick Test Script

```python
# test_leds_quick.py
from app.arduino_integration import ArduinoController

controller = ArduinoController(port='COM3', baudrate=9600)

if controller.connect():
    print("✅ Arduino connected")
    
    # Test Green LED (compliance 85%)
    controller.send_compliance_level(85)
    print("🟢 Green LED should light up")
    
    # Wait 2 sec
    import time
    time.sleep(2)
    
    # Test Yellow LED (compliance 70%)
    controller.send_compliance_level(70)
    print("🟡 Yellow LED should light up")
    
    time.sleep(2)
    
    # Test Red LED + Buzzer (compliance 30%)
    controller.send_compliance_level(30)
    print("🔴 Red LED + Buzzer should activate")
    
    controller.disconnect()
else:
    print("❌ Failed to connect to Arduino")
```

---

## Checklist Finale

- [ ] Arduino branché avec câble USB
- [ ] Driver Arduino installé
- [ ] PySerial installé (`pip install pyserial`)
- [ ] Port Arduino correct (COM3/COM4/etc)
- [ ] Code Arduino uploadé
- [ ] LEDs et buzzer branchés correctement
- [ ] Variable ARDUINO_PORT configurée
- [ ] Serveur Flask lancé
- [ ] Logs affichent: "Arduino initialisé et connecté"
- [ ] Lors de détection: "Arduino reçoit détection:"
- [ ] LEDs s'allument et buzzer sonne!

---

## SOS - If All Else Fails

```bash
# 1. Redémarrer Arduino
# Débrancher et rebrancher le câble USB

# 2. Redémarrer le serveur
Ctrl+C
python run_app.py dev

# 3. Redémarrer l'ordinateur (dernière option!)
shutdown /r /t 0
```

📞 **Besoin d'aide?** Vérifiez les logs dans `logs/app.log`
