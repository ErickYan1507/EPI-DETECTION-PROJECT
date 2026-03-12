# 🎯 SYSTÈME ARDUINO AUTOMATIQUE - GUIDE COMPLET

## ✅ ÉTA ACTUEL

### 🎉 CONFIRMÉ FONCTIONNEL
```
✅ Arduino MEGA 2560 connecté sur COM3
✅ Communication série 9600 baud établie  
✅ Système prêt pour activation automatique
✅ LEDs et buzzer prêts à répondre
```

---

## 🚀 COMMENT ÇA FONCTIONNE AUTOMATIQUEMENT

### Flow Complet: Caméra → Détection → Arduino s'allume

```
1. 📷 CAMÉRA CAPTURE UNE IMAGE
   ↓
2. 🔍 /api/detect ANALYSE L'IMAGE
   - Détecte helmet (oui/non)
   - Détecte vest (oui/non)
   - Détecte glasses (oui/non)
   - Calcule confidence (0-100%)
   ↓
3. 🤖 CALCUL AUTOMATIQUE DE COMPLIANCE
   - Compliance = (helmet + vest + glasses) * confidence / 100
   ↓
4. 📡 ENVOI AUTOMATIQUE À ARDUINO
   - send_detection_data() appelle Arduino
   - Envoie: "DETECT:helmet=1,vest=0,glasses=1,confidence=85"
   - Arduino reçoit et calcule le score
   ↓
5. 💡 ARDUINO ACTIVE LES LEDs EN TEMPS RÉEL
   ┌─────────────────────────────────────┐
   │ Compliance >= 80%  → LED🟢 VERTE    │
   │ Compliance 60-79%  → LED🟡 JAUNE    │
   │ Compliance < 60%   → LED🔴 ROUGE    │
   │                      + 🔊 BUZZER    │
   │                        1500Hz/500ms │
   └─────────────────────────────────────┘
```

---

## 🎮 TESTER LE SYSTÈME

### Méthode 1: Interface Web (Recommandée)

```bash
1. Ouvrir navigateur:
   http://localhost:5000/unified_monitoring.html

2. Cliquer "Choisir un fichier"

3. Sélectionner une image avec des personnes

4. Observer les LEDs s'allumer automatiquement:
   🟢 = Personnel avec EPI complet
   🟡 = Personnel avec EPI partiel
   🔴 = Personnel sans EPI (+ buzzer)
```

### Méthode 2: API directe via PowerShell

```powershell
# Test 1: Compliance 80% → LED VERTE
Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/80" `
  -Method Post -UseBasicParsing | Select-Object -ExpandProperty Content

# Test 2: Compliance 70% → LED JAUNE
Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/70" `
  -Method Post -UseBasicParsing | Select-Object -ExpandProperty Content

# Test 3: Compliance 30% → LED ROUGE + BUZZER
Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/30" `
  -Method Post -UseBasicParsing | Select-Object -ExpandProperty Content

# Test 4: Simulation détection EPI complet
$data = @{helmet=$true; vest=$true; glasses=$true; confidence=95} | ConvertTo-Json
Invoke-WebRequest "http://localhost:5000/api/arduino/test-detection" `
  -Method Post -ContentType "application/json" -Body $data `
  -UseBasicParsing | Select-Object -ExpandProperty Content
```

---

## 📋 CONFIGURATION ACTUELLE

### Python - Flask
```
Mode:        Production (no watchdog reloader)
Port:        5000
Debug:       Disabled
SocketIO:    Enabled
```

### Arduino
```
Port Serial: COM3
Baudrate:   9600
Protocol:   Text-based custom
LED Red:    Pin 30
LED Yellow: Pin 26
LED Green:  Pin 36
Buzzer:     Pin 9
```

### Communication
```
Python → Arduino:
  - "Cn" où n = compliance (0-100)
  - "DETECT:helmet=1,vest=0,glasses=1,confidence=85"

Arduino → Python:
  - "[SENSOR] temp=25.5,humidity=60"
  - "[STATUS] ✅ SAFE (Compliance: 80%) - LED: VERT"
  - "[CMD] Received compliance level: 80"
```

---

## 🚀 LANCER LE SYSTÈME

### Une Seule Commande:
```powershell
$env:ARDUINO_PORT = "COM3"; .\.venv\Scripts\python.exe run_app.py dev
```

### Vérifier qu'Arduino est connecté:
```powershell
Invoke-WebRequest "http://localhost:5000/api/arduino/status" `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**Devrait afficher:**
```json
{
  "baudrate": 9600,
  "connected": true,
  "message": "Arduino is connected",
  "port": "COM3"
}
```

---

## 🎯 COMPORTEMENT ATTENDU

### Scénario 1: Personne avec EPI complet
```
Entry:     Image d'une personne avec casque, gilet, lunettes
Detection: helmet=✓, vest=✓, glasses=✓, confidence=95%
Compliance: (100 * 95) / 100 = 95%
Result:    🟢 LED VERTE s'allume
           Buzzer OFF
           Console: "[STATUS] ✅ SAFE (Compliance: 95%) - LED: VERT"
```

### Scénario 2: Personne avec EPI partiel
```
Entry:     Image d'une personne avec casque + gilet, pas de lunettes
Detection: helmet=✓, vest=✓, glasses=✗, confidence=70%
Compliance: (66 * 70) / 100 = 46% (partiellement pénalisé)
Result:    🟡 LED JAUNE s'allume  
           Buzzer OFF
           Console: "[STATUS] ⚠️ WARNING (Compliance: 46%) - LED: JAUNE"
```

### Scénario 3: Personne SANS EPI
```
Entry:     Image d'une personne sans équipement
Detection: helmet=✗, vest=✗, glasses=✗, confidence=10%
Compliance: (0 * 10) / 100 = 0%
Result:    🔴 LED ROUGE s'allume
           🔊 BUZZER SONNE (1500Hz, 500ms)
           Console: "[STATUS] 🚨 DANGER (Compliance: 0%) - LED: ROUGE + BUZZER"
```

---

## 📊 MONITORING ET LOGS

### Voir les commandes Arduino envoyées:
```powershell
Get-Content logs/epi_detection.log | Select-String "Commande envoyée|reçoit détection"
```

### Example de logs:
```
[2026-02-18 22:05:42] epi_detection - DEBUG - 📤 Commande envoyée: C80
[2026-02-18 22:05:45] epi_detection - INFO - ✅ Arduino reçoit détection: H=True, V=True, G=True, Conf=95%
[2026-02-18 22:05:47] epi_detection - DEBUG - 📤 Commande envoyée: DETECT:helmet=1,vest=1,glasses=1,confidence=95
[2026-02-18 22:05:48] epi_detection - DEBUG - 📤 Arduino: [STATUS] ✅ SAFE (Compliance: 95%) - LED: VERT
```

---

## ⚠️ DÉPANNAGE

### Problème: Arduino affiche "Hors ligne"
**Solution:**
1. Vérifier le câble USB Arduino
2. Vérifier que Arduino est alimenté
3. Redémarrer Arduino (débrancher/rebrancher)
4. Relancer Flask: `$env:ARDUINO_PORT = "COM3"; python run_app.py dev`

### Problème: LEDs ne s'allument pas
**Vérifier:**
1. Connexion USB: `Get-WmiObject Win32_SerialPort`
   - Devrait afficher "Arduino Mega 2560 (COM3)"
2. Logs Flask: `Get-Content logs/epi_detection.log | Select-String "envoyée"`
   - Confirmer les commandes sont envoyées
3. Code Arduino chargé: Serial Monitor affiche "[STARTUP]"?

### Problème: Buzzer ne sonne pas (mais LED fonctionne)
**Vérifier:**
1. Pin 9 est bien configuré
2. Buzzer a de l'alimentation (5V + GND)
3. Compliance < 60% (c'est la condition du buzzer)

### Problème: Port COM3 verrouillé
```powershell
# Tuer TOUS les processus Python
Get-Process python | Stop-Process -Force

# Attendre 3 secondes
Start-Sleep -Seconds 3

# Relancer Flask
$env:ARDUINO_PORT = "COM3"; python run_app.py dev
```

---

## 📈 PROCHAINES ÉTAPES

### ✅ Actuellement Implémenté
- [x] Détection EPI via caméra/image
- [x] Calcul automatique compliance par image
- [x] Envoi automatique à Arduino COM3
- [x] LEDs changent couleur selon compliance
- [x] Buzzer sonne pour compliance faible

### 🎯 À Ajouter (Optionnel)
- [ ] Historique des détections dans DB
- [ ] Statistiques par horaire/zone
- [ ] Dashboard avec graphiques temps réel
- [ ] Stockage des images détectées
- [ ] Alertes email si compliance faible
- [ ] Integration MQTT pour monitoring
- [ ] API pour récupérer compliance actuel

---

## 📚 RÉFÉRENCES

### Fichiers Clés
- `app/routes_api.py` - Logique détection + envoi Arduino
- `app/arduino_integration.py` - Communication série
- `scripts/tinkercad_arduino.ino` - Code Arduino MEGA
- `app/main_new.py` - Initialisation Flask + Arduino

### Endpoints API
- `GET /api/arduino/status` - État de l'Arduino
- `POST /api/arduino/test-compliance/<level>` - Tester compliance
- `POST /api/arduino/test-detection` - Tester détection
- `POST /api/detect` - Détecter EPI dans image (AUTOMATIQUE)

---

## ✨ RÉSUM CONCIS

**L'Arduino s'allume AUTOMATIQUEMENT lors de chaque détection caméra sans aucune action manuelle!**

1. Uploadez image → Flask détecte EPI → Arduino reçoit commande → LEDs s'allument
2. Compliance ≥ 80% → 🟢 Vert (safe)
3. Compliance 60-79% → 🟡 Jaune (warning)
4. Compliance < 60% → 🔴 Rouge + 🔊 Buzzer (danger)

**C'est maintenant un système complet et automatisé!** 🚀
