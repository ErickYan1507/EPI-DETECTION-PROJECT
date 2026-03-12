#!/usr/bin/env python3
"""
🤖 GUIDE DE CONFIGURATION: Activation Automatique Arduino lors de Détection
Démarrage automatique du système Arduino physique avec tous ses composants

Étapes complètes pour activation automatique:
"""

import os
import subprocess
import time
from pathlib import Path

print("""
╔═══════════════════════════════════════════════════════════════════════╗
║     🚀 ACTIVATION AUTOMATIQUE ARDUINO PHYSIQUE LORS DE DÉTECTION      ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

# ============================================================================
# ÉTAPE 1: Configuration de l'Arduino
# ============================================================================

print("""
📌 ÉTAPE 1: Configuration Arduino Physique
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ À faire AVANT de lancer le système:

   A) TÉLÉCHARGER LE CODE ARDUINO
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. Ouvrir: https://www.tinkercad.com
   2. Importer le fichier: tinkercad_arduino.ino
   3. Copier le sketch complet
   
   B) CHARGER DANS ARDUINO MEGA 2560
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. Ouvrir Arduino IDE
   2. Coller le sketch
   3. Sélectionner: Tools → Board → Arduino MEGA 2560
   4. Sélectionner: Tools → Port → COM3
   5. Cliquer: Sketch → Upload
   
   C) VÉRIFIER LES CONNEXIONS MATÉRIELLES
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📍 PIN 2: Capteur PIR (mouvement)
   📍 PIN 3: LED JAUNE (avertissement)
   📍 PIN 4: LED VERTE (conforme)
   📍 PIN 5: LED ROUGE (danger)
   📍 PIN 9: BUZZER (alerte sonore)
   📍 A0: Capteur température
   📍 A1: Capteur humidité
   
   D) TESTER LA CONNEXION SÉRIE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Arduino IDE → Tools → Serial Monitor
   Doit afficher: "[STARTUP] EPI Detection Arduino MEGA Controller"

✨ Configuration Arduino: ✅ COMPLÈTE
""")

# ============================================================================
# ÉTAPE 2: Lancer le système Flask
# ============================================================================

print("""
📌 ÉTAPE 2: Démarrage du système Flask
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION A: Lancer avec le port Arduino automatiquement (RECOMMANDÉ)
─────────────────────────────────────────────────────────────────

Exécuter DANS PowerShell:

   $env:ARDUINO_PORT = "COM3"
   .\.venv\Scripts\python.exe run_app.py prod

Attendez le message: "✅ Arduino connecté sur COM3"


OPTION B: Test en mode simulation d'abord
──────────────────────────────────────────

   $env:ARDUINO_PORT = "SIMULATION"
   .\.venv\Scripts\python.exe run_app.py dev

(Permet de tester sans hardware)
""")

# ============================================================================
# ÉTAPE 3: Vérifier que tout fonctionne
# ============================================================================

print("""
📌 ÉTAPE 3: Vérification du Système
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Exécuter DANS PowerShell (après le lancement de Flask):

   # Vérifier que Arduino est connecté
   Invoke-WebRequest "http://localhost:5000/api/arduino/status" `
     -UseBasicParsing | ConvertFrom-Json
   
   # Tester LED VERTE (compliance >= 80%)
   Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/90" `
     -Method Post -UseBasicParsing
   
   # Tester LED JAUNE (compliance 60-79%)
   Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/70" `
     -Method Post -UseBasicParsing
   
   # Tester LED ROUGE + BUZZER (compliance < 60%)
   Invoke-WebRequest "http://localhost:5000/api/arduino/test-compliance/30" `
     -Method Post -UseBasicParsing

💡 Vous devriez VOIR les LEDs s'allumer sur l'Arduino!
""")

# ============================================================================
# ÉTAPE 4: Test de détection en temps réel
# ============================================================================

print("""
📌 ÉTAPE 4: Test de Détection Automatique
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE AUTOMATIC ACTIVATION WORKS LIKE THIS:

   1️⃣ UTILISATEUR UPLOAD UNE IMAGE
      Navigateur → http://127.0.0.1:5000/upload
      Sélectionner une image (avec/sans EPI)
   
   2️⃣ SYSTÈME ANALYSE L'IMAGE
      Flask détecte: helmet (oui/non)
                     vest (oui/non)
                     glasses (oui/non)
                     confidence (score %)
   
   3️⃣ ARDUINO S'ACTIVE AUTOMATIQUEMENT
      ✅ DETECTION COMPLÈTE → LED VERTE
         (helmet=1, vest=1, glasses=1, confidence>80)
      
      ⚠️  DETECTION PARTIELLE → LED JAUNE
         (certains EPI manquent ou confidence 60-79%)
      
      ❌ DETECTION INSUFFISANTE → LED ROUGE + BUZZER
         (EPI manquants ou confidence < 60%)

🎬 FLUX COMPLET AUTOMATIQUE:
   Image → Analyse → Calcul Compliance → COMMANDE ARDUINO → ACTIVATION PHYSIQUE

VOUS NE DEVEZ RIEN FAIRE MANUELLEMENT - C'EST AUTOMATIQUE!
""")

# ============================================================================
# ÉTAPE 5: Commandes manuelles pour tests
# ============================================================================

print("""
📌 ÉTAPE 5: Commandes Manuelles pour Tests (Optionnel)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Si vous voulez tester manuellement, exécuter en PowerShell:

   A) Tester DÉTECTION COMPLÈTE (LED VERTE)
      ────────────────────────────────────────
      $data = @{helmet=$true; vest=$true; glasses=$true; confidence=95} | ConvertTo-Json
      Invoke-WebRequest "http://localhost:5000/api/arduino/test-detection" `
        -Method Post -ContentType "application/json" -Body $data `
        -UseBasicParsing
   
   
   B) Tester DÉTECTION PARTIELLE (LED JAUNE)
      ──────────────────────────────────────
      $data = @{helmet=$true; vest=$false; glasses=$true; confidence=70} | ConvertTo-Json
      Invoke-WebRequest "http://localhost:5000/api/arduino/test-detection" `
        -Method Post -ContentType "application/json" -Body $data `
        -UseBasicParsing
   
   
   C) Tester DÉTECTION MANQUANTE (LED ROUGE + BUZZER)
      ──────────────────────────────────────────────
      $data = @{helmet=$false; vest=$false; glasses=$false; confidence=0} | ConvertTo-Json
      Invoke-WebRequest "http://localhost:5000/api/arduino/test-detection" `
        -Method Post -ContentType "application/json" -Body $data `
        -UseBasicParsing

💡 Les LEDs doivent s'allumer sur l'Arduino en temps réel!
""")

# ============================================================================
# ÉTAPE 6: Monitoring et debugging
# ============================================================================

print("""
📌 ÉTAPE 6: Monitoring et Déboggage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VOIR LES LOGS ARDUINO EN TEMPS RÉEL:

   PowerShell:
   ───────────
   Get-Content logs/epi_detection.log -Tail 50 -Wait
   
   Ou chercher les lignes importantes:
   Get-Content logs/epi_detection.log | Select-String "DETECT:|Arduino|LED"

MONITORER L'ACTIVITÉ:

   📊 Dashboard web: http://127.0.0.1:5000/unified_monitoring.html
   
   📡 Endpoint statut: http://localhost:5000/api/arduino/status
   
   📈 Endpoint stats: http://localhost:5000/api/detections/last


DÉBOGGER LES PROBLÈMES:

   ❌ "Arduino non connecté"
      → Vérifier: COM3 dans Gestionnaire périphériques
      → Relancer: $env:ARDUINO_PORT = "COM3"
      → Vérifier le sketch Arduino est chargé
   
   ❌ "LEDs ne s'allument pas"
      → Tester manuel: Invoke-WebRequest ".../test-compliance/50"
      → Vérifier les connexions PIN
      → Ouvrir Serial Monitor Arduino IDE
   
   ❌ "Buzzer ne sonne pas"
      → Vérifier PIN 9 configuré
      → Tester: Invoke-WebRequest ".../test-compliance/20"
      → Vérifier les logs pour "[STATUS] 🚨 DANGER"
""")

# ============================================================================
# ÉTAPE 7: Architecture du système
# ============================================================================

print("""
📌 ARCHITECTURE SYSTÈME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FICHIERS PRINCIPAUX:

   📄 app/arduino_integration.py
      └─ Classe: ArduinoController
         └─ Méthodes principales:
            • connect() → Établir connexion série
            • send_detection_data() → Envoyer DETECT:...
            • send_compliance_level() → Envoyer C<level>
   
   📄 app/routes_api.py (@app.route('/api/detect'))
      └─ Endpoint qui:
         1. Analyse l'image
         2. Détecte EPI (helmet, vest, glasses)
         3. Appelle: send_detection_data() ← ACTIVATION AUTO
         4. Retourne JSON avec compliance score
   
   📄 tinkercad_arduino.ino (sur l'Arduino)
      └─ Reçoit: DETECT:helmet=X,vest=X,glasses=X,confidence=Y
      └─ Calcule: compliance score
      └─ Active les LEDs et buzzer en fonction du score


FLUX DE COMMUNICATION:

   Python Flask                          Arduino MEGA
   ─────────────────────────────────────────────────────
   1. Détecte EPI dans image
                           ──DETECT:...──>
                                         2. Reçoit dato
                                         3. Parse values
                                         4. Calcule score
                                         5. Active LEDs/Buzzer
                           <──STATUS:...──
   6. Affiche résultat


THRESHOLDS (Configurables dans tinkercad_arduino.ino):

   HIGH_COMPLIANCE_THRESHOLD = 80    → LED VERTE
   MEDIUM_COMPLIANCE_THRESHOLD = 60  → LED JAUNE
   < 60                               → LED ROUGE + BUZZER
""")

# ============================================================================
# ÉTAPE FINALE: Checklist de démarrage
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                   ✅ CHECKLIST DE DÉMARRAGE RAPIDE                    ║
╚═══════════════════════════════════════════════════════════════════════╝

AVANT LE DÉMARRAGE:
   ☐ Arduino MEGA 2560 branché USB sur COM3
   ☐ Code Arduino (tinkercad_arduino.ino) chargé dans la carte
   ☐ LEDs branchées sur PIN 3 (JAUNE), 4 (VERTE), 5 (ROUGE)
   ☐ Buzzer branché sur PIN 9
   ☐ Capteur PIR optionnel sur PIN 2
   ☐ Alimentations vérifiées

DÉMARRAGE:
   ☐ Ouvrir PowerShell dans le dossier projet
   ☐ Exécuter: $env:ARDUINO_PORT = "COM3"
   ☐ Exécuter: .\.venv\Scripts\python.exe run_app.py prod
   ☐ Attendre: "✅ Arduino connecté sur COM3"

TEST:
   ☐ Naviguer vers: http://127.0.0.1:5000/upload
   ☐ Sélectionner une image avec personne(s)
   ☐ Observer les LEDs s'allumer automatiquement!

TOUT FONCTIONNE? 🎉
   ✅ LED VERTE = Personne avec EPI complet
   ✅ LED JAUNE = Personne avec EPI partiel
   ✅ LED ROUGE + BUZZER = Personne sans EPI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ C'est automatique - pas besoin de manipulation manuelle!
🚀 Le système détecte et active Arduino en temps réel!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

if __name__ == "__main__":
    print("\n📝 Pour mémoriser cette procédure, exécutez:")
    print("   python ARDUINO_AUTO_ACTIVATION_SETUP.py\n")
