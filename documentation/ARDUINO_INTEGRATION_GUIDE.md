# Arduino Integration Guide - Utilisation avec EPI Detection

## 🚀 Mise en Marche Rapide

### 1. Connexion Arduino
```javascript
// Initialiser l'Arduino Manager
const arduino = new ArduinoManager('COM3');  // Changez COM3 par votre port

// Connecter à l'Arduino
await arduino.connect();

// Envoyer des données de détection
await arduino.sendDetection(
    helmet = true,   // Casque détecté
    vest = true,     // Gilet détecté
    glasses = true,  // Lunettes détectées
    confidence = 92  // Confiance en %
);

// Envoyer le niveau de conformité
await arduino.sendCompliance(85);  // 85% conforme
```

## 📡 Architecture de Communication

### Arduino → Python (Reçu)
L'Arduino envoie:
```
[STARTUP] EPI Detection Arduino Controller v2.0
[INFO] System ready - waiting for commands
[SENSOR] temp=25.5,humidity=60
[MOTION] Motion detected!
[DETECT] Helmet:✓ Vest:✗ Glasses:✓ Confidence:92%
[STATUS] ✅ SAFE (Compliance: 92%)
```

### Python → Arduino (Envoyé)
Le système Python envoie:
```
C85                                    # Niveau de conformité 85%
DETECT:helmet=1,vest=0,glasses=1,confidence=92  # Données EPI
```

## 🔌 Specifications Arduino TinkerCAD

### Pins
- **Pin 2**: PIR Motion Sensor (Détecteur de mouvement)
- **Pin 3**: Red LED (LED rouge - Danger)
- **Pin 4**: Green LED (LED verte - Sécurisé)
- **Pin 5**: Buzzer (Buzzer d'alerte)
- **A0**: Temperature Sensor (Capteur température)
- **A1**: Humidity Sensor (Capteur humidité)

### Niveaux de Conformité
- **≥ 80%**: 🟢 LED VERTE - État SAFE
- **60-79%**: 🟡 LED ROUGE sans son - État WARNING
- **< 60%**: 🔴 LED ROUGE + 🔊 Buzzer - État DANGER

## 🖥️ API Endpoints

### Connexion
```
POST /api/physical/arduino/connect
{
  "port": "COM3"
}

POST /api/physical/arduino/disconnect
{
  "port": "COM3"
}
```

### Envoi Données
```
POST /api/physical/arduino/send-compliance
{
  "port": "COM3",
  "compliance": 85
}

POST /api/physical/arduino/send-detection
{
  "port": "COM3",
  "helmet": true,
  "vest": true,
  "glasses": true,
  "confidence": 92
}
```

### Lecture Données
```
GET /api/physical/arduino/metrics?port=COM3
→ Retourne les métriques actuelles

GET /api/physical/arduino/history?port=COM3&limit=50
→ Retourne l'historique (jusqu'à 50 entrées)
```

### Flux Temps Réel
```
GET /api/physical/arduino/metrics-stream?port=COM3
→ Server-Sent Events (SSE) streaming
```

## 🎯 Cas d'Usage

### 1. Détection EPI → Arduino LED/Buzzer
```javascript
// Quand une détection est faite
socket.on('detection_update', (detectionData) => {
    // Envoyer à Arduino
    await arduinoManager.sendDetection(
        detectionData.helmet,
        detectionData.vest,
        detectionData.glasses,
        detectionData.confidence
    );
    
    // Arduino allume LED verte si conforme, LED rouge + buzzer sinon
});
```

### 2. Surveillance Capteurs Arduino → Dashboard
```javascript
// Les métriques Arduino sont mises à jour en temps réel via SSE
arduinoManager.eventStream.onmessage = (event) => {
    const metrics = JSON.parse(event.data);
    
    console.log('Température:', metrics.temperature);
    console.log('Humidité:', metrics.humidity);
    console.log('Mouvement:', metrics.motion_detected);
    console.log('Conformité:', metrics.compliance);
};
```

### 3. Alerte en Cas de Non-Conformité
```javascript
// Déclencher alerte si conformité < 60%
if (metrics.compliance < 60) {
    // Arduino buzzera automatiquement
    // Afficher alerte sur dashboard
    showAlert('⚠️ DANGER! Équipement non conforme!');
}
```

## 🔧 Installation des Dépendances

```bash
# Installation de PySerial pour communication série
pip install pyserial

# Optionnel: Vérifier la connexion
python -c "import serial; print('PySerial ✅')"
```

## 🐛 Dépannage

### Arduino ne se connecte pas
1. Vérifiez le port COM (Device Manager → COM Ports)
2. Vérifiez les drivers Arduino (CH340 ou FTDI)
3. Essayez un autre port USB

### Pas de données reçues
1. Vérifiez le baudrate (9600 dans le code Arduino)
2. Vérifiez le câble USB
3. Redémarrez l'Arduino (appuyez sur RESET)

### LEDs ne s'allument pas
1. Vérifiez les connexions des LEDs sur les pins 3 et 4
2. Vérifiez les resistances limitatrices (220Ω recommandé)
3. Vérifiez les cavaliers de soudure

## 📊 Monitoring en Temps Réel

Accédez à: `http://localhost:5000/unified_monitoring.html`

- Section "⚙️ Arduino TinkerCad" affiche:
  - 💡 État des LEDs (🟢 🔴 🔊)
  - 📊 Métriques en temps réel (Temp, Humidité, Conformité)
  - 📡 État de connexion

## 💡 Tips & Tricks

### 1. Test Rapide
```bash
# Lancer l'app et aller au dashboard
python run.py
# Puis ouvrir http://localhost:5000/unified_monitoring.html
```

### 2. Simuler Arduino (Sans hardware)
```python
# Modifiez app/arduino_integration.py pour retourner des données fictives
# Utile pour tests/développement sans Arduino physique
```

### 3. Logs Détaillés
```python
# Dans app/logger.py
logger.debug("Message de debug")  # Activé en développement
logger.info("Message d'info")     # Toujours visible
```

## 🎓 Ressources

- Arduino IDE: https://www.arduino.cc/en/software
- TinkerCAD Circuits: https://www.tinkercad.com
- PySerial Docs: https://pythonhosted.org/pyserial/
- EPI Detection Docs: /START_HERE.md

## 📝 Notes de Version

**v2.0** - Code Arduino TinkerCAD avec support complet EPI Detection
- ✅ PIR Motion Detection
- ✅ Température/Humidité
- ✅ LEDs RGB adaptatives
- ✅ Buzzer contrôlé
- ✅ Communication bidirectionnelle

