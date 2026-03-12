# 🐛 GUIDE DE DIAGNOSTIQUE - Destinataires non sauvegardés

## Problème signalé
- ❌ Les emails ajoutés ne restent pas (compteur reste à 0)
- ❌ Les emails ne sont pas envoyés

## ✅ Ce que j'ai déjà vérifié

Je viens de vérifier et **le service Python fonctionne parfaitement** :
- ✅ Les fichiers `.notification_recipients` sont créés
- ✅ Les permissions d'écriture sont OK
- ✅ L'ajout/suppression fonctionne via le Python direct
- ✅ Le chemin complet est: `D:\projet\EPI-DETECTION-PROJECT\.notification_recipients`

**Par contre, le problème vient probablement du frontend ou de la communication Flask ↔ Frontend**

---

## 🚀 Comment diagnostiquer

### Étape 1: Démarrer Flask

Ouvrez un terminal PowerShell et lancez:

```powershell
cd d:\projet\EPI-DETECTION-PROJECT
python run_app.py
```

Ou si ça ne marche pas:
```powershell
.venv/Scripts/python.exe run_app.py
```

**Attendez jusqu'à voir:**
```
* Running on http://127.0.0.1:5000
```

### Étape 2: Accéder à la page DEBUG

Ouvrez votre navigateur et allez à:

**http://localhost:5000/api/notifications/debug**

Vous verrez une page noire avec une console verte et des boutons de test.

### Étape 3: Exécuter les tests dans l'ordre

1. **TEST 1: Vérifier la connexion Flask**
   - Cliquez le bouton
   - Vous devez voir ✅ en vert

2. **TEST 2: Récupérer les destinataires**
   - Cliquez le bouton
   - Vous devez voir une réponse JSON

3. **TEST 3: Ajouter un destinataire**
   - Cliquez le bouton "Ajouter"
   - Regardez la console pour les logs

4. **TEST 4: Récupérer après l'ajout**
   - Cliquez le bouton
   - **Important**: Vérifiez si le destinataire apparaît dans la liste!

5. **TEST 5: Supprimer**
   - Cliquez le bouton "Supprimer"
   - Vérifiez que c'est supprimé dans le test 4

---

## 📊 Analyser les résultats

### ✅ Succès - Tout fonctionne!
Si tous les tests affichent des réponses vertes (success: true), alors:
1. Votre Flask fonctionne
2. L'API fonctionne
3. Le problème est dans le **frontend notifications.html**

**Solution**: Utilisez simplement l'URL `/api/notifications/debug` pour ajouter vos emails!

### ⚠️ Erreur à l'étape 1
Si Flask ne démarre pas:
1. Vérifiez qu'aucune autre app n'utilise le port 5000
2. Vérifiez que `run_app.py` existe
3. Vérifiez les erreurs dans le terminal

### ⚠️ Erreur à l'étape 2
Si vous ne pouvez pas accéder à l'API:
1. Vérifiez que Flask tourne (regardez le terminal)
2. Vérifiez l'URL exacte: `http://localhost:5000/api/notifications/debug`
3. Essayez `http://127.0.0.1:5000/api/notifications/debug`

### ⚠️ Erreur à l'étape 3 ou 4
Si l'API retourne une erreur:
- Regardez le **message d'erreur exact** dans la console
- Copiez l'erreur et envoyez-la moi
- Regardez aussi le terminal de Flask pour les logs

---

## 🔧 Fichiers de test créés

J'ai créé ces fichiers pour vous aider:

1. **`test_service_direct.py`** - Teste le service Python seul
   ```bash
   python test_service_direct.py
   ```

2. **`diagnose_file_paths.py`** - Vérifie les chemins des fichiers
   ```bash
   python diagnose_file_paths.py
   ```

3. **`test_api_flask.py`** - Teste l'API Flask (besoin que Flask tourne)
   ```bash
   python test_api_flask.py
   ```

4. **`templates/notifications_debug.html`** - Page interactive de test

---

## 💡 Prochaines étapes

Une fois que vous avez les résultats des tests:

1. **Si les tests réussissent**: Le bug est dans le `notifications.html` original, je peux le fixer
2. **Si l'ajout fonctionne via le test**: Utilisez le `/api/notifications/debug` pour vos emails
3. **Si une erreur spécifique apparaît**: Envoyez-moi le message d'erreur exact

---

## 🆘 Besoin d'aide?

Exécutez ceci et envoyez-moi les résultats:

```powershell
python test_service_direct.py
python diagnose_file_paths.py
```

Et aussi préparez:
- Le message d'erreur exact de la console Flask
- L'URL que vous essayez d'accéder
- Une capture d'écran de la page DEBUG

---

**Commencez par l'Étape 1 (lancer Flask)** 🚀

