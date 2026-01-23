# 🌙☀️ Guide Utilisateur - Mode Sombre/Clair

Bienvenue dans le **Système de Thème EPI Detection** ! Vous pouvez maintenant choisir entre un mode sombre confortable et un mode clair lumineux.

## 🎯 Utilisation Rapide

### Basculer le Thème
1. **Cherchez le bouton** dans la barre de navigation (coin haut-droit)
2. **Cliquez dessus** pour alterner entre mode sombre et clair
3. **L'icône change** (Lune = sombre disponible, Soleil = clair disponible)

### C'est tout ! 
Votre choix est **automatiquement sauvegardé** et sera rappelé la prochaine fois que vous visiterez le site.

## 🎨 Modes Disponibles

### 🌙 Mode Sombre (Par Défaut)
- **Fond**: Très sombre pour moins fatiguer les yeux la nuit
- **Texte**: Blanc éclatant pour une lisibilité parfaite
- **Couleurs d'accent**: Garnet (#8B1538) et Bleu Royal (#4169E1)
- **Idéal pour**: Utilisation nocturne, faible luminosité

**Avantages:**
- ✅ Réduit la fatigue oculaire
- ✅ Économise batterie (écrans OLED)
- ✅ Élégant et moderne
- ✅ Pré-configuré pour le travail en conditions sombres

### ☀️ Mode Clair
- **Fond**: Blanc et gris clair
- **Texte**: Noir/gris foncé pour lire facilement
- **Couleurs d'accent**: Identiques (Garnet + Bleu Royal)
- **Idéal pour**: Bureau bien éclairé, impression, présentation

**Avantages:**
- ✅ Haute lisibilité en lumière naturelle
- ✅ Professionnel pour présenter à des collègues
- ✅ Meilleur contraste selon certains standards
- ✅ Familier pour les utilisateurs traditionnels

## ⚙️ Contrôle Automatique

Le système détecte également votre **préférence système** :
- Si vous ne l'avez jamais changée manuellement
- Il utilisera le réglage de votre OS (Windows/Mac/Linux)
- Cela change automatiquement à jour/nuit selon votre système

**Comment vérifier sur Windows 10/11:**
1. Paramètres → Personnalisation → Couleurs
2. Choisir "Mode sombre" ou "Mode clair"
3. EPI Detection utilisera cette préférence

## 💾 Où sont Mes Données ?

Votre choix est stocké dans le **navigateur uniquement**:
- Pas envoyé au serveur
- Pas partagé avec d'autres sites
- Persiste entre les sessions
- Peut être réinitialisé en vidant le cache

**Pour réinitialiser:**
1. Ouvrir les outils de développement (F12)
2. Console → Taper: `localStorage.clear()`
3. Recharger la page

## 🎯 Commandes Clavier (Pour Développeurs)

Si vous êtes un développeur, ouvrez la Console (F12) et utilisez:

```javascript
// Basculer le thème
toggleTheme()

// Vérifier le thème actuel
themeToggle.isDarkMode()  // Retourne true/false

// Forcer le mode sombre
themeToggle.setDarkMode(true)

// Forcer le mode clair
themeToggle.setDarkMode(false)

// Vérifier la préférence sauvegardée
localStorage.getItem('theme-mode')
```

## 🌐 Compatibilité Navigateurs

| Navigateur | Support | Notes |
|-----------|---------|-------|
| Chrome/Edge | ✅ | Support complet |
| Firefox | ✅ | Support complet |
| Safari | ✅ | Support complet |
| Opera | ✅ | Support complet |
| IE 11 | ⚠️ | Basique (pas localStorage) |
| Mobile Safari | ✅ | Support complet |
| Chrome Android | ✅ | Support complet |

## ❓ Questions Fréquemment Posées

### Q: Mon choix est perdu après fermeture
**A:** Vérifiez que localStorage n'est pas désactivé. Certains navigateurs en mode privé le désactivent.

### Q: Pourquoi le site change tout seul de thème?
**A:** Vous avez probablement changé la préférence système (Windows/Mac). Cliquez sur le bouton pour le changer manuellement.

### Q: Peut-on avoir un calendrier jour/nuit?
**A:** C'est une feature future! Pour l'instant, vous devez changer manuellement.

### Q: Tous les éléments s'adaptent?
**A:** Oui! Dashboard, graphiques, tableaux, formulaires... tout s'adapte automatiquement.

### Q: Est-ce que c'est accessible?
**A:** Oui! Les contrastes respectent les standards WCAG AA pour la lisibilité.

### Q: Ça ralentit le site?
**A:** Non! Zéro impact de performance. Les changements sont instantanés.

## 🎨 Palette de Couleurs

Les deux modes utilisent les **mêmes couleurs** pour les accents:

| Couleur | Code | Utilisation |
|---------|------|------------|
| Garnet | #8B1538 | Primaire, boutons |
| Bleu Royal | #4169E1 | Secondaire, liens |
| Vert Teal | #4bc0a8 | Succès, positif |
| Orange | #ffa500 | Avertissement |
| Rouge | #ff6b6b | Danger, erreur |

## 🚀 Conseils d'Utilisation

1. **Travail nocturne?** → Mode sombre (économise batterie sur portable)
2. **Présentation?** → Mode clair (plus professionnel)
3. **Impression?** → Mode clair (économise l'encre)
4. **Lunettes anti-lumière?** → Mode sombre (réduit le bleu)

## 📱 Sur Mobile

Le bouton toggle fonctionne identiquement:
- Visible sur petit écran
- Tap pour basculer
- Choix sauvegardé
- Transitions fluides

## ♿ Accessibilité

- ✅ Contraste texte OK dans les deux modes
- ✅ Compatibilité lecteur d'écran
- ✅ Clavier navigable
- ✅ Support mode réduit si disponible

## 🔍 Troubleshooting

| Problème | Solution |
|----------|----------|
| Thème ne sauvegarde pas | Vérifier localStorage (F12 → Application → Storage) |
| Bouton invisible | Scroller la navbar à droite sur mobile |
| Transitions saccadées | Vérifier GPU acceleration (généralement OK) |
| Mauvais contraste | Report bug avec screenshot |

## 💡 Astuce Pro

Vous pouvez créer un **raccourci clavier** personnalisé:
1. Paramètres navigateur
2. Chercher "raccourcis"
3. Créer: `javascript:toggleTheme()` avec raccourci de votre choix

## 📞 Support

Rencontrez un problème?
1. Vérifiez cette page (FAQ)
2. Videz le cache (Ctrl+Shift+Delete)
3. Réessayez dans un autre navigateur
4. Contactez support: contact@epi-detection.com

## 🎓 En Savoir Plus

Pour les utilisateurs techniques:
- Lire `THEME_GUIDE.md` pour la documentation complète
- Consulter `THEME_SYSTEM.md` pour les APIs développeurs
- Voir `IMPLEMENTATION_SUMMARY.md` pour les détails techniques

---

**Version**: 1.0  
**Mis à jour**: 17 Décembre 2025  

Profitez du système de thème! 🌟
