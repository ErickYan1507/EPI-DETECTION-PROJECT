{% extends "base.html" %}

{% block title %}Monitoring Temps Réel - EPI Detection{% endblock %}

{% block content %}
<div class="realtime-container">
    <div class="realtime-header">
        <h1><i class="fas fa-bolt"></i> Monitoring Temps Réel</h1>
        <div class="realtime-stats">
            <div class="stat-item">
                <i class="fas fa-clock"></i>
                <span id="uptime">00:00:00</span>
                <small>Uptime</small>
            </div>
            <div class="stat-item">
                <i class="fas fa-microchip"></i>
                <span id="fps">30</span>
                <small>FPS</small>
            </div>
            <div class="stat-item">
                <i class="fas fa-plug"></i>
                <span id="connections">1</span>
                <small>Connexions</small>
            </div>
        </div>
    </div>

    <div class="realtime-grid">
        <!-- Flux vidéo en direct -->
        <div class="video-card">
            <h3><i class="fas fa-video"></i> Flux Vidéo</h3>
            <div class="video-container">
                <div class="video-placeholder" id="videoPlaceholder">
                    <i class="fas fa-video-slash"></i>
                    <p>Flux vidéo non disponible</p>
                    <button onclick="startVideoStream()" class="btn btn-stream">
                        <i class="fas fa-play"></i> Démarrer le flux
                    </button>
                </div>
                <canvas id="videoCanvas" style="display: none;"></canvas>
            </div>
            <div class="video-controls">
                <button onclick="toggleVideo()" class="btn btn-control">
                    <i class="fas fa-play"></i> Démarrer
                </button>
                <button onclick="captureFrame()" class="btn btn-control">
                    <i class="fas fa-camera"></i> Capturer
                </button>
                <button onclick="toggleDetection()" class="btn btn-control">
                    <i class="fas fa-eye"></i> Détection: <span id="detectionStatus">OFF</span>
                </button>
            </div>
        </div>

        <!-- Détections en direct -->
        <div class="detections-card">
            <h3><i class="fas fa-bullseye"></i> Détections en Direct</h3>
            <div class="detections-list" id="detectionsList">
                <!-- Rempli dynamiquement -->
            </div>
            <div class="detections-stats">
                <div class="stat-box">
                    <div class="stat-label">Personnes</div>
                    <div class="stat-value" id="livePersons">0</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Casques</div>
                    <div class="stat-value" id="liveHelmets">0</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Conformité</div>
                    <div class="stat-value" id="liveCompliance">0%</div>
                </div>
            </div>
        </div>

        <!-- Logs en temps réel -->
        <div class="logs-card">
            <h3><i class="fas fa-terminal"></i> Logs Système</h3>
            <div class="logs-container" id="logsContainer">
                <!-- Logs en temps réel -->
            </div>
            <div class="logs-controls">
                <button onclick="clearLogs()" class="btn btn-small">
                    <i class="fas fa-trash"></i> Effacer
                </button>
                <button onclick="toggleAutoScroll()" class="btn btn-small">
                    <i class="fas fa-scroll"></i> Auto-scroll: <span id="autoScrollStatus">ON</span>
                </button>
            </div>
        </div>

        <!-- Graphiques temps réel -->
        <div class="charts-card">
            <h3><i class="fas fa-chart-line"></i> Métriques Temps Réel</h3>
            <div class="realtime-charts">
                <div class="chart-container">
                    <canvas id="realtimeChart"></canvas>
                </div>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-label">Latence</div>
                        <div class="metric-value" id="latencyValue">0ms</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Détections/min</div>
                        <div class="metric-value" id="detectionsPerMin">0</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Alertes actives</div>
                        <div class="metric-value" id="activeAlertsLive">0</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Commandes système -->
    <div class="system-commands">
        <h3><i class="fas fa-cogs"></i> Commandes Système</h3>
        <div class="commands-grid">
            <button onclick="restartDetection()" class="btn btn-command">
                <i class="fas fa-redo"></i> Redémarrer détection
            </button>
            <button onclick="calibrateModel()" class="btn btn-command">
                <i class="fas fa-ruler-combined"></i> Calibrer modèle
            </button>
            <button onclick="testNotification()" class="btn btn-command">
                <i class="fas fa-bell"></i> Tester notification
            </button>
            <button onclick="exportLogs()" class="btn btn-command">
                <i class="fas fa-download"></i> Exporter logs
            </button>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/realtime.js') }}"></script>
{% endblock %}