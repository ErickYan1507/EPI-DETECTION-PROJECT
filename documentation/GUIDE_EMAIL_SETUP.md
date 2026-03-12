# 📧 GUIDE COMPLET - Configuration Email Réelle avec Gmail

## **PHASE 1: Préparation Gmail (5 minutes)**

### Étape 1.1 - Activer la vérification en 2 étapes

1. Allez sur https://myaccount.google.com/
2. Cliquez **Sécurité** (en haut à gauche)
3. Descendez jusqu'à **Vérification en 2 étapes**
4. Cliquez **Activer la vérification en 2 étapes**
5. Suivez les instructions (SMS ou authenticator)
6. ✅ Une fois terminé, vous verrez "✔️ 2-Step Verification is on"

### Étape 1.2 - Générer le mot de passe d'application

1. Retournez à https://myaccount.google.com/
2. Cliquez **Sécurité** → Scroll jusqu'à **Mots de passe des applications**
3. Si vous ne voyez pas cette option → la 2FA n'est pas correctement activée !
4. **Sélectionnez:**
   - **Appareil:** Windows (ou votre OS)
   - **Application:** Mail
5. Cliquez **Générer**
6. Google génère un mot de passe de 16 caractères
7. ✅ **Copiez et collez-le quelque part** (vous en aurez besoin au prochain étape)

**Exemple:** `abcd efgh ijkl mnop`

---

## **PHASE 2: Configuration de l'Application (5 minutes)**

### Étape 2.1 - Remplir le fichier .env.email

1. Ouvrez le fichier `.env.email` dans le projet:
   ```
   d:\projet\EPI-DETECTION-PROJECT\.env.email
   ```

2. **Remplissez les champs obligatoires:**

```ini
# Votre email Gmail
SENDER_EMAIL=votre.email.avec.2fa@gmail.com

# Le mot de passe d'application généré (16 caractères)
SENDER_PASSWORD=abcdefghijklmnop

# Email(s) où recevoir les rapports (vous pouvez mettre plusieurs)
RECIPIENT_EMAILS=votre.email@company.com,manager@company.com

# Heure d'envoi du rapport quotidien (0-23)
DAILY_REPORT_HOUR=08

# Jour et heure du rapport hebdomadaire (0=lundi, 1=mardi... 6=dimanche)
WEEKLY_REPORT_DAY=1
WEEKLY_REPORT_HOUR=09

# Jour et heure du rapport mensuel
MONTHLY_REPORT_DAY=1
MONTHLY_REPORT_HOUR=09
```

3. **Sauvegardez le fichier** (Ctrl+S)

---

## **PHASE 3: Test de Connexion (2 minutes)**

### Étape 3.1 - Lancer le script de test

1. Ouvrez un terminal PowerShell dans le projet
2. Tapez cette commande:

```powershell
python test_email_config.py
```

3. Vous verrez l'une de ces réponses:

**✅ SI ÇA MARCHE:**
```
============================================================
TEST DE CONFIGURATION EMAIL
============================================================

1️⃣ VÉRIFICATION DES PARAMÈTRES:
   SMTP Server: smtp.gmail.com
   SMTP Port: 587
   Sender Email: votre.email@gmail.com
   Password: ****************

✅ Paramètres trouvés

2️⃣ TEST DE CONNEXION SMTP:
   ✅ Connexion établie avec smtp.gmail.com:587
   ✅ TLS activé
   ✅ Authentification réussie...
   ✅ Déconnexion

3️⃣ TEST D'ENVOI D'EMAIL:
   ✅ Email envoyé à votre.email@gmail.com

============================================================
✅ TOUS LES TESTS RÉUSSIS!
============================================================
```

**❌ SI ERREUR "Authentification échouée":**
- Vérifiez que la 2FA est activée sur votre compte
- Vérifiez que vous avez généré et copié le bon mot de passe d'application
- Réessayez après 1 minute

**❌ SI ERREUR "SENDER_EMAIL n'est pas configuré":**
- Vérifiez que vous avez rempli le fichier `.env.email` correctement
- Assurez-vous de ne pas avoir d'espaces avant/après l'email

---

## **PHASE 4: Activation des Rapports Automatiques**

### Option A: Rapports Quotidiens

Le rapport quotidien s'enverra à `DAILY_REPORT_HOUR` tous les jours.

```ini
# Dans .env.email:
DAILY_REPORT_HOUR=08        # S'envoie chaque jour à 8h
RECIPIENT_EMAILS=admin@company.com
```

### Option B: Rapports Hebdomadaires

```ini
WEEKLY_REPORT_DAY=1         # 1=mardi
WEEKLY_REPORT_HOUR=09       # À 9h du matin
```

**Jours disponibles:**
- 0 = Lundi
- 1 = Mardi
- 2 = Mercredi
- 3 = Jeudi
- 4 = Vendredi
- 5 = Samedi
- 6 = Dimanche

### Option C: Rapports Mensuels

```ini
MONTHLY_REPORT_DAY=1        # Le 1er de chaque mois
MONTHLY_REPORT_HOUR=09      # À 9h du matin
```

### Option D: Alertes Immédates

```ini
SEND_ALERTS_ENABLED=true    # Active les alertes
ALERT_THRESHOLD=80          # Alerte si compliance < 80%
```

---

## **PHASE 5: Vérifier que ça Fonctionne**

### Test Manuel d'Envoi

Créez ce fichier: `test_send_email.py`

```python
from app.email_notifications import EmailNotifier
from config import config

# Créer le notifier
notifier = EmailNotifier()

# Envoyer un email test
subject = "Test Manuel - EPI Detection"
html = "<h1>Test Email</h1><p>Si vous recevez ceci, l'email fonctionne!</p>"
recipient = config.SENDER_EMAIL

success = notifier.send_email(recipient, subject, html)
print("✅ Email envoyé!" if success else "❌ Erreur lors de l'envoi")
```

Puis lancez:
```powershell
python test_send_email.py
```

---

## **DÉPANNAGE COURANT**

### ❌ "Authentification échouée"
```
Solution:
1. Vérifiez que 2FA est ON sur https://myaccount.google.com/security
2. Régénérez le mot de passe d'application
3. Copiez exactement (pas d'espaces supplémentaires)
4. Vérifiez que le domaine d'email contient "gmail.com"
```

### ❌ "Connection refused" ou "Network error"
```
Solution:
1. Vérifiez votre connexion Internet
2. Assurez-vous que smtp.gmail.com n'est pas bloqué par votre firewall
3. Vérifiez le port 587 (TLS)
4. Essayez un VPN si bloqué régionalement
```

### ❌ "Email ne reçoit pas"
```
Solution:
1. Vérifiez le dossier SPAM/Promotions
2. Vérifiez que RECIPIENT_EMAILS est correct
3. Vérifiez que le serveur Flask est lancé
4. Vérifiez les logs: cat logs/app.log
```

### ❌ "SENDER_PASSWORD contient des espaces"
```
Solution:
Gmail génère: "abcd efgh ijkl mnop" (avec espaces)
Copié dans .env.email: abcd efgh ijkl mnop (sans guillemets)
✅ C'est correct ! Les espaces sont normaux
```

---

## **INTÉGRATION AVEC L'APPLICATION**

### Où sont envoyés les rapports?

1. **Rapport Présence PDF** → RECIPIENT_EMAILS
2. **Email d'Alerte** (compliance < ALERT_THRESHOLD) → RECIPIENT_EMAILS
3. **Rapport Quotidien** (tous les jours à DAILY_REPORT_HOUR) → RECIPIENT_EMAILS
4. **Rapport Hebdomadaire** (le WEEKLY_REPORT_DAY à WEEKLY_REPORT_HOUR) → RECIPIENT_EMAILS

### Format des Emails

Les emails contiennent:
- ✅ Statistiques du jour/semaine/mois
- ✅ Graphiques en HTML
- ✅ Liens vers les détections
- ✅ Alertes si non-conformité

---

## **CHECKLIST FINALE**

- [ ] 2FA activée sur Gmail
- [ ] Mot de passe d'application généré
- [ ] `.env.email` complété avec email et password
- [ ] `test_email_config.py` exécuté avec succès ✅
- [ ] Test email reçu
- [ ] `.env.email` configuré avec RECIPIENT_EMAILS
- [ ] Horaires d'envoi définis
- [ ] Serveur Flask redémarré
- [ ] Email de test reçu dans les 24h

---

## **SUPPORT**

Si ça ne marche pas:

1. **Vérifiez les logs:**
   ```powershell
   type logs/app.log | findstr /I "email"
   ```

2. **Testez la connexion SMTP manuellement:**
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('votre.email@gmail.com', 'votre_password_app')
   ```

3. **Contactez le support Google:** https://support.google.com

---

**Besoin d'aide? Les fichiers clés sont:**
- Configuration: `.env.email`
- Test: `test_email_config.py`
- Code: `app/email_notifications.py`
- Config app: `config.py`
