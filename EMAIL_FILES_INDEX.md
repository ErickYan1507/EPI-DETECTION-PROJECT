# 📧 EMAIL SETUP - GUIDE COMPLET DES FICHIERS

## 🎯 PAR OÙ COMMENCER?

### 👉 DÉBUTANT? COMMENCEZ ICI:
1. **Lisez:** [START_EMAIL_HERE.md](START_EMAIL_HERE.md) ← 5 minutes
2. **Exécutez:** `python setup_email_interactive.py` ← Assistant automatique
3. **Vérifiez:** Email test reçu ✅

---

## 📁 STRUCTURE COMPLÈTE

### 🚀 DÉMARRAGE
```
START_EMAIL_HERE.md              ← Commencez ici!
  └─ 3 commandes pour configurer
  └─ Checklist
  └─ Template .env.email
```

### 📖 DOCUMENTATION
```
README_EMAIL_SETUP.md            ← Résumé complet de ce qui est fait
EMAIL_QUICK_START.md             ← Résumé 1 page
GUIDE_EMAIL_SETUP.md             ← Documentation complète (70 lignes)
EMAIL_EXAMPLES.py                ← 10 exemples d'utilisation
INTEGRATION_SCHEDULER.txt        ← Code d'intégration
```

### ⚙️ CONFIGURATION
```
.env.email                       ← Votre configuration (À REMPLIR!)
  ├─ SENDER_EMAIL
  ├─ SENDER_PASSWORD
  ├─ RECIPIENT_EMAILS
  ├─ DAILY_REPORT_HOUR
  ├─ WEEKLY_REPORT_DAY
  ├─ MONTHLY_REPORT_DAY
  └─ ALERT_THRESHOLD
```

### 🧪 SCRIPTS DE TEST
```
setup_email_interactive.py       ← Assistant interactif (À LANCER EN PREMIER!)
test_email_config.py             ← Test connexion SMTP
verify_email_config.py           ← Vérification complète
show_scheduler_status.py         ← Affiche état du scheduler
```

### 💻 CODE
```
config.py                        ← +6 lignes pour charger .env.email
run.py                           ← +7 lignes pour intégrer scheduler
app/email_notifications.py       ← +60 lignes pour generate_monthly_report()
app/report_scheduler.py          ← Nouveau: Scheduler des rapports
```

### 📦 DÉPENDANCES
```
python-dotenv                    ← Charger .env.email ✅ Installé
APScheduler                      ← Rapports programmés ✅ Installé
```

---

## 🎓 GUIDE PAR PROFIL

### 👨‍💼 POUR LES GESTIONNAIRES
1. Lisez: [README_EMAIL_SETUP.md](README_EMAIL_SETUP.md)
2. Données clés: Rapports envoyés tous les jours/semaine/mois
3. Avantage: Conformité EPI suivie automatiquement

### 👨‍💻 POUR LES DÉVELOPPEURS
1. Lisez: [EMAIL_EXAMPLES.py](EMAIL_EXAMPLES.py) - 10 exemples
2. Code: `app/report_scheduler.py` et modifications
3. Test: `python verify_email_config.py`

### 🔧 POUR LES ADMINISTRATEURS
1. Configuration: [.env.email](.env.email)
2. Déploiement: `python run.py --mode run`
3. Monitoring: `python show_scheduler_status.py`

### 📚 POUR LES DÉBUTANTS
1. START: [START_EMAIL_HERE.md](START_EMAIL_HERE.md)
2. SETUP: `python setup_email_interactive.py`
3. LEARN: [GUIDE_EMAIL_SETUP.md](GUIDE_EMAIL_SETUP.md)

---

## 🚀 FLUX DE CONFIGURATION

```
START_EMAIL_HERE.md
  ↓
setup_email_interactive.py (A LANCER!)
  ↓
Email de test reçu ✅
  ↓
.env.email configuré
  ↓
python run.py --mode run
  ↓
Rapports automatiques envoyés! 🎉
```

---

## 📋 FICHIERS PAR ORDRE D'IMPORTANCE

### 1️⃣ ESSENTIELS (MAINTENANT)
- [ ] [START_EMAIL_HERE.md](START_EMAIL_HERE.md) - Lisez d'abord
- [ ] `.env.email` - Complétez avec vos infos
- [ ] `python setup_email_interactive.py` - Exécutez

### 2️⃣ IMPORTANT (APRÈS SETUP)
- [ ] [README_EMAIL_SETUP.md](README_EMAIL_SETUP.md) - Comprendre ce qu'on a fait
- [ ] [EMAIL_QUICK_START.md](EMAIL_QUICK_START.md) - Résumé
- [ ] `python run.py --mode run` - Lancer l'app

### 3️⃣ UTILE (SI BESOIN)
- [ ] [GUIDE_EMAIL_SETUP.md](GUIDE_EMAIL_SETUP.md) - Doc complète
- [ ] [EMAIL_EXAMPLES.py](EMAIL_EXAMPLES.py) - Exemples
- [ ] `python show_scheduler_status.py` - Vérifier état

### 4️⃣ RÉFÉRENCE (DÉPANNAGE)
- [ ] `python verify_email_config.py` - Check tout
- [ ] `python test_email_config.py` - Test SMTP
- [ ] `type logs/app.log` - Voir les erreurs

---

## ✅ CHECKLIST DE CONFIGURATION

### Avant de lancer `setup_email_interactive.py`:
- [ ] Vous avez un compte Gmail
- [ ] Gmail a la 2FA activée (https://myaccount.google.com/security)
- [ ] Vous avez généré un mot de passe application (16 caractères)
- [ ] Vous avez edité `.env.email` avec vos paramètres

### Après `setup_email_interactive.py`:
- [ ] Email de test reçu ✅
- [ ] Configuration sauvegardée
- [ ] Rapports programmés
- [ ] Scheduler actif après `python run.py`

---

## 🎯 RACCOURCIS RAPIDES

### Configuration rapide (5 min)
```powershell
# 1. Configuez .env.email manuellement
notepad .env.email

# 2. Lancez l'assistant
python setup_email_interactive.py

# 3. Attendez email de test
# Cherchez dans Gmail...

# 4. Lancez l'app
python run.py --mode run
```

### Vérification (2 min)
```powershell
# Vérifier tout
python verify_email_config.py

# Voir l'état scheduler
python show_scheduler_status.py

# Test SMTP
python test_email_config.py
```

### Troubleshooting
```powershell
# Voir les logs
type logs/app.log | findstr email

# Vérifier la connexion
python test_email_config.py

# Re-configurer
python setup_email_interactive.py
```

---

## 📞 SUPPORT PAR PROBLÈME

### ❌ "Module not found"
```
pip install python-dotenv APScheduler
```
→ Voir: [GUIDE_EMAIL_SETUP.md](GUIDE_EMAIL_SETUP.md#dépannage-courant)

### ❌ "Authentification échouée"
```
1. Vérifier 2FA sur https://myaccount.google.com/security
2. Régénérer mot de passe app
3. Vérifier dans .env.email
```
→ Voir: [START_EMAIL_HERE.md](START_EMAIL_HERE.md#-problème)

### ❌ "Email ne reçoit pas"
```
1. Vérifier SPAM
2. Vérifier RECIPIENT_EMAILS dans .env.email
3. Vérifier logs/app.log
```
→ Voir: [GUIDE_EMAIL_SETUP.md](GUIDE_EMAIL_SETUP.md#dépannage-courant)

### ❌ "Scheduler ne fonctionne pas"
```
python show_scheduler_status.py
type logs/app.log | findstr -i scheduler
```
→ Voir: [README_EMAIL_SETUP.md](README_EMAIL_SETUP.md#-points-clés-à-retenir)

---

## 📊 ÉTAT DES FICHIERS

### ✅ Créés (nouveaux fichiers)
- .env.email
- app/report_scheduler.py
- test_email_config.py
- setup_email_interactive.py
- verify_email_config.py
- show_scheduler_status.py
- START_EMAIL_HERE.md
- EMAIL_QUICK_START.md
- GUIDE_EMAIL_SETUP.md
- EMAIL_SETUP_SUMMARY.md
- EMAIL_EXAMPLES.py
- README_EMAIL_SETUP.md
- INTEGRATION_SCHEDULER.txt (ce fichier)

### ✏️ Modifiés (mises à jour)
- config.py (+6 lignes)
- app/email_notifications.py (+60 lignes)
- run.py (+7 lignes)

### ✅ Installés (dépendances)
- python-dotenv
- APScheduler

---

## 🎓 DOCUMENTATION COMPLÈTE

| Document | Contenu | Durée |
|----------|---------|-------|
| [START_EMAIL_HERE.md](START_EMAIL_HERE.md) | Démarrage rapide | 5 min |
| [EMAIL_QUICK_START.md](EMAIL_QUICK_START.md) | Résumé 1 page | 3 min |
| [README_EMAIL_SETUP.md](README_EMAIL_SETUP.md) | Vue d'ensemble | 10 min |
| [GUIDE_EMAIL_SETUP.md](GUIDE_EMAIL_SETUP.md) | Doc détaillée | 20 min |
| [EMAIL_EXAMPLES.py](EMAIL_EXAMPLES.py) | 10 exemples | 15 min |
| [INTEGRATION_SCHEDULER.txt](INTEGRATION_SCHEDULER.txt) | Code intégration | 5 min |

---

## 🎯 PROCHAINES ÉTAPES

```
1. Ouvrez: START_EMAIL_HERE.md
2. Exécutez: python setup_email_interactive.py
3. Attendez: Email de test
4. Lancez: python run.py --mode run
5. Profitez: Rapports automatiques! 🎉
```

---

**Vous êtes maintenant prêt à envoyer des emails réels!** 📧🚀
