# 🤖 Arduino TinkerCAD - Guide d'Utilisation Rapide

## 📌 Résumé

Le système EPI Detection peut maintenant communiquer avec un Arduino TinkerCAD pour :
- Recevoir les données des capteurs (température, humidité, mouvement)
- Envoyer l'état de conformité des EPI
- Contrôler les LEDs d'alerte (vert = sûr, rouge = danger)
- Déclencher le buzzer en cas de non-conformité

## 🚀 Mise en Route

### 1. Installation de PySerial
```bash
pip install pyserial
```

### 2. Brancher l'Arduino
- Connectez votre Arduino/TinkerCAD via USB
- Notez le port COM (Windows) ou /dev/ttyUSB (Linux/Mac)
- Par défaut: `COM3` sur Windows

### 3. Démarrer l'Application
```bash
python run.py
```

### 4. Accéder au Dashboard
Ouvrir dans le navigateur:
```
http://localhost:5000/unified_monitoring.html
```

## 🎮 Utilisation dans le Dashboard

### Section Arduino
Vous verrez une nouvelle section "⚙️ Arduino TinkerCad - Système EPI Detection" avec:

#### 📊 Capteurs IoT
- 👷 Travailleurs en zone
- 🪖 Casques détectés
- 🟧 Gilets détectés
- 👓 Lunettes détectées
- 📊 Taux de conformité

#### 💡 État des LEDs
- 🟢 LED Verte (Conformité ≥ 80%)
- 🔴 LED Rouge (Conformité < 80%)
- 🔊 Buzzer (Alerte si conformité < 60%)

## 🔌 Architecture

### Arduino envoie:
```
[SENSOR] temp=25.5,humidity=60     # Capteurs de température/humidité
[MOTION] Motion detected!           # Détecteur PIR
[STATUS] ✅ SAFE (Compliance: 92%) # État global
```

### Python envoie à Arduino:
```
C85                                  # Niveau de conformité (0-100)
DETECT:helmet=1,vest=1,glasses=1,confidence=95  # Données EPI
```

## 📱 Code JavaScript (Utilisation dans unified_monitoring.html)

```javascript
// Initialiser Arduino Manager
const arduino = new ArduinoManager('COM3');

// Connecter
await arduino.connect();

// Envoyer détection EPI
await arduino.sendDetection(
    helmet = true,    // Casque détecté
    vest = true,      // Gilet détecté
    glasses = false,  // Pas de lunettes
    confidence = 85   // Confiance 85%
);

// Envoyer niveau de conformité
await arduino.sendCompliance(92);

// Recevoir les métriques en temps réel via SSE
// (Automatique avec startMetricsStream())
```

## 🔋 Schéma Arduino TinkerCAD

```
Digital Pins:
  Pin 2:  PIR Motion Sensor
  Pin 3:  Red LED (Danger)
  Pin 4:  Green LED (Safe)
  Pin 5:  Buzzer

Analog Pins:
  A0: Temperature Sensor
  A1: Humidity Sensor

Serial: 9600 baud
```

## ⚠️ États et Alertes

| Conformité | LED | Buzzer | État |
|-----------|-----|--------|------|
| ≥ 80%     | 🟢  | 🔇    | SAFE ✅ |
| 60-79%    | 🔴  | 🔇    | WARNING ⚠️ |
| < 60%     | 🔴  | 🔊    | DANGER 🚨 |

## 🧪 Test Sans Hardware

Pour tester sans Arduino physique:

```bash
# Lance les tests de parsing et simulation
python test_arduino_integration.py --test simulation

# Vérifier les formats de commandes
python test_arduino_integration.py --test commands

# Tous les tests
python test_arduino_integration.py --test all
```

## 🔗 API Endpoints

```
POST   /api/physical/arduino/connect
POST   /api/physical/arduino/disconnect
GET    /api/physical/arduino/metrics
GET    /api/physical/arduino/history
POST   /api/physical/arduino/send-compliance
POST   /api/physical/arduino/send-detection
GET    /api/physical/arduino/metrics-stream (SSE)
```

## 📊 Exemple Flux Complet

1. **Caméra détecte un travailleur sans casque**
   - Confidence: 50%
   - Casque: ❌ Non détecté
   - Gilet: ✅ Détecté
   - Lunettes: ✅ Détectées

2. **Python envoie à Arduino**
   ```
   DETECT:helmet=0,vest=1,glasses=1,confidence=50
   ```

3. **Arduino calcule la conformité**
   - (0 + 1 + 1) / 3 × 50% = 33%

4. **Arduino met à jour les LEDs**
   - 🔴 LED Rouge s'allume
   - 🔊 Buzzer retentit (conformité < 60%)

5. **Dashboard affiche**
   - 🚨 DANGER
   - Taux conformité: 33%
   - Alerte visuelle

## 🐛 Troubleshooting

### Arduino ne se connecte pas
- ✅ Vérifiez le port COM
- ✅ Vérifiez les drivers Arduino
- ✅ Essayez un autre câble USB

### Pas de données
- ✅ Vérifiez le baudrate (9600)
- ✅ Appuyez sur le bouton RESET de l'Arduino
- ✅ Redémarrez l'application

### LEDs ne s'allument pas
- ✅ Vérifiez les connexions (pins 3, 4, 5)
- ✅ Vérifiez les résistances (220Ω)
- ✅ Testez les LEDs séparément

## 📚 Fichiers Associés

- `app/arduino_integration.py` - Module Arduino avancé
- `app/routes_physical_devices.py` - API endpoints
- `templates/unified_monitoring.html` - Frontend avec ArduinoManager
- `ARDUINO_INTEGRATION_GUIDE.md` - Documentation détaillée
- `scripts/tinkercad_arduino.ino` - Code Arduino TinkerCAD

## 💡 Pro Tips

### Personnaliser le port Arduino
```javascript
// Dans unified_monitoring.html
const arduino = new ArduinoManager('COM5');  // Changez le port ici
```

### Logger les données Arduino
```javascript
arduino.registerCallback((metrics) => {
    console.log('Arduino metrics:', metrics);
});
```

### Tester la communication
```bash
# Terminal: connecter avec Arduino Monitor
python -m serial.tools.miniterm COM3 9600

# Puis envoyer des commandes:
# C85
# DETECT:helmet=1,vest=1,glasses=1,confidence=95
```

## 📞 Support

Pour plus de détails:
- Consultez `ARDUINO_INTEGRATION_GUIDE.md`
- Lancez `python test_arduino_integration.py --test all`
- Vérifiez les logs dans le terminal

---

**Version:** 2.0 - EPI Detection Arduino Integration
**Date:** Janvier 2026
**Status:** ✅ Production Ready

