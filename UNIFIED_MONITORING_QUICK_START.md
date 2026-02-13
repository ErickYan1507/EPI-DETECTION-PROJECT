# 🎯 Guide Rapide - Unified Monitoring v2.1

## 🚀 Démarrage Rapide

### 1️⃣ Accéder à la Page
```
http://localhost:5000/unified
```

### 2️⃣ Démarrer la Caméra
Cliquer sur **▶️ Démarrer Webcam**
- Autoriser l'accès à la caméra
- Attendre 2-3 secondes pour initialisation

### 3️⃣ Observer les Détections
- Les **boîtes englobantes colorées** apparaissent autour des objets détectés
- La **liste en direct** s'actualise à droite
- Les **statistiques** se mettent à jour en temps réel

---

## 📹 Interface Utilisateur

### Layout Unified (3 Colonnes)

```
┌─────────────────────────────────────────────────────────────┐
│ 🎥 Flux Caméra │ 🔍 Détections │ ⚠️ Alertes + Stats       │
│   en Direct    │  en Temps Réel  │   et Infos              │
├────────────────┼─────────────────┼────────────────────────┤
│                │                 │                         │
│  [Video]       │ 👤: 5 personnes │ 📊 FPS: 30            │
│  [Detections]  │ 🪖: 4 casques   │ ⏱️ Inférence: 45ms    │
│                │ 🟧: 3 gilets    │ 📈 Conformité: 80%    │
│  ▶️ Start      │ 👓: 1 lunette   │                        │
│  ⏹️ Stop       │ 👢: 2 bottes    │ Détections:           │
│  📸 Capture    │                 │ #1 🪖 Casque 95%      │
│                │ Détails:        │ #2 🟧 Gilet 87%       │
│                │ #1 🪖 Casque    │ #3 👤 Personne 92%    │
│                │ #2 🟧 Gilet     │                        │
│                │ #3 👤 Personne  │ 🔊 Audio: [ON]       │
│                │ #4 👓 Lunette   │ [Test] [Effacer]      │
│                │ #5 👢 Bottes    │                        │
│                │                 │                        │
│                │ +3 détections   │                        │
│                │                 │                        │
└────────────────┴─────────────────┴────────────────────────┘
```

---

## 🎨 Code Couleur Détections

| Classe | Emoji | Couleur | Utilisation |
|--------|-------|---------|------------|
| 🪖 Casque | 🪖 | 🟢 Vert | Protection tête |
| 🟧 Gilet | 🟧 | 🟠 Orange | Protection torse |
| 👓 Lunettes | 👓 | 🔵 Cyan | Protection yeux |
| 👤 Personne | 👤 | 🟣 Indigo | Détection générale |
| 👢 Bottes | 👢 | 🟣 Violet | Protection pieds |

---

## 📊 Détails des Boîtes Englobantes

### Structure Visuelle
```
     ┌─ Ombre (noir transparent)
     │  ┌─ Cadre Principal (couleur classe)
     │  │  ┌─ Cadre Interne (pointillé)
     │  │  │
     │  │  │  ┌──────────────────────────┐
     │  │  │  │ 🪖 Casque │ 95%  │ ①   │ ← Label avec confiance
     │  │  │  └──────────────────────────┘
     │  │  │
     │  │  │  [Objet Détecté]
     │  │  │
     │  │  └─ Coins stylisés (larges)
     │  └─ Bordure épaisse (adaptée taille)
     └─ Ombre portée (meilleur contraste)
```

### Informations Affichées
- **Emoji**: Identifie rapidement la classe
- **Label**: Nom complet de la classe
- **Confiance**: Pourcentage (ex: 95%)
- **Numéro**: ID de détection (#1, #2, etc.)

---

## ⚙️ Modes de Détection

### Mode Single (best.pt)
- Modèle unique rapide
- Idéal pour FPS élevé
- Sélectionner: `Mode: Single (best.pt)`

### Mode Ensemble
- Multi-modèles pour précision
- Plus lent mais plus exact
- Sélectionner: `Mode: Ensemble (Multi-Modèles)`

---

## 🎮 Contrôles

### Boutons Caméra
| Bouton | Action | Raccourci |
|--------|--------|-----------|
| ▶️ Démarrer | Lance le flux caméra | - |
| ⏹️ Arrêter | Arrête le flux caméra | - |
| 📸 Capture | Télécharge l'image actuelle | - |

### Boutons Alertes
| Bouton | Action |
|--------|--------|
| 🔊 Test | Test l'alerte audio |
| 🗑️ Effacer | Efface l'historique d'alertes |

---

## 📊 Statistiques en Temps Réel

### Compteurs Principaux
```
👤 Personnes: 5      ← Total de personnes détectées
🪖 Casques: 4        ← Avec équipement de tête
🟧 Gilets: 3         ← Avec équipement torse
👓 Lunettes: 1       ← Avec protection yeux
👢 Bottes: 2         ← Avec protection pieds
```

### Métriques Performance
```
📊 FPS: 30           ← Images par seconde (cible)
⏱️ Inférence: 45ms   ← Temps de traitement
📈 Conformité: 80%   ← Pourcentage d'équipement
```

---

## 🔧 Dépannage Rapide

### Problème: Flux Caméra Noir
**Solution:**
1. Vérifier permissions caméra
2. Cliquer "Arrêter" puis "Démarrer"
3. Attendre 3 secondes
4. Relancer page si besoin

### Problème: Pas de Détections
**Solution:**
1. S'assurer objet dans le cadre
2. Augmenter lumière
3. Essayer mode "Single"
4. Vérifier API `/api/detect`

### Problème: FPS Faible
**Solution:**
1. Utiliser mode "Single"
2. Réduire résolution caméra
3. Arrêter autres applications
4. Vérifier GPU/CPU

### Problème: Liste Détections Figée
**Solution:**
1. Arrêter caméra
2. Actualiser page (F5)
3. Relancer détection

---

## 🎯 Cas d'Usage

### ✅ Inspection de Chantier
1. Démarrer flux caméra
2. Pointer chaque travailleur
3. Observer conformité (couleur/%).
4. Noter les non-conformités

### ✅ Rapport d'Audit
1. Capture écran avec boîtes
2. Export statistiques
3. Créer rapport temps réel

### ✅ Formation Équipe
1. Montrer détections en direct
2. Expliquer couleurs et confiance
3. Démontrer importance équipement

---

## 💡 Conseils Pratiques

### Pour Meilleures Détections:
- ✅ Bonne illumination
- ✅ Caméra stable
- ✅ Distance 1-3 mètres
- ✅ Angle frontal
- ✅ Équipement visible

### Pour Performance Optimale:
- ✅ Mode "Single" pour vidéo
- ✅ Mode "Ensemble" pour upload
- ✅ Intervalle détection: 1500ms
- ✅ Max 5 détections affichées

---

## 🔄 Cycle de Détection

```
1. Capture Frame      [50ms]
   ↓
2. Conversion JPEG    [20ms]
   ↓
3. API /api/detect    [45ms]
   ↓
4. Traitement résult  [10ms]
   ↓
5. Affichage UI       [5ms]
   ↓
Cycle = 1500ms (0.67 Hz)
```

---

## 📞 Contacts Support

- **Erreur API**: Vérifier serveur Flask
- **Permissions**: Vérifier paramètres navigateur
- **Performance**: Vérifier ressources système
- **Détections**: Vérifier modèle et données

---

## 🎓 Comprendre Confiance

La **confiance** (%) indique la certitude du modèle:

- **90-100%** 🟢 Excellent - Faire confiance
- **80-89%** 🟡 Bon - Généralement fiable
- **70-79%** 🟠 Moyen - Vérifier visuellement
- **<70%** 🔴 Faible - Ne pas considérer

---

## 📱 Responsive Design

Interface s'adapte à l'écran:
- **Large (>1600px)**: 3 colonnes
- **Medium (1200-1600px)**: 2 colonnes
- **Small (<1200px)**: 1 colonne

---

**Dernière mise à jour:** 30 Janvier 2026  
**Version:** 2.1  
**Statut:** ✅ Prêt pour production

*Consulter UNIFIED_MONITORING_IMPROVEMENTS.md pour détails techniques*
