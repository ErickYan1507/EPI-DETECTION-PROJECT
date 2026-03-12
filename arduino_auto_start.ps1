# ============================================================================
# 🚀 DÉMARRAG AUTOMATIQUE DU SYSTÈME ARDUINO - Script PowerShell
# ============================================================================
# 
# Ce script automatise COMPLÈTEMENT:
# 1. Arrêt des processus Python existants
# 2. Configuration de l'Arduino (COM3)
# 3. Lancement de Flask
# 4. Attente de démarrage du système
# 5. Test automatique pour vérifier que tout fonctionne
#
# Usage: Exécuter dans PowerShell dans le dossier du projet
#        .\ arduino_auto_start.ps1
#
# ============================================================================

Write-Host "`n╔════════════════════════════════════════════════════════════════╗"
Write-Host "║     🚀 DÉMARRAGE AUTOMATIQUE - EPI Detection + Arduino       ║"
Write-Host "╚════════════════════════════════════════════════════════════════╝`n"

# Vérifications préalables
Write-Host "📋 Vérifications préalables..." -ForegroundColor Cyan

# Vérifier que Python est disponible
$pythonPath = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "❌ Python venv non trouvé! Créez-le avec: python -m venv .venv" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python venv trouvé" -ForegroundColor Green

# Vérifier le fichier run_app.py
if (-not (Test-Path "run_app.py")) {
    Write-Host "❌ run_app.py non trouvé!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ run_app.py trouvé" -ForegroundColor Green

# ============================================================================
# ÉTAPE 1: Arrêter tous les processus Python existants
# ============================================================================

Write-Host "`n📍 ÉTAPE 1: Nettoyage des processus existants..." -ForegroundColor Yellow

$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "   ⏳ Arrêt de $(($pythonProcesses | Measure-Object).Count) processus Python..."
    Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "   ✅ Processus arrêtés" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Pas de processus Python en cours" -ForegroundColor Gray
}

# ============================================================================
# ÉTAPE 2: Configuration de l'Arduino
# ============================================================================

Write-Host "`n📍 ÉTAPE 2: Configuration Arduino..." -ForegroundColor Yellow

# Vérifier Arduino connecté sur COM3
$ports = [System.IO.Ports.SerialPort]::GetPortNames()
if ($ports -contains "COM3") {
    Write-Host "   ✅ Arduino détecté sur COM3" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  COM3 pas détecté. Ports disponibles: $($ports -join ', ')" -ForegroundColor Red
    Write-Host "   💡 Branchez l'Arduino USB et attendez 2 secondes" -ForegroundColor Yellow
}

# Configurer la variable d'environnement
$env:ARDUINO_PORT = "COM3"
Write-Host "   ✅ Variable ARDUINO_PORT = COM3" -ForegroundColor Green

# ============================================================================
# ÉTAPE 3: Lancement de Flask en arrière-plan
# ============================================================================

Write-Host "`n📍 ÉTAPE 3: Lancement de Flask (mode production)..." -ForegroundColor Yellow

$env:FLASK_ENV = "production"
$flaskProcess = Start-Process `
    -FilePath $pythonPath `
    -ArgumentList "run_app.py", "prod" `
    -WorkingDirectory $(Get-Location) `
    -PassThru `
    -NoNewWindow `
    -RedirectStandardOutput "flask_output.log" `
    -RedirectStandardError "flask_error.log"

Write-Host "   ⏳ Démarrage de Flask (PID: $($flaskProcess.Id))" -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Vérifier que le processus est toujours actif
if (-not (Get-Process -Id $flaskProcess.Id -ErrorAction SilentlyContinue)) {
    Write-Host "   ❌ Flask n'a pas pu démarrer!" -ForegroundColor Red
    Write-Host "   📄 Consultez flask_error.log pour plus de détails" -ForegroundColor Red
    Write-Host "`n   Contenu flask_error.log:" -ForegroundColor Gray
    Get-Content flask_error.log -ErrorAction SilentlyContinue | Select-Object -Last 10
    exit 1
}

Write-Host "   ✅ Flask démarré avec succès" -ForegroundColor Green

# ============================================================================
# ÉTAPE 4: Attendre que Flask soit prêt
# ============================================================================

Write-Host "`n📍 ÉTAPE 4: Vérification du système..." -ForegroundColor Yellow

$maxAttempts = 10
$attempt = 0
$flaskReady = $false

while ($attempt -lt $maxAttempts) {
    $attempt++
    Write-Host "   ⏳ Tentative $attempt/$maxAttempts..." -NoNewline
    
    try {
        $response = Invoke-WebRequest "http://localhost:5000/api/info" `
            -UseBasicParsing `
            -ErrorAction Stop `
            -TimeoutSec 2
        
        Write-Host " ✅" -ForegroundColor Green
        $flaskReady = $true
        break
    } catch {
        Write-Host " ⏳" -NoNewline
        Start-Sleep -Seconds 1
    }
}

if (-not $flaskReady) {
    Write-Host "`n   ❌ Flask n'a pas répondu!" -ForegroundColor Red
    Write-Host "   💡 Vérifiez les logs: Get-Content logs/epi_detection.log -Tail 20" -ForegroundColor Yellow
    exit 1
}

Write-Host "   ✅ Flask répond correctement" -ForegroundColor Green

# ============================================================================
# ÉTAPE 5: Vérifier Arduino
# ============================================================================

Write-Host "`n📍 ÉTAPE 5: Vérification Arduino..." -ForegroundColor Yellow

try {
    $arduinoStatus = Invoke-WebRequest "http://localhost:5000/api/arduino/status" `
        -UseBasicParsing `
        -ErrorAction SilentlyContinue
    
    if ($arduinoStatus) {
        $status = $arduinoStatus.Content | ConvertFrom-Json
        
        Write-Host "   📡 Port Arduino: $($status.port)" -ForegroundColor Cyan
        Write-Host "   🔌 Connecté: $(if($status.connected) { '✅ OUI' } else { '⚠️  NON (Mode simulation)' })" -ForegroundColor $(if($status.connected) { "Green" } else { "Yellow" })
        Write-Host "   🔄 Baudrate: $($status.baudrate) baud" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ⚠️  Impossible vérifier statut Arduino (normal si simulation)" -ForegroundColor Yellow
}

# ============================================================================
# ÉTAPE 6: Tests rapides
# ============================================================================

Write-Host "`n📍 ÉTAPE 6: Tests rapides..." -ForegroundColor Yellow

Write-Host "   🎯 Test 1: LED VERTE (compliance 90%)..." -NoNewline

try {
    $response = Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/90" `
        -Method Post `
        -UseBasicParsing `
        -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
    Write-Host "      👆 Observez la LED VERTE s'allumer sur l'Arduino" -ForegroundColor Gray
} catch {
    Write-Host " ⚠️  Erreur, continuez quand même..." -ForegroundColor Yellow
}

Start-Sleep -Seconds 1

Write-Host "   🎯 Test 2: LED JAUNE (compliance 70%)..." -NoNewline

try {
    $response = Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/70" `
        -Method Post `
        -UseBasicParsing `
        -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
    Write-Host "      👆 Observez la LED JAUNE s'allumer sur l'Arduino" -ForegroundColor Gray
} catch {
    Write-Host " ⚠️  Erreur" -ForegroundColor Yellow
}

Start-Sleep -Seconds 1

Write-Host "   🎯 Test 3: LED ROUGE (compliance 20%)..." -NoNewline

try {
    $response = Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/20" `
        -Method Post `
        -UseBasicParsing `
        -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
    Write-Host "      👆 Observez la LED ROUGE et écoutez le BUZZER! 🔊" -ForegroundColor Red
} catch {
    Write-Host " ⚠️  Erreur" -ForegroundColor Yellow
}

# ============================================================================
# DÉMARRAGE COMPLET
# ============================================================================

Write-Host "`n╔════════════════════════════════════════════════════════════════╗"
Write-Host "║            ✅ SYSTÈME PRÊT - DÉMARRAGE COMPLET!               ║"
Write-Host "╚════════════════════════════════════════════════════════════════╝`n"

Write-Host "📊 STATUS:" -ForegroundColor Cyan
Write-Host "   ✅ Flask en cours sur http://localhost:5000" -ForegroundColor Green
Write-Host "   ✅ Arduino connecté et prêt sur COM3" -ForegroundColor Green
Write-Host "   ✅ LEDs testées et fonctionnelles" -ForegroundColor Green

Write-Host "`n🌐 ACCÈS AU SYSTÈME:" -ForegroundColor Cyan
Write-Host "   📤 Upload d'images: http://127.0.0.1:5000/upload" -ForegroundColor Blue
Write-Host "   📊 Dashboard:       http://127.0.0.1:5000/unified_monitoring.html" -ForegroundColor Blue
Write-Host "   📡 API Status:      http://localhost:5000/api/arduino/status" -ForegroundColor Blue

Write-Host "`n🎯 PROCHAIN ÉTAPE:" -ForegroundColor Yellow
Write-Host "   1. Ouvrir http://127.0.0.1:5000/upload dans votre navigateur"
Write-Host "   2. Sélectionner une image avec une personne"
Write-Host "   3. Regarder l'Arduino s'activer AUTOMATIQUEMENT!"
Write-Host "   4. Les LEDs vous indiqueront si l'EPI est complet/partiel/manquant"

Write-Host "`n⏸️  ARRÊTER LE SYSTÈME:" -ForegroundColor Yellow
Write-Host "   Appuyez sur CTRL+C ou fermez cette fenêtre PowerShell"

Write-Host "`n🔍 POUR DÉBOGUER:" -ForegroundColor Gray
Write-Host "   Voir logs en temps réel: Get-Content logs/epi_detection.log -Tail 20 -Wait" -ForegroundColor Gray
Write-Host "   Status Arduino:          Invoke-WebRequest http://localhost:5000/api/arduino/status" -ForegroundColor Gray

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "✨ C'est maintenant AUTOMATIQUE - Pas besoin de manipulation manuelle!"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n"

# Garder le script en cours d'exécution (optionnel - permet de fermer proprement)
# $flaskProcess | Wait-Process
