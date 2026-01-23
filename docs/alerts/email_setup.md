# 📧 Configuration Alertes Email - EPI Detection System

## 🚀 Démarrage Rapide (Gmail gratuit)

### Étape 1: Activer 2FA sur Gmail

1. Aller à https://myaccount.google.com/
2. Cliquer **Sécurité** (gauche)
3. Activer **Vérification en deux étapes**

### Étape 2: Créer App Password

1. Aller à https://myaccount.google.com/apppasswords
2. Sélectionner:
   - **Mail**
   - **Windows (ou autre système)**
3. **Copier** le mot de passe généré (format: `xxxx xxxx xxxx xxxx`)

### Étape 3: Configurer .env

Copier et adapter dans `.env`:

```bash
# ============================================================
# CONFIGURATION ALERTES EMAIL (Gmail gratuit)
# ============================================================

# Activer les alertes
ALERT_EMAIL_ENABLED=True

# Expéditeur (votre email Gmail)
ALERT_EMAIL_FROM=your.email@gmail.com

# Mot de passe d'application Google (16 caractères sans espaces)
ALERT_EMAIL_PASSWORD=xxxxxxxxxxxx

# Destinataires (comma-separated)
ALERT_EMAIL_RECIPIENTS=admin@example.com,manager@example.com,security@example.com

# Serveur SMTP Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# ============================================================
# PARAMÈTRES DES ALERTES
# ============================================================

# Nombre minimum de détections par minute
MIN_DETECTIONS_PER_MINUTE=1

# Seuil: alerte si pas de détection pendant N secondes
NO_DETECTION_THRESHOLD_SECONDS=300

# Cooldown entre alertes similaires (secondes)
ALERT_COOLDOWN_SECONDS=600
```

### Étape 4: Tester

```bash
# Requête de test
curl -X POST http://localhost:5000/api/alerts/test

# Réponse
{
  "success": true,
  "message": "Email de test envoyé"
}
```

---

## 🔧 Configuration Avancée

### Variables d'Environnement Complètes

```bash
# Général
ALERT_EMAIL_ENABLED=True                    # Activer/désactiver
ALERT_EMAIL_FROM=your.email@gmail.com       # Email expéditeur
ALERT_EMAIL_PASSWORD=xxxx xxxx xxxx xxxx    # App password Google
ALERT_EMAIL_RECIPIENTS=email1@.com,email2@.com

# SMTP
SMTP_SERVER=smtp.gmail.com                  # Serveur (gmail)
SMTP_PORT=587                               # Port (587 = TLS)

# Seuils d'alerte
MIN_DETECTIONS_PER_MINUTE=1                 # Min détections/min
NO_DETECTION_THRESHOLD_SECONDS=300          # 5 min sans détection
ALERT_COOLDOWN_SECONDS=600                  # 10 min entre alertes similaires
```

---

## 📧 Types d'Alertes

### 1️⃣ Alerte EPI Manquant

**Quand:** Pas de détection d'un EPI pendant N secondes

**Exemple:**
```json
POST /api/alerts/missing-epi
{
  "epi_type": "helmet",
  "duration_seconds": 300
}
```

**Email reçu:**
```
Objet: 🚨 ALERTE EPI - HELMET NON DÉTECTÉ

Type EPI manquant: HELMET
Durée sans détection: 300 secondes
...
```

---

### 2️⃣ Alerte Taux de Détection Faible

**Quand:** Moins de détections que le minimum configuré

**Exemple:**
```json
POST /api/alerts/low-detection
{
  "detection_count": 2,
  "time_window_minutes": 10
}
```

**Email reçu:**
```
Objet: ⚠️ ALERTE - Taux de détection faible (2/10)

Détections sur les 10 dernières minutes: 2
Minimum attendu: 10
...
```

---

### 3️⃣ Alerte Erreur Système

**Quand:** Erreur technique détectée

**Exemple:**
```json
POST /api/alerts/error
{
  "error_type": "WebcamError",
  "error_message": "Camera not found"
}
```

**Email reçu:**
```
Objet: 🔴 ERREUR SYSTÈME - WebcamError

Type d'erreur: WebcamError
Message: Camera not found
...
```

---

## 🌐 API Endpoints

### GET /api/alerts/config
Récupère la configuration

**Response:**
```json
{
  "enabled": true,
  "configured": true,
  "recipients": ["admin@example.com"],
  "sender_email": "your.email[at]gmail.com",
  "no_detection_threshold_seconds": 300,
  "min_detections_per_minute": 1,
  "alert_cooldown_seconds": 600
}
```

---

### GET /api/alerts/status
État du système

**Response:**
```json
{
  "status": "operational",
  "configuration": {
    "enabled": true,
    "configured": true,
    "sender_email": "your.email[at]gmail.com",
    "recipients": ["admin@example.com"],
    "recipients_count": 1,
    "smtp_connection": "OK"
  },
  "timestamp": "2026-01-09T10:30:45.123456"
}
```

---

### POST /api/alerts/test
Envoyer email de test

**Response:**
```json
{
  "success": true,
  "message": "Email de test envoyé"
}
```

---

### POST /api/alerts/missing-epi
Alerte EPI manquant

**Body:**
```json
{
  "epi_type": "helmet",
  "duration_seconds": 300
}
```

**Response:**
```json
{
  "success": true,
  "message": "Alerte envoyée pour helmet absent pendant 300s"
}
```

---

### POST /api/alerts/low-detection
Alerte taux faible

**Body:**
```json
{
  "detection_count": 5,
  "time_window_minutes": 10
}
```

---

### POST /api/alerts/error
Alerte erreur

**Body:**
```json
{
  "error_type": "WebcamError",
  "error_message": "Camera connection lost"
}
```

---

## 🔐 Sécurité

### Bonnes Pratiques

✅ **Ne JAMAIS** commiter le mot de passe en clair
```bash
# Mauvais ❌
git add .env
git commit -m "config"

# Bon ✅
echo ".env" >> .gitignore
# Ajouter .env à Git via secret management
```

✅ Utiliser **App Passwords** Google (pas le vrai mot de passe)

✅ Limiter les **destinataires** à la sécurité

✅ Configurer **ALERT_COOLDOWN_SECONDS** pour éviter spam

---

## 🐛 Dépannage

### "SMTP Authentication Error"

**Cause:** Mot de passe incorrect

**Solution:**
1. Vérifier que 2FA est activé sur Gmail
2. Régénérer le mot de passe d'application
3. Copier sans espaces: `xxxxxxxxxxxx`

---

### "Connection refused on SMTP"

**Cause:** Port bloqué

**Solution:**
```bash
# Vérifier firewall
# Port 587 doit être ouvert pour SMTP TLS
```

---

### Les emails ne sont pas reçus

**Checklist:**
- [ ] `.env` contient `ALERT_EMAIL_ENABLED=True`
- [ ] `SMTP_SERVER=smtp.gmail.com` correct
- [ ] `ALERT_EMAIL_FROM` = email Gmail valide
- [ ] `ALERT_EMAIL_PASSWORD` = app password (16 caractères)
- [ ] `ALERT_EMAIL_RECIPIENTS` non vide
- [ ] Tester avec `/api/alerts/test`

---

## 📊 Intégration avec Détection

### Exemple: Déclencher alerte automatiquement

```python
# app/detection.py
from app.alert_manager import alert_manager

def process_detections(self, detections):
    """Traiter détections et déclencher alertes si nécessaire"""
    
    # Vérifier chaque classe
    detected_classes = [d['class'] for d in detections]
    
    for epi_class in ['helmet', 'vest', 'glasses']:
        if epi_class not in detected_classes:
            # Pas d'EPI détecté
            alert_manager.alert_missing_epi(epi_class, duration_seconds=300)
    
    # Vérifier taux de détection
    if len(detections) < 1:
        alert_manager.alert_low_detection_rate(0, time_window_minutes=10)
```

---

## 🎯 Exemples de Script

### Test Complet

```bash
#!/bin/bash
# test_alerts.sh

echo "1. Vérifier config..."
curl http://localhost:5000/api/alerts/config | jq

echo -e "\n2. Tester envoi email..."
curl -X POST http://localhost:5000/api/alerts/test

echo -e "\n3. Voir status..."
curl http://localhost:5000/api/alerts/status | jq

echo -e "\n4. Simuler alerte missing EPI..."
curl -X POST http://localhost:5000/api/alerts/missing-epi \
  -H "Content-Type: application/json" \
  -d '{"epi_type":"helmet","duration_seconds":300}'
```

**Lancer:**
```bash
chmod +x test_alerts.sh
./test_alerts.sh
```

---

## 📝 Notes

- Les alertes sont envoyées **asynchronement** (non-bloquant)
- Les emails ont format **HTML** (beau rendu) + texte plain
- **Cooldown** évite les emails en spam (1 alert max toutes les 10 min)
- Compatible avec n'importe quel domaine email (pas juste Gmail)

---

## 🔗 Ressources

- [Google App Passwords](https://support.google.com/accounts/answer/185833)
- [Gmail SMTP Settings](https://support.google.com/a/answer/176600)
- [Python smtplib Docs](https://docs.python.org/3/library/smtplib.html)

---

**Statut:** ✅ Production Ready  
**Coût:** 💰 GRATUIT (Gmail)  
**Setup Time:** ⏱️ 5 minutes
