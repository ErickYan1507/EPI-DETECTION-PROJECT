# 🔔 System de Notifications - Documentation

## Vue d'ensemble

Le système de notifications a été complètement restructuré pour supporter:
- ✅ **Notifications manuelles** - Envoi ad-hoc via formulaire
- ✅ **Rapports automatiques** - Quotidien, hebdomadaire, mensuel
- ✅ **Configuration graphique** - Tout configurable via l'interface web
- ✅ **Historique complet** - Suivi de tous les envois
- ✅ **Dashboard** - État des configurations en temps réel

## Architecture

### Fichiers créés/modifiés

```
app/
├── notification_service.py          # Service métier pour les notifications
├── routes_notification_api.py       # Endpoints API REST
└── main.py                          # (modifié: ajout import et enregistrement blueprint)

templates/
└── notifications.html               # (modifié: refonte complète de l'interface)
```

## Endpoints API

Tous les endpoints utilisent le préfixe: `/api/notifications`

### Configuration

#### GET /api/notifications/config
Récupérer la configuration actuelle

**Réponse:**
```json
{
  "success": true,
  "config": {
    "sender_email": "votre.email@gmail.com",
    "sender_password": "****",
    "daily_enabled": true,
    "daily_hour": 8,
    "weekly_enabled": false,
    "weekly_day": 0,
    "weekly_hour": 9,
    "monthly_enabled": false,
    "monthly_day": 1,
    "monthly_hour": 9
  }
}
```

#### POST /api/notifications/config
Sauvegarder la configuration de l'expéditeur

**Données:**
```json
{
  "sender_email": "your.email@gmail.com",
  "sender_password": "your_password"
}
```

### Destinataires

#### GET /api/notifications/recipients
Récupérer tous les destinataires configurés

**Réponse:**
```json
{
  "success": true,
  "recipients": ["admin@company.com", "manager@company.com"]
}
```

#### POST /api/notifications/recipients
Ajouter un destinataire

**Données:**
```json
{
  "email": "newadmin@company.com"
}
```

#### DELETE /api/notifications/recipients
Supprimer un destinataire

**Données:**
```json
{
  "email": "admin@company.com"
}
```

### Test de connexion

#### POST /api/notifications/test-connection
Tester la connexion SMTP

**Réponse:**
```json
{
  "success": true,
  "message": "Connection successful"
}
```

### Notifications manuelles

#### POST /api/notifications/send-manual
Envoyer une notification manuelle

**Données:**
```json
{
  "subject": "Alerte Conformité EPI",
  "message": "Message détaillé ici\nAvec plusieurs lignes",
  "recipient": "admin@company.com"
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Notification envoyée à admin@company.com"
}
```

### Configuration des rapports

#### POST /api/notifications/reports-config
Sauvegarder la configuration des rapports programmés

**Données:**
```json
{
  "daily_enabled": true,
  "daily_hour": 8,
  "weekly_enabled": true,
  "weekly_day": 0,
  "weekly_hour": 9,
  "monthly_enabled": true,
  "monthly_day": 1,
  "monthly_hour": 9
}
```

### Envoi de rapports

#### POST /api/notifications/send-report
Envoyer un rapport immédiatement

**Données:**
```json
{
  "type": "daily"  // or "weekly" or "monthly"
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Report sent to 3 recipient(s)",
  "sent_count": 3,
  "total_count": 3
}
```

### Historique

#### GET /api/notifications/history
Récupérer l'historique des notifications

**Paramètres:**
- `limit` (optionnel): nombre max d'entrées (défaut: 100)

**Réponse:**
```json
{
  "success": true,
  "history": [
    {
      "timestamp": "17/02/2026 14:32:45",
      "type": "manual",
      "recipient": "admin@company.com",
      "subject": "Alerte Conformité",
      "status": "success",
      "details": "OK"
    },
    {
      "timestamp": "17/02/2026 10:00:00",
      "type": "daily",
      "recipient": "manager@company.com",
      "subject": "Rapport Quotidien",
      "status": "success",
      "details": "OK"
    }
  ],
  "count": 2
}
```

## Utilisation de l'interface web

### 1. Configuration de l'expéditeur
1. Accédez à `/notifications`
2. Section "Configuration Email - Expéditeur"
3. Entrez votre email (Gmail recommandé)
4. Entrez votre clé API ou mot de passe d'application
5. Cliquez "Sauvegarder Configuration Expéditeur"
6. Cliquez "Tester Connexion" pour valider

### 2. Ajouter des destinataires
1. Section "Gestion des Destinataires"
2. Entrez une adresse email
3. Cliquez "Ajouter"
4. Répétez pour ajouter d'autres destinataires

### 3. Envoyer une notification manuelle
1. Section "Envoi Manuel de Notifications"
2. Remplissez les champs:
   - **Objet**: Titre de la notification
   - **Message**: Contenu (supports multi-ligne)
   - **Envoyer à**: Sélectionnez le destinataire
3. Cliquez "Envoyer Immédiatement"

### 4. Configurer les rapports automatiques
1. Section "Configuration des Rapports Automatiques"
2. Pour chaque rapport (Quotidien/Hebdomadaire/Mensuel):
   - **Activer**: Cliquez le toggle ON/OFF
   - **Heure d'envoi**: Entrez l'heure (0-23)
   - Pour hebdo: Sélectionnez le jour
   - Pour mensuel: Sélectionnez le jour du mois
3. Cliquez "Sauvegarder Configuration des Rapports"

### 5. Consulter l'historique
La section "Historique des Notifications" affiche:
- Date/heure d'envoi
- Type (manuel, daily, weekly, monthly)
- Destinataire
- Statut (✅ Envoyé, ⏳ En attente, ❌ Erreur)
- Détails

## Configuration Gmail

Pour utiliser Gmail comme expéditeur:

1. **Activer l'authentification à 2 facteurs** sur votre compte Gmail
2. **Créer une clé d'application**:
   - Accédez à: https://myaccount.google.com/apppasswords
   - Sélectionnez "Mail" et "Windows"
   - Copiez le mot de passe généré (16 caractères)
3. **Utiliser cette clé** comme mot de passe dans EPI Detection

## Stockage des données

Les configurations et données sont stockées dans:
- `.notification_config.json` - Configuration générale
- `.notification_recipients` - Liste des destinataires
- `.notifications_db.json` - Historique des notifications

## Rapports générés

### Rapport Quotidien
- Nombre total de détections
- Taux de conformité moyen
- Nombre d'alertes
- Nombre de présences

### Rapport Hebdomadaire
- Total des détections sur 7 jours
- Conformité moyenne de la semaine

### Rapport Mensuel
- Total des détections du mois
- Conformité moyenne du mois

## Prochaines étapes (optionnel)

### Planification automatique (APScheduler)
Pour activer l'envoi automatique aux horaires configurés:

```python
# Dans app/main.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.notification_service import notification_service

scheduler = BackgroundScheduler()

def schedule_reports():
    config = notification_service.get_config()
    
    # Rapport quotidien
    if config.get('daily_enabled'):
        hour = config.get('daily_hour', 8)
        scheduler.add_job(
            notification_service.send_report,
            'cron',
            hour=hour,
            minute=0,
            args=['daily'],
            id='daily_report'
        )
    
    # Rapport hebdomadaire
    if config.get('weekly_enabled'):
        day = config.get('weekly_day', 0)
        hour = config.get('weekly_hour', 9)
        scheduler.add_job(
            notification_service.send_report,
            'cron',
            day_of_week=day,
            hour=hour,
            minute=0,
            args=['weekly'],
            id='weekly_report'
        )
    
    # Rapport mensuel
    if config.get('monthly_enabled'):
        day = config.get('monthly_day', 1)
        hour = config.get('monthly_hour', 9)
        scheduler.add_job(
            notification_service.send_report,
            'cron',
            day=day,
            hour=hour,
            minute=0,
            args=['monthly'],
            id='monthly_report'
        )
    
    scheduler.start()

# À l'initialisation de l'app
schedule_reports()
```

## Dépannage

### "Email expéditeur ou mot de passe manquant"
- Vérifiez que vous avez sauvegardé la configuration
- Assurez-vous que l'email est valide

### "Erreur de connexion"
- Réduisez les accès d'application à Gmail dans les paramètres de sécurité
- Utilisez une clé d'application au lieu du mot de passe Gmail

### "Destinataire non trouvé"
- Vérifiez le format de l'email
- Assurez-vous que le destinataire est ajouté

### Les rapports ne sont pas envoyés aux horaires
- La planification automatique nécessite APScheduler
- Pour le moment, utilisez "Envoyer Maintenant" pour tester

## Notes techniques

- Les emails sont envoyés via SMTP (port 587)
- Support HTML complet pour les rapports
- Historique limité aux 500 dernières notifications
- Tous les fichiers sont UTF-8 encodées

