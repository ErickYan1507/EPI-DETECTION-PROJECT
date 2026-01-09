// static/js/realtime.js - MONITORING TEMPS RÉEL

let videoStream = null;
let detectionInterval = null;
let isDetectionActive = false;
let startTime = Date.now();
let logs = [];
let autoScroll = true;
let realtimeChart = null;

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    initializeRealtimeChart();
    startUptimeCounter();
    connectWebSocket();
    loadInitialLogs();
    setupEventListeners();
});

// Initialiser le graphique temps réel
function initializeRealtimeChart() {
    const ctx = document.getElementById('realtimeChart').getContext('2d');
    realtimeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                    label: 'Conformité (%)',
                    data: [],
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'Personnes',
                    data: [],
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    borderWidth: 2,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            animation: {
                duration: 0 // Pas d'animation pour temps réel
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Temps'
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Mettre à jour le compteur uptime
function startUptimeCounter() {
    setInterval(() => {
        const elapsed = Date.now() - startTime;
        const hours = Math.floor(elapsed / 3600000);
        const minutes = Math.floor((elapsed % 3600000) / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);

        document.getElementById('uptime').textContent =
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

// Connecter WebSocket
function connectWebSocket() {
    // Écouter les événements du serveur
    socket.on('new_alert', function(data) {
        addLog(`ALERTE: ${data.message}`, 'warning');
        updateActiveAlerts();
    });

    socket.on('compliance_update', function(data) {
        updateRealtimeChart(data.compliance_rate, data.persons || 0);
        updateLiveMetrics(data);
    });

    socket.on('detection_result', function(data) {
        addDetectionToLiveView(data);
        updateDetectionStats(data);
    });

    socket.on('system_log', function(data) {
        addLog(data.message, data.type || 'info');
    });
}

// Démarrer le flux vidéo
function startVideoStream() {
    const placeholder = document.getElementById('videoPlaceholder');
    const canvas = document.getElementById('videoCanvas');

    // Simulation - en production, utiliser getUserMedia ou flux RTSP
    placeholder.style.display = 'none';
    canvas.style.display = 'block';

    // Simuler un flux vidéo
    simulateVideoStream(canvas);

    addLog('Flux vidéo démarré', 'success');
}

// Simuler un flux vidéo (pour démo)
function simulateVideoStream(canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = 640;
    canvas.height = 480;

    let frameCount = 0;

    videoStream = setInterval(() => {
        // Effacer le canvas
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Dessiner un cadre de simulation
        ctx.strokeStyle = '#3498db';
        ctx.lineWidth = 2;
        ctx.strokeRect(20, 20, canvas.width - 40, canvas.height - 40);

        // Texte de simulation
        ctx.fillStyle = '#ffffff';
        ctx.font = '20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('SIMULATION FLUX VIDÉO', canvas.width / 2, 50);
        ctx.fillText(`Frame: ${frameCount++}`, canvas.width / 2, 80);

        // Dessiner des "personnes" aléatoires
        const personCount = Math.floor(Math.random() * 4) + 1;
        for (let i = 0; i < personCount; i++) {
            drawRandomPerson(ctx, canvas);
        }

        // Si la détection est active, simuler la détection
        if (isDetectionActive) {
            simulateDetectionOnCanvas(ctx, canvas, personCount);
        }

    }, 1000 / 30); // 30 FPS

    addLog('Simulation vidéo démarrée (30 FPS)', 'info');
}

// Dessiner une personne aléatoire
function drawRandomPerson(ctx, canvas) {
    const x = Math.random() * (canvas.width - 100) + 50;
    const y = Math.random() * (canvas.height - 150) + 100;
    const size = 40 + Math.random() * 30;

    // Corps
    ctx.fillStyle = '#e74c3c';
    ctx.beginPath();
    ctx.arc(x, y, size / 2, 0, Math.PI * 2);
    ctx.fill();

    // Tête
    ctx.fillStyle = '#f1c40f';
    ctx.beginPath();
    ctx.arc(x, y - size / 1.5, size / 3, 0, Math.PI * 2);
    ctx.fill();

    // Possibilité de casque
    if (Math.random() > 0.3) {
        ctx.strokeStyle = '#3498db';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(x, y - size / 1.5, size / 3 + 5, 0, Math.PI * 2);
        ctx.stroke();
    }
}

// Simuler la détection sur le canvas
function simulateDetectionOnCanvas(ctx, canvas, personCount) {
    const helmets = Math.floor(Math.random() * (personCount + 1));
    const vests = Math.floor(Math.random() * (personCount + 1));

    // Afficher les stats
    ctx.fillStyle = '#2ecc71';
    ctx.font = '16px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`Personnes: ${personCount}`, 30, canvas.height - 60);
    ctx.fillText(`Casques: ${helmets}`, 30, canvas.height - 40);
    ctx.fillText(`Gilets: ${vests}`, 30, canvas.height - 20);

    // Calculer la conformité
    const compliance = Math.round((helmets + vests) / (personCount * 2) * 100);
    ctx.fillText(`Conformité: ${compliance}%`, 180, canvas.height - 40);

    // Envoyer les données simulées
    const detectionData = {
        timestamp: new Date().toISOString(),
        persons: personCount,
        helmets: helmets,
        vests: vests,
        compliance: compliance
    };

    // Mettre à jour l'affichage
    updateLiveMetrics(detectionData);

    // Ajouter aux logs
    if (Math.random() > 0.7) {
        addLog(`Détection: ${personCount} personnes, ${helmets} casques`, 'info');
    }
}

// Basculer la détection
function toggleDetection() {
    isDetectionActive = !isDetectionActive;
    const statusElement = document.getElementById('detectionStatus');

    if (isDetectionActive) {
        statusElement.textContent = 'ON';
        statusElement.style.color = '#2ecc71';

        // Démarrer l'intervalle de détection
        detectionInterval = setInterval(() => {
            // Simuler une détection
            simulateRandomDetection();
        }, 2000);

        addLog('Détection activée', 'success');
    } else {
        statusElement.textContent = 'OFF';
        statusElement.style.color = '#e74c3c';

        // Arrêter l'intervalle
        if (detectionInterval) {
            clearInterval(detectionInterval);
            detectionInterval = null;
        }

        addLog('Détection désactivée', 'info');
    }
}

// Simuler une détection aléatoire
function simulateRandomDetection() {
    const persons = Math.floor(Math.random() * 5) + 1;
    const helmets = Math.floor(Math.random() * (persons + 1));
    const vests = Math.floor(Math.random() * (persons + 1));
    const glasses = Math.floor(Math.random() * (persons + 1));
    const compliance = Math.round((helmets + vests + glasses) / (persons * 3) * 100);

    const detection = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString(),
        persons: persons,
        helmets: helmets,
        vests: vests,
        glasses: glasses,
        compliance: compliance,
        status: compliance >= 80 ? 'safe' : compliance >= 50 ? 'warning' : 'danger'
    };

    // Émettre l'événement
    socket.emit('simulated_detection', detection);

    // Mettre à jour l'affichage
    addDetectionToLiveView(detection);
    updateLiveMetrics(detection);
    updateRealtimeChart(compliance, persons);
}

// Ajouter une détection à la vue en direct
function addDetectionToLiveView(detection) {
    const list = document.getElementById('detectionsList');
    const detectionElement = document.createElement('div');
    detectionElement.className = `detection-item detection-${detection.status}`;
    detectionElement.innerHTML = `
        <div class="detection-time">${detection.timestamp}</div>
        <div class="detection-count">${detection.persons} pers.</div>
        <div class="detection-epi">
            <span class="epi-item" title="Casques"><i class="fas fa-hard-hat"></i> ${detection.helmets}</span>
            <span class="epi-item" title="Gilets"><i class="fas fa-vest"></i> ${detection.vests}</span>
            <span class="epi-item" title="Lunettes"><i class="fas fa-glasses"></i> ${detection.glasses}</span>
        </div>
        <div class="detection-compliance">${detection.compliance}%</div>
    `;

    list.insertBefore(detectionElement, list.firstChild);

    // Limiter à 10 éléments
    if (list.children.length > 10) {
        list.removeChild(list.lastChild);
    }
}

// Mettre à jour les métriques en direct
function updateLiveMetrics(data) {
    if (data.persons !== undefined) {
        document.getElementById('livePersons').textContent = data.persons;
    }
    if (data.helmets !== undefined) {
        document.getElementById('liveHelmets').textContent = data.helmets;
    }
    if (data.compliance !== undefined) {
        document.getElementById('liveCompliance').textContent = data.compliance + '%';
    }

    // Mettre à jour les FPS (simulation)
    document.getElementById('fps').textContent = '30';

    // Mettre à jour la latence
    const latency = Math.floor(Math.random() * 100) + 50;
    document.getElementById('latencyValue').textContent = latency + 'ms';

    // Mettre à jour les détections/min
    const detectionsPerMin = Math.floor(Math.random() * 20) + 5;
    document.getElementById('detectionsPerMin').textContent = detectionsPerMin;
}

// Mettre à jour le graphique temps réel
function updateRealtimeChart(compliance, persons) {
    const now = new Date();
    const timeLabel = now.getHours().toString().padStart(2, '0') + ':' +
        now.getMinutes().toString().padStart(2, '0') + ':' +
        now.getSeconds().toString().padStart(2, '0');

    // Ajouter les nouvelles données
    realtimeChart.data.labels.push(timeLabel);
    realtimeChart.data.datasets[0].data.push(compliance);
    realtimeChart.data.datasets[1].data.push(persons);

    // Garder seulement les 20 derniers points
    if (realtimeChart.data.labels.length > 20) {
        realtimeChart.data.labels.shift();
        realtimeChart.data.datasets[0].data.shift();
        realtimeChart.data.datasets[1].data.shift();
    }

    // Mettre à jour le graphique
    realtimeChart.update();
}

// Gérer les logs
function loadInitialLogs() {
    // Logs initiaux
    addLog('Système de monitoring démarré', 'info');
    addLog('Connexion WebSocket établie', 'success');
    addLog('En attente de flux vidéo...', 'info');
}

function addLog(message, type = 'info') {
    const logsContainer = document.getElementById('logsContainer');
    const logEntry = document.createElement('div');

    const timestamp = new Date().toLocaleTimeString();
    const typeIcon = {
        'info': 'info-circle',
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'error': 'times-circle'
    }[type] || 'info-circle';

    logEntry.className = `log-entry log-${type}`;
    logEntry.innerHTML = `
        <span class="log-time">[${timestamp}]</span>
        <i class="fas fa-${typeIcon}"></i>
        <span class="log-message">${message}</span>
    `;

    logsContainer.appendChild(logEntry);
    logs.push({ timestamp, type, message });

    // Auto-scroll
    if (autoScroll) {
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
}

function clearLogs() {
    document.getElementById('logsContainer').innerHTML = '';
    logs = [];
    addLog('Logs effacés', 'info');
}

function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const statusElement = document.getElementById('autoScrollStatus');
    statusElement.textContent = autoScroll ? 'ON' : 'OFF';
    statusElement.style.color = autoScroll ? '#2ecc71' : '#e74c3c';
}

// Commandes système
function restartDetection() {
    addLog('Redémarrage de la détection...', 'warning');

    if (detectionInterval) {
        clearInterval(detectionInterval);
    }

    // Réinitialiser
    isDetectionActive = false;
    document.getElementById('detectionStatus').textContent = 'OFF';
    document.getElementById('detectionStatus').style.color = '#e74c3c';

    setTimeout(() => {
        addLog('Détection redémarrée', 'success');
    }, 1000);
}

function calibrateModel() {
    addLog('Calibration du modèle en cours...', 'info');

    // Simulation de calibration
    setTimeout(() => {
        const improvement = Math.floor(Math.random() * 10) + 5;
        addLog(`Calibration terminée: +${improvement}% de précision`, 'success');
    }, 3000);
}

function testNotification() {
    socket.emit('test_notification', {
        message: 'Notification de test',
        type: 'info'
    });
    addLog('Notification de test envoyée', 'info');
}

function exportLogs() {
    const logData = logs.map(log =>
        `[${log.timestamp}] ${log.type.toUpperCase()}: ${log.message}`
    ).join('\n');

    const blob = new Blob([logData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `epi_logs_${new Date().toISOString().slice(0,10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    addLog('Logs exportés', 'success');
}

function setupEventListeners() {
    // Gérer la fermeture de la page
    window.addEventListener('beforeunload', function() {
        if (videoStream) {
            clearInterval(videoStream);
        }
        if (detectionInterval) {
            clearInterval(detectionInterval);
        }
        socket.disconnect();
    });
}

// Mettre à jour les alertes actives
function updateActiveAlerts() {
    const count = Math.floor(Math.random() * 5);
    document.getElementById('activeAlertsLive').textContent = count;
}

// Mettre à jour les connexions
function updateConnections() {
    const connections = Math.floor(Math.random() * 10) + 1;
    document.getElementById('connections').textContent = connections;
}

// Mettre à jour périodiquement
setInterval(updateConnections, 5000);
setInterval(updateActiveAlerts, 10000);