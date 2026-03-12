# Test de connexion SMTP Gmail directement

$email = "ainaerickandrianavalona09@gmail.com"
$password = "mqoc zsrh lrsh zhhn"  # Votre clé d'application

Write-Host "=" * 60
Write-Host "🔌 TEST CONNEXION SMTP GMAIL"
Write-Host "=" * 60
Write-Host ""
Write-Host "Email: $email"
Write-Host "Clé: $password"
Write-Host ""

# Créer les credentials
$secPassword = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential ($email, $secPassword)

# Tester l'envoi
$mailParams = @{
    To = $email
    From = $email
    Subject = "🧪 Test SMTP Gmail"
    Body = "Ceci est un test de connexion SMTP."
    SmtpServer = "smtp.gmail.com"
    Port = 587
    UseSsl = $true
    Credential = $credential
    ErrorAction = "Stop"
}

try {
    Send-MailMessage @mailParams
    Write-Host "✅ EMAIL ENVOYÉ AVEC SUCCÈS!"
    Write-Host ""
    Write-Host "Votre configuration fonctionne! 🎉"
    Write-Host ""
    Write-Host "Allez maintenant à: http://localhost:5000/notifications"
    Write-Host "et envoyer des emails ✉️"
} catch {
    Write-Host "❌ ERREUR: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Problèmes possibles:"
    Write-Host "1. Clé d'application incorrect"
    Write-Host "2. 2FA non activée"
    Write-Host "3. Email incorrect"
    Write-Host ""
    Write-Host "Solution:"
    Write-Host "  • Allez à https://myaccount.google.com/apppasswords"
    Write-Host "  • Créez une NOUVELLE clé"
    Write-Host "  • Copiez-la exactement (avec espaces)"
}
