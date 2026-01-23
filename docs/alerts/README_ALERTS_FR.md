# 📧 Système d'Alertes Email - EPI Detection

## 🎯 Objectif
Envoyer automatiquement des emails en cas de **non-conformité EPI** (équipement manquant, détections insuffisantes, erreurs système).

## ⚡ Démarrage Rapide (5 minutes)

### 1️⃣ Préparer Gmail
- Allez sur https://myaccount.google.com
- Activez **Vérification en 2 étapes** (Sécurité → Vérification en deux étapes)
- Générez un **mot de passe d'application** (Mots de passe des applications)
- Copiez les 16 caractères

### 2️⃣ Configurer .env
```bash
ALERT_EMAIL_ENABLED=True
ALERT_EMAIL_FROM=votre.email@gmail.com
ALERT_EMAIL_PASSWORD=xxxx xxxx xxxx xxxx    # Les 16 caractères
ALERT_EMAIL_RECIPIENTS=admin@example.com
```

### 3️⃣ Tester
```bash
# Lancer l'app
python run_app.py

# Visiter le dashboard
http://localhost:5000/api/alerts/dashboard

# Cliquer "Envoyer Email de Test"
# Vérifier votre inbox Gmail
```

## 🚀 Fonctionnalités

| Alerte | Condition | Exemple |
|--------|-----------|---------|
| **EPI Manquant** | Aucune détection pendant 5 min | Pas de casque détecté |
| **Taux Bas** | < 1 détection/minute | Seulement 2 détections en 10 min |
| **Erreur Système** | Crash ou erreur critique | Perte de connexion DB |

## 📊 Architecture

```
app/
├── alert_manager.py          # Core logic - Gestion des emails
├── routes_alerts.py          # API REST - 6 endpoints
└── main.py                   # Integration - Blueprint register

templates/
└── alert_dashboard.html      # UI - Dashboard web

docs/alerts/
├── email_setup.md           # Guide détaillé
└── CONFIGURATION_ALERTS_FR.md # Documentation complète
```

## 🔌 API Endpoints

### Dashboard Web
```
GET /api/alerts/dashboard
```
Interface web pour gérer les alertes

### Configuration
```
GET /api/alerts/config
```
Récupère la configuration actuelle

### Test Email
```
POST /api/alerts/test
```
Envoie un email de test

### Alerte EPI Manquant
```
POST /api/alerts/missing-epi
{
  "epi_type": "helmet",
  "duration_seconds": 300
}
```

### Alerte Taux Bas
```
POST /api/alerts/low-detection
{
  "detection_count": 2,
  "time_window_minutes": 10
}
```

### Alerte Erreur Système
```
POST /api/alerts/error
{
  "error_type": "DBError",
  "error_message": "Connection failed"
}
```

## 🛠️ Configuration Complète

Voir [CONFIGURATION_ALERTS_FR.md](./CONFIGURATION_ALERTS_FR.md) pour:
- Configuration avancée
- Autres domaines email (Outlook, Office365, custom)
- Troubleshooting complet
- Exemples d'intégration

## 🧪 Tests

```bash
# Envoyer un email de test
curl -X POST http://localhost:5000/api/alerts/test

# Vérifier la configuration
curl http://localhost:5000/api/alerts/config

# Voir le statut système
curl http://localhost:5000/api/alerts/status

# Déclencher une alerte EPI manquant
curl -X POST http://localhost:5000/api/alerts/missing-epi \
  -H "Content-Type: application/json" \
  -d '{"epi_type": "helmet", "duration_seconds": 300}'
```

## ❓ FAQ

**Q: C'est payant?**  
A: Non, 100% gratuit. Utilise le SMTP gratuit de Gmail.

**Q: Combien d'emails par jour?**  
A: Gmail permet 500+ emails/jour pour un compte free.

**Q: Peut-on envoyer à plusieurs personnes?**  
A: Oui, séparez par des virgules: `email1@company.com,email2@company.com`

**Q: Comment désactiver les alertes?**  
A: Mettez `ALERT_EMAIL_ENABLED=False` dans .env

**Q: Quel est le cooldown?**  
A: 10 minutes par défaut (configurable dans .env)

## 📈 Intégration dans la Détection

Exemple pour intégrer automatiquement:

```python
from app.alert_manager import alert_manager

def detect_and_alert(frame):
    detections = model.detect(frame)
    
    # Alerte si pas de casque
    if 'helmet' not in [d.class_name for d in detections]:
        alert_manager.alert_missing_epi(
            epi_type='helmet',
            duration_seconds=300
        )
    
    return detections
```

## 🔒 Sécurité

- ✅ Mot de passe **jamais** sauvegardé en clair
- ✅ Connexion **TLS chiffrée** (port 587)
- ✅ Pas de vraie données sensibles en test
- ✅ Logs automatiques de toutes les tentatives

## 📝 Logs

```bash
# Voir les logs d'alertes
docker logs epi_detection | grep "alert"

# Ou dans le fichier
tail -f logs/app.log
```

## 🎓 Ressources

- 📖 [Guide Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- 📖 [Python smtplib Docs](https://docs.python.org/3/library/smtplib.html)
- 📖 [Documentation Complète](./CONFIGURATION_ALERTS_FR.md)

---

**✅ Prêt à envoyer des alertes email!**

Pour démarrer: [Voir le guide de configuration](./CONFIGURATION_ALERTS_FR.md)
