# Système de Thème (Mode Sombre/Clair)

## 📋 Vue d'ensemble

Le projet EPI Detection dispose d'un système de thème complet permettant aux utilisateurs de basculer entre un mode sombre et un mode clair.

## 🎨 Fichiers du Système

### 1. **static/js/theme-toggle.js**
- Classe `ThemeToggle` : Gère le basculement du thème
- Stocke les préférences dans `localStorage`
- Respecte les préférences système (`prefers-color-scheme`)
- Déclenche un événement personnalisé `themechange`

### 2. **static/css/theme.css**
- Variables CSS pour les deux modes
- Styles spécifiques au thème
- Transitions fluides (0.3s)
- Support pour tous les éléments (inputs, buttons, tables, etc.)

### 3. **static/css/modern-glassmorphism.css**
- Design glassmorphism avec support du thème
- Adaptations pour le mode clair
- Styles hover et interactions

### 4. **templates/base.html**
- Bouton de toggle en haut à droite
- Initialisé avec le thème système par défaut
- Styles inline pour les transitions fluides

## 🔧 Utilisation

### Basculer le thème manuellement
```javascript
toggleTheme();  // Bascule entre sombre et clair
```

### Vérifier le thème actuel
```javascript
themeToggle.isDarkMode()  // Retourne true/false
```

### Définir un thème spécifique
```javascript
themeToggle.setDarkMode(true);   // Force le mode sombre
themeToggle.setDarkMode(false);  // Force le mode clair
```

### Écouter les changements de thème
```javascript
window.addEventListener('themechange', (event) => {
    if (event.detail.isDark) {
        console.log('Mode sombre activé');
    } else {
        console.log('Mode clair activé');
    }
});
```

## 🎯 Palette de Couleurs

### Mode Sombre
- **Background Primaire**: `#0F1419`
- **Background Secondaire**: `#1A1F2E`
- **Background Tertiaire**: `#252D3D`
- **Texte Primaire**: `#FFFFFF`
- **Texte Secondaire**: `#D0D0D0`
- **Texte Tertiaire**: `#888888`
- **Bordures**: `rgba(255,255,255,0.1)`

### Mode Clair
- **Background Primaire**: `#F8F9FA`
- **Background Secondaire**: `#FFFFFF`
- **Background Tertiaire**: `#F0F2F5`
- **Texte Primaire**: `#1A1A1A`
- **Texte Secondaire**: `#4A4A4A`
- **Texte Tertiaire**: `#999999`
- **Bordures**: `rgba(0,0,0,0.1)`

### Couleurs Constantes (Les Deux Modes)
- **Garnet (Primaire)**: `#8B1538`
- **Royal Blue (Secondaire)**: `#4169E1`
- **Succès**: `#4bc0a8`
- **Avertissement**: `#ffa500`
- **Danger**: `#ff6b6b`

## 📊 Variables CSS Disponibles

```css
--bg-primary       /* Couleur de fond principale */
--bg-secondary     /* Couleur de fond secondaire */
--bg-tertiary      /* Couleur de fond tertiaire */
--text-primary     /* Couleur de texte principale */
--text-secondary   /* Couleur de texte secondaire */
--text-tertiary    /* Couleur de texte tertiaire */
--border-color     /* Couleur des bordures */
--glass-bg         /* Fond glassmorphe */
--color-primary    /* Garnet */
--color-secondary  /* Royal Blue */
--color-success    /* Vert */
--color-warning    /* Orange */
--color-danger     /* Rouge */
```

## 🔄 Persistance des Données

Le thème choisi est sauvegardé dans `localStorage` avec la clé `theme-mode`:
- Valeur: `'dark'` ou `'light'`
- Persiste entre les sessions de navigation
- Peut être supprimé manuellement : `localStorage.removeItem('theme-mode')`

## 🎬 Transitions Fluides

Tous les changements de couleur ont une transition de 0.3s pour une expérience douce :
```css
transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
```

## 🔐 Respect des Préférences Système

Si l'utilisateur n'a jamais choisi de thème :
1. Le système détecte la préférence : `prefers-color-scheme: dark`
2. Applique le thème correspondant par défaut
3. L'utilisateur peut toujours le changer manuellement

## 📱 Responsivité

Le bouton de toggle :
- Se redimensionne sur mobile
- Accessible via la navigation repliée (navbar collapse)
- Conserve la même fonctionnalité à tous les breakpoints

## ✨ Intégration avec Chart.js

Les graphiques Chart.js s'adaptent automatiquement au thème :
- Couleurs des axes changent selon le thème
- Mode clair applique `filter: brightness(1.1)` pour la lisibilité
- Les labels restent lisibles dans les deux modes

## 🚀 Performance

- Pas de requête réseau pour les préférences
- Stockage local via `localStorage` (très rapide)
- Pas d'animation de charge visible lors du basculement
- Transitions CSS matérialisées (pas JavaScript lourd)

## 🐛 Dépannage

### Le thème ne change pas ?
1. Vérifier la console pour les erreurs
2. S'assurer que `theme-toggle.js` est chargé avant le contenu
3. Vérifier que `localStorage` est activé dans le navigateur

### Les couleurs ne s'appliquent pas ?
1. Vérifier que `theme.css` est chargé après le HTML
2. S'assurer que les variables CSS sont bien définies
3. Vérifier que la classe `dark-mode` ou `light-mode` est appliquée au `<body>`

### Modifier le système ?
Tous les fichiers CSS sont configurables :
- Ajouter des variables dans `:root`
- Modifier les valeurs dans `body.light-mode`
- Ajouter des transitions dans les sélecteurs spécifiques
