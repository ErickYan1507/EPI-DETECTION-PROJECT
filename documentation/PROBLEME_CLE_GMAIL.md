# 🆘 PROBLÈME: Clé Gmail rejetée

## Diagnostic
```
❌ ERREUR: Username and Password not accepted
❌ Clé actuelle: mqoc zsrh lrsh zhhn (INVALIDE)
```

---

## ✅ SOLUTION: Générer une clé VALIDE

### IMPORTANT: Activez d'abord la 2FA

Gmail **refuse les app passwords** si la **vérification en 2 étapes** n'est pas activée!

**Étape 1: Activez la 2FA**

1. Allez à: https://myaccount.google.com/security

2. Cherchez **"Vérification en deux étapes"**

3. Cliquez **"Activer la vérification en deux étapes"**

4. Suivez les instructions (code par SMS ou Google Authenticator)

5. Une fois **ACTIVÉE**, continuez...

### Étape 2: Générez une app password

1. Allez à: https://myaccount.google.com/apppasswords

2. Si vous voyez **"App passwords"** (pas grisé):
   - **App**: Mail
   - **Device**: Windows
   - Cliquez **Generate**

3. Vous verrez une clé:
   ```
   xxxx xxxx xxxx xxxx
   ```
   
4. **COPIEZ-LA EXACTEMENT**

### Étape 3: Testez-la

Remplacez la clé dans le script:
```python
PASSWORD = "votre-nouvelle-clé-ici"  # Format: xxxx xxxx xxxx xxxx
```

Puis relancez:
```powershell
python test_smtp_direct.py
```

Si ✅ vert = La clé est valide!

---

## 📋 Résumé

| Étape | Action | Status |
|-------|--------|--------|
| 1 | Activer 2FA | À faire! |
| 2 | Générer clé app | À faire! |
| 3 | Tester la clé | À faire! |
| 4 | Configurer dans EPI | À faire! |

---

## 🎯 Rapide: 2 cas possibles

### Cas 1: 2FA n'est PAS activée
- Vous ne voyez pas "App passwords" sur https://myaccount.google.com/apppasswords
- **Solution**: Activez 2FA d'abord!

### Cas 2: 2FA EST activé
- Vous voyez "App passwords"
- La clé `mqoc zsrh lrsh zhhn` a été rejetée
- **Solution**: Générez une NOUVELLE clé

---

## 💡 Conseil
La clé dans`mdp.txt` est peut-être vieille ou fausse. Générez-en une **NOUVELLE** vous-même depuis myaccount.google.com.

Une fois que vous avez la bonne clé, le système d'emails **FONCTIONNERA PARFAITEMENT**! ✅

