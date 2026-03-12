# 📧 Système de Notifications - Documentation Complète

## Vue d'ensemble

Le nouveau système de notifications intégrés offre :
- **Configuration email SMTP** complète avec support Gmail, Outlook, etc.
- **Gestion des destinataires** - Ajouter/supprimer des emails
- **Envoi manuel immédiat** de notifications
- **Rapports automatisés** (quotidiens, hebdomadaires, mensuels)
- **Historique complet** de tous les envois
- **Mode sombre et clair** manuel
- **Support MySQL et SQLite** pour la base de données

## Accès

### Page Web
Ouvrez votre navigateur et allez à :
```
http://localhost:5000/notifications
```

### API REST
Toutes les fonctionnalités sont disponibles via les points d'accès API REST :
- Base URL: `/api/notifications`

## Configuration

### 1️⃣ Configuration Email (SMTP)

**Interface :** Section "Configuration Email - Expéditeur"

**Paramètres :**
- **Email Expéditeur** : Votre adresse email (ex: votre-email@gmail.com)
- **Mot de Passe / Clé API** : Votre mot de passe ou clé d'application
- **Serveur SMTP** : smtp.gmail.com (pour Gmail)
- **Port SMTP** : 587 (généralement)
- **Utiliser TLS** : Oui (activé par défaut)

**Exemples de serveurs SMTP :**
| Fournisseur | SMTP | Port | TLS |
|---|---|---|---|
| Gmail | smtp.gmail.com | 587 | Oui |
| Outlook | smtp-mail.outlook.com | 587 | Oui |
| Yahoo | smtp.mail.yahoo.com | 587 | Oui |
| SendGrid | smtp.sendgrid.net | 587 | Oui |

**Boutons :**
- 💾 **Sauvegarder Configuration** : Enregistre vos paramètres SMTP
- ✅ **Tester Connexion** : Vérifie que les paramètres sont corrects

## Gestionnaires des Destinataires

### Ajouter un Destinataire

1. Saisissez l'adresse email dans le champ "➕ Ajouter un Email Destinataire"
2. Cliquez sur le bouton "Ajouter"
3. L'email apparaît dans la liste "📬 Destinataires Configurés"

### Supprimer un Destinataire

1. Trouvez l'email dans la liste "📬 Destinataires Configurés"
2. Cliquez sur le bouton "🗑️ Supprimer" à droite
3. Confirmez la suppression

## Envoi Manuel de Notifications

**Section :** "Envoi Manuel de Notifications"

**Étapes :**
1. **Objet** : Saisissez le titre de la notification
2. **Message** : Écrivez le contenu du message
3. **Destinataire** : Sélectionnez un email dans la liste déroulante
4. Cliquez sur **"⚡ Envoyer Immédiatement"**

**Caractéristiques :**
- Formatage HTML automatique
- Timestamp de l'envoi inclus
- Branding EPI Detection

## Rapports Automatiques

### Configuration

La section "Configuration des Rapports Automatiques" permet de configurer :

#### Rapport Quotidien
- **Fréquence** : Tous les jours
- **Paramètres** : Heure d'envoi (0-23h)
- **État** : Activé/Désactivé via le toggle

#### Rapport Hebdomadaire
- **Fréquence** : Une fois par semaine
- **Paramètres** : Jour de la semaine + Heure d'envoi
- **Jours** : Lundi (0) à Dimanche (6)

#### Rapport Mensuel
- **Fréquence** : Une fois par mois
- **Paramètres** : Jour du mois (1-31) + Heure d'envoi
- **Note** : Les jours > 28 s'adapteront aux mois plus courts

### Activation/Désactivation

Chaque rapport a un toggle on/off :
- **Toggle vert** = Activé (sera envoyé selon la fréquence)
- **Toggle gris** = Désactivé (ne sera pas envoyé)

### Envoi Immédiat

Cliquez sur **"⚡ Envoyer Maintenant"** pour envoyer un rapport immédiatement, sans attendre la prochaine date prévue.

## Historique des Notifications

**Section :** "Historique des Notifications"

Tableau affichant :
| Colonne | Description |
|---|---|
| 📅 Date/Heure | Timestamp de l'envoi |
| 📌 Type | manual ou report |
| 📧 Destinataire | Email du destinataire |
| ✅ Statut | success, pending, ou error |
| 📝 Détails | Message d'erreur le cas échéant |

**Actualisation :** Automatique toutes les 60 secondes

## Mode Sombre/Clair

**Bouton :** 🌙/☀️ en bas à droite de la page

**Fonctionnalités :**
- Bascule entre mode clair (blanc) et sombre (gris foncé)
- Préférence sauvegardée dans le navigateur (localStorage)
- Transition fluide entre les thèmes

## API REST

### Endpoints

#### Configuration Email
```
GET  /api/notifications/config
POST /api/notifications/config
POST /api/notifications/test-connection
```

#### Destinataires
```
GET    /api/notifications/recipients
POST   /api/notifications/recipients
DELETE /api/notifications/recipients
```

#### Envoi Manual
```
POST /api/notifications/send-manual
```

#### Rapports
```
GET  /api/notifications/reports-config
POST /api/notifications/reports-config
POST /api/notifications/send-report
```

#### Historique
```
GET /api/notifications/history
```

### Exemples de Requêtes

#### Sauvegarder la configuration email
```bash
curl -X POST http://localhost:5000/api/notifications/config \
  -H "Content-Type: application/json" \
  -d '{
    "sender_email": "votre-email@gmail.com",
    "sender_password": "votre-mot-de-passe",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": true
  }'
```

#### Ajouter un destinataire
```bash
curl -X POST http://localhost:5000/api/notifications/recipients \
  -H "Content-Type: application/json" \
  -d '{"email": "destinataire@example.com"}'
```

#### Envoyer une notification manuel
```bash
curl -X POST http://localhost:5000/api/notifications/send-manual \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Alerte Conformité",
    "message": "Détection d'"'"'une anomalie EPI.",
    "recipient": "destinataire@example.com"
  }'
```

#### Envoyer un rapport d'envoi
```bash
curl -X POST http://localhost:5000/api/notifications/send-report \
  -H "Content-Type: application/json" \
  -d '{"type": "daily"}'
```

## Base de Données

### SQLite (Par défaut)
- **Localisation** : `database/notifications.db`
- **Tables** :
  - `recipients` - Liste des destinataires
  - `notification_history` - Historique d'envois
  - `report_schedules` - Configuration des rapports
  - `email_config` - Configuration SMTP

### MySQL
Pour utiliser MySQL à la place de SQLite, modifiez le fichier `app/routes_notifications_api.py` :
```python
notif_manager = NotificationsManager(db_type='mysql')
```

## Dépannage

### Problème : "Connexion SMTP échouée"

**Solutions :**
1. Vérifiez votre email et mot de passe
2. Vérifiez le serveur SMTP correct
3. Pour Gmail, utilisez une clé d'application (2FA)
4. Vérifiez le pare-feu/proxy

### Problème : Les rapports ne s'envoient pas

**Solutions :**
1. Vérifiez que le rapport est "activé" (toggle vert)
2. Vérifiez une seule destinataire configué
3. Vérifiez l'heure système du serveur
4. Regardez l'historique pour les erreurs

### Problème : Les emails arrivent dans les spams

**Solutions :**
1. Ajouter votre adresse à la whitelist
2. Vérifier le SPF/DKIM du domaine
3. Utiliser un service d'email professionnel (SendGrid, etc.)

## Performance

- **Historique** : Stocke les 100 derniers envois
- **Destinataires** : Illimité
- **Rapports** : Jusqu'à 3 (quotidien, hebdomadaire, mensuel)
- **Temps d'envoi** : ~2-5 secondes par email

## Sécurité

⚠️ **Important :**
- Les mots de passe SMTP sont stockés en clair dans JSON
- Utilisez des variables d'environnement en production
- Limitez l'accès à `/api/notifications` via une authentification
- Utilisez HTTPS en production

## Support

Pour toute question ou problème :
1. Vérifiez les logs de l'application
2. Consultez la section "Dépannage"
3. Vérifiez l'historique des notifications pour les détails d'erreur

---

Version 1.0 - 2026
EPI Detection System
