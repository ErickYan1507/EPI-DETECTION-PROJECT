# 🤖 Configuration Arduino MEGA - Alertes Temps Réel

## 📋 Configuration Matérielle

### Composants
- **Microcontrôleur**: Arduino MEGA
- **Buzzer**: Connecté au port **9** (PWM)
- **LED Rouge**: Connecté au port **30** (Danger/Stop)
- **LED Jaune**: Connecté au port **26** (Avertissement)
- **LED Vert**: Connecté au port **36** (Safe/OK)

### État des LEDs par Niveau de Conformité

| Niveau de Conformité | LED Active | Buzzer | État |
|----------------------|-----------|--------|------|
| ≥ 80% | 🟢 VERT (pin 36) | ❌ Non | ✅ SAFE |
| 60-79% | 🟡 JAUNE (pin 26) | ❌ Non | ⚠️ WARNING |
| < 60% | 🔴 ROUGE (pin 30) | ✅ Oui | 🚨 DANGER |

## 🔌 Protocole de Communication

### Vitesse de transmission
- **Baudrate**: 9600 bps
- **Format**: 8 bits de données, 1 bit d'arrêt, pas de parité

### Commandes Host → Arduino

#### 1. Niveau de Conformité
```
C<niveau>
Exemple: C85
```
- Définit le niveau de conformité (0-100)
- Contrôle l'état des LEDs et buzzer

#### 2. Données de Détection
```
DETECT:helmet=<0|1>,vest=<0|1>,glasses=<0|1>,confidence=<0-100>
Exemple: DETECT:helmet=1,vest=0,glasses=1,confidence=92
```
- Envoie les données EPI détectées
- Calcule automatiquement la conformité
- Met à jour l'affichage LED

### Messages Arduino → Host

#### Status
```
[STATUS] ✅ SAFE (Compliance: 85%) - LED: VERT
[STATUS] ⚠️ WARNING (Compliance: 65%) - LED: JAUNE
[STATUS] 🚨 DANGER (Compliance: 45%) - LED: ROUGE + BUZZER
```

#### Détection
```
[DETECT] Helmet:✓ Vest:✗ Glasses:✓ Confidence:92% - LED: VERT
```

#### Motion
```
[MOTION] Motion detected!
```

## 🔧 Configuration Python

### Port de Connexion
```python
# Port COM standard sous Windows (à adapter selon votre système)
# Vérifier dans Gestionnaire des Périphériques
COM_PORT = 'COM3'  # ou 'COM4', 'COM5', etc.
BAUDRATE = 9600
```

### Code d'Intégration Python
```python
from app.arduino_integration import ArduinoController

# Initialiser
arduino = ArduinoController(port='COM3', baudrate=9600)
arduino.connect()

# Envoyer niveau de conformité
arduino.send_compliance_level(75)

# Envoyer détection EPI
arduino.send_detection_data(
    helmet=True, 
    vest=False, 
    glasses=True, 
    confidence=92
)

# Fermer
arduino.disconnect()
```

## 🧪 Test de Configuration

### 1. Vérifier les ports disponibles
```bash
python -m serial.tools.list_ports
```

### 2. Lancer le test Arduino
```bash
python test_arduino_integration.py --simulation
```

### 3. Vérifier les LEDs
- **Startup**: Séquence Vert → Jaune → Rouge
- **Safe (85%)**: LED Vert active
- **Warning (70%)**: LED Jaune active
- **Danger (45%)**: LED Rouge + Buzzer

## ⚠️ Troubleshooting

### Arduino non détecté
1. Vérifier le câble USB
2. Installer les drivers CH340 (si nécessaire)
3. Vérifier dans Gestionnaire des Périphériques
4. Noter le numéro de port COM

### Pas de communication
1. Vérifier le baudrate (9600)
2. S'assurer que PySerial est installé: `pip install pyserial`
3. Fermer le Serial Monitor si ouvert
4. Redémarrer Arduino

### LED ne s'allume pas
1. Vérifier la polarité (+ en haut, - en bas)
2. Tester avec un multimètre
3. Vérifier la résistance de protection

### Buzzer ne sonne pas
1. Tester à l'ohmmètre
2. Vérifier l'alimentation positive
3. Essayer un buzzer actif vs passif

## 📝 Notes Importantes

1. **Alimentation**: Utiliser une alimentation externe pour Arduino MEGA si plus de 500mA nécessaire
2. **Protection**: Ajouter des résistances 220Ω en série des LEDs
3. **Fréquence Buzzer**: 1500Hz pour le son d'alerte (configurable dans le code)
4. **Durée Signal**: 500ms + 300ms de pause (buzer)

## 📚 Fichiers Modifiés

- `scripts/tinkercad_arduino.ino` - Code Arduino MEGA
- `app/arduino_integration.py` - Contrôleur Python (compatible)
- `test_arduino_integration.py` - Tests

## ✅ Checklist de Déploiement

- [ ] Arduino MEGA connecté en USB
- [ ] COM port identifié
- [ ] LEDs testées avec batterie
- [ ] Buzzer testée avec batterie
- [ ] PySerial installé
- [ ] Code Arduino chargé
- [ ] Communication série testée
- [ ] Alertes en temps réel opérationnelles

