#!/usr/bin/env python3
"""
🤖 EXEMPLE D'INTÉGRATION - Arduino MEGA + Unified Monitoring
Prêt à copier-coller dans votre projet
"""

from flask import Flask, render_template, jsonify, request, current_app
from app.arduino_integration import ArduinoController
from app.logger import logger
import threading
from datetime import datetime

# ════════════════════════════════════════════════════════════════════════════
# 1️⃣ INITIALISATION ARDUINO (À AJOUTER à run_app.py ou app.py)
# ════════════════════════════════════════════════════════════════════════════

def init_arduino_for_app(app):
    """
    Initialiser Arduino pour l'application Flask
    
    Utilisation:
        app = create_app()
        init_arduino_for_app(app)
        app.run()
    """
    arduino_controller = None
    
    def connect_arduino():
        """Connexion asynchrone Arduino"""
        nonlocal arduino_controller
        
        try:
            # Paramètres (adapter selon votre config)
            port = 'COM3'  # À modifier selon votre port
            baudrate = 9600
            
            logger.info(f"🤖 Tentative connexion Arduino sur {port}...")
            
            # Créer le contrôleur
            arduino_controller = ArduinoController(port=port, baudrate=baudrate)
            
            # Connecter
            if arduino_controller.connect():
                logger.info("✅ Arduino MEGA connecté au système de monitoring")
                app.arduino = arduino_controller
                return True
            else:
                logger.warning("⚠️ Arduino MEGA non trouvé - Mode dégradé")
                app.arduino = None
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Arduino: {e}")
            app.arduino = None
            return False
    
    # Lancer la connexion en thread pour ne pas bloquer le démarrage
    thread = threading.Thread(target=connect_arduino, daemon=True)
    thread.start()
    
    return app


# ════════════════════════════════════════════════════════════════════════════
# 2️⃣ ROUTES API (À AJOUTER à app/dashboard.py)
# ════════════════════════════════════════════════════════════════════════════

class ArduinoRoutes:
    """
    Routes Flask pour contrôler Arduino
    
    Utilisation:
        from app.dashboard import ArduinoRoutes
        app.register_blueprint(ArduinoRoutes.get_blueprint())
    """
    
    @staticmethod
    def get_blueprint():
        """Obtenir le blueprint des routes Arduino"""
        from flask import Blueprint
        
        bp = Blueprint('arduino_api', __name__, url_prefix='/api/arduino')
        
        @bp.route('/status')
        def get_status():
            """Vérifier l'état de la connexion Arduino"""
            try:
                arduino = current_app.arduino
                
                if arduino:
                    return jsonify({
                        'status': 'success',
                        'connected': arduino.connected,
                        'port': arduino.port,
                        'baudrate': 9600,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Arduino non initialisé',
                        'connected': False
                    }), 503
                    
            except Exception as e:
                logger.error(f"Erreur status Arduino: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'connected': False
                }), 500
        
        @bp.route('/alert/<int:level>', methods=['POST'])
        def send_alert(level):
            """Envoyer une alerte conformité à Arduino"""
            try:
                # Valider le niveau
                level = max(0, min(100, level))
                
                arduino = current_app.arduino
                
                if not arduino or not arduino.connected:
                    return jsonify({
                        'status': 'error',
                        'message': 'Arduino non connecté'
                    }), 503
                
                # Envoyer la commande
                success = arduino.send_compliance_level(level)
                
                if success:
                    # Déterminer la LED
                    if level >= 80:
                        led_color = 'VERT'
                        alert_type = 'SAFE'
                    elif level >= 60:
                        led_color = 'JAUNE'
                        alert_type = 'WARNING'
                    else:
                        led_color = 'ROUGE'
                        alert_type = 'DANGER'
                    
                    logger.info(f"✅ Alerte Arduino: {level}% - LED {led_color}")
                    
                    return jsonify({
                        'status': 'success',
                        'compliance': level,
                        'led': led_color,
                        'alert_type': alert_type,
                        'message': f'Alerte envoyée: {alert_type}'
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Erreur envoi à Arduino'
                    }), 500
                    
            except Exception as e:
                logger.error(f"Erreur alerte Arduino: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @bp.route('/detection', methods=['POST'])
        def send_detection():
            """Envoyer détection EPI à Arduino"""
            try:
                data = request.json or {}
                
                # Récupérer les données
                helmet = data.get('helmet', False)
                vest = data.get('vest', False)
                glasses = data.get('glasses', False)
                confidence = int(data.get('confidence', 0))
                
                arduino = current_app.arduino
                
                if not arduino or not arduino.connected:
                    return jsonify({
                        'status': 'error',
                        'message': 'Arduino non connecté'
                    }), 503
                
                # Envoyer à Arduino
                success = arduino.send_detection_data(helmet, vest, glasses, confidence)
                
                if success:
                    # Calculer conformité
                    compliance = calculate_compliance(helmet, vest, glasses, confidence)
                    
                    logger.info(f"✅ EPI Détection envoyée: H={helmet}, V={vest}, G={glasses}, Conf={confidence}%, Compliance={compliance}%")
                    
                    return jsonify({
                        'status': 'success',
                        'detection': {
                            'helmet': helmet,
                            'vest': vest,
                            'glasses': glasses,
                            'confidence': confidence,
                            'compliance': compliance
                        }
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Erreur envoi détection'
                    }), 500
                    
            except Exception as e:
                logger.error(f"Erreur détection Arduino: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        return bp


def calculate_compliance(helmet, vest, glasses, confidence):
    """Calculer le score de conformité (0-100)"""
    score = 0
    if helmet:
        score += 33
    if vest:
        score += 33
    if glasses:
        score += 34
    
    # Appliquer multiplicateur confiance
    score = (score * confidence) // 100
    
    return max(0, min(100, score))


# ════════════════════════════════════════════════════════════════════════════
# 3️⃣ EXEMPLE COMPLET run_app.py
# ════════════════════════════════════════════════════════════════════════════

"""
# Ajouter à run_app.py:

from app_integration_arduino_example import init_arduino_for_app, ArduinoRoutes
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

def create_app():
    app = Flask(__name__)
    
    # Init Arduino
    app = init_arduino_for_app(app)
    
    # Routes dashboard
    from app.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    # Routes Arduino
    app.register_blueprint(ArduinoRoutes.get_blueprint())
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
"""


# ════════════════════════════════════════════════════════════════════════════
# 4️⃣ EXEMPLE HTML POUR DASHBOARD
# ════════════════════════════════════════════════════════════════════════════

ARDUINO_HTML_COMPONENT = """
<!-- Ajouter à unified_monitoring.html -->

<!-- Arduino Status Section -->
<div class="card" style="border-left: 4px solid #3b82f6;">
    <h3>🤖 Alertes Arduino MEGA</h3>
    
    <div class="arduino-controls" style="display: flex; flex-direction: column; gap: 15px;">
        
        <!-- Status -->
        <div>
            <label>État:</label>
            <span id="arduino-status-indicator" 
                  style="display: inline-block; width: 12px; height: 12px; 
                         border-radius: 50%; background: red; margin-left: 10px;"></span>
            <span id="arduino-status-text">Hors ligne</span>
        </div>
        
        <!-- Compliance Slider -->
        <div>
            <label>Niveau Conformité:</label>
            <div style="display: flex; gap: 10px; align-items: center;">
                <input type="range" id="compliance-slider" min="0" max="100" value="50" 
                       style="flex: 1;">
                <span id="compliance-display" style="min-width: 50px;">50%</span>
            </div>
        </div>
        
        <!-- Send Alert Button -->
        <button id="send-alert-btn" onclick="sendArduinoAlert()" 
                style="padding: 10px; background: #3b82f6; color: white; 
                       border: none; border-radius: 5px; cursor: pointer;">
            📤 Envoyer Alerte
        </button>
        
        <!-- Response Message -->
        <div id="arduino-response" style="padding: 10px; border-radius: 5px; 
                                         display: none; text-align: center; font-weight: bold;">
        </div>
        
    </div>
</div>

<script>
// Variables
let arduinoConnected = false;

// Constantes LED
const LED_COLORS = {
    VERT: '#22c55e',
    JAUNE: '#eab308',
    ROUGE: '#ef4444'
};

// Vérifier status Arduino
function checkArduinoStatus() {
    fetch('/api/arduino/status')
        .then(r => r.json())
        .then(data => {
            const indicator = document.getElementById('arduino-status-indicator');
            const statusText = document.getElementById('arduino-status-text');
            const btn = document.getElementById('send-alert-btn');
            
            if (data.connected) {
                indicator.style.background = LED_COLORS.VERT;
                statusText.textContent = '✅ En ligne';
                btn.disabled = false;
                arduinoConnected = true;
            } else {
                indicator.style.background = LED_COLORS.ROUGE;
                statusText.textContent = '❌ Hors ligne';
                btn.disabled = true;
                arduinoConnected = false;
            }
        })
        .catch(e => {
            console.error('Erreur status:', e);
            document.getElementById('send-alert-btn').disabled = true;
        });
}

// Mettre à jour l'affichage du slider
document.getElementById('compliance-slider').addEventListener('input', (e) => {
    document.getElementById('compliance-display').textContent = e.target.value + '%';
});

// Envoyer alerte
function sendArduinoAlert() {
    if (!arduinoConnected) {
        alert('Arduino non connecté');
        return;
    }
    
    const level = document.getElementById('compliance-slider').value;
    
    fetch(`/api/arduino/alert/${level}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            const responseEl = document.getElementById('arduino-response');
            
            if (data.status === 'success') {
                responseEl.innerHTML = `✅ ${data.alert_type}: ${level}% - LED ${data.led}`;
                responseEl.style.background = '#d1fae5';
                responseEl.style.color = '#065f46';
            } else {
                responseEl.innerHTML = `❌ Erreur: ${data.message}`;
                responseEl.style.background = '#fee2e2';
                responseEl.style.color = '#7f1d1d';
            }
            
            responseEl.style.display = 'block';
            setTimeout(() => {
                responseEl.style.display = 'none';
            }, 3000);
        })
        .catch(e => {
            console.error('Erreur:', e);
            document.getElementById('arduino-response').innerHTML = '❌ Erreur de connexion';
            document.getElementById('arduino-response').style.display = 'block';
        });
}

// Vérifier régulièrement
setInterval(checkArduinoStatus, 5000);
checkArduinoStatus(); // Première vérification
</script>
"""


# ════════════════════════════════════════════════════════════════════════════
# 5️⃣ TEST DES ROUTES
# ════════════════════════════════════════════════════════════════════════════

"""
# Tester avec curl ou requests:

# 1. Vérifier status
curl http://localhost:5000/api/arduino/status

# 2. Envoyer alerte 85%
curl -X POST http://localhost:5000/api/arduino/alert/85

# 3. Envoyer détection EPI
curl -X POST http://localhost:5000/api/arduino/detection \\
  -H "Content-Type: application/json" \\
  -d '{"helmet": true, "vest": false, "glasses": true, "confidence": 92}'

# Avec Python requests:
import requests

# Status
r = requests.get('http://localhost:5000/api/arduino/status')
print(r.json())

# Alerte
r = requests.post('http://localhost:5000/api/arduino/alert/75')
print(r.json())

# Détection
r = requests.post('http://localhost:5000/api/arduino/detection', json={
    'helmet': True,
    'vest': False, 
    'glasses': True,
    'confidence': 92
})
print(r.json())
"""


if __name__ == '__main__':
    print("📖 Ceci est un exemple d'intégration Arduino MEGA")
    print("\n✅ À copier-coller dans votre projet:")
    print("\n1. Fonction: init_arduino_for_app() → run_app.py")
    print("2. Classe: ArduinoRoutes → app/dashboard.py")
    print("3. HTML: ARDUINO_HTML_COMPONENT → templates/unified_monitoring.html")
    print("\n🚀 Puis lancer: python run_app.py")
    print("\n📖 Documentation complète:")
    print("   ARDUINO_MONITORING_INTEGRATION.md")
