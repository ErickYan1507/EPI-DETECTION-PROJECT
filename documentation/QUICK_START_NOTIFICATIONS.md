# 🚀 Guide Démarrage Rapide - Système de Notifications

## Étape 1 : Démarrer l'application Flask

### Option A : Via PowerShell (Windows)
```powershell
cd "d:\projet\EPI-DETECTION-PROJECT"
.venv\Scripts\python run_app.py
```

### Option B : Via Terminal (Linux/Mac)
```bash
cd /path/to/EPI-DETECTION-PROJECT
source .venv/bin/activate
python run_app.py
```

### Option C : Tâche VS Code (Recommandé)
Dans VS Code, appuyez sur `Ctrl+Shift+B` ou allez à Terminal → Lancer une tâche :
- Sélectionnez "Flask Dev Server"

## Étape 2 : Accéder à l'interface

1. Ouvrez votre navigateur
2. Allez à : **http://localhost:5000/notifications**
3. La page devrait se charger avec un design moderne

## Étape 3 : Configuration initiale (2-3 minutes)

### 1. Configurer l'email SMTP

Dans la section **"Configuration Email - Expéditeur"** :

**Exemple avec Gmail :**
- Email : `votre-email@gmail.com`
- Mot de passe : `votre-clé-application` (si 2FA activé)
- Serveur SMTP : `smtp.gmail.com`
- Port : `587`
- Utiliser TLS : ✅ Oui (déjà sélectionné)

**Puis :**
1. Cliquez **"💾 Sauvegarder Configuration"**
2. Cliquez **"✅ Tester Connexion"** pour vérifier

### 2. Ajouter des destinataires

Dans la section **"Gestion des Destinataires"** :
1. Entrez votre email : `test@example.com`
2. Cliquez **"➕ Ajouter"**
3. Répétez pour d'autres emails si souhaité

### 3. Tester l'envoi manuel

Dans la section **"Envoi Manuel de Notifications"** :
1. **Objet** : `Test de notification`
2. **Message** : `Ceci est un email de test`
3. **Destinataire** : Sélectionnez l'email ajouté
4. Cliquez **"⚡ Envoyer Immédiatement"**

Vous devriez recevoir un email dans quelques secondes ✉️

## Étape 4 : Configurer les rapports automatiques

### Rapport Quotidien (Recommandé)
1. Activez le toggle (vert)
2. Choisissez l'heure : `8` (8h du matin)
3. Les emails seront envoyés chaque jour à 8h

### Rapport Hebdomadaire (Optionnel)
1. Activez le toggle
2. Jour : `Lundi` (ou votre choix)
3. Heure : `9` (9h du matin)

### Rapport Mensuel (Optionnel)
1. Activez le toggle
2. Jour : `1` (1er du mois)
3. Heure : `10` (10h du matin)

**Sauvegardez :** Cliquez **"💾 Sauvegarder Configuration Rapports"**

## Étape 5 : Vérifier l'historique

La section **"Historique des Notifications"** en bas de la page affiche :
- ✅ Emails envoyés avec succès
- ❌ Emails en erreur
- ⏳ Emails en attente

L'historique se met à jour automatiquement toutes les 60 secondes.

## 🎨 Utiliser le mode sombre

Cliquez sur le bouton **🌙** en bas à droite pour basculer entre :
- Mode clair (blanc) : Parfait de jour
- Mode sombre (gris foncé) : Parfait la nuit

La préférence est sauvegardée automatiquement.

## 🔧 Configuration avancée

### Changer le serveur SMTP

**Si vous utilisez :**
- **Outlook** : `smtp-mail.outlook.com:587`
- **Yahoo** : `smtp.mail.yahoo.com:587`
- **SendGrid** : `smtp.sendgrid.net:587`
- **Custom** : Mettez vos paramètres

### Utiliser MySQL à la place de SQLite

Modifiez `app/routes_notifications_api.py` :
```python
notif_manager = NotificationsManager(db_type='mysql')
```

## 📱 API REST pour intégration tierce

Vous pouvez intégrer le système de notifications dans d'autres applications.

**Exemple : Envoyer une notification depuis un script Python**

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:5000/api/notifications"

# 1. Ajouter un destinataire
requests.post(
    f"{BASE_URL}/recipients",
    json={"email": "alert@example.com"},
    headers={"Content-Type": "application/json"}
)

# 2. Envoyer une notification
requests.post(
    f"{BASE_URL}/send-manual",
    json={
        "subject": "Alerte Détection",
        "message": "Une violation EPI a été détectée!",
        "recipient": "alert@example.com"
    },
    headers={"Content-Type": "application/json"}
)
```

## 🐛 Dépannage

### Problème : "Page non trouvée (404)"
**Solution :** Assurez-vous que :
1. Flask est en cours d'exécution
2. L'URL est correcte : `http://localhost:5000/notifications`
3. Actualisez la page (F5)

### Problème : "Erreur de connexion SMTP"
**Solutions :**
1. Vérifiez l'email et le mot de passe
2. Pour Gmail, générez une clé d'application :
   - Allez à https://myaccount.google.com/apppasswords
   - Générez une 16-car clé
   - Utilisez cette clé au lieu du mot de passe
3. Vérifiez le port SMTP (généralement 587)
4. Vérifiez que TLS est activé

### Problème : Les emails arrivent dans les SPAMS
**Solutions :**
1. Ajouter l'adresse à la whitelist
2. Envoyer depuis un domaine professionnel
3. Utiliser un service professionnel (SendGrid)

### Problème : Les rapports ne s'envoient pas
**Solutions :**
1. Vérifiez que le toggle est vert (activé)
2. Vérifiez qu'un destinataire existe
3. Vérifiez l'heure du serveur
4. Cliquez "⚡ Envoyer Maintenant" pour tester

## ⌚ Planification automatique

**Note importante :** La planification des rapports automatiques n'est **pas** exécutée automatiquement en arrière-plan. Pour cela, vous avez deux options :

### Option 1 : Cron job (Linux/Mac)
```bash
# Envoi quotidien à 8h
0 8 * * * curl -X POST http://localhost:5000/api/notifications/send-report \
  -H "Content-Type: application/json" \
  -d '{"type":"daily"}'

# Envoi hebdomadaire le lundi à 9h
0 9 * * 1 curl -X POST http://localhost:5000/api/notifications/send-report \
  -H "Content-Type: application/json" \
  -d '{"type":"weekly"}'
```

### Option 2 : Task Scheduler (Windows)
Voir `NOTIFICATIONS_GUIDE_FR.md` pour les détails.

### Option 3 : Celery/APScheduler
Intéger Celery pour les tâches en arrière-plan (avancé).

## 📊 Affichage du Dashboard

Le **Tableau de Bord** en haut affiche :
- **📧 Email Expéditeur** : L'adresse configurée
- **📬 Destinataires** : Nombre d'emails ajoutés
- **⏰ Rapports Programmés** : Nombre de rapports activés

## 💬 Exemple d'utilisation pratique

**Scénario :** Vous voulez envoyer une alerte tous les jours à 18h30

1. Configurez l'email SMTP
2. Ajoutez `manager@company.com` as destination
3. Activez le **Rapport Quotidien**
4. Changez l'heure à `18` (18h)
5. Sauvegardez
6. Le rapport s'enverra chaque jour à 18h

## 📋 Checklist d'installation

- [ ] Flask démarré avec succès
- [ ] Page `/notifications` accessible
- [ ] Email SMTP configuré
- [ ] Connexion SMTP testée (✅)
- [ ] Destinataire ajouté
- [ ] Test d'envoi manuel réussi
- [ ] Email reçu dans votre boîte de réception
- [ ] Rapports configurés (optionnel)
- [ ] Mode sombre testé

## 🎉 Prochaines étapes

Les notifications sont maintenant **opérationnelles** ! Vous pouvez :

1. **Automatiser les détections :** Faire déclencher une notification lors d'une détection EPI
2. **Intégrer avec Arduino :** Envoyer des alertes depuis les capteurs
3. **Créer des rapports personnalisés :** Adapter le contenu des rapports
4. **Ajouter des pièces jointes :** PDF, images, etc.
5. **Intégrer Slack/SMS :** Diversifier les canaux

---

**Questions ?** Consultez `NOTIFICATIONS_GUIDE_FR.md`

**Besoin d'aide ?** Vérifiez les logs : `tail -f logs/*.log`

---

Version 1.0 - Installation & Configuration Rapide
