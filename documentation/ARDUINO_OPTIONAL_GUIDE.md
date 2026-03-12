# Guide: Exécuter app/main.py avec ou sans Arduino

## Overview

L'application Flask dans `app/main.py` peut maintenant fonctionner **avec ou sans Arduino**. L'intégration Arduino est complètement optionnelle et gracieuse - si Arduino n'est pas disponible ou désactivé, l'application continue de fonctionner normalement.

## Configuration

### Option 1: Désactiver Arduino (Par défaut, Arduino est activé)

Pour désactiver Arduino, définissez la variable d'environnement `ARDUINO_ENABLED` :

#### ✅ Sous Windows (PowerShell)
```powershell
# Exécuter une seule fois durant cette session
$env:ARDUINO_ENABLED = "false"
python run_app.py

# OU le faire persistant (optionnel)
[Environment]::SetEnvironmentVariable("ARDUINO_ENABLED", "false", "User")
```

#### ✅ Sous Windows (CMD)
```cmd
set ARDUINO_ENABLED=false
python run_app.py
```

#### ✅ Sous Linux/Mac
```bash
export ARDUINO_ENABLED=false
python run_app.py
# OU
ARDUINO_ENABLED=false python run_app.py
```

### Option 2: Activer Arduino (Comportement par défaut)

```powershell
# Aucune variable d'environnement nécessaire - Arduino est activé par défaut
python run_app.py

# OU explicitement :
$env:ARDUINO_ENABLED = "true"
python run_app.py
```

### Option 3: Configurer le port Arduino (si Arduino est activé)

```powershell
$env:ARDUINO_PORT = "COM3"      # Port série (défaut: COM3)
$env:ARDUINO_BAUD = "115200"    # Vitesse baud (défaut: 9600)
$env:ARDUINO_ENABLED = "true"   # Activer Arduino
python run_app.py
```

## Valeurs Acceptées pour ARDUINO_ENABLED

| Valeur | Effet |
|--------|-------|
| `true`, `1`, `yes` | ✅ Arduino **activé** |
| `false`, `0`, `no` | ❌ Arduino **désactivé** |
| Non défini | ✅ Arduino **activé par défaut** |

## Comportement selon la Configuration

### Scenario 1: Arduino Activé + Connecté ✅
```
Logs:
  ✅ ArduinoSession initialisé et connecté (port=COM3)
  
Détections en temps réel:
  → Les données sont envoyées à l'Arduino
  
Routes Arduino:
  → /api/arduino/status → connected: true
  → /api/arduino/send-detection → envoie à l'Arduino
  → /api/arduino/send-compliance → envoie à l'Arduino
```

### Scenario 2: Arduino Activé + Non Connecté / USB Débranché ⚠️
```
Logs:
  ℹ️ Arduino non connecté immédiatement — activation de l'auto-reconnect
  
Détections en temps réel:
  → Les données ne sont PAS envoyées (pas de crash)
  → Continune d'afficher les détections localement
  
Routes Arduino:
  → /api/arduino/status → connected: false
  → /api/arduino/send-detection → Retorne "Arduino non connecté"
  → /api/arduino/send-compliance → Retorne "Arduino non connecté"
```

### Scenario 3: Arduino Désactivé (ARDUINO_ENABLED=false) ℹ️
```
Logs:
  ℹ️ Arduino désactivé via ARDUINO_ENABLED=false
  
Détections en temps réel:
  → Les données ne sont PAS envoyées à l'Arduino
  → Continune d'afficher les détections localement
  → Pas de tentatives de connexion, pas de logs d'erreur
  
Routes Arduino:
  → /api/arduino/status → connected: false
  → /api/arduino/send-detection → "Arduino non initié"
  → /api/arduino/send-compliance → "Arduino non initié"
```

### Scenario 4: Module Arduino Indisponible (ImportError) ⚠️
```
Logs:
  ⚠️ Module Arduino non disponible - Arduino sera désactivé
  
Détections en temps réel:
  → Les données ne sont PAS envoyées
  → L'application fonctionne normalement
  
Routes Arduino:
  → /api/arduino/status → connected: false
  → /api/arduino/send-detection → "Arduino non initié"
```

## Architecture de la Modification

### 1. Import Optionnel
```python
# app/main.py
try:
    from app.arduino_integration import ArduinoSessionManager
    ARDUINO_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  Module Arduino non disponible")
    ArduinoSessionManager = None
    ARDUINO_AVAILABLE = False
```

### 2. Initialisation Gracieuse
```python
def init_arduino():
    # Vérifie ARDUINO_ENABLED
    arduino_enabled = os.getenv('ARDUINO_ENABLED', 'true').lower() in ('true', '1', 'yes')
    
    if not arduino_enabled:
        logger.info("ℹ️  Arduino désactivé via ARDUINO_ENABLED=false")
        app.arduino = None
        return
    
    # Vérifie si le module est disponible
    if not ARDUINO_AVAILABLE:
        logger.warning("⚠️  Arduino non disponible")
        app.arduino = None
        return
    
    # Lance le thread d'initialisation Arduino
    # ...
```

### 3. Routes Défensives
Toutes les routes Arduino utilisent `getattr(app, 'arduino', None)` et vérifient l'état :

```python
@app.route('/api/arduino/status')
def arduino_status():
    ar = getattr(app, 'arduino', None)
    if not ar:
        return jsonify({'connected': False, ...}), 200  # Gracieux
    # ...
```

### 4. Détections Gracieuses
Le flux de caméra capture les erreurs Arduino et continue :

```python
try:
    # Accéder Arduino
    main_module = sys.modules.get('__main__')
    if hasattr(main_module, 'app') and hasattr(main_module.app, 'arduino'):
        arduino = main_module.app.arduino
        if arduino and arduino.connected:
            arduino.send_detection_data(...)
except Exception as e:
    logger.debug(f"Arduino error: {e}")  # Log silencieux, pas de crash
```

## Cas d'Usage Recommandés

### 🚀 Production avec Arduino
```powershell
# Arduino en USB stabilisé, port identifié
$env:ARDUINO_PORT = "COM5"
$env:ARDUINO_BAUD = "115200"
$env:ARDUINO_ENABLED = "true"
python run_app.py
```

### 🧪 Développement sans Arduino
```powershell
# Tester l'app sans matériel
$env:ARDUINO_ENABLED = "false"
python run_app.py
```

### 🔧 Test avec Arduino Auto-Reconnect
```powershell
# Arduino peut être débranché/rebranché, auto-reconnect activé
$env:ARDUINO_ENABLED = "true"
# Autres config par défaut
python run_app.py
```

### 📦 Docker / Conteneur (éventuellement)
```dockerfile
# Dans Dockerfile, Arduino est activé par défaut
# Mais peut être désactivé au runtime :
ENV ARDUINO_ENABLED=false
```

## Vérification

### 1. Vérifier que l'app démarre
```powershell
$env:ARDUINO_ENABLED = "false"
python run_app.py
# Devrait voir : "ℹ️  Arduino désactivé via ARDUINO_ENABLED=false"
```

### 2. Vérifier que Arduino fonctionne avec connexion
```powershell
python run_app.py  # Arduino activé par défaut
# Devrait voir : "✅ ArduinoSession initialisé et connecté (port=COM3)"
```

### 3. Vérifier que les routes répondent
```bash
# Arduino status (sans Arduino) - Should return connected: false
curl http://localhost:5000/api/arduino/status

# Arduino status (avec Arduino) - Should return connected: true (si connecté)
curl http://localhost:5000/api/arduino/status
```

### 4. Vérifier les logs
Regarder les logs pour les messages d'état Arduino :
- ✅ Arduino connecté
- ⚠️  Arduino indisponible
- ℹ️  Arduino désactivé
- ❌ Erreurs Arduino (catturées et loggées, pas de crash)

## Troubleshooting

### Issue: "Arduino désactivé" mais je veux l'activer
```powershell
# Remplacer par:
$env:ARDUINO_ENABLED = "true"
# OU supprimer la variable pour utiliser la valeur par défaut (true)
Remove-Item Env:ARDUINO_ENABLED
```

### Issue: Arduino timeout / pas de détection
```
Vérifications :
1. Arduino est bien branché en USB
2. Le COM port est correct (COM3 par défaut, ou ARDUINO_PORT=COMx)
3. Regarder les logs pour auto-reconnect
4. Vérifier le firmware Arduino
```

### Issue: Module "app.arduino_integration" introuvable
```
→ Arduino sera désactivé automatiquement
→ L'app fonctionnera sans Arduino
→ Voir: "⚠️  Module Arduino non disponible"
```

## Résumé

| Configuration | Arduino Activé | Fonctionne? | Détails |
|---------------|---|---|---|
| Défaut (rien) | ✅ Oui | ✅ Oui | Arduino lancé si disponible et connecté |
| `ARDUINO_ENABLED=false` | ❌ Non | ✅ Oui | App sans Arduino, plus rapide |
| `ARDUINO_ENABLED=true` | ✅ Oui | ✅ Oui | Arduino forcé, auto-reconnect si déconnecté |
| Module manquant | ❌ Non | ✅ Oui | Gracieux fallback, pas d'erreur |

---

**Version:** 1.0 (February 2026)
**Compatibilité:** Python 3.8+, Flask 2.0+
