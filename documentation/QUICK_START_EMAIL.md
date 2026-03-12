# 📧 Configuration Email - Guide de Démarrage Rapide

## ✅ Status d'Intégration

L'interface web graphique pour la configuration email est maintenant **COMPLÈTEMENT INTÉGRÉE** dans votre application Flask!

### Quelle a changé ?

1. ✅ **Routes email enregistrées** dans `app/main.py`
   - Blueprint `email_bp` importé et activé
   - 8 endpoints API REST disponibles

2. ✅ **Interface web redessinée** dans `templates/notifications.html`
   - 5 sections principales: Configuration, Destinataires, Planification, Actions, Statut
   - Interface moderne avec statut en temps réel
   - Boutons pour tester et envoyer manuellement

3. ✅ **Packages Python installés**
   - python-dotenv ✅
   - APScheduler ✅
   - flask-sqlalchemy ✅

4. ⏳ **À faire par l'utilisateur**
   - Remplir `.env.email` avec vos identifiants Gmail
   - Tester la connexion SMTP via l'interface

---

## 🚀 Comment Démarrer (3 étapes)

### Étape 1: Préparer votre compte Gmail
Avant de configurer, vous avez besoin d'un **mot de passe d'application Gmail**:

1. Allez sur: https://myaccount.google.com/apppasswords
2. Sélectionnez "Mail" et "Windows Computer" (ou votre appareil)
3. Copiez le mot de passe généré (16 caractères)
4. Gardez ce mot de passe à côté (vous le pasterez dans l'interface)

### Étape 2: Lancer le serveur

```bash
# Ouvrir un terminal PowerShell dans le dossier du projet
cd d:\projet\EPI-DETECTION-PROJECT

# Lancer le serveur
python run.py --mode run
```

Vous verrez:
```
========================================
SYSTÈME DE DÉTECTION EPI - DASHBOARD
========================================
Serveur démarré sur: http://0.0.0.0:5000
Dashboard: http://127.0.0.1:5000/dashboard
API: http://127.0.0.1:5000/api/detect
📧 Initialisation du scheduler de rapports...
========================================
```

### Étape 3: Configurer via l'Interface Web

1. **Ouvrez votre navigateur** et allez à:
   ```
   http://127.0.0.1:5000/notifications
   ```

2. **Vous verrez 5 sections:**

   **📧 CONFIGURATION SMTP**
   - Email: `votremail@gmail.com`
   - Mot de passe: Le mot de passe d'application que vous avez copié
   - Serveur: `smtp.gmail.com` (pré-rempli)
   - Port: `587` (pré-rempli)
   
   Cliquez sur **"Test de connexion SMTP"** pour vérifier

   **👥 RECIPIENTS**
   - Ajoutez les emails qui recevront les rapports
   - Cliquez "Ajouter Destinataire"

   **📅 PLANIFICATION DES RAPPORTS**
   - Rapport Daily: À quelle heure chaque jour?
   - Rapport Weekly: Quel jour et à quelle heure?
   - Rapport Monthly: Quel jour du mois et à quelle heure?
   - Seuil d'alerte: Alerter si conformité < X%?

   **⚡ ACTIONS RAPIDES**
   - "Envoyer Rapport Daily Maintenant"
   - "Envoyer Rapport Weekly Maintenant"
   - "Envoyer Rapport Monthly Maintenant"

   **💓 STATUT SYSTÈME**
   - Vérifie la configuration SMTP ✅/❌
   - Connexion active ✅/❌
   - Nombre de destinataires
   - Scheduler en cours d'exécution ✅/❌

---

## 🔧 Endpoints API Disponibles

Si vous voulez utiliser directement l'API (sans l'interface):

### Configuration SMTP
```bash
# GET: Récupérer la configuration
curl http://127.0.0.1:5000/api/email/config

# POST: Sauvegarder la configuration
curl -X POST http://127.0.0.1:5000/api/email/config \
  -H "Content-Type: application/json" \
  -d '{
    "SENDER_EMAIL": "votremail@gmail.com",
    "SENDER_PASSWORD": "votre_mot_de_passe_app",
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": 587
  }'

# POST: Tester la connexion
curl -X POST http://127.0.0.1:5000/api/email/test-connection

# POST: Envoyer un email de test
curl -X POST http://127.0.0.1:5000/api/email/send-test \
  -H "Content-Type: application/json" \
  -d '{"recipient": "destinataire@example.com"}'
```

### Gestion des Destinataires
```bash
# GET: Lister les destinataires
curl http://127.0.0.1:5000/api/email/recipients

# POST: Ajouter un destinataire
curl -X POST http://127.0.0.1:5000/api/email/recipients \
  -H "Content-Type: application/json" \
  -d '{"email": "nouveau@example.com"}'

# DELETE: Supprimer un destinataire
curl -X DELETE "http://127.0.0.1:5000/api/email/recipients?email=ancien@example.com"
```

### Planification et Envoi
```bash
# POST: Sauvegarder la planification
curl -X POST http://127.0.0.1:5000/api/email/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "DAILY_REPORT_HOUR": 8,
    "WEEKLY_REPORT_DAY": "monday",
    "WEEKLY_REPORT_HOUR": 9,
    "MONTHLY_REPORT_DAY": 1,
    "MONTHLY_REPORT_HOUR": 10,
    "SEND_ALERTS_ENABLED": true,
    "ALERT_THRESHOLD": 80
  }'

# POST: Envoyer un rapport manuellement
curl -X POST http://127.0.0.1:5000/api/email/send-report \
  -H "Content-Type: application/json" \
  -d '{"report_type": "daily"}'
```

### Statut Système
```bash
# GET: Vérifier l'état du système
curl http://127.0.0.1:5000/api/email/status

# GET: Lister les jobs du scheduler
curl http://127.0.0.1:5000/api/email/scheduler-status
```

---

## 📋 Structure des Fichiers Créés

```
.env.email                          # Configuration email (à remplir)
.email_recipients                   # Destinataires (créé automatiquement)
app/
  ├── main.py                       # ✅ Intégration blueprint (modifié)
  ├── routes_email_config.py        # ✅ 8 endpoints API (créé)
  ├── email_notifications.py        # ✅ Logique d'envoi SMTP (créé)
  └── report_scheduler.py           # ✅ Scheduler APScheduler (créé)
templates/
  └── notifications.html            # ✅ Interface web (redessinée)
run.py                              # ✅ Scheduler init (modifié)
config.py                           # ✅ Charges .env.email (modifié)
verify_email_integration.py         # Vérification d'intégration
```

---

## 🆘 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier la configuration
python verify_email_integration.py

# Vérifier les imports
python -c "import dotenv; import apscheduler; import flask_sqlalchemy; print('OK')"
```

### "Cannot connect to SMTP server"
- Vérifiez que l'email et le mot de passe sont corrects
- Gmail nécessite un **mot de passe d'application**, pas votre mot de passe Gmail normal
- Vérifiez que votre pare-feu permet les connexions à smtp.gmail.com:587

### Les emails ne s'envoient pas
- Vérifiez que des destinataires sont configurés
- Cliquez d'abord sur "Test de connexion SMTP"
- Envoyez un email de test via le bouton
- Regardez les logs du serveur pour les erreurs

### Accès à /notifications donne 404
- Vérifiez que le serveur est bien lancé avec `python run.py --mode run`
- L'adresse correcte est `http://127.0.0.1:5000/notifications` (pas `http://0.0.0.0`)

---

## 📊 Automatisation (Comment ça marche)

Une fois configuré, voici le flux automatique:

```
1. Scheduler APScheduler démarre avec run.py
   └─> Crée des jobs pour:
        • Reports quotidiens à l'heure configurée
        • Reports hebdomadaires à jour.heure configurés
        • Reports mensuels à jour.heure configurés

2. À l'heure prévue, le job déclenche:
   └─> EmailNotifier.generate_daily_report()
        EmailNotifier.generate_weekly_report()
        EmailNotifier.generate_monthly_report()

3. Rapports générés en HTML avec:
   └─> Statistiques des détections
        Conformité EPI
        Graphiques de performance
        Alertes si seuil dépassé

4. Emails envoyés via SMTP à tous les destinataires
   └─> Via smtp.gmail.com:587 (TLS)
        Avec authentification
        HTML formaté
```

---

## ✨ Fonctionnalités Spéciales

### 1. Envoi Manuel de Rapports
Sans attendre l'heure planifiée, vous pouvez envoyer immédiatement depuis l'interface

### 2. Alertes Conditionnelles
Basées sur le seuil de conformité EPI
```
Si conformité < seuil configuré → Alerte email envoyée
```

### 3. Historique des Destinataires
Les destinataires sont sauvegardés dans `.email_recipients`

### 4. Status en Temps Réel
La table "STATUT SYSTÈME" montre:
- Configuration présente ✅/❌
- Connexion SMTP opérationnelle ✅/❌
- Nombre de destinataires configurés
- Scheduler en exécution ✅/❌

---

## 🎯 Prochaines Étapes (Optionnel)

1. **Intégration avec JIRA** - Exporter les rapports comme issues
2. **Webhook Slack** - Notifications Slack en plus d'email
3. **Stockage des rapports** - Archive PDF des rapports envoyés
4. **Template personnalisé** - Créer vos propres templates HTML

---

**Vous êtes prêt à utiliser le système d'email!** 📧✅

Questions? Consultez les logs dans le terminal de la console du navigateur (F12)
