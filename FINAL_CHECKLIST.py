#!/usr/bin/env python3
"""
GUIDE FINAL - Check tout avant de lancer!
À imprimer ou garder ouvert pendant la configuration
"""

CHECKLIST = """
████████████████████████████████████████████████████████░░░░░░░░ 100%
"""

print("""
╔════════════════════════════════════════════════════════════════════╗
║                  📧 CONFIGURATION EMAIL - CHECKLIST               ║
╚════════════════════════════════════════════════════════════════════╝

ÉTAPE 1: PRÉPARER GMAIL (5 min)
════════════════════════════════════════════════════════════════════

  [ ] Compte Gmail existant
  
  [ ] Aller sur https://myaccount.google.com/security
  
  [ ] Cliquer "Vérification en 2 étapes" → Activer
      └─ Confirmer avec SMS ou authenticator
  
  [ ] Retourner à https://myaccount.google.com/apppasswords
  
  [ ] Sélectionner "Mail" et "Windows" (ou votre OS)
  
  [ ] Cliquer "Générer"
  
  [ ] COPIER le mot de passe (16 caractères)
      Exemple format: abcd efgh ijkl mnop
  
  ✅ Gmail préparé!


ÉTAPE 2: CONFIGURER .env.email (2 min)
════════════════════════════════════════════════════════════════════

  [ ] Ouvrir le fichier: .env.email
  
  [ ] Remplir SENDER_EMAIL = votre.email@gmail.com
  
  [ ] Remplir SENDER_PASSWORD = abcd efgh ijkl mnop
      (sans guillemets, les espaces sont normaux)
  
  [ ] Remplir RECIPIENT_EMAILS = admin@company.com
      (peut être plusieurs séparés par virgules)
  
  [ ] Configurer DAILY_REPORT_HOUR = 08
      (0-23, exemple 08 = 8h du matin)
  
  [ ] Configurer WEEKLY_REPORT_DAY = 1
      (0=lun, 1=mar, 2=mer, 3=jeu, 4=ven, 5=sam, 6=dim)
  
  [ ] SAUVEGARDER le fichier (Ctrl+S)
  
  ✅ Configuration complétée!


ÉTAPE 3: TESTER LA CONFIGURATION (3 min)
════════════════════════════════════════════════════════════════════

  [ ] Ouvrir Terminal PowerShell dans le projet
  
  [ ] Lancer assistant:
      python setup_email_interactive.py
  
  [ ] Attendre les 5 étapes:
      1. Vérification paramètres
      2. Test connexion SMTP
      3. Test d'envoi email
      4. Rapport sur configuration
      5. Résumé final
  
  [ ] Attendre "✅ TOUS LES TESTS RÉUSSIS!"
  
  [ ] Vérifier que vous avez reçu un email de test
      └─ Vérifier aussi le dossier SPAM
  
  ✅ Configuration testée!


ÉTAPE 4: LANCER L'APPLICATION (instant)
════════════════════════════════════════════════════════════════════

  [ ] Lancer l'app:
      python run.py --mode run
  
  [ ] Attendre le message de démarrage:
      """Scheduler de rapports démarré"""
  
  [ ] Vérifier dans la console:
      "✅ Rapport quotidien programmé à 8h00"
      "✅ Rapport hebdomadaire programmé..."
      "✅ Scheduler de rapports démarré"
  
  ✅ Application lancée avec scheduler!


ÉTAPE 5: VÉRIFIER L'ÉTAT (optionnel)
════════════════════════════════════════════════════════════════════

  Dans un autre Terminal PowerShell:
  
  [ ] Voir l'état du scheduler:
      python show_scheduler_status.py
  
  [ ] Vérifier les logs:
      type logs/app.log | findstr /i email
  
  ✅ Scheduler en cours d'exécution!


🎉 PRÊT!
════════════════════════════════════════════════════════════════════

  Vous avez maintenant:
  ✅ Configuration SMTP Gmail
  ✅ Rapports programmés automatiquement
  ✅ Tests réussis
  ✅ Scheduler actif

  Les rapports seront envoyés selon l'horaire:
  📊 Quotidien: Tous les jours
  📅 Hebdo: Une fois par semaine
  📆 Mensuel: Une fois par mois
  🚨 Alertes: Immédiat si compliance faible


❓ TROUBLESHOOTING
════════════════════════════════════════════════════════════════════

  ❌ "Authentification échouée"
     → Vérifier 2FA activée
     → Régénérer mot de passe app
     → Vérifier dans .env.email

  ❌ "Connection refused"
     → Vérifier connexion Internet
     → Vérifier firewall (port 587)

  ❌ "Email ne reçoit pas"
     → Vérifier SPAM
     → Vérifier RECIPIENT_EMAILS dans .env.email
     → Vérifier logs/app.log

  ❌ "Module not found"
     → pip install python-dotenv APScheduler


📖 DOCUMENTATION
════════════════════════════════════════════════════════════════════

  Besoin d'aide? Consultez:
  
  1. START_EMAIL_HERE.md         ← Démarrage rapide
  2. GUIDE_EMAIL_SETUP.md        ← Documentation complète
  3. EMAIL_EXAMPLES.py           ← Exemples de code
  4. MAIL_SETUP_FINAL.md         ← Résumé final


✅ À IMPRIMER OU GARDER OUVERT!
════════════════════════════════════════════════════════════════════

""")

# Afficher les fichiers importants
print("\n📁 FICHIERS IMPORTANTS:\n")
import os
from pathlib import Path

files = {
    '.env.email': 'Configuration (À REMPLIR!)',
    'setup_email_interactive.py': 'Assistant (À LANCER EN PREMIER!)',
    'START_EMAIL_HERE.md': 'Guide de démarrage',
    'GUIDE_EMAIL_SETUP.md': 'Documentation complète',
    'test_email_config.py': 'Test SMTP',
    'verify_email_config.py': 'Vérification complète',
    'show_scheduler_status.py': 'État du scheduler',
    'EMAIL_EXAMPLES.py': 'Exemples de code',
}

project_root = Path(__file__).parent
for filename, description in files.items():
    filepath = project_root / filename
    exists = "✅" if filepath.exists() else "❌"
    print(f"  {exists} {filename:40} - {description}")

print("\n" + "="*70)
print("Êtes-vous prêt? Lancez: python setup_email_interactive.py")
print("="*70 + "\n")
