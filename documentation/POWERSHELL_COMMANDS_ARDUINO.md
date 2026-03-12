# 🚀 PowerShell Commands - Test Arduino LED et Buzzer

## ⚡ Important: Commandes PowerShell (Pas Bash!)

PowerShell utilise `Invoke-WebRequest` au lieu de `curl`. Voici les bonnes commandes:

---

## 🧪 Tests Rapides (Copier-Coller)

### Test 1: Vérifier connexion Arduino
```powershell
Invoke-WebRequest http://localhost:5000/api/arduino/status | Select-Object -ExpandProperty Content
```

**Résultat attendu:**
```json
{
  "connected": true,
  "port": "COM3",
  "baudrate": 9600,
  "message": "Arduino is connected"
}
```

---

### Test 2: Tester LED Verte (80% compliance = SAFE)
```powershell
Invoke-WebRequest -Uri http://localhost:5000/api/arduino/test-compliance/80 -Method POST | Select-Object -ExpandProperty Content
```

**Résultat attendu:**
```json
{
  "sent": true,
  "expected_led": "GREEN (✅ SAFE)",
  "expected_buzzer": "OFF"
}
```

**Visual:** 🟢 La LED VERTE s'allume  
**Audio:** 🔇 Buzzer SILENCIEUX

---

### Test 3: Tester LED Jaune (70% compliance = WARNING)
```powershell
Invoke-WebRequest -Uri http://localhost:5000/api/arduino/test-compliance/70 -Method POST | Select-Object -ExpandProperty Content
```

**Résultat attendu:**
```json
{
  "sent": true,
  "expected_led": "YELLOW (⚠️ WARNING)",
  "expected_buzzer": "OFF"
}
```

**Visual:** 🟡 La LED JAUNE s'allume  
**Audio:** 🔇 Buzzer SILENCIEUX

---

### Test 4: Tester LED Rouge + Buzzer (30% compliance = DANGER)
```powershell
Invoke-WebRequest -Uri http://localhost:5000/api/arduino/test-compliance/30 -Method POST | Select-Object -ExpandProperty Content
```

**Résultat attendu:**
```json
{
  "sent": true,
  "expected_led": "RED (🚨 DANGER)",
  "expected_buzzer": "ON (1500Hz)"
}
```

**Visual:** 🔴 La LED ROUGE s'allume  
**Audio:** 🔊 Buzzer SONNE (1500Hz)

---

### Test 5: Tester Envoi Données Détection
```powershell
$body = @{
    helmet = $true
    vest = $true
    glasses = $true
    confidence = 95
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://localhost:5000/api/arduino/test-detection `
  -Method POST `
  -ContentType "application/json" `
  -Body $body | Select-Object -ExpandProperty Content
```

**Résultat attendu:**
```json
{
  "sent": true,
  "message": "Detection data sent to Arduino",
  "data": {
    "helmet": true,
    "vest": true,
    "glasses": true,
    "confidence": 95
  }
}
```

---

## 🔍 Vérifier les Logs en Temps Réel

```powershell
# Voir les 50 dernières lignes du log
Get-Content logs/epi_detection.log -Tail 50

# Suivre les logs en temps réel (Ctrl+C pour arrêter):
Get-Content logs/epi_detection.log -Wait -Tail 20
```

**Chercher dans les logs (grep PowerShell):**
```powershell
Get-Content logs/epi_detection.log | Select-String "Arduino" | Select-Object -Last 10
```

---

## 🎯 Scénarios de Test Complets

### Scénario 1: EPI Complet (Attendu: LED VERTE)
```powershell
$data = @{
    helmet = $true
    vest = $true
    glasses = $true
    confidence = 95
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://localhost:5000/api/arduino/test-detection `
  -Method POST `
  -ContentType "application/json" `
  -Body $data
```

### Scénario 2: EPI Partiel (Attendu: LED JAUNE)
```powershell
$data = @{
    helmet = $true
    vest = $false
    glasses = $true
    confidence = 65
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://localhost:5000/api/arduino/test-detection `
  -Method POST `
  -ContentType "application/json" `
  -Body $data
```

### Scénario 3: Pas d'EPI (Attendu: LED ROUGE + BUZZER)
```powershell
$data = @{
    helmet = $false
    vest = $false
    glasses = $false
    confidence = 0
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://localhost:5000/api/arduino/test-detection `
  -Method POST `
  -ContentType "application/json" `
  -Body $data
```

---

## 🔧 Configuration Arduino

### Option 1: Détection Automatique (Recommandé)
L'application cherche automatiquement Arduino sur les ports commun (COM3, COM4, COM5, etc.).

Juste relancer l'app:
```powershell
python run_app.py dev
```

### Option 2: Spécifier le Port Exactement
```powershell
$env:ARDUINO_PORT = "COM3"
$env:ARDUINO_BAUD = "9600"

python run_app.py dev
```

### Option 3: Tester Sans Arduino (Simulation)
```powershell
python test_arduino_simulation.py
```

---

## 🐛 Troubleshooting

### Arduino non détecté
1. Brancher l'Arduino au port USB
2. Vérifier dans Gestionnaire de périphériques sous "Ports (COM et LPT)"
3. Redémarrer l'application

### Erreur "Arduino controller not initialized"
Cela signifie que l'Arduino n'est pas branché. L'application continue mais:
- ❌ Les LEDs ne s'allument pas
- ❌ Le buzzer ne sonne pas
- ✅ Le système de détection fonctionne normalement

### PowerShell Error: "Impossible de trouver un paramètre correspondant au nom X"
Vous avez utilisé une commande Bash `curl`. En PowerShell, utiliser `Invoke-WebRequest`:

```powershell
# ❌ Bash (ne fonctionne PAS):
curl http://localhost:5000/api/arduino/status

# ✅ PowerShell (correct):
Invoke-WebRequest http://localhost:5000/api/arduino/status
```

---

## 📊 Tableau Récapitulatif

| Compliance | LED | Buzzer | Commande PowerShell |
|-----------|-----|--------|-------------------|
| ≥ 80% | 🟢 | OFF | `test-compliance/80` |
| 60-79% | 🟡 | OFF | `test-compliance/70` |
| < 60% | 🔴 | ON | `test-compliance/30` |

---

## 💡 Tips

### Formater la réponse JSON proprement:
```powershell
Invoke-WebRequest http://localhost:5000/api/arduino/status | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json
```

### Extraire une valeur spécifique:
```powershell
$response = Invoke-WebRequest http://localhost:5000/api/arduino/status
$json = $response.Content | ConvertFrom-Json
$json.connected
```

### Tester en boucle (5 fois):
```powershell
for ($i = 1; $i -le 5; $i++) {
    Write-Host "Test $i/5 - Compliance 80%"
    Invoke-WebRequest -Uri http://localhost:5000/api/arduino/test-compliance/80 -Method POST | Out-Null
    Start-Sleep -Seconds 1
}
```

---

**Besoin d'aide?** Vérifier les logs avec:
```powershell
Get-Content logs/epi_detection.log | Select-String "Arduino" -Context 2
```
