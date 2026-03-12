# 🔌 Schéma de Branchement Arduino MEGA

## 📊 Vue d'ensemble des Connexions

```
Arduino MEGA
┌─────────────────────────────────────────────┐
│                                             │
│   ╔════════════════════════════════════╗   │
│   ║       ARDUINO MEGA 2560            ║   │
│   ╚════════════════════════════════════╝   │
│                                             │
│  Alimentation:                              │
│  ┌─ 5V  ←── Alimentation positive          │
│  └─ GND ←── Masse (0V)                      │
│                                             │
│  Ports Numériques (Signal):                 │
│  Pin 9   → BUZZER        [Sortie PWM]      │
│  Pin 26  → LED JAUNE     [Sortie Digital]  │
│  Pin 30  → LED ROUGE     [Sortie Digital]  │
│  Pin 36  → LED VERT      [Sortie Digital]  │
│                                             │
│  Port Série (Communication):                │
│  TX → Vers PC (via USB)                     │
│  RX → Depuis PC (via USB)                   │
│                                             │
└─────────────────────────────────────────────┘
```

## 🔴 Détails de Branchement par Composant

### 1. 🔊 BUZZER (Actif ou Passif)

#### Paramètres:
- **Port**: 9 (PWM)
- **Tension**: 5V
- **Intensité**: 40-200mA selon modèle

#### Branchement BUZZER ACTIF (le plus courant):
```
Buzzer Actif
    ⊕ (rouge)  → Pin 9 sur Arduino
    ⊖ (noir)   → GND sur Arduino
    
Connexion directe sans résistance
```

#### Branchement BUZZER PASSIF:
```
Buzzer Passif
    ⊕ (rouge)  → Pin 9 via résistance 220Ω → Arduino
    ⊖ (noir)   → GND
    
Résistance de protection
```

### 2. 🟢 LED VERT (Safe/Ok)

#### Paramètres:
- **Port**: 36
- **Couleur**: Vert
- **Tension directe**: 2V (LED standard)
- **Intensité**: 20mA

#### Branchement:
```
LED Vert
    ⊕ (Longue broche)  → Pin 36 via Résistance 220Ω → Arduino
    ⊖ (Courte broche)  → GND
    
[Arduino Pin 36] ─── [Résistance 220Ω] ───|>|─── [GND]
                                    LED Vert
```

### 3. 🟡 LED JAUNE (Warning/Attention)

#### Paramètres:
- **Port**: 26
- **Couleur**: Jaune
- **Tension directe**: 2V
- **Intensité**: 20mA

#### Branchement:
```
LED Jaune
    ⊕ (Longue broche)  → Pin 26 via Résistance 220Ω → Arduino
    ⊖ (Courte broche)  → GND
    
[Arduino Pin 26] ─── [Résistance 220Ω] ───|>|─── [GND]
                                    LED Jaune
```

### 4. 🔴 LED ROUGE (Danger/Stop)

#### Paramètres:
- **Port**: 30
- **Couleur**: Rouge
- **Tension directe**: 2V
- **Intensité**: 20mA

#### Branchement:
```
LED Rouge
    ⊕ (Longue broche)  → Pin 30 via Résistance 220Ω → Arduino
    ⊖ (Courte broche)  → GND
    
[Arduino Pin 30] ─── [Résistance 220Ω] ───|>|─── [GND]
                                    LED Rouge
```

## 🔌 Schéma Complet de Connexion

```
                    ALIMENTATION EXTERNE
                           |
                    ┌──────┴──────┐
                    │             │
                   5V            GND
                    │             │
    ┌───────────────┼─────────────┼──────────────┐
    │               │             │              │
    │        ┌──────┴─┐    ┌──────┴─┐            │
    │        │ Arduino│    │External│            │
    │        │ 5V In  │    │GND In  │            │
    │        └────────┘    └────────┘            │
    │                                            │
    │        Arduino MEGA 2560                   │
    │   ┌──────────────────────────┐             │
    │   │                          │             │
    │   │ Pin 36 (PWM) → LED VERT  │             │
    │   │ Pin 30 → LED ROUGE       │             │
    │   │ Pin 26 → LED JAUNE       │             │
    │   │ Pin 9 (PWM) → BUZZER     │             │
    │   │ GND → Masse (GND)        │             │
    │   │                          │             │
    │   └──────────────────────────┘             │
    │         │        │         │   │           │
    │         │        │         │   │           │
    │    ┌────┘   ┌────┘    ┌───┘   └───┐       │
    │    │        │         │           │       │
    │   R220Ω    R220Ω     R220Ω      270Ω    │
    │    │        │         │      (si passif)   │
    │   ┌┴┐      ┌┴┐       ┌┴┐        ┌──┐      │
    │   │|>| V  │|>| A   │|>| R     |~ ~| Buzzer│
    │   └┬┘      └┬┘       └┬┘        └──┘      │
    │    │        │         │           │       │
    └────┼────────┼─────────┼───────────┼──────┘
         │        │         │           │
         └────────┴─────────┴───────────┘
                      GND
```

## 📦 Liste des Composants Supplémentaires

### Résistances (protection des LEDs)
```
Composant: Résistance 220Ω (carbone ou film)
Tolérance: ±5%
Puissance: 1/4W minimum
Quantité: 3 (une par LED)

Code couleur (pour reconnaissance):
Anneau 1: Rouge (2)
Anneau 2: Rouge (2)
Anneau 3: Marron (×10)
Anneau 4: Or (±5%)
```

### Câbles
```
Câble Dupont femelle-femelle (opcional)
Ou soudure directe (préféré pour fiabilité)
```

## 🧪 Procédure de Test Manuel

### Avant de brancher l'Arduino:

1. **Vérifier les LEDs isolément** (avec batterie 5V):
   ```
   Batterie 5V
   Positif → Résistance 220Ω → Longue broche LED → Batterie négatif
   ```
   ✅ LED s'allume? → OK
   ❌ LED ne s'allume pas → Broche inversée ou LED défectueuse

2. **Tester le buzzer** (avec batterie 5V):
   ```
   Batterie 5V
   Positif → Buzzer ⊕ → Batterie Négatif
   ```
   ✅ Buzzer sonne? → OK
   ❌ Buzzer silencieux → Polarité inversée ou buzzer défectif

### Après branchement à l'Arduino:

1. **Test séquentiel des ports**:
   ```
   - Pin 36 (Vert): Vérifier allumage LED vert
   - Pin 26 (Jaune): Vérifier allumage LED jaune
   - Pin 30 (Rouge): Vérifier allumage LED rouge
   - Pin 9 (Buzzer): Vérifier son du buzzer
   ```

2. **Test des niveaux de conformité**:
   ```
   Compliance > 80%  → LED Vert seule s'allume
   60% ≤ Compliance ≤ 79% → LED Jaune seule s'allume
   Compliance < 60%  → LED Rouge s'allume + Buzzer sonne
   ```

## ⚡ Notes de Sécurité Importantes

### 1. Alimentation
```
⚠️ NE PAS:
   - Connecter plus de 500mA sur puissance 5V Arduino (risque de perte de données)
   - Utiliser alimentation insuffisante pour Arduino
   
✅ FAIRE:
   - Utiliser alimentation externe 5V 1A minimum
   - Diode de protection si plusieurs composants (100mA par composant)
```

### 2. Polarité des Composants
```
⚠️ IMPORTANT:
   - LEDs: Longue broche = Positive, Courte broche = Négative
   - Buzzer actif: Souder correctement respect de la polarité
   - Inversion = Composant non-fonctionnel ou défectueux
```

### 3. Résistances
```
⚠️ OBLIGE:
   - Résistance 220Ω OBLIGATOIRE pour chaque LED
   - Protection du port Arduino contre surcharge
   - Calcul simple: (5V - 2V_LED) / 20mA = 150Ω → 220Ω (valeur standard)
```

## 📝 Aide au Dépannage

### Arduino ne reconnaît pas le port
```bash
# Lister les ports disponibles
python -m serial.tools.list_ports

# Vérifier câble USB
# Vérifier drivers
```

### Composants ne répondent pas
```
1. Vérifier branchement avec multimètre
2. Tester le composant isolément
3. Vérifier tensions: Arduino 5V = ok
4. Vérifier masse commune entre tous les composants
```

### Comportement erratique
```
- Ajouter condensateur 100µF entre 5V et GND (décuplage)
- Vérifier câbles bien enfoncés
- Éloigner du wifi 2.4GHz si possible
```

