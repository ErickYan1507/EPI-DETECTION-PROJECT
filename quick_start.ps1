#!/usr/bin/env pwsh
# Quick Start Script pour Windows PowerShell
# Démarrage rapide du système Dual Database

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║     🚀 EPI DETECTION - DUAL DATABASE QUICK START 🚀           ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$ProjectRoot = Get-Location

Write-Host "ÉTAPE 1: Installer les dépendances Python" -ForegroundColor Green
Write-Host "═════════════════════════════════════════════════════════════════`n" -ForegroundColor Green

$packages = @(
    'mysql-connector-python',
    'PyMySQL',
    'python-dotenv',
    'tabulate'
)

Write-Host "📦 Installation des packages...`n"
foreach ($package in $packages) {
    Write-Host "  $package... " -NoNewline
    try {
        $null = & python -m pip install -q $package 2>$null
        Write-Host "✓" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  (continuer...)" -ForegroundColor Yellow
    }
}

Write-Host "`nÉTAPE 2: Créer les répertoires" -ForegroundColor Green
Write-Host "═════════════════════════════════════════════════════════════════`n" -ForegroundColor Green

$dirs = @('database', 'logs', 'instance')
foreach ($dir in $dirs) {
    $path = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $path)) {
        $null = New-Item -ItemType Directory -Path $path
    }
    Write-Host "  ✓ $dir/" -ForegroundColor Green
}

Write-Host "`nÉTAPE 3: Créer .env (si nécessaire)" -ForegroundColor Green
Write-Host "═════════════════════════════════════════════════════════════════`n" -ForegroundColor Green

$envFile = Join-Path $ProjectRoot ".env"
$envExample = Join-Path $ProjectRoot ".env.example"

if (Test-Path $envFile) {
    Write-Host "  ✓ .env existe déjà" -ForegroundColor Green
} elseif (Test-Path $envExample) {
    Copy-Item $envExample $envFile
    Write-Host "  ✓ .env créé depuis .env.example" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  .env.example non trouvé" -ForegroundColor Yellow
}

Write-Host "`n════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ SETUP RAPIDE TERMINÉ!`n" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "PROCHAINES ÉTAPES:" -ForegroundColor Yellow
Write-Host "`n1️⃣  CONFIGURER MYSQL:" -ForegroundColor Yellow
Write-Host "   python app\mysql_config_setup.py --all" -ForegroundColor Cyan

Write-Host "`n2️⃣  LANCER LA SYNC:" -ForegroundColor Yellow
Write-Host "   python app\sync_databases.py --watch" -ForegroundColor Cyan

Write-Host "`n3️⃣  APP FLASK (autre PowerShell):" -ForegroundColor Yellow
Write-Host "   python run_app.py run" -ForegroundColor Cyan

Write-Host "`nDOCUMENTATION:" -ForegroundColor Yellow
Write-Host "   START_HERE_DUAL_DB.txt" -ForegroundColor Cyan
Write-Host "   GUIDE_DUAL_DATABASE.md" -ForegroundColor Cyan
Write-Host "   INDEX_DUAL_DATABASE.txt" -ForegroundColor Cyan

Write-Host "`n════════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
