# 🚀 Script de Démarrage Rapide d'Entraînement Optimisé
# Usage: .\quick_train_optimized.ps1 -epochs 50 -batch 8

param(
    [int]$epochs = 100,
    [int]$batch = 16,
    [int]$imgSize = 640,
    [string]$dataset = "dataset",
    [string]$mode = "standard"  # standard, fast, quality, multi
)

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║    🚀 ENTRAÎNEMENT OPTIMISÉ - DÉMARRAGE RAPIDE            ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Afficher la configuration
Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "  - Mode: $mode"
Write-Host "  - Epochs: $epochs"
Write-Host "  - Batch Size: $batch"
Write-Host "  - Image Size: $imgSize"
Write-Host "  - Dataset: $dataset"
Write-Host ""

# Prédéfinis de mode
switch ($mode) {
    "fast" {
        Write-Host "⚡ Mode RAPIDE" -ForegroundColor Yellow
        $epochs = 50
        $batch = 8
        $imgSize = 416
        Write-Host "  - Epochs: 50 (moins), Batch: 8, Size: 416"
    }
    "quality" {
        Write-Host "🎯 Mode QUALITÉ" -ForegroundColor Green
        $epochs = 200
        $batch = 8
        $imgSize = 800
        Write-Host "  - Epochs: 200 (plus), Batch: 8, Size: 800"
    }
    "multi" {
        Write-Host "🔄 Mode MULTI-ENTRAÎNEMENTS" -ForegroundColor Magenta
        $numTrainings = 3
        Write-Host "  - Lancer 3 entraînements successifs"
    }
    "standard" {
        Write-Host "📊 Mode STANDARD (Équilibré)" -ForegroundColor Blue
        Write-Host "  - Epochs: $epochs, Batch: $batch, Size: $imgSize"
    }
}

Write-Host ""

# Vérifier le dataset
if (!(Test-Path $dataset)) {
    Write-Host "⚠️  Dataset non trouvé: $dataset" -ForegroundColor Red
    Write-Host "Créez la structure:" -ForegroundColor Yellow
    Write-Host "  $dataset/images/train/"
    Write-Host "  $dataset/images/val/"
    Write-Host "  $dataset/labels/train/"
    Write-Host "  $dataset/labels/val/"
    Read-Host "Appuyez sur Entrée pour continuer..."
}

# Nettoyer les anciens modèles (optionnel)
Write-Host ""
$clean = Read-Host "Nettoyer les anciens modèles? (o/n)"
if ($clean -eq "o" -or $clean -eq "O") {
    Write-Host "🧹 Suppression de models/..." -ForegroundColor Yellow
    Remove-Item -Path "models" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Nettoyé"
}

Write-Host ""
Write-Host "🚀 Démarrage de l'entraînement..." -ForegroundColor Green
Write-Host "═" * 60

# Lancer l'entraînement
if ($mode -eq "multi") {
    & python train.py --dataset $dataset --epochs $epochs --batch-size $batch --img-size $imgSize --num-trainings $numTrainings
} else {
    & python train.py --dataset $dataset --epochs $epochs --batch-size $batch --img-size $imgSize
}

Write-Host "═" * 60
Write-Host ""
Write-Host "✅ ENTRAÎNEMENT TERMINÉ" -ForegroundColor Green
Write-Host ""

# Vérifier le résultat
if (Test-Path "models/best.pt") {
    $size = (Get-Item "models/best.pt").Length / 1MB
    Write-Host "📊 Résultat:" -ForegroundColor Cyan
    Write-Host "  ✓ Modèle sauvegardé: models/best.pt"
    Write-Host "  ✓ Taille: $([Math]::Round($size, 1)) MB"
    Write-Host ""
    Write-Host "🎯 Utilisation:" -ForegroundColor Cyan
    Write-Host "  python detect.py --weights models/best.pt --source image.jpg"
} else {
    Write-Host "❌ Erreur: Modèle non créé" -ForegroundColor Red
}

Write-Host ""
Read-Host "Appuyez sur Entrée pour terminer"
