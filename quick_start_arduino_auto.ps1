# Quick start PowerShell script - Démarrage automatique Arduino + serveur Flask
# Usage: Exécuter depuis le dossier du projet (PowerShell)
# Exemple: .\quick_start_arduino_auto.ps1

# --- Configuration (modifiez si nécessaire) ---
$arduinoPort = $env:ARDUINO_PORT -or "COM3"
$arduinoBaud = $env:ARDUINO_BAUD -or "9600"
$retries = $env:ARDUINO_START_RETRIES -or "10"
$retryDelay = $env:ARDUINO_START_RETRY_DELAY -or "1.5"

Write-Host "Quick start: ARDUINO_PORT=$arduinoPort ARDUINO_BAUD=$arduinoBaud"

# Set environment variables for this session
$env:ARDUINO_PORT = $arduinoPort
$env:ARDUINO_BAUD = $arduinoBaud
$env:ARDUINO_START_RETRIES = $retries
$env:ARDUINO_START_RETRY_DELAY = $retryDelay
$env:FLASK_ENV = "development"

# Activate venv if present
$venvActivate = Join-Path -Path (Get-Location) -ChildPath ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activation de l'environnement virtuel .venv..."
    & $venvActivate
} else {
    Write-Warning ".venv non trouvé. Assurez-vous d'utiliser l'environnement Python souhaité"
}

# Install pyserial if missing (ask for confirmation)
try {
    python -c "import serial" 2>$null
} catch {
    Write-Host "pyserial non installé. Installation en cours..."
    pip install pyserial
}

Write-Host "Démarrage du serveur Flask (mode dev) — ouvrez http://localhost:5000/unified_monitoring.html une fois prêt"
.\.venv\Scripts\python.exe run_app.py dev
