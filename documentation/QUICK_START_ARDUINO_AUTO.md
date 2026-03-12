# ✨ DÉMARRAGE RAPIDE - Activation Automatique Arduino
# ═══════════════════════════════════════════════════════════════

# 🚀 OPTION 1: Sur 1 LIGNE SEULEMENT (Démarrage complet automatique)
# ═════════════════════════════════════════════════════════════════════

PowerShell -ExecutionPolicy Bypass -File arduino_auto_start.ps1


# 🎯 OPTION 2: Commandes manuelles (si vous préférez contrôler)
# ═════════════════════════════════════════════════════════════════════

## A) Arrêter les processus Python en cours
taskkill /F /IM python.exe 2>&1
Start-Sleep -Seconds 2

## B) Configurer Arduino et lancer Flask
$env:ARDUINO_PORT = "COM3"
.\.venv\Scripts\python.exe run_app.py prod

## C) Dans une autre fenêtre PowerShell, vérifier le statut
Invoke-WebRequest "http://localhost:5000/api/arduino/status" -UseBasicParsing | ConvertFrom-Json


# 🔧 OPTION 3: Tests manuels (après démarrage)
# ═════════════════════════════════════════════════════════════════════

## Test 1: Vérifier que Flask répond
Invoke-WebRequest "http://localhost:5000/api/info" -UseBasicParsing

## Test 2: Vérifier Arduino connecté
Invoke-WebRequest "http://localhost:5000/api/arduino/status" -UseBasicParsing | ConvertFrom-Json

## Test 3: Déclencher LED VERTE (compliance >= 80%)
Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/90" -Method Post -UseBasicParsing

## Test 4: Déclencher LED JAUNE (compliance 60-79%)
Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/70" -Method Post -UseBasicParsing

## Test 5: Déclencher LED ROUGE + BUZZER (compliance < 60%)
Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/30" -Method Post -UseBasicParsing

## Test 6: Envoyer une détection EPI manuelle
$data = @{helmet=$true; vest=$false; glasses=$true; confidence=65} | ConvertTo-Json
Invoke-WebRequest "http://localhost:5000/api/arduino/test-detection" `
  -Method Post -ContentType "application/json" -Body $data -UseBasicParsing


# 🎥 OPTION 4: Upload et détection automatique
# ═════════════════════════════════════════════════════════════════════

## A) Ouvrir l'interface web d'upload
Start-Process "http://127.0.0.1:5000/upload"

## B) Sélectionner une image et cliquer "Envoyer"
## C) Regarder l'Arduino s'activer AUTOMATIQUEMENT! 🎉


# 📊 OPTION 5: Monitoring en temps réel
# ═════════════════════════════════════════════════════════════════════

## A) Voir les logs Arduino en direct
Get-Content logs/epi_detection.log -Tail 50 -Wait

## B) Filtrer seulement les actions Arduino
Get-Content logs/epi_detection.log | Select-String "DETECT:|LED|BUZZER|ARDUINO|STATUS" -Last 20

## C) Voir les détections
Get-Content logs/epi_detection.log | Select-String "Detection|detect|helmet|vest|glasses" -Last 20


# 🛠️ OPTION 6: Debug avancé
# ═════════════════════════════════════════════════════════════════════

## A) Vérifier les processus Python actifs
Get-Process | Where-Object {$_.ProcessName -eq "python"}

## B) Tuer un processus Flask complètement
Get-Process python | Stop-Process -Force

## C) Vérifier les ports en utilisation
netstat -ano | findstr "5000"

## D) Voir les erreurs détaillées
flask_error.log
flask_output.log

## E) Tester la connexion série directement
$port = [System.IO.Ports.SerialPort]::new("COM3", 9600, 8, "One", "None")
$port.Open()
Write-Host $port.IsOpen  # Doit afficher: True
$port.Close()


# 📋 ARCHITECTURE DU SYSTÈME AUTOMATIQUE
# ═════════════════════════════════════════════════════════════════════

<#
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTÈME AUTOMATIQUE COMPLET                  │
└─────────────────────────────────────────────────────────────────┘

      Utilisateur                Flask App                Arduino
      ───────────────────────────────────────────────────────────

  1. 📷 Ouvre navigateur
     Upload image
            │
            └──────> /api/detect
                       │
                  2. 🔍 Analyse image
                       ├─ helmet=1
                       ├─ vest=1
                       ├─ glasses=0
                       └─ confidence=75
                       │
                  3. 📊 Calcul compliance
                       └─ (1+1+0)*75/100 = 150
                       │
                  4. 📡 send_detection_data()
                       └──────────────────────> DETECT:helmet=1,...
                                                 │
                                           5. 🤖 Arduino parse & calcule
                                                 ├─ Calcul score
                                                 ├─ score = 150 (>80%)
                                                 │
                                           6. 💡 Activation LED
                                                 └─ digitalWrite(GREEN, HIGH)
                                                    ✅ LED VERTE s'allume!

  🎉 RÉSULTAT: L'Arduino s'active AUTOMATIQUEMENT lors de la détection!
              Aucune manipulation manuelle nécessaire!

┌─────────────────────────────────────────────────────────────────┐
│                    THRESHOLDS CONFIGURABLES                    │
└─────────────────────────────────────────────────────────────────┘

   LED VERTE (Sûr):       compliance >= 80%
   LED JAUNE (Avertir):   compliance 60-79%
   LED ROUGE + BUZZER:    compliance < 60%

   Ces valeurs sont définies dans:
   - Python: app/arduino_integration.py - calculateCompliance()
   - Arduino: tinkercad_arduino.ino - HIGH_COMPLIANCE_THRESHOLD

┌─────────────────────────────────────────────────────────────────┐
│              POINTS D'INTÉGRATION POUR MODIFICATIONS            │
└─────────────────────────────────────────────────────────────────┘

   A) Modifier les seuils:
      📄 tinkercad_arduino.ino - Lines: 42-44
         const int HIGH_COMPLIANCE_THRESHOLD = 80;
         const int MEDIUM_COMPLIANCE_THRESHOLD = 60;
   
   B) Ajouter actions supplémentaires:
      📄 app/arduino_integration.py - handleDetectionData()
      📄 app/routes_api.py - fonction /api/detect
   
   C) Ajouter nouveaux capteurs Arduino:
      📄 Déjà supportés: Température (A0), Humidité (A1)
      📄 Ajouter PIN + logique dans tinkercad_arduino.ino
#>


# ⚡ COMMANDE FINALE RAPIDE (Copier-coller juste ça!)
# ═════════════════════════════════════════════════════════════════════

# Mettre le curseur sur la commande ci-dessous et appuyer CTRL+SHIFT+C pour copier

PowerShell -ExecutionPolicy Bypass -File arduino_auto_start.ps1


# 🎬 C'EST PRÊT! 
# Exécutez cette commande et le système démarre avec activation Arduino automatique!
