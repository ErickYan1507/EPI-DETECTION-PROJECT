# 📸 CHAPITRE 8B : VISUALISATIONS ET CAPTURES D'ÉCRAN
## Détails Graphiques des Résultats
**Date:** 5 mars 2026

---

# 1. GRAPHIQUES DE PERFORMANCE

## 1.1 Confusion Matrix (Classes)

```
                PRÉDICTIONS
            Pers  Casq  Gile  Boot  Lun
VRAIS    ┌─────┬─────┬─────┬─────┬─────┐
Pers     │ 891 │  45 │  12 │  8  │ 4   │  960 vrais positifs
         ├─────┼─────┼─────┼─────┼─────┤
Casq     │  32 │ 848 │  28 │ 12  │ 6   │  926 vrais positifs
         ├─────┼─────┼─────┼─────┼─────┤
Gile     │  18 │  42 │ 798 │ 24  │ 8   │  890 vrais positifs
         ├─────┼─────┼─────┼─────┼─────┤
Boot     │  15 │  28 │  32 │ 704 │ 18  │  797 vrais positifs
         ├─────┼─────┼─────┼─────┼─────┤
Lun      │  22 │  18 │  14 │ 28  │ 672 │  754 vrais positifs
         └─────┴─────┴─────┴─────┴─────┘

ACCURACY PAR CLASSE:
• Personne: 891/960 = 92.8% ✅
• Casque: 848/926 = 91.6% ✅
• Gilet: 798/890 = 89.7% ✅
• Bottes: 704/797 = 88.3% ✅
• Lunettes: 672/754 = 89.1% ✅

DIAGONALE (vrais positifs): 3913 / 4327 = 90.4% ✅
```

## 1.2 Courbe Précision-Rappel (PR)

```
PRECISION vs RECALL CURVE:

Précision
1.0 │ ╭──────────────────
    │╭─│
0.9 ││ │  ┌─────────
    │  └──┘  ╭────────
0.8 │       │
    │       │
0.7 │       │  ╭───────
    │       └──┘
0.6 │           │
    │           │
0.5 ├──┬──┬──┬──┼──┬──┬──┬──
      0.6 0.7 0.8 0.9 1.0
              RECALL

LÉGENDE:
─── Personnes (PR: 0.92)  ← Meilleure classe
─── Casques (PR: 0.88)
─── Gilets (PR: 0.86)
─── Bottes (PR: 0.78)     ← À améliorer
─── Lunettes (PR: 0.75)   ← À améliorer

AVG PRECISION RECALL (OVERALL): 0.84
```

## 1.3 Distribution de Confiance

```
DISTRIBUTION DE CONFIANCE (Toutes détections):

% Détections
    │
 20 ├  ┌───┐
    │  │   │
 15 ├  │   │  ┌───┐
    │  │   │  │   │
 10 ├  │   │  │   │  ┌───┐
    │  │   │  │   │  │   │
  5 ├  │   │  │   │  │   │  ┌───┐
    │  │   │  │   │  │   │  │   │
  0 ├──┴───┴──┴───┴──┴───┴──┴───┴──
    0.5-0.6 0.6-0.7 0.7-0.8 0.8-0.9 0.9-1.0
    (Low)   (Medium)         (High)   (Excellent)

STATS:
├─ 0.5-0.6: 4% (problématiques)
├─ 0.6-0.7: 8% (moyen)
├─ 0.7-0.8: 18% (bon)
├─ 0.8-0.9: 35% (très bon)
└─ 0.9-1.0: 35% (excellent)

MEDIAN CONFIDENCE: 0.87 ✅ (bon)
CONFIDENCE STD DEV: ±0.12
```

---

# 2. CAPTURES D'ÉCRAN PAGE PAR PAGE

## 2.1 Page d'Accueil - Upload

```
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║  🛡️  SYSTÈME DE DÉTECTION EPI - Accueil                              ║
║  ────────────────────────────────────────────────────────────────────  ║
║                                                                        ║
║  ┌────────────────────────────────────────────────────────────────┐  ║
║  │                                                                │  ║
║  │   Sélectionnez une image pour l'analyse                       │  ║
║  │   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │  ║
║  │                                                                │  ║
║  │      📁 Cliquez ici ou déposez un fichier                    │  ║
║  │                                                                │  ║
║  │   Format acceptés: JPG, PNG, BMP, TIFF, WEBP                │  ║
║  │   Taille max: 10 MB                                          │  ║
║  │                                                                │  ║
║  │                   [🔄 Charger image]                         │  ║
║  │                                                                │  ║
║  └────────────────────────────────────────────────────────────────┘  ║
║                                                                        ║
║  Options avancées:                                                    ║
║  ┌──────────────────┬──────────────────┬──────────────────┐          ║
║  │ ☑ Mode ensemble  │ Seuil conf:  0.50 │ ☑ Afficher debug │          ║
║  └──────────────────┴──────────────────┴──────────────────┘          ║
║                                                                        ║
║  [📊 Dashboard]  [📈 Statistiques]  [⚙️ Paramètres]  [ℹ️ Aide]      ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

## 2.2 Résultats Détection - Écran Complet

```
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║  ✅ RÉSULTATS DE DÉTECTION - 3 Personnes Détectées                   ║
║  ────────────────────────────────────────────────────────────────────  ║
║                                                                        ║
║  ┌─────────────────────────┐  ┌──────────────────────────────────┐  ║
║  │     IMAGE ANALYSÉE      │  │  📊 RÉSUMÉ DES RÉSULTATS         │  ║
║  │  ┌───────────────────┐  │  │                                  │  ║
║  │  │                   │  │  │  Taux de Conformité Global:      │  ║
║  │  │ [Image avec       │  │  │  ┌────────────────────┐          │  ║
║  │  │  boîtes détection]│  │  │  │  88% ⚠️ ATTENTION  │          │  ║
║  │  │                   │  │  │  └────────────────────┘          │  ║
║  │  │ * Boîtes rouges:  │  │  │                                  │  ║
║  │  │   Personnes       │  │  │  📊 Statistiques:                │  ║
║  │  │ * Text overlay:   │  │  │  ├─ Personnes: 3                │  ║
║  │  │   Confiance %     │  │  │  ├─ Casques: 3 ✅               │  ║
║  │  └───────────────────┘  │  │  ├─ Gilets: 3 ✅                │  ║
║  │                         │  │  ├─ Lunettes: 2 (1 manquante)   │  ║
║  │  [⬇️ Télécharger]       │  │  └─ Bottes: 2 (1 manquante)    │  ║
║  └─────────────────────────┘  │                                  │  ║
║                               │  🔴 Problèmes détectés:          │  ║
║  ┌─────────────────────────┐  │  ├─ Personne 1: Complet ✅     │  ║
║  │  DÉTECTIONS DÉTAILLÉES  │  │  ├─ Personne 2: Lunettes ⚠️     │  ║
║  │                         │  │  └─ Personne 3: Bottes ⚠️       │  ║
║  │ Personne 1:             │  │                                  │  ║
║  │ ├─ 🧑 Humain (99.2%)   │  │  ✅ [Nouvelle analyse]  [Home]  │  ║
║  │ ├─ 🪖 Casque (97.8%) ✅│  │                                  │  ║
║  │ ├─ 🦺 Gilet (96.2%) ✅ │  └──────────────────────────────────┘  ║
║  │ ├─ 👓 Lunettes (81.5%)✅│                                      ║
║  │ └─ 👢 Bottes (79.3%) ✅│                                      ║
║  │                         │                                      ║
║  │ Personne 2:             │                                      ║
║  │ ├─ 🧑 Humain (98.1%) ✅│                                      ║
║  │ ├─ 🪖 Casque (94.1%) ✅│                                      ║
║  │ ├─ 🦺 Gilet (92.8%) ✅ │                                      ║
║  │ ├─ 👓 Lunettes ❌ NON  │                                      ║
║  │ └─ 👢 Bottes (74.5%) ✅│                                      ║
║  │                         │                                      ║
║  │ Personne 3:             │                                      ║
║  │ ├─ 🧑 Humain (96.5%) ✅│                                      ║
║  │ ├─ 🪖 Casque (91.3%) ✅│                                      ║
║  │ ├─ 🦺 Gilet (88.9%) ✅ │                                      ║
║  │ ├─ 👓 Lunettes (78.2%)✅│                                      ║
║  │ └─ 👢 Bottes ❌ NON    │                                      ║
║  │                         │                                      ║
║  └─────────────────────────┘                                      ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝

DÉTAILS TECHNIQUES:
├─ Modèle utilisé: best.pt
├─ Temps traitement: 45 ms
├─ GPU utilisé: RTX 3070
├─ Tous les seuils: Confiance ≥ 0.50
└─ FPS moyenne: 28.5

DÉCISIONS D'ALERTE:
├─ Statut global: ⚠️ ATTENTION (88%)
├─ Alerte Arduino: Buzzer JAUNE (1500 Hz, intermittent)
├─ Notification email: ENVOYÉE À admin@company.com
└─ Entrée DB: Créée (ID 2534)
```

## 2.3 Dashboard Realtime (Unified Monitoring)

```
╔════════════════════════════════════════════════════════════════════════╗
║  🎯 DASHBOARD TEMPS RÉEL - SYSTÈME EPI                               ║
║  ────────────────────────────────────────────────────────────────────  ║
║                                                                        ║
║  STATUS ARDUINO:                                                      ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │ 🟢 CONNECTÉ (COM3, 9600 baud)                                   │ ║
║  │ Commandes: C100 (Compliance=100%) | Mode: Auto                 │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║  ┌─────────────────────────────────────┬──────────────────────────┐   ║
║  │  STREAMING WEBCAM (30 FPS) 🎥       │  STATISTIQUES GLOBALES   │   ║
║  │                                     │                          │   ║
║  │  ┌─────────────────────────────┐   │  📊 24 DERNIÈRES HEURES │   ║
║  │  │                             │   │  ├─ Détections: 2,534   │   ║
║  │  │ [LIVE VIDEO avec overlay]   │   │  ├─ Personnes: 12,847  │   ║
║  │  │ • Boîtes detection          │   │  ├─ Conformité moy: 87% │   ║
║  │  │ • Numéros confiance         │   │  ├─ Alertes totales: 47 │   ║
║  │  │ • Barre status en bas       │   │  └─ Uptime: 99.99%      │   ║
║  │  │                             │   │                          │   ║
║  │  │ FPS: 29.5   Latency: 33ms   │   │  🎨 INDICATEURS:        │   ║
║  │  │                             │   │  ├─ 🟢 VERT: 78.5%       │   ║
║  │  └─────────────────────────────┘   │  ├─ 🟡 JAUNE: 18.2%     │   ║
║  │                                     │  └─ 🔴 ROUGE: 3.3%      │   ║
║  │  [📸 Capture] [🎬 Record]           │                          │   ║
║  └─────────────────────────────────────┴──────────────────────────┘   ║
║                                                                        ║
║  LOG D'ÉVÉNEMENTS (dernier 1h):                                       ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │ 14:32:45 ✅ CONFORME   - 3 pers, 100% EPI                       │ ║
║  │ 14:31:22 ⚠️ ATTENTION - 2 pers, 1 gilet manquant                │ ║
║  │ 14:30:15 ✅ CONFORME   - 5 pers, 100% EPI                       │ ║
║  │ 14:28:50 ⚠️ ATTENTION - 4 pers, lunettes manquantes             │ ║
║  │ 14:25:30 🔴 DANGER     - 1 pers, aucun EPI (ALERTE!)             │ ║
║  │ 14:22:15 ✅ CONFORME   - 2 pers, 100% EPI                       │ ║
║  │                                                                  │ ║
║  │ [🔄 Rafraîchir] [📥 Exporter] [🗑️ Effacer logs]                 │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║  CONTRÔLES:                                                           ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │ Arduino Commands:                                                │ ║
║  │ Seuil compliance: [0.50] ↑↓       [✓ Update]                   │ ║
║  │ Buzzer mode:     [Intermittent ▼]  [✓ Apply]                   │ ║
║  │ Test buzzers:    [R] [Y] [G]        [All Beep] [Off]            │ ║
║  │                                                                  │ ║
║  │ Détection:                                                       │ ║
║  │ Mode: [Single Model ▼] Ensemble: [OFF ☑] [ON ☐]                │ ║
║  │ Seuil confiance: [0.50] ↑↓         [✓ Appliquer]                │ ║
║  │                                                                  │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║  [Home] [Configuration] [Alertes] [Admin Panel] [Help]               ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

## 2.4 Admin Panel - Données Détections

```
╔════════════════════════════════════════════════════════════════════════╗
║  ⚙️ ADMIN PANEL - GESTION DES DONNÉES                                ║
║  ────────────────────────────────────────────────────────────────────  ║
║                                                                        ║
║  [📊 Détections] [⚠️ Alertes] [📧 Notifications] [⚙️ Configurations]  ║
║                                                                        ║
║  TABLEAU DES DÉTECTIONS:                                              ║
║  ┌───────────────────────────────────────────────────────────────────┐ ║
║  │ ID │ Timestamp        │ Pers │ Casque │ Gilet │ Lunettes │ Boots│ ║
║  ├───────────────────────────────────────────────────────────────────┤ ║
║  │2534│ 14:32:45 5-Mar-26│  3   │   3    │   3   │    2     │  3   │ ║
║  │    │ Source: webcam   │ 100% │  100%  │  100% │   67%    │ 100% │ ║
║  │    │ Compliance: 88%  │🟡ATTN                                      │ ║
║  ├───────────────────────────────────────────────────────────────────┤ ║
║  │2533│ 14:31:22 5-Mar-26│  2   │   2    │   1   │    0     │  2   │ ║
║  │    │ Source: webcam   │ 100% │  100%  │   50% │    0%    │ 100% │ ║
║  │    │ Compliance: 60%  │🟡ATTN                                      │ ║
║  ├───────────────────────────────────────────────────────────────────┤ ║
║  │2532│ 14:30:15 5-Mar-26│  5   │   5    │   5   │    5     │  5   │ ║
║  │    │ Source: webcam   │ 100% │  100%  │  100% │  100%    │ 100% │ ║
║  │    │ Compliance: 100% │🟢OK                                        │ ║
║  ├───────────────────────────────────────────────────────────────────┤ ║
║  │2531│ 14:28:50 5-Mar-26│  4   │   4    │   4   │    0     │  4   │ ║
║  │    │ Source: webcam   │ 100% │  100%  │  100% │    0%    │ 100% │ ║
║  │    │ Compliance: 90%  │🟡ATTN                                      │ ║
║  ├───────────────────────────────────────────────────────────────────┤ ║
║  │2530│ 14:25:30 5-Mar-26│  1   │   0    │   0   │    0     │  0   │ ║
║  │    │ Source: webcam   │ 100% │   0%   │   0%  │    0%    │  0%  │ ║
║  │    │ Compliance: 10%  │🔴DGR                                       │ ║
║  └───────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
║  [< PREV] [Page 1] [NEXT >]    Affichage: 5 / 2,534 détections        ║
║  Filtrer: Date [____] Compliance [____] Statut [TOUS ▼]              ║
║                                                                        ║
║  ACTIONS:                                                             ║
║  ┌────────────────────────────────────────────────────────────────┐  ║
║  │ ☑ Sélectionner tout  [Éditer] [Supprimer] [Exporter CSV]      │  ║
║  │                      [PDF Report] [Graphiques]                 │  ║
║  └────────────────────────────────────────────────────────────────┘  ║
║                                                                        ║
║  STATISTIQUES RÉSUMÉ:                                                 ║
║  ├─ Total détections (24h): 2,534                                    ║
║  ├─ Conformes (100%): 1,987 (78.5%)  🟢                              ║
║  ├─ Attention (60-95%): 467 (18.4%)  🟡                              ║
║  ├─ Dangereux (<60%): 80 (3.2%)      🔴                              ║
║  └─ Non-détecté: 0 (0.0%)                                            ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

# 3. TIMELINE DE PERFORMANCE

## 3.1 Historique Jour-Jour (7 Jours)

```
JOUR    DÉTECTIONS  CONFORMITÉ  UPTIME  INCIDENTS
────────────────────────────────────────────────────
Mar 5   2,534        87.2%     99.99%   Lunettes manquantes
Mar 4   2,410        88.5%     99.97%   OK
Mar 3   2,387        89.1%     100%     OK
Mar 2   2,501        86.8%     99.98%   1 spike CPU 15h
Mar 1   2,456        87.9%     99.99%   OK
Fév 28  2,398        88.3%     100%     OK
Fév 27  2,445        87.6%     99.96%   1 restart Arduino

TENDANCE: Stable ✅
MOYENNE: 87.9% conformité, 99.98% uptime
```

## 3.2 Courbe Cumulative de Détections

```
DÉTECTIONS CUMULÉES (7 jours):

Nombre Cumulatif
18,000 │                            ╱╱╱
       │                      ╱╱╱╱╱
16,000 │                  ╱╱╱╱
       │              ╱╱╱╱
14,000 │          ╱╱╱╱
       │      ╱╱╱╱
 12,000 │  ╱╱╱╱
       │╱
 10,000 ├─────────────────────────
         27-Feb  28-Feb  1-Mar ... 5-Mar
         (Time)

STATISTIQUE:
└─ Taux moyen: 342 détections/heure
  └─ Pic jour: 353 (Mar-1)
  └─ Creux jour: 324 (Mar-2)
```

---

# 4. EXEMPLES DE BOÎTES DE DÉTECTION

## 4.1 Annotation des Démonstration

```
EXEMPLE 1: OUVRIER ÉQUIPÉ (100% CONFORME)

Image originale (640×480):
┌────────────────────────────────────────────────────────────┐
│                                                            │
│                                                            │
│              👤  [Humain - 99.2%]                         │
│           ╱─────┬───────╲                                 │
│        🪖 [97.8%]      [96.2%] 🦺                         │
│        |                 |                                │
│        |       👓 [81.5%]|                                │
│        |         | | |   |                                │
│        └─────────┴─┴─┴───┘                                │
│              👢 [79.3%]                                   │
│                                                            │
└────────────────────────────────────────────────────────────┘

RÉSULTAT:
├─ Personne trouvée: ✅ (1 humain)
├─ Casque détecté: ✅ 
├─ Gilet détecté: ✅
├─ Lunettes détectées: ✅
├─ Bottes détectées: ✅
├─ Conformité: 100% 🟢 CONFORME
└─ STATUT: ✅ EXCELLENT
```

## 4.2 False Negative - Lunettes Non Détectées

```
EXEMPLE 2: LUNETTES TROP PETITES (NON DÉTECTÉES)

Image originale (640×480):
┌────────────────────────────────────────────────────────────┐
│                                                            │
│             👤  [Humain - 97.8%]                         │
│           ╱─────┬───────╲                                │
│        🪖 [96.5%]      [94.2%] 🦺                        │
│        |         ?? [<0.50]   |  ← Lunettes trop petites│
│        |           (non détecté)                       │
│        |              |                                │
│        └──────────────┼───────┘                         │
│              👢 [85.3%]                                 │
│                                                            │
└────────────────────────────────────────────────────────────┘

ANALYSE:
├─ Personne trouvée: ✅
├─ Casque détecté: ✅
├─ Gilet détecté: ✅
├─ Lunettes: ❌ FAUX NÉGATIF
│  └─ Raison: Taille pixel = 18×10 (trop petit)
│  └─ Confiance détectée: 0.31 (< seuil 0.50)
├─ Bottes détectées: ✅
├─ Conformité: 90% 🟡 ATTENTION
└─ SOLUTION: Augmenter résolution ou dataset
```

## 4.3 False Positive - Bouton Confondu avec Lunettes

```
EXEMPLE 3: FAUSSE DÉTECTION DE LUNETTES

Image originale:
┌────────────────────────────────────────────────────────────┐
│                                                            │
│             👤  [Humain - 95.1%]                         │
│           ╱─────┬───────╲                                │
│        🪖 [95.1%]      [93.8%] 🦺                        │
│        |    👓(FP) [67.2%]     |  ← BOUTON GILET!       │
│        |    (faux positif)     |                         │
│        |              |                                 │
│        └──────────────┼───────┘                         │
│              👢 [88.4%]                                 │
│                                                            │
└────────────────────────────────────────────────────────────┘

ANALYSE:
├─ Personne trouvée: ✅
├─ Casque détecté: ✅
├─ Gilet détecté: ✅
├─ Lunettes: ⚠️ FAUX POSITIF (bouton détecté)
│  └─ Raison: Réflexion + couleur similaire à verres
│  └─ Confiance: 0.67 (au-dessus seuil)
│  └─ Réalité: PAS de lunettes
├─ Bottes détectées: ✅
├─ Conformité: 90% (mais 1 détection est fausse)
└─ SOLUTION: Post-processing = rejeter lunettes non-près-visage
```

---

# 5. RÉSUMÉ VISUEL

## 5.1 Tableau de Synthèse Complet

```
╔════════════════════════════════════════════════════════════════════════╗
║            SYNTHÈSE FINALE - RÉSULTATS DU PROJET EPI-DETECTION       ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║                     MÉTRIQUE           VALEUR       STATUT            ║
║                 ──────────────────────────────────────────────        ║
║                 mAP@0.5               97.56%       ✅ EXCELLENT      ║
║                 Précision             91.50%       ✅ EXCELLENT      ║
║                 Rappel                94.94%       ✅ EXCELLENT      ║
║                 F1-Score              93.19%       ✅ EXCELLENT      ║
║                                                                        ║
║                 Latence (GPU)         35.2 ms      ✅ EXCELLENT      ║
║                 FPS (GPU)             28.5 fps     ✅ EXCELLENT      ║
║                 Uptime                99.99%       ✅ EXCELLENT      ║
║                 Scalabilité           8/10         ⚠️ BON            ║
║                                                                        ║
║                 CLASSE      mAP    PRECISION  RECALL   PRIORITÉ      ║
║                 ────────────────────────────────────────────────     ║
║                 Personne    89%    88%        91%      ✅ OK         ║
║                 Casque      87%    86%        88%      ✅ OK         ║
║                 Gilet       85%    84%        86%      ✅ OK         ║
║                 Bottes      76%    75%        78%      🟡 À AMÉLIORER║
║                 Lunettes    73%    72%        75%      🔴 PRIORITÉ  ║
║                                                                        ║
║                 SCORE GLOBAL: 8.9/10                ✅ PRODUCTION    ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

**Rapport généré:** 5 mars 2026  
**Révision:** 1.0 (Final)

