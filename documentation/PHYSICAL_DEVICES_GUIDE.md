# 🔌 Guide d'Intégration des Périphériques Physiques Optionnels

## Vue d'ensemble

Le système EPI Detection v2.0 supporte maintenant l'intégration **optionnelle** de plusieurs types de périphériques physiques directement via le dashboard `unified_monitoring.html`.

## ✨ Caractéristiques Principales

### 1. **Intégration Multiprotocole**
- 🔌 **Arduino / TinkerCAD** - Communication série
- 🌐 **MQTT** - Pub/Sub temps réel
- 📡 **Réseau (HTTP)** - APIs REST personnalisées
- 🔵 **Bluetooth** - Appareils BLE wearables
- 🔌 **USB** - Capteurs USB directs
- ☁️ **Cloud / Edge** - Azure IoT, AWS IoT Core, Google Cloud IoT

### 2. **Fonctionnalités**
- ✅ Activation/Désactivation optionnelle de chaque périphérique
- ✅ Configuration automatique via interface web
- ✅ Test de connectivité pour chaque appareil
- ✅ Visualisation de l'état de connexion en temps réel
- ✅ Contrôle direct (LEDs, Buzzers)
- ✅ Streaming de données temps réel
- ✅ Gestion d'erreurs robuste

## 🚀 Démarrage Rapide

### 1. Accéder à la Section de Configuration

1. Ouvrez `unified_monitoring.html`
2. Cliquez sur **"⚙️ Configuration Périphériques Physiques"**
3. Une section de configuration se déploie

### 2. Activer les Périphériques Souhaités

Cochez les cases des périphériques que vous souhaitez utiliser :

```
☑️ Arduino TinkerCAD        → Port: COM3
☑️ Capteurs MQTT            → Broker: localhost:1883
☑️ Capteurs Réseau (HTTP)   → Endpoint: http://localhost:8000/api/sensors
☐ Appareils Bluetooth       → Device UUID
☐ Appareils USB             → Vendor ID:Product ID
☐ Cloud / Edge Computing    → API Key
```

### 3. Configurer les Paramètres

Pour chaque périphérique activé, entrez les paramètres :

| Périphérique | Paramètre | Valeur par défaut | Exemple |
|---|---|---|---|
| **Arduino** | Port série | `COM3` | `COM3`, `/dev/ttyUSB0`, `COM4` |
| **MQTT** | Broker | `localhost:1883` | `mqtt.local:1883`, `broker.hivemq.com:1883` |
| **Réseau** | Endpoint HTTP | `http://localhost:8000/api/sensors` | `http://sensor-api.local/data` |
| **Bluetooth** | Device UUID | (vide) | `00000000-1111-2222-3333-444444444444` |
| **USB** | Device ID | (vide) | `1234:5678` |
| **Cloud** | Config | (vide) | API Key ou Connection String |

### 4. Ajuster les Paramètres Généraux

```
⏱️ Intervalle de scan:       5000 ms (5 secondes)
⏱️ Timeout de connexion:     10 secondes
🔄 Tentatives de reconnexion: 5
```

### 5. Appliquer et Tester

Deux boutons principaux :

- **✅ Appliquer Configuration** - Sauvegarde les paramètres
- **🧪 Tester Périphériques** - Vérifie la connectivité de chaque appareil

## 📡 Types de Périphériques Détaillés

### 🔌 Arduino TinkerCAD

**Utilisation** : Détection de mouvement, capteurs température/humidité, LEDs d'état, buzzer

**Prérequis** :
```bash
pip install pyserial
```

**Code Arduino fourni** : `scripts/tinkercad_arduino.ino`

**Commandes supportées** :
```
C85                          → Set compliance level (85%)
DETECT:helmet=1,vest=0,...  → Send detection data
```

**Exemple** :
```javascript
// Envoyer une commande via API
fetch('/api/physical/arduino/command', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    command: 'C85',
    port: 'COM3'
  })
});
```

### 🌐 MQTT (Capteurs Réseau)

**Utilisation** : Temperature, humidity, air quality, pressure

**Prérequis** :
```bash
pip install paho-mqtt
```

**Topics supportés** :
```
sensors/temperature    → Température
sensors/humidity       → Humidité
sensors/pressure       → Pression
sensors/air_quality    → Qualité air
```

**Configuration Broker** :
- Broker public (test) : `broker.hivemq.com:1883`
- Broker local : `localhost:1883` ou `192.168.1.100:1883`

### 📡 Réseau HTTP

**Utilisation** : APIs REST personnalisées, webhooks IoT

**Format de réponse attendu** :
```json
{
  "temperature": 23.5,
  "humidity": 55,
  "motion": false,
  "compliance": 85
}
```

**Exemple d'endpoint** :
```
GET http://sensor-api.local/api/sensors
GET http://localhost:8000/api/sensors?last=10
```

### 🔵 Bluetooth (Web Bluetooth API)

**Utilisation** : Capteurs BLE wearables, traceurs de position, montres connectées

**Prérequis** :
- Navigateur supportant Web Bluetooth API (Chrome, Edge)
- Appareil Bluetooth compatible

**Caractéristiques GATT supportées** :
- `180A` - Device Information
- `180F` - Battery Service
- `181A` - Environmental Sensing

### 🔌 USB (WebUSB API)

**Utilisation** : Capteurs USB directs, caméras thermiques, lecteurs de badge

**Prérequis** :
- Navigateur supportant WebUSB API
- Appareil USB compatible

### ☁️ Cloud / Edge

**Services supportés** :
- ☁️ Azure IoT Hub
- ☁️ AWS IoT Core
- ☁️ Google Cloud IoT
- 🖥️ Edge Devices (Nvidia Jetson, Raspberry Pi)

## 🔌 API Routes

### Configuration

```
GET  /api/physical/config              → Récupérer config
POST /api/physical/config              → Définir config
GET  /api/physical/status              → État de tous les périphériques
```

### Tests

```
POST /api/physical/arduino/test        → Tester Arduino
POST /api/physical/mqtt/test           → Tester MQTT
POST /api/physical/network/test        → Tester HTTP
POST /api/physical/bluetooth/test      → Tester Bluetooth
POST /api/physical/usb/test            → Tester USB
POST /api/physical/cloud/test          → Tester Cloud
```

### Commandes Directes

```
POST /api/physical/arduino/command     → Envoyer commande Arduino
POST /api/physical/led/control         → Contrôler LEDs
POST /api/physical/buzzer/control      → Contrôler Buzzer
GET  /api/physical/stream/<device>     → Flux temps réel (SSE)
```

## 📋 Exemple de Configuration Complète

```json
{
  "devices": {
    "arduino": true,
    "mqtt": true,
    "network": false,
    "bluetooth": false,
    "usb": false,
    "cloud": false
  },
  "settings": {
    "arduino_port": "COM3",
    "mqtt_broker": "broker.hivemq.com:1883",
    "network_endpoint": "http://localhost:8000/api/sensors",
    "bluetooth_device": "",
    "usb_device_id": "",
    "cloud_config": "",
    "scan_interval": 5000,
    "connection_timeout": 10,
    "reconnect_attempts": 5
  }
}
```

## 🧪 Tester la Connectivité

1. **Pour Arduino** :
   - Branchez l'appareil Arduino via USB
   - Entrez le port (COM3, /dev/ttyUSB0, etc.)
   - Cliquez **Tester Périphériques**
   - Vérifiez le statut ✅ ou ❌

2. **Pour MQTT** :
   - Entrez l'adresse du broker
   - Assurez-vous que le broker est accessible
   - Cliquez **Tester Périphériques**

3. **Pour Réseau HTTP** :
   - Entrez l'URL complète de l'endpoint
   - L'endpoint doit répondre en JSON
   - Cliquez **Tester Périphériques**

## 📊 Monitoring en Temps Réel

Après activation, les données des périphériques apparaissent :

- Dans la section **Arduino TinkerCad** du dashboard
- Dans le **Moniteur Série** (simulé ou réel)
- Dans les **Alertes Actives** (mouvement détecté, etc.)
- Dans les **Statistiques** (température, humidité, compliance rate)

## 🔧 Dépannage

### Arduino non reconnecté
```
Erreur: "Impossible d'ouvrir le port COM3"
Solution: 
1. Vérifiez que l'appareil est connecté
2. Vérifiez le numéro de port dans le Gestionnaire de périphériques
3. Assurez-vous que pyserial est installé
```

### MQTT timeout
```
Erreur: "Connection timeout"
Solution:
1. Vérifiez que le broker MQTT est en ligne
2. Vérifiez la connectivité réseau
3. Testez avec mosquitto_sub: mosquitto_sub -h <broker> -t "sensors/#"
```

### HTTP endpoint inaccessible
```
Erreur: "Connection refused"
Solution:
1. Vérifiez que le service est accessible
2. Testez avec curl: curl http://endpoint/api/sensors
3. Vérifiez les logs du serveur
```

## 📚 Ressources Supplémentaires

- **Arduino Code** : `scripts/tinkercad_arduino.ino`
- **Documentation TinkerCAD** : https://www.tinkercad.com
- **MQTT** : https://mqtt.org
- **Web Bluetooth** : https://webbluetoothcg.github.io/web-bluetooth/
- **WebUSB** : https://wicg.github.io/webusb/

## 🎯 Cas d'Usage

### Usine / Atelier
```
✅ Arduino → Détection PIR + LEDs d'alerte
✅ MQTT → Capteurs température des zones
✅ Réseau → API sensor gateway
```

### Chantier de Construction
```
✅ Arduino → Buzzer d'alerte non-conformité
✅ Bluetooth → Traceurs de position des ouvriers
✅ Cloud → Historique compliance Azure IoT
```

### Laboratoire
```
✅ MQTT → Capteurs lab (température contrôlée)
✅ USB → Analyseurs spécialisés
✅ HTTP → Système LIMS intégré
```

## 🔐 Sécurité

- Les configurations sont sauvegardées en **localStorage** (poste client)
- Utilisez des **connexions MQTT sécurisées** (TLS)
- Protégez les **API tokens** en variables d'environnement
- Validez toujours les données reçues des périphériques

## 📝 Licences des Dépendances

- **pyserial** - BSD
- **paho-mqtt** - EPL/EDL
- **requests** - Apache 2.0

## 💡 Astuce

Vous pouvez utiliser plusieurs types de périphériques **en même temps** ! Par exemple :
- Arduino pour les alertes locales
- MQTT pour le monitoring distribué
- Cloud pour la sauvegarde à long terme

---

**Version** : 2.0  
**Dernière mise à jour** : Janvier 2026  
**Support** : Voir CONTRIBUTING.md
