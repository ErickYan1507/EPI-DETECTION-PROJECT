# 🚀 Guide de Démarrage Rapide - Système de Notifications

## Résumé des modifications

Le système de notifications a été complètement refondu avec les changements suivants:

### ✅ Fichiers créés:
- `app/notification_service.py` - Logique métier
- `app/routes_notification_api.py` - Endpoints API
- `templates/notifications.html` - Interface refactorisée
- `NOTIFICATION_SYSTEM.md` - Documentation complète
- `test_notification_system.py` - Tests unitaires
- `examples_notifications_api.py` - Exemples d'utilisation

### ✅ Fichiers modifiés:
- `app/main.py` - Ajout import et enregistrement du blueprint

## Démarrage rapide

### 1. Installation des dépendances

```bash
pip install python-dotenv smtplib
```

### 2. Configuration initiale

#### Option A: Via l'interface web (RECOMMANDÉ)

1. Démarrez l'application Flask
2. Accédez à `http://localhost:5000/notifications`
3. Section "Configuration Email - Expéditeur":
   - Email: `votre.email@gmail.com`
   - Mot de passe: Votre clé d'application Gmail
4. Cliquez "Sauvegarder Configuration Expéditeur"

#### Option B: Via fichier .env (optionnel)

Créez `.env.notifications`:
```
NOTIFICATIONS_SENDER_EMAIL=your.email@gmail.com
NOTIFICATIONS_SENDER_PASSWORD=your_password
```

### 3. Ajouter des destinataires

Interface web - Section "Gestion des Destinataires":
1. Entrez l'email
2. Cliquez "Ajouter"
3. Répétez pour chaque destinataire

### 4. Tester la connexion

1. Section "Configuration Email - Expéditeur"
2. Cliquez "Tester Connexion"
3. Vous devriez voir ✅ Connexion réussie!

### 5. Envoyer une première notification

1. Section "Envoi Manuel de Notifications"
2. Objet: "Test 123"
3. Message: "Ceci est un test"
4. Destinataire: Sélectionnez un email
5. Cliquez "Envoyer Immédiatement"

### 6. Configurer les rapports

1. Section "Configuration des Rapports Automatiques"
2. Pour "Rapport Quotidien":
   - Cliquez toggle pour activer (ON)
   - Heure: 8 (pour 8h du matin)
3. Cliquez "Sauvegarder Configuration des Rapports"

## Tests API avec cURL

### Tester la configuration

```bash
curl http://localhost:5000/api/notifications/config
```

### Ajouter un destinataire

```bash
curl -X POST http://localhost:5000/api/notifications/recipients \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com"}'
```

### Envoyer une notification manuelle

```bash
curl -X POST http://localhost:5000/api/notifications/send-manual \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Alerte Test",
    "message": "Ceci est un message de test",
    "recipient": "admin@company.com"
  }'
```

### Envoyer un rapport

```bash
curl -X POST http://localhost:5000/api/notifications/send-report \
  -H "Content-Type: application/json" \
  -d '{"type": "daily"}'
```

### Voir l'historique

```bash
curl http://localhost:5000/api/notifications/history?limit=20
```

## Tests Python

### Test simple

```bash
python examples_notifications_api.py --quick
```

### Test complet

```bash
python examples_notifications_api.py
```

### Tests unitaires

```bash
python -m pytest test_notification_system.py -v
```

## Architecture

```
Frontend (HTML/JS)
       ↓
   API Routes
   /api/notifications/*
       ↓
NotificationService
(logic métier)
       ↓
    SMTP/Email
    Database
    Fichiers JSON
```

## Structure des données

### Configuration (.notification_config.json)
```json
{
  "sender_email": "votre.email@gmail.com",
  "sender_password": "****",
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

### Destinataires (.notification_recipients)
```
admin@company.com
manager@company.com
supervisor@company.com
```

### Historique (.notifications_db.json)
```json
[
  {
    "timestamp": "17/02/2026 14:32:45",
    "type": "manual",
    "recipient": "admin@company.com",
    "subject": "Alerte Conformité",
    "status": "success",
    "details": "OK"
  }
]
```

## Coniguration Gmail

### Étapes importantes:

1. **Activer l'authentification 2FA**:
   - Google Account → Security
   - Enable 2-Step Verification

2. **Créer une clé d'application**:
   - Google Account → App passwords
   - Select "Mail" and "Windows"
   - Copy the 16-character password

3. **Utiliser dans EPI Detection**:
   - Email: votre.email@gmail.com
   - Password: votre_cle_app_16_caracteres

## Dépannage

### "Connexion échouée"
```bash
✓ Vérifiez que l'email est valide
✓ Vérifiez que la clé d'application est correcte
✓ Vérifiez la connectivité internet
✓ Vérifiez le pare-feu (port 587)
```

### "Destinataire non trouvé"
```bash
✓ Vérifiez le format de l'email (doit contenir @)
✓ Listez les destinataires: GET /api/notifications/recipients
```

### "Aucun rapport envoyé"
```bash
✓ Vérifiez que les destinataires sont configurés
✓ Vérifiez la configuration (toggle doit être ON)
✓ Vérifiez que l'heure est correcte (format: 0-23)
```

### "Service non disponible"
```bash
✓ Vérifiez que l'app Flask est en cours d'exécution
✓ Vérifiez que le port 5000 est accessible
✓ Vérifiez les erreurs dans le terminal Flask
```

## Prochaines étapes

### À faire:
- [x] Interface de gestion manuelle
- [x] API REST complète
- [x] Stockage des historiques
- [x] Support des rapports HTML
- [ ] Planification automatique (APScheduler)
- [ ] Dashboard en temps réel
- [ ] Support SMS/Slack/Teams
- [ ] Modèles d'emails personnalisés

### Pour activer la planification automatique:

1. Installez APScheduler:
```bash
pip install APScheduler
```

2. Décommentez dans `app/main.py`:
```python
from app.report_scheduler import setup_scheduler
setup_scheduler(app)
```

3. Créez `app/report_scheduler.py` (à développer)

## Support

Pour plus d'aide:
- Consultez `NOTIFICATION_SYSTEM.md` pour la doc complète
- Consultez `examples_notifications_api.py` pour les exemples
- Exécutez `test_notification_system.py` pour vérifier

## Checklist de configuration

- [ ] Application Flask démarrée
- [ ] Navigué vers `/notifications`
- [ ] Configuré l'email expéditeur
- [ ] Testé la connexion (✅ réussi)
- [ ] Ajouté au moins un destinataire
- [ ] Testé l'envoi manuel
- [ ] Configuré les rapports (si désiré)
- [ ] Consultez l'historique des notifications

---

**C'est terminé! Votre système de notifications est opérationnel.** 🎉

