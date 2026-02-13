# 📧 EMAIL SETUP - START HERE!

## ⚡ 3 COMMANDES POUR CONFIGURER

### 1️⃣ Assistant Interactif (RECOMMANDÉ)
```powershell
python setup_email_interactive.py
```
✅ Vous guide étape par étape  
✅ Teste automatiquement  
✅ Envoie un email test  

**Durée: 5 minutes**

---

### 2️⃣ Configuration Manuelle

**Étape 1: Préparer Gmail**
- Allez sur https://myaccount.google.com/security
- Activer 2FA
- Générer mot de passe app (https://myaccount.google.com/apppasswords)

**Étape 2: Remplir .env.email**
```ini
SENDER_EMAIL=votre.email@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop
RECIPIENT_EMAILS=admin@company.com
DAILY_REPORT_HOUR=08
```

**Étape 3: Tester**
```powershell
python test_email_config.py
```

**Durée: 10 minutes**

---

### 3️⃣ Vérification Complète
```powershell
python verify_email_config.py
```
Check tous les paramètres + teste la connexion SMTP

---

## 🚀 LANCER L'APP AVEC RAPPORTS

```powershell
python run.py --mode run
```

✅ Le scheduler se lance automatiquement  
✅ Les rapports s'envoient selon l'horaire  
✅ Voir les logs avec: `type logs/app.log`

---

## 📊 VOS RAPPORTS

| Quand | Fréquence | Destinataires |
|-------|-----------|---|
| **Quotidien** | Tous les jours à DAILY_REPORT_HOUR | RECIPIENT_EMAILS |
| **Hebdo** | WEEKLY_REPORT_DAY à WEEKLY_REPORT_HOUR | RECIPIENT_EMAILS |
| **Mensuel** | MONTHLY_REPORT_DAY à MONTHLY_REPORT_HOUR | RECIPIENT_EMAILS |
| **Alertes** | Immédiate (si compliance < seuil) | RECIPIENT_EMAILS |

---

## ✅ CHECKLIST

- [ ] Gmail 2FA activée
- [ ] Mot de passe app généré
- [ ] `.env.email` rempli
- [ ] `python setup_email_interactive.py` ✅ réussi
- [ ] Email test reçu
- [ ] App lancée: `python run.py --mode run`
- [ ] Rapports reçus selon l'horaire

---

## 📁 FICHIERS CLÉS

```
.env.email                      ← Votre configuration
setup_email_interactive.py      ← Assistant (à lancer d'abord!)
test_email_config.py            ← Test SMTP
verify_email_config.py          ← Vérification complète
show_scheduler_status.py        ← Voir l'état du scheduler
EMAIL_QUICK_START.md            ← Résumé rapide
GUIDE_EMAIL_SETUP.md            ← Documentation complète
EMAIL_EXAMPLES.py               ← Exemples de code
```

---

## 🆘 PROBLÈME?

**"Module 'dotenv' not found"**
```powershell
pip install python-dotenv
```

**"Module 'apscheduler' not found"**
```powershell
pip install APScheduler
```

**"Authentification échouée"**
1. Vérifiez 2FA à https://myaccount.google.com/security
2. Régénérez le mot de passe app
3. Copiez-le dans `.env.email`

**"Email ne reçoit pas"**
1. Vérifiez SPAM
2. Vérifiez `RECIPIENT_EMAILS` dans `.env.email`
3. Vérifiez les logs: `type logs/app.log`

---

## 📝 TEMPLATE .env.email

```ini
# Email (votre compte Gmail avec 2FA)
SENDER_EMAIL=votre.email@gmail.com

# Mot de passe d'application (16 caractères)
SENDER_PASSWORD=abcd efgh ijkl mnop

# Email(s) pour recevoir rapports
RECIPIENT_EMAILS=admin@company.com,manager@company.com

# Heures d'envoi (0-23)
DAILY_REPORT_HOUR=08
WEEKLY_REPORT_DAY=1
WEEKLY_REPORT_HOUR=09
MONTHLY_REPORT_DAY=1
MONTHLY_REPORT_HOUR=09

# Alertes
SEND_ALERTS_ENABLED=true
ALERT_THRESHOLD=80

# SMTP (ne pas changer pour Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

---

## 🎯 PROCHAINES ÉTAPES

```
1. python setup_email_interactive.py     ← Lancez ceci d'abord
2. Attendez email de test                ← Vérifiez votre boîte
3. python run.py --mode run              ← Lancez l'app
4. Rapports automatiques envoyés!        ← Fait! 🎉
```

---

**Questions?** 📖 Consultez `GUIDE_EMAIL_SETUP.md`
