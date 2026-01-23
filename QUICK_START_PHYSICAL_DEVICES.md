# 🔌 Périphériques Physiques - Guide Rapide

## ⚡ Démarrage en 3 Minutes

### 1️⃣ Installer les dépendances optionnelles
```bash
python install_physical_devices.py
```
Choisissez les périphériques que vous voulez utiliser.

### 2️⃣ Accéder au dashboard
Ouvrez votre navigateur:
```
http://localhost:5000/unified_monitoring.html
```

### 3️⃣ Configurer les périphériques
1. Cliquez **"⚙️ Configuration Périphériques Physiques"** (en haut)
2. Cochez les appareils à utiliser
3. Entrez les paramètres (port COM, broker MQTT, etc)
4. Cliquez **"✅ Appliquer Configuration"**
5. Cliquez **"🧪 Tester Périphériques"**

## 🔌 Paramètres par Type de Périphérique

| Périphérique | Paramètre | Exemple | Dépendance |
|---|---|---|---|
| **Arduino** | Port | `COM3` ou `/dev/ttyUSB0` | `pyserial` |
| **MQTT** | Broker | `localhost:1883` | `paho-mqtt` |
| **Réseau** | Endpoint | `http://localhost:8000/api/sensors` | `requests` ✓ |
| **Bluetooth** | Device UUID | `00000000-0000-0000-0000-000000000000` | `bleak` |
| **USB** | Device ID | `1234:5678` | `pyusb` |
| **Cloud** | Config | API Key ou Connection String | Varies |

## 🎯 Exemples Rapides

### Exemple 1: Arduino Seulement
```
✅ Cocher: Arduino TinkerCAD
📝 Port: COM3
✅ Appliquer
```

### Exemple 2: MQTT Seul
```
✅ Cocher: Capteurs MQTT
📝 Broker: broker.hivemq.com:1883
✅ Appliquer
```

### Exemple 3: Plusieurs Périphériques
```
✅ Cocher: Arduino + MQTT + Réseau
📝 Arduino Port: COM3
📝 MQTT Broker: localhost:1883
📝 Network Endpoint: http://localhost:8000/api/sensors
✅ Appliquer
```

## 🧪 Tester la Connexion

Après configuration, cliquez **"🧪 Tester Périphériques"**

Vérifiez les résultats:
- ✅ **CONNECTÉ** - Périphérique opérationnel
- ❌ **ERREUR** - Vérifiez les paramètres ou la connexion
- ⏳ **EN ATTENTE** - Test en cours (Bluetooth, USB, Cloud)

## 📊 Où voir les données?

Une fois connecté:
1. **Section "Arduino TinkerCad"** - Détections (casques, gilets, lunettes)
2. **Alertes Actives** - Mouvements détectés
3. **Moniteur Série** - Messages bruts
4. **Statistiques** - Température, humidité, conformité

## 🔧 Dépannage Rapide

### Arduino ne se connecte pas
```
1. Vérifier le port COM dans Gestionnaire de périphériques
2. Essayer: COM3, COM4, COM5
3. Vérifier que PySerial est installé
```

### MQTT timeout
```
1. Vérifier que le broker est accessible
2. Essayer: broker.hivemq.com:1883
3. Tester: mosquitto_sub -h broker -t "sensors/#"
```

### HTTP endpoint inaccessible
```
1. Vérifier que le service est en ligne
2. Tester: curl http://endpoint/api/sensors
3. Vérifier les logs du serveur
```

## 📚 Ressources

| Ressource | Chemin | Contenu |
|-----------|--------|---------|
| **Guide Complet** | `PHYSICAL_DEVICES_GUIDE.md` | Détails complets |
| **Exemples Config** | `PHYSICAL_DEVICES_CONFIG.example.ini` | 7 exemples prêts |
| **Résumé Technique** | `PHYSICAL_DEVICES_SUMMARY.md` | Architecture |
| **Code Arduino** | `scripts/tinkercad_arduino.ino` | Sketch complet |

## 🚀 Prochaines Étapes

1. ✅ Configurer les premiers périphériques
2. ✅ Vérifier la connectivité avec "Tester Périphériques"
3. ✅ Consulter le guide complet pour configuration avancée
4. ✅ Utiliser les exemples pour cas d'usage spécifiques

## 💡 Astuce Pro

Vous pouvez utiliser **plusieurs types simultanément**!

Par exemple pour une usine:
- Arduino → Alertes locales (LEDs, buzzer)
- MQTT → Capteurs distribués (température, humidité)
- Cloud → Historique et conformité long-terme

## 🎯 Cas d'Utilisation Courant

### Chantier de Construction
```
Arduino      → Détection PIR + LEDs d'alerte
MQTT         → Capteurs température des zones
Cloud (Azure) → Historique conformité
```

### Usine / Atelier
```
Arduino → Buzzer non-conformité
MQTT   → Capteurs IoT distribués
HTTP   → Gateway central
```

### Laboratoire
```
MQTT → Environnement contrôlé
USB  → Instruments spécialisés
HTTP → Système LIMS
```

## ❓ Questions Fréquentes

**Q: Je n'ai pas d'Arduino, je peux encore utiliser le système?**
A: Oui! Utilisez MQTT, HTTP ou Cloud selon vos ressources.

**Q: Dois-je installer toutes les dépendances?**
A: Non, uniquement celles que vous utilisez. Le script `install_physical_devices.py` vous laisse choisir.

**Q: Où sont sauvegardées les configurations?**
A: Sur votre navigateur (localStorage). Elles persistent entre les sessions.

**Q: Puis-je utiliser un Arduino sur un autre PC?**
A: Oui, mais il faut configurer le réseau ou utiliser une gateway HTTP.

**Q: Comment sécuriser mes credentials Cloud?**
A: Stockez-les en variables d'environnement, pas dans la config du navigateur.

## 📞 Besoin d'Aide?

1. Consultez `PHYSICAL_DEVICES_GUIDE.md` pour les détails
2. Vérifiez `PHYSICAL_DEVICES_CONFIG.example.ini` pour les exemples
3. Ouvrez une issue GitHub
4. Consultez `CONTRIBUTING.md`

---

**Version**: 2.0 | **Mise à jour**: Janvier 2026 | **Status**: ✅ Prêt

🚀 **Bon développement!**
