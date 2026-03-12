# 📧 GUIDE COMPLET - CONFIGURATION GMAIL POUR NOTIFICATIONS

## 🔴 Problème actuel
```
5.7.8 Username and Password not accepted
```

Cela signifie que vos **identifiants Gmail sont rejetés**. Suivez ce guide pour résoudre.

---

## ✅ Étape 1: Vérifier que votre Email est CORRECT

### ❌ FAUX:
- `20firmino09` (pas complet)
- `20firmino09gmail` (pas de @)
- `20firmino09@gmail` (pas de .com)

### ✅ BON:
- `20firmino09@gmail.com` ← Format correct

**Assurez-vous d'utiliser le format complet: `email@gmail.com`**

---

## ✅ Étape 2: Créer une Clé d'Application Gmail

**IMPORTANT**: Gmail refuse les mots de passe ordinaires. Vous **DEVEZ** créer une "App Password".

### Comment créer une clé:

1. **Ouvrez**: https://myaccount.google.com/apppasswords

2. **Connectez-vous** avec votre compte de gmail (`20firmino09@gmail.com`)

3. **Si vous voyez une erreur**:
   - Allez à: https://myaccount.google.com/security
   - Scrollez jusqu'à "Vérification en deux étapes"
   - Cliquez **"Activer la vérification en deux étapes"**
   - Suivez les instructions
   - Puis revenez à https://myaccount.google.com/apppasswords

4. **Dans la page "App Password"**:
   - "Select the app": Choisissez **Mail**
   - "Select the device": Choisissez **Windows PC** (ou autre)
   - Cliquez **Generate**

5. **Vous verrez une clé**: 
   ```
   xxxx xxxx xxxx xxxx
   ```
   Exemple: `mqoc zsrh lrsh zhhn`

6. **COPIEZ-LA EXACTEMENT** (avec les espaces!) 

---

## ✅ Étape 3: Configurer dans EPI Detection

### Option A: Via l'Interface Web (Recommandée)

1. Ouvrez: **http://localhost:5000/notifications**

2. Dans **"Configuration Email - Expéditeur"**:
   - **Email Expéditeur**: `20firmino09@gmail.com`
   - **Mot de Passe**: `mqoc zsrh lrsh zhhn` (votre clé)

3. Cliquez **"Sauvegarder Configuration Expéditeur"**

4. Cliquez **"Tester Connexion"**
   - ✅ Si vert = C'est bon!
   - ❌ Si rouge = Vérifiez votre clé

### Option B: Via le Script

Exécutez:
```powershell
python setup_gmail_interactive.py
```

Puis entrez:
- Votre email: `20firmino09@gmail.com`
- Votre clé: `mqoc zsrh lrsh zhhn`

---

## 🐛 Troubleshooting

### "Username and Password not accepted"

**Solution**:
1. ✅ Vérifiez que c'est une **clé d'application** (pas votre mot de passe)
2. ✅ Vérifiez qu'il n'y a **pas d'espaces au début/fin**
3. ✅ Vérifiez que l'email est **complet** (`xxx@gmail.com`)
4. ✅ Vérifiez que **2FA est activé** sur votre compte

### "Invalid credentials"

**Solution**:
1. Allez à: https://myaccount.google.com/security
2. Cherchez "Mots de passe d'application"
3. Supprimez les anciens, créez un nouveau

### "Can't connect to SMTP server"

**Solution**:
1. Vérifiez votre **connexion internet**
2. Vérifiez que le **firewall** n'est pas bloqué
3. Redémarrez Flask: `Ctrl+C` puis `python run_app.py`

---

## ✅ Tester après configuration

Une fois configuré, testez:

### Via l'Interface Web:
1. Allez à: http://localhost:5000/notifications
2. Entrez un destinataire (email valide)
3. Cliquez "Ajouter"
4. Envoyez un test via "Manuel Notification"

### Via le Script de Test:
```powershell
python test_send_email.py
```

---

## 📋 Résumé

| Étape | Quoi faire | Résultat attendu |
|-------|-----------|-----------------|
| 1 | Créer clé app sur myaccount.google.com | Clé de 16 caractères |
| 2 | Entrer email + clé dans l'interface | ✅ Succès |
| 3 | Tester connexion | ✅ Vert |
| 4 | Envoyer email de test | ✅ Email reçu |

---

## 🆘 Vous êtes bloqué?

Envoyez-moi:
1. Votre email Gmail (ex: xxx@gmail.com)
2. Le **message d'erreur exact** (rouge) de l'interface
3. Une capture d'écran du test de connexion

**Je peux vous aider à déboguer!** 🚀

