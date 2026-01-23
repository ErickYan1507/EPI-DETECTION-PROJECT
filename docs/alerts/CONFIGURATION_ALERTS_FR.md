# Configuration Complète des Alertes Email

## Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Configuration Gmail rapide](#configuration-gmail-rapide)
3. [Configuration avancée](#configuration-avancée)
4. [API des alertes](#api-des-alertes)
5. [Troubleshooting](#troubleshooting)
6. [Exemples d'intégration](#exemples-dintégration)

---

## Vue d'ensemble

Le système d'alertes email détecte les **non-conformités EPI** et envoie des notifications en temps réel via Gmail.

### Types d'alertes disponibles:
- **Alerte EPI Manquant** - Pas d'EPI détecté pendant X secondes
- **Alerte Taux Bas** - Nombre de détections inférieur au seuil
- **Alerte Erreur Système** - Erreurs critiques du système

### Caractéristiques:
✅ **100% Gratuit** (utilise Gmail SMTP)  
✅ **Sans dépendance externe** (Python smtplib intégré)  
✅ **Asynchrone** (n'affecte pas les performances)  
✅ **Configurable** (seuils, fréquence, destinataires)  
✅ **Cooldown** (évite le spam d'alertes)  

---

## Configuration Gmail Rapide

### Étape 1: Activer la Vérification en Deux Étapes

1. Aller à [myaccount.google.com](https://myaccount.google.com)
2. Cliquer sur **Sécurité** (menu gauche)
3. Chercher **Vérification en deux étapes**
4. Cliquer **Activer**
5. Suivre les instructions (téléphone requis)

### Étape 2: Générer un Mot de Passe d'Application

1. Retourner sur [myaccount.google.com/security](https://myaccount.google.com/security)
2. Aller à **Mots de passe des applications** (appear après 2FA activé)
3. Sélectionner:
   - **Application:** Mail
   - **Appareil:** Windows PC (ou autre)
4. Google génère un mot de passe de **16 caractères**
5. **COPIER** ce mot de passe - vous ne le verrez qu'une fois!

### Étape 3: Configurer le Fichier .env

```bash
# Variables d'alerte
ALERT_EMAIL_ENABLED=True
ALERT_EMAIL_FROM=your.email@gmail.com
ALERT_EMAIL_PASSWORD=xxxx xxxx xxxx xxxx   # Les 16 caractères de Google
ALERT_EMAIL_RECIPIENTS=admin@example.com,manager@example.com

# Configuration SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Seuils de détection
MIN_DETECTIONS_PER_MINUTE=1
NO_DETECTION_THRESHOLD_SECONDS=300   # 5 minutes
ALERT_COOLDOWN_SECONDS=600           # 10 minutes entre les alertes
```

### Étape 4: Tester le Système

Accéder au dashboard: **http://localhost:5000/api/alerts/dashboard**

Cliquer sur **"Envoyer Email de Test"**

Attendre 5 secondes - un email doit arriver!

---

## Configuration Avancée

### Variables d'Environnement Complètes

```ini
# === EMAIL CONFIGURATION ===
ALERT_EMAIL_ENABLED=True                    # Activer/désactiver les alertes

# Gmail Account (IMPORTANT: mot de passe d'application, pas votre mot de passe)
ALERT_EMAIL_FROM=your.email@gmail.com
ALERT_EMAIL_PASSWORD=abcd efgh ijkl mnop   # 16 caractères de Google App Passwords

# Destinataires (comma-separated pour plusieurs)
ALERT_EMAIL_RECIPIENTS=admin@company.com,manager@company.com,safety@company.com

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True

# === DETECTION THRESHOLDS ===
MIN_DETECTIONS_PER_MINUTE=1                # Minimum 1 détection/minute
NO_DETECTION_THRESHOLD_SECONDS=300         # Alerter après 5 minutes sans détection

# === ALERT MANAGEMENT ===
ALERT_COOLDOWN_SECONDS=600                 # Ne pas spammer (1 alerte/10 min max)
ALERT_HTML_FORMAT=True                     # Email en HTML (plus beau)

# === EPI TYPES ===
EPI_TYPES=helmet,vest,glasses,boots        # Types d'EPI à monitorer
```

### Configuration par Domaine Email

#### Gmail (Recommandé - Gratuit)
```ini
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
ALERT_EMAIL_PASSWORD=App_Password_From_Google  # 16 chars
```

#### Outlook/Hotmail
```ini
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USE_TLS=True
ALERT_EMAIL_PASSWORD=Your_Account_Password
```

#### Office 365
```ini
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USE_TLS=True
ALERT_EMAIL_PASSWORD=Your_Account_Password
```

#### Custom SMTP Server
```ini
SMTP_SERVER=mail.company.com
SMTP_PORT=587  # ou 25 ou 465
SMTP_USE_TLS=True
ALERT_EMAIL_PASSWORD=Your_Password
```

---

## API des Alertes

### Base URL
```
http://localhost:5000/api/alerts
```

### 1. GET /config - Configuration Actuelle
```bash
curl http://localhost:5000/api/alerts/config
```

**Réponse:**
```json
{
  "enabled": true,
  "configured": true,
  "sender_email": "your.email[at]gmail.com",
  "recipients_count": 2,
  "no_detection_threshold_seconds": 300,
  "min_detections_per_minute": 1,
  "alert_cooldown_seconds": 600
}
```

### 2. GET /status - Statut Complet du Système
```bash
curl http://localhost:5000/api/alerts/status
```

**Réponse:**
```json
{
  "system_status": "operational",
  "last_detection": "2024-01-15T10:30:45Z",
  "total_detections_today": 245,
  "average_detection_rate": "2.4 per minute",
  "configuration": {
    "configured": true,
    "smtp_connection": "✓ Connected"
  },
  "recent_alerts": [
    {
      "type": "missing_epi",
      "timestamp": "2024-01-15T10:25:10Z",
      "epi_type": "helmet"
    }
  ]
}
```

### 3. POST /test - Envoyer Email de Test
```bash
curl -X POST http://localhost:5000/api/alerts/test
```

**Réponse réussie:**
```json
{
  "success": true,
  "message": "Test email sent successfully",
  "recipients": ["admin@company.com", "manager@company.com"]
}
```

**Réponse avec erreur:**
```json
{
  "success": false,
  "message": "SMTP connection failed: 535 5.7.8 Username and password not accepted"
}
```

### 4. POST /missing-epi - Alerte EPI Manquant
```bash
curl -X POST http://localhost:5000/api/alerts/missing-epi \
  -H "Content-Type: application/json" \
  -d '{
    "epi_type": "helmet",
    "duration_seconds": 300,
    "camera_id": "camera_1"
  }'
```

**Réponse:**
```json
{
  "success": true,
  "message": "Missing EPI alert sent",
  "epi_type": "helmet",
  "alert_sent_to": 2
}
```

### 5. POST /low-detection - Alerte Taux Bas
```bash
curl -X POST http://localhost:5000/api/alerts/low-detection \
  -H "Content-Type: application/json" \
  -d '{
    "detection_count": 2,
    "time_window_minutes": 10,
    "threshold": 1
  }'
```

**Réponse:**
```json
{
  "success": true,
  "message": "Low detection rate alert sent",
  "detection_count": 2,
  "time_window_minutes": 10
}
```

### 6. POST /error - Alerte Erreur Système
```bash
curl -X POST http://localhost:5000/api/alerts/error \
  -H "Content-Type: application/json" \
  -d '{
    "error_type": "DatabaseError",
    "error_message": "Connection to database failed",
    "severity": "critical"
  }'
```

**Réponse:**
```json
{
  "success": true,
  "message": "System error alert sent",
  "error_type": "DatabaseError",
  "alert_sent_to": 2
}
```

---

## Troubleshooting

### ❌ "Nom d'utilisateur ou mot de passe incorrect"

**Cause:** Vous utilisez le mauvais mot de passe

**Solutions:**
1. ✅ Utiliser le mot de passe d'**application Google** (16 chars), PAS votre mot de passe Google
2. ✅ Vérifier que 2FA est activé sur le compte Gmail
3. ✅ Régénérer un nouveau mot de passe d'application

### ❌ "SMTP connection timeout"

**Cause:** Serveur SMTP non accessible

**Solutions:**
1. ✅ Vérifier que SMTP_SERVER=smtp.gmail.com est correct
2. ✅ Vérifier que SMTP_PORT=587 (TLS) pas 465 (SSL)
3. ✅ Vérifier la connexion internet
4. ✅ Tester avec `telnet smtp.gmail.com 587`

### ❌ "Unexpected end-of-data"

**Cause:** Mot de passe avec espaces non échappés

**Solutions:**
```bash
# ❌ WRONG
ALERT_EMAIL_PASSWORD=abcd efgh ijkl mnop

# ✅ CORRECT
ALERT_EMAIL_PASSWORD="abcd efgh ijkl mnop"
```

### ❌ "No recipient addresses"

**Cause:** Pas de destinataire configuré

**Solutions:**
```bash
# Au minimum un destinataire
ALERT_EMAIL_RECIPIENTS=admin@company.com

# Ou plusieurs
ALERT_EMAIL_RECIPIENTS=admin@company.com,manager@company.com
```

### ❌ Email n'arrive pas

**Checklist:**
1. ✅ Vérifier spam/junk folder
2. ✅ S'assurer que l'email n'est pas bloqué par firewall
3. ✅ Tester avec `/api/alerts/test`
4. ✅ Vérifier les logs: `docker logs epi_detection`
5. ✅ Vérifier permissions de sécurité Gmail

---

## Exemples d'Intégration

### Intégration dans le Pipeline de Détection

```python
from app.alert_manager import alert_manager

def process_frame(frame):
    """Traitement avec alertes"""
    detections = detector.detect(frame)
    
    # Alerte si pas de détection
    if len(detections) == 0:
        alert_manager.alert_missing_epi(
            epi_type='helmet',
            duration_seconds=300
        )
    
    # Alerte si peu de détections
    if len(detections) < 1:
        alert_manager.alert_low_detection_rate(
            detection_count=len(detections),
            time_window_minutes=10
        )
    
    return detections
```

### Intégration avec Vérifications Périodiques

```python
import threading
from datetime import datetime, timedelta
from app.alert_manager import alert_manager

def monitor_detection_rate():
    """Thread de monitoring"""
    while True:
        try:
            # Checker les détections de la dernière heure
            last_hour = datetime.now() - timedelta(hours=1)
            detections = Detection.query.filter(
                Detection.timestamp > last_hour
            ).all()
            
            if len(detections) < 60:  # Moins de 1 par minute
                alert_manager.alert_low_detection_rate(
                    detection_count=len(detections),
                    time_window_minutes=60,
                    threshold=60
                )
        
        except Exception as e:
            alert_manager.alert_system_error(
                error_type=type(e).__name__,
                error_message=str(e),
                severity='error'
            )
        
        # Checker chaque 15 minutes
        time.sleep(900)

# Démarrer le thread
monitor_thread = threading.Thread(
    target=monitor_detection_rate,
    daemon=True
)
monitor_thread.start()
```

### Intégration avec Détection d'Événements

```python
from app.alert_manager import alert_manager
from app.detection import EPIDetector

detector = EPIDetector(model_path='models/best.pt')

def detect_epi_compliance(frame):
    """Détecter la conformité EPI"""
    
    results = detector.detect(frame)
    required_epi = ['helmet', 'vest', 'glasses', 'boots']
    
    detected_epi = set()
    for detection in results:
        detected_epi.add(detection.epi_type)
    
    # Alerter pour chaque EPI manquant
    for epi in required_epi:
        if epi not in detected_epi:
            alert_manager.alert_missing_epi(
                epi_type=epi,
                duration_seconds=300,  # 5 min sans cet EPI
                location='Production Floor',
                severity='critical'
            )
    
    return detected_epi
```

---

## Dashboard des Alertes

Accéder à: **http://localhost:5000/api/alerts/dashboard**

Features du dashboard:
- 📊 État système en temps réel
- ⚙️ Configuration actuelles
- 🧪 Test d'email
- 🚨 Déclenchement manuel d'alertes
- 📖 Instructions intégrées
- 📈 Statistiques d'utilisation

---

## Support & Ressources

### Documentation officielle
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Python smtplib docs](https://docs.python.org/3/library/smtplib.html)

### Tests rapides

**Vérifier la configuration:**
```bash
curl http://localhost:5000/api/alerts/config
```

**Envoyer un test:**
```bash
curl -X POST http://localhost:5000/api/alerts/test
```

**Vérifier l'état du système:**
```bash
curl http://localhost:5000/api/alerts/status
```

---

## Prochaines Étapes

Une fois configuré:

1. **Déployer en production** - Ajouter les variables .env au serveur
2. **Monitorer les alertes** - Consulter le dashboard régulièrement
3. **Ajuster les seuils** - Selon vos besoins operationnels
4. **Intégrer des canaux supplémentaires** - SMS, Slack, Teams (optionnel)
5. **Auditer les logs** - Vérifier que tout fonctionne correctement

---

**Version:** 1.0  
**Dernière mise à jour:** Janvier 2024  
**Auteur:** EPI Detection System Team
