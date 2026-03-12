# Setup complet — EPI Detection (FR)

Ce document résume la configuration qui a été appliquée au projet:

- Arduino integration:
  - `app/arduino_integration.py` : contrôleur série, parser, session manager
  - Auto-reconnect et thread watcher pour hot-plug
  - Simulation uniquement si `ARDUINO_SIMULATION=1` ou `ARDUINO_PORT=SIMULATION`

- Démarrage automatique:
  - Tentatives immédiates au démarrage (variable `ARDUINO_START_RETRIES`)
  - Auto-reconnect en arrière-plan (scan ports communs)
  - Endpoint API: `/api/arduino/status`, `/api/arduino/connect`, `/api/arduino/scan`
  - UI: `/arduino` et page unifiée `/unified_monitoring.html`

- Fichiers utiles:
  - `quick_start_arduino_auto.ps1` — script PowerShell pour démarrer rapidement
  - `documentation/requirements.txt` mis à jour avec `pyserial` recommandé

- Remarques:
  - En cas d'`Access denied` sur le port, vérifier quel processus tient le port (Process Explorer / Handle)
  - Les LEDs et buzzer sont pilotés par le firmware Arduino (fichier .ino dans repo)

