# 📧 CONFIGURATION EMAIL - QUICK REFERENCE

## 🚀 3 FAÇONS DE CONFIGURER

### **Option 1: Assistant Interactif (Recommandé)**
```bash
python setup_email_interactive.py
```
✅ Vous guide étape par étape  
✅ Vérifie la configuration automatiquement  
✅ Envoie un email test

---

### **Option 2: Configuration Manuelle**

1. **Préparez Gmail:**
   - Activer 2FA: https://myaccount.google.com/security
   - Générer mot de passe app: https://myaccount.google.com/apppasswords

2. **Éditez `.env.email`:**
   ```ini
   SENDER_EMAIL=votre.email@gmail.com
   SENDER_PASSWORD=motdepasse_app_16_caracteres
   RECIPIENT_EMAILS=admin@company.com
   DAILY_REPORT_HOUR=08
   ```

3. **Testez:**
   ```bash
   python test_email_config.py
   ```

---

### **Option 3: Documentation Complète**
📖 Lire: `GUIDE_EMAIL_SETUP.md`

---

## ✅ CHECKLIST RAPIDE

```
[ ] Gmail 2FA activée
[ ] Mot de passe d'application généré (16 caractères)
[ ] .env.email complété:
    [ ] SENDER_EMAIL
    [ ] SENDER_PASSWORD
    [ ] RECIPIENT_EMAILS
    [ ] DAILY_REPORT_HOUR
[ ] test_email_config.py exécuté avec succès ✅
[ ] Email test reçu
[ ] Serveur Flask redémarré
```

---

## 🔧 FICHIERS CLÉS

```
.env.email                  ← Votre configuration
config.py                   ← Charge .env.email (ne pas modifier)
app/email_notifications.py  ← Code d'envoi (ne pas modifier)
test_email_config.py        ← Script de test
setup_email_interactive.py  ← Assistant interactif
GUIDE_EMAIL_SETUP.md        ← Documentation complète
```

---

## ⚡ COMMANDES RAPIDES

```powershell
# 1. Assistant interactif (début ici!)
python setup_email_interactive.py

# 2. Tester la configuration
python test_email_config.py

# 3. Envoyer un email manuel
python -c "from app.email_notifications import EmailNotifier; from config import config; EmailNotifier().send_email(config.SENDER_EMAIL, 'Test', '<h1>Test</h1>')"

# 4. Vérifier les logs
type logs/app.log | findstr /I "email"

# 5. Redémarrer le serveur
# (Arrêtez et relancez Flask)
```

---

## 📊 RAPPORTS AUTOMATIQUES

| Rapport | Fréquence | Heure | Configurable |
|---------|-----------|-------|--------------|
| 📊 Quotidien | Tous les jours | `DAILY_REPORT_HOUR` | ✅ |
| 📅 Hebdomadaire | `WEEKLY_REPORT_DAY` | `WEEKLY_REPORT_HOUR` | ✅ |
| 📆 Mensuel | `MONTHLY_REPORT_DAY` | `MONTHLY_REPORT_HOUR` | ✅ |
| 🚨 Alerte | Immédiate (si compliance < seuil) | N/A | ✅ |

---

## 🆘 PROBLÈMES COURANTS

| Erreur | Solution |
|--------|----------|
| "Authentification échouée" | Vérifier 2FA + mot de passe app |
| "SENDER_EMAIL not configured" | Éditer .env.email |
| "Connection refused" | Vérifier firewall port 587 |
| "Email ne reçoit pas" | Vérifier SPAM + RECIPIENT_EMAILS |

---

## 📧 FORMAT DES EMAILS

**De:** SENDER_EMAIL  
**À:** RECIPIENT_EMAILS  
**Contenu:**
- ✅ Statistiques du jour/semaine/mois
- ✅ Graphiques en HTML
- ✅ Compliance %
- ✅ Détections par EPI

---

## 🎯 PROCHAINES ÉTAPES

1. ✅ Lancez `setup_email_interactive.py`
2. ✅ Vérifiez que l'email test arrive
3. ✅ Configurez vos rapports préférés dans `.env.email`
4. ✅ Redémarrez Flask
5. ✅ Les rapports s'enverront automatiquement selon l'horaire

---

**Questions?** Consultez `GUIDE_EMAIL_SETUP.md` pour la documentation complète!
