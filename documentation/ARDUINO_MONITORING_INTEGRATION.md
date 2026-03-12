🤖 INTÉGRATION ARDUINO MEGA DANS UNIFIED MONITORING
════════════════════════════════════════════════════════════════════════════

Architecture:
  Application Flask (run_app.py)
         ↓
  Dashboard Unifié (unified_monitoring.html)
         ↓
  Arduino MEGA (Alertes temps réel)


═══════════════════════════════════════════════════════════════════════════════

1️⃣ ARCHITECTURE SYSTÈME
════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│                     APPLICATION FLASK                               │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
                     ┌──────────────────────┐
                     │  run_app.py          │
                     │  • Init Flask app    │
                     │  • Init Arduino      │
                     │  • Register routes   │
                     └──────────────────────┘
                                ↓
        ┌───────────────────────┴───────────────────────┐
        ↓                                               ↓
    ┌─────────────┐                            ┌─────────────────────┐
    │ dashboard.py│                            │ arduino_integration │
    │ (Routes API)│                            │ (Controller)        │
    └─────────────┘                            └─────────────────────┘
        ↓                                               ↓
    Statistiques                                   Communication
    Détections                                     Arduino MEGA
    Alertes                                        LEDs + Buzzer


═══════════════════════════════════════════════════════════════════════════════

2️⃣ POINT D'ENTRÉE - run_app.py (Ou app.py)
════════════════════════════════════════════════════════════════════════════

Ajouter au démarrage de l'application:

```python
# run_app.py ou app.py

from app.arduino_integration import ArduinoController
import threading

# Variables globales
arduino_controller = None

def init_arduino():
    """Initialiser Arduino au démarrage de l'app"""
    global arduino_controller
    
    try:
        # Créer le contrôleur
        arduino_controller = ArduinoController(port='COM3', baudrate=9600)
        
        # Connecter (redémarrer en tant que thread)
        def connect_async():
            if arduino_controller.connect():
                logger.info("✅ Arduino MEGA connecté au dashboard")
            else:
                logger.warning("⚠️ Arduino MEGA non trouvé - mode dégradé")
        
        # Lancer en thread pour ne pas bloquer le démarrage
        thread = threading.Thread(target=connect_async, daemon=True)
        thread.start()
        
        return arduino_controller
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation Arduino: {e}")
        return None


# Au démarrage de l'app
if __name__ == '__main__':
    app = create_app()
    
    # Initialiser Arduino
    arduino_controller = init_arduino()
    
    # Stocker dans app context
    app.arduino = arduino_controller
    
    # Lancer Flask
    app.run(debug=True, port=5000)
```


═══════════════════════════════════════════════════════════════════════════════

3️⃣ ROUTES API DANS dashboard.py
════════════════════════════════════════════════════════════════════════════

Ajouter les nouvelles routes:

```python
# app/dashboard.py

from flask import current_app

# 🆕 Route: Envoyer alertes à Arduino
@dashboard_bp.route('/api/arduino/alert/<int:compliance_level>', methods=['POST'])
def send_arduino_alert(compliance_level):
    """Envoyer le niveau de conformité à Arduino"""
    try:
        arduino = current_app.arduino
        
        if not arduino or not arduino.connected:
            return jsonify({
                'status': 'error',
                'message': 'Arduino non connecté'
            }), 503
        
        # Envoyer la commande
        success = arduino.send_compliance_level(compliance_level)
        
        if success:
            logger.info(f"✅ Alerte Arduino: {compliance_level}%")
            return jsonify({
                'status': 'success',
                'compliance': compliance_level,
                'message': 'Alerte envoyée'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Erreur envoi commande'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur alerte Arduino: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# 🆕 Route: Envoyer détection EPI à Arduino
@dashboard_bp.route('/api/arduino/detection', methods=['POST'])
def send_arduino_detection():
    """Envoyer détection EPI à Arduino"""
    try:
        data = request.json
        arduino = current_app.arduino
        
        if not arduino or not arduino.connected:
            return jsonify({'status': 'error', 'message': 'Arduino non connecté'}), 503
        
        # Récupérer les données
        helmet = data.get('helmet', False)
        vest = data.get('vest', False)
        glasses = data.get('glasses', False)
        confidence = data.get('confidence', 0)
        
        # Envoyer à Arduino
        success = arduino.send_detection_data(helmet, vest, glasses, confidence)
        
        if success:
            return jsonify({
                'status': 'success',
                'detection': {
                    'helmet': helmet,
                    'vest': vest,
                    'glasses': glasses,
                    'confidence': confidence
                }
            })
        else:
            return jsonify({'status': 'error', 'message': 'Envoi échoué'}), 500
            
    except Exception as e:
        logger.error(f"Erreur détection Arduino: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 🆕 Route: Vérifier status Arduino
@dashboard_bp.route('/api/arduino/status')
def get_arduino_status():
    """Vérifier l'état de la connexion Arduino"""
    try:
        arduino = current_app.arduino
        
        return jsonify({
            'connected': arduino.connected if arduino else False,
            'port': arduino.port if arduino else 'N/A',
            'baudrate': 9600,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```


═══════════════════════════════════════════════════════════════════════════════

4️⃣ INTÉGRATION DANS LE DASHBOARD (unified_monitoring.html)
════════════════════════════════════════════════════════════════════════════

Ajouter une section Arduino dans le dashboard:

```html
<!-- Dans unified_monitoring.html, ajouter cette section -->

<!-- Section Arduino Status -->
<div class="card arduino-status-card">
    <div class="card-title">
        🤖 Alertes Arduino MEGA
    </div>
    
    <div class="arduino-status">
        <div class="status-item">
            <span>État:</span>
            <span id="arduino-status" class="status-indicator offline">Hors ligne</span>
        </div>
        
        <div class="status-item">
            <span>Port:</span>
            <span id="arduino-port">--</span>
        </div>
        
        <div class="status-item">
            <span>Niveau Conformité:</span>
            <input type="range" id="compliance-slider" min="0" max="100" value="50">
            <span id="compliance-value">50%</span>
        </div>
    </div>
    
    <button id="send-alert-btn" class="btn btn-primary">
        📤 Envoyer Alerte
    </button>
    
    <div id="arduino-response" class="response-msg" style="display: none;"></div>
</div>

<!-- JavaScript -->
<script>
// Vérifier l'état Arduino
function checkArduinoStatus() {
    fetch('/api/arduino/status')
        .then(r => r.json())
        .then(data => {
            const statusEl = document.getElementById('arduino-status');
            
            if (data.connected) {
                statusEl.textContent = '✅ En ligne';
                statusEl.className = 'status-indicator online';
                document.getElementById('arduino-port').textContent = data.port;
                document.getElementById('send-alert-btn').disabled = false;
            } else {
                statusEl.textContent = '❌ Hors ligne';
                statusEl.className = 'status-indicator offline';
                document.getElementById('send-alert-btn').disabled = true;
            }
        })
        .catch(e => console.error('Erreur Arduino status:', e));
}

// Mettre à jour le slider
document.getElementById('compliance-slider').addEventListener('input', (e) => {
    document.getElementById('compliance-value').textContent = e.target.value + '%';
});

// Envoyer l'alerte
document.getElementById('send-alert-btn').addEventListener('click', () => {
    const level = document.getElementById('compliance-slider').value;
    
    fetch(`/api/arduino/alert/${level}`, {
        method: 'POST'
    })
    .then(r => r.json())
    .then(data => {
        const responseEl = document.getElementById('arduino-response');
        
        if (data.status === 'success') {
            responseEl.innerHTML = `✅ Alerte envoyée: ${level}%`;
            responseEl.style.color = 'green';
        } else {
            responseEl.innerHTML = `❌ Erreur: ${data.message}`;
            responseEl.style.color = 'red';
        }
        
        responseEl.style.display = 'block';
        setTimeout(() => { responseEl.style.display = 'none'; }, 3000);
    })
    .catch(e => console.error('Erreur:', e));
});

// Vérifier tous les 5 secondes
setInterval(checkArduinoStatus, 5000);
checkArduinoStatus(); // Première vérification
</script>

<style>
.arduino-status-card {
    border-left: 4px solid #3b82f6;
}

.arduino-status {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-bottom: 20px;
}

.status-item {
    display: flex;
    align-items: center;
    gap: 10px;
    justify-content: space-between;
}

#compliance-slider {
    flex: 1;
    max-width: 200px;
}

.status-indicator {
    padding: 5px 10px;
    border-radius: 5px;
    font-size: 0.9em;
    font-weight: bold;
}

.status-indicator.online {
    background: #d1fae5;
    color: #065f46;
}

.status-indicator.offline {
    background: #fee2e2;
    color: #7f1d1d;
}

.response-msg {
    padding: 10px;
    border-radius: 5px;
    text-align: center;
    font-weight: bold;
}
</style>
```


═══════════════════════════════════════════════════════════════════════════════

5️⃣ INTÉGRATION AUTOMATIQUE LORS DE DÉTECTIONS
════════════════════════════════════════════════════════════════════════════

Modifier votre code de détection EPI:

```python
# Après une détection EPI (dans votre système de détection)

from app.arduino_integration import ArduinoController
from flask import current_app

def on_epi_detection(helmet, vest, glasses, confidence):
    """Callback quand une personne est détectée"""
    
    # Envoyer à Arduino
    arduino = current_app.arduino
    if arduino and arduino.connected:
        arduino.send_detection_data(
            helmet=helmet,
            vest=vest,
            glasses=glasses,
            confidence=confidence
        )
    
    # Calculer conformité
    compliance = calculate_compliance(helmet, vest, glasses, confidence)
    
    # Stocker en base de données
    detection = Detection(
        timestamp=datetime.utcnow(),
        helmet_detected=helmet,
        vest_detected=vest,
        glasses_detected=glasses,
        confidence=confidence,
        compliance_rate=compliance
    )
    db.session.add(detection)
    db.session.commit()
    
    # Envoyer alerte aussi en API
    requests.post(f'http://localhost:5000/api/arduino/alert/{compliance}')
    
    logger.info(f"EPI Détection: Helmet={helmet}, Vest={vest}, Glasses={glasses}, Compliance={compliance}%")


def calculate_compliance(helmet, vest, glasses, confidence):
    """Calculer conformité (0-100)"""
    score = 0
    if helmet: score += 33
    if vest: score += 33
    if glasses: score += 34
    
    # Appliquer multiplicateur confiance
    score = (score * confidence) // 100
    return max(0, min(100, score))
```


═══════════════════════════════════════════════════════════════════════════════

6️⃣ CONFIGURATION POUR DÉMARRAGE AUTOMATIQUE
════════════════════════════════════════════════════════════════════════════

Ajouter à .env.local ou config.py:

```
# Arduino Configuration
ARDUINO_PORT=COM3
ARDUINO_BAUDRATE=9600
ARDUINO_ENABLED=true
```

Adapter run_app.py:

```python
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

def init_arduino():
    """Initialiser Arduino depuis config"""
    global arduino_controller
    
    if not os.getenv('ARDUINO_ENABLED', 'false').lower() == 'true':
        logger.info("Arduino désactivé dans config")
        return None
    
    port = os.getenv('ARDUINO_PORT', 'COM3')
    baudrate = int(os.getenv('ARDUINO_BAUDRATE', 9600))
    
    arduino_controller = ArduinoController(port=port, baudrate=baudrate)
    
    thread = threading.Thread(target=lambda: arduino_controller.connect(), daemon=True)
    thread.start()
    
    return arduino_controller
```


═══════════════════════════════════════════════════════════════════════════════

7️⃣ MONITORER LES ALERTES ARDUINO EN TEMPS RÉEL
════════════════════════════════════════════════════════════════════════════

Via WebSocket (Optionnel mais recommandé):

```python
# app/websocket_handler.py (Nouveau fichier)

from flask_socketio import SocketIO, emit
import json

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    """Client connecté au WebSocket"""
    emit('response', {'data': 'Connecté au monitoring Arduino'})


@socketio.on('get_arduino_status')
def handle_arduino_status(json):
    """Obtenir status Arduino en temps réel"""
    from flask import current_app
    
    arduino = current_app.arduino
    
    emit('arduino_status', {
        'connected': arduino.connected if arduino else False,
        'port': arduino.port if arduino else 'N/A'
    })


def notify_alert(compliance_level, led_color):
    """Notifier tous les clients connectés"""
    socketio.emit('arduino_alert', {
        'compliance': compliance_level,
        'led': led_color,
        'timestamp': datetime.utcnow().isoformat()
    }, broadcast=True)
```

Et dans run_app.py:

```python
from app.websocket_handler import socketio

app = create_app()
socketio.init_app(app)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
```


═══════════════════════════════════════════════════════════════════════════════

8️⃣ TEST DE L'INTÉGRATION
════════════════════════════════════════════════════════════════════════════════

```bash
# 1. Démarrer l'Arduino code
# → Arduino IDE → Upload scripts/tinkercad_arduino.ino

# 2. Démarrer l'application
python run_app.py

# 3. Ouvrir le dashboard
# Aller à: http://localhost:5000/

# 4. Accéder au nouveau dashboard unifié
# Aller à: http://localhost:5000/unified_monitoring.html

# 5. Section Arduino visible avec:
#    ✓ État de connexion
#    ✓ Port COM
#    ✓ Slider conformité
#    ✓ Bouton Envoyer Alerte

# 6. Tester
#    - Bouger slider
#    - Cliquer "Envoyer Alerte"
#    - Voir LEDs Arduino réagir
#    - Voir Buzzer sonner si < 60%
```


═══════════════════════════════════════════════════════════════════════════════

9️⃣ STRUCTURE COMPLÈTE FINALE
════════════════════════════════════════════════════════════════════════════════

```
EPI-DETECTION-PROJECT/
│
├── run_app.py ........................... ⭐ MODIFIÉ (Init Arduino)
│
├── app/
│   ├── dashboard.py ..................... ⭐ MODIFIÉ (Routes Arduino)
│   ├── arduino_integration.py ........... (Contrôleur Arduino)
│   ├── websocket_handler.py ............ (Optional - Nouveau)
│   └── database_unified.py ............ (Intégration données)
│
├── templates/
│   ├── unified_monitoring.html ......... ⭐ MODIFIÉ (Section Arduino)
│   └── base.html
│
├── scripts/
│   └── tinkercad_arduino.ino ........... (Code Arduino v2.1)
│
└── config/
    └── .env.local ..................... (Arduino config)
```


🔟 RÉSUMÉ DES ÉTAPES
════════════════════════════════════════════════════════════════════════════

1. Modifier run_app.py → init_arduino()
2. Ajouter routes dans dashboard.py → /api/arduino/*
3. Ajouter section dans unified_monitoring.html
4. Tester les connexions
5. Intégrer dans détections EPI
6. Configurer .env.local
7. Lancer et tester

✅ L'Arduino MEGA est maintenant intégré au monitoring unifié!


═══════════════════════════════════════════════════════════════════════════════

❓ QUESTIONS FRÉQUENTES
════════════════════════════════════════════════════════════════════════════════

Q: Arduino ne se connecte pas?
A: Vérifier:
   - Port COM dans .env.local
   - Arduino code chargé
   - Câble USB connecté
   - PySerial installé

Q: LEDs ne réagissent pas?
A: Vérifier:
   - Pins correctes (30, 26, 36)
   - Résistances 220Ω présentes
   - Branchement GND commun

Q: Routes API non trouvées?
A: Vérifier:
   - Routes ajoutées dans dashboard.py
   - Blueprint enregistré dans app
   - Flask en mode debug

Q: WebSocket optionnel?
A: Oui! Fonctionne sans pour MVP
   Recommandé pour temps réel avancé

═══════════════════════════════════════════════════════════════════════════════

Vous êtes prêt! 🚀 L'Arduino MEGA fonctionne maintenant avec le monitoring! 

