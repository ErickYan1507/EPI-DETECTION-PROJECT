# Démarrage rapide — EPI Detection (FR)

Ce guide permet de lancer rapidement l'application avec l'Arduino physique connecté.

Prérequis
- Windows (PowerShell) ou Linux/macOS
- Python 3.10+ et environnement virtuel `.venv`
- Arduino MEGA branché (ex: COM3)

Étapes rapides
1. Placer l'Arduino sur le port USB (ex: COM3).
2. Ouvrir PowerShell dans le dossier du projet.
3. Lancer le script rapide :

```powershell
.\quick_start_arduino_auto.ps1
```

4. Ouvrir le monitoring unifié : http://localhost:5000/unified_monitoring.html

Points d'attention
- Si le port est occupé, fermez l'Arduino IDE / Serial Monitor / autres applications.
- Pour forcer la reconnexion après branchement, utilisez l'API:
  - `GET /api/arduino/scan` — lister les ports
  - `POST /api/arduino/connect` — tenter la connexion

Fini — le serveur essaye de se connecter automatiquement et envoie les données de détection à l'Arduino après chaque upload/détection.
