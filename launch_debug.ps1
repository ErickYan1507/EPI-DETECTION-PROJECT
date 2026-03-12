# Script PowerShell pour lancer Flask et ouvrir la page DEBUG

Write-Host "=" * 60
Write-Host "🚀 Lancement de Flask + Page DEBUG"
Write-Host "=" * 60

# Aller au répertoire projet
cd d:/projet/EPI-DETECTION-PROJECT

# Attendre un peu
Write-Host ""
Write-Host "🔄 Démarrage de Flask..."
Write-Host "[Attendez 3 secondes...]"
Write-Host ""

# Lancer Flask en arrière-plan
$flaskProcess = Start-Process -FilePath ".venv/Scripts/python.exe" -ArgumentList "run_app.py" -PassThru -NoNewWindow

# Attendre 3 secondes que Flask se lance
Start-Sleep -Seconds 3

# Vérifier que Flask tourne
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/" -ErrorAction Stop -TimeoutSec 2
    Write-Host "✅ Flask est actif!"
    Write-Host ""
    Write-Host "🌐 Ouverture de la page DEBUG dans le navigateur..."
    Write-Host ""
    
    # Ouvrir la page DEBUG
    Start-Process "http://localhost:5000/api/notifications/debug"
    
    Write-Host "✅ Page DEBUG ouverte!"
    Write-Host ""
    Write-Host "=" * 60
    Write-Host "Consignes:"
    Write-Host "1. Exécutez les tests dans l'ordre (TEST 1 → TEST 5)"
    Write-Host "2. Regardez les logs verts/rouges dans la console"
    Write-Host "3. Verifiez si les emails sont sauvegardés"
    Write-Host ""
    Write-Host "❌ Pour arrêter Flask:"
    Write-Host "   Stop-Process -Id $($flaskProcess.Id)"
    Write-Host "=" * 60
    
    # Garder le script ouvert
    Read-Host "Appuyez sur ENTRÉE pour arrêter Flask"
    Stop-Process -Id $flaskProcess.Id
    Write-Host "✅ Flask arrêté"
} catch {
    Write-Host "❌ Flask n'a pas démarré correctement"
    Write-Host "Erreur: $_"
    if ($flaskProcess) {
        Stop-Process -Id $flaskProcess.Id -Force
    }
}
