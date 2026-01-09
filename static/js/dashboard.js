// Dashboard JavaScript - Fonctionnalités temps réel

let complianceChart, distributionChart, hourlyChart;
let socket = io();
let realtimeUpdateInterval;

// Initialisation du dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    loadInitialData();
    setupRealtimeUpdates();
    setupEventListeners();
});

// Initialiser les graphiques Chart.js
function initializeCharts() {
    const ctx1 = document.getElementById('complianceChart').getContext('2d');
    complianceChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Taux de Conformité (%)',
                data: [],
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'Conformité (%)' }
                }
            }
        }
    });

    const ctx2 = document.getElementById('epiDistributionChart').getContext('2d');
    distributionChart = new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: ['Casques', 'Gilets', 'Lunettes', 'Manquants'],
            datasets: [{
                data: [45, 38, 25, 12],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#E7E9ED'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right' }
            }
        }
    });

    const ctx3 = document.getElementById('hourlyChart').getContext('2d');
    hourlyChart = new Chart(ctx3, {
        type: 'bar',
        data: {
            labels: ['08h', '09h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h'],
            datasets: [{
                label: 'Détections',
                data: [12, 19, 15, 25, 22, 18, 30, 28, 24, 20],
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Nombre de détections' }
                }
            }
        }
    });
}

// Charger les données initiales
function loadInitialData() {
    fetch('/api/realtime')
        .then(response => response.json())
        .then(data => {
            updateKPICards(data);
            updateComplianceChart(data);
            updateDetectionsTable(data);
        })
        .catch(error => console.error('Erreur chargement données:', error));
}

// Mettre à jour les cartes KPI
function updateKPICards(data) {
    if (data.compliance_rates && data.compliance_rates.length > 0) {
        const avgCompliance = data.compliance_rates.reduce((a, b) => a + b, 0) / data.compliance_rates.length;
        document.getElementById('complianceRate').textContent = `${avgCompliance.toFixed(1)}%`;
    }

    if (data.persons && data.persons.length > 0) {
        const totalPersons = data.persons.reduce((a, b) => a + b, 0);
        document.getElementById('totalPersons').textContent = totalPersons;
    }

    document.getElementById('activeAlerts').textContent = data.alerts || 0;
}

// Mettre à jour le graphique de conformité
function updateComplianceChart(data) {
    if (data.timestamps && data.compliance_rates) {
        complianceChart.data.labels = data.timestamps.slice(-10);
        complianceChart.data.datasets[0].data = data.compliance_rates.slice(-10);
        complianceChart.update();
    }
}

// Mettre à jour la table des détections
function updateDetectionsTable(data) {
    // Simulation - en production, utiliser les vraies données
    const tableBody = document.getElementById('detectionsTable');
    tableBody.innerHTML = '';

    for (let i = 0; i < 5; i++) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatTime(new Date(Date.now() - i * 600000))}</td>
            <td>${Math.floor(Math.random() * 5) + 1}</td>
            <td>${Math.floor(Math.random() * 5)}</td>
            <td>${Math.floor(Math.random() * 5)}</td>
            <td>${Math.floor(Math.random() * 3)}</td>
            <td>${(Math.random() * 40 + 60).toFixed(1)}%</td>
            <td><span class="status-badge status-${Math.random() > 0.7 ? 'danger' : Math.random() > 0.5 ? 'warning' : 'safe'}">
                ${Math.random() > 0.7 ? 'DANGER' : Math.random() > 0.5 ? 'WARNING' : 'SAFE'}
            </span></td>
        `;
        tableBody.appendChild(row);
    }
}

// Configurer les mises à jour temps réel
function setupRealtimeUpdates() {
    // Écouter les événements WebSocket
    socket.on('new_alert', function(data) {
        showNotification(data.message, data.severity);
        updateAlertCount();
    });

    socket.on('compliance_update', function(data) {
        updateComplianceInRealTime(data.compliance_rate);
    });

    socket.on('detection_result', function(data) {
        addNewDetectionToTable(data);
    });

    // Mettre à jour périodiquement
    realtimeUpdateInterval = setInterval(function() {
        socket.emit('request_update');
    }, 5000);
}

// Configurer les écouteurs d'événements
function setupEventListeners() {
    // Bouton d'export PDF
    document.querySelector('.btn-export') ? .addEventListener('click', exportPDF);

    // Bouton d'actualisation
    document.querySelector('.btn-refresh') ? .addEventListener('click', refreshData);

    // Bouton de simulation TinkerCad
    document.querySelector('.btn-simulate') ? .addEventListener('click', simulateDetection);
}

// Exporter en PDF
function exportPDF() {
    fetch('/export/pdf')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `epi_report_${new Date().toISOString().slice(0,10)}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Erreur export PDF:', error);
            alert('Erreur lors de l\'export PDF');
        });
}

// Actualiser les données
function refreshData() {
    loadInitialData();
    showNotification('Données actualisées', 'info');
}

// Simuler une détection
function simulateDetection() {
    fetch('/api/simulate', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showNotification('Simulation lancée', 'success');
            console.log('Résultat simulation:', data);
        })
        .catch(error => {
            console.error('Erreur simulation:', error);
            showNotification('Erreur simulation', 'error');
        });
}

// Afficher une notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;

    document.body.appendChild(notification);

    // Supprimer après 5 secondes
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Obtenir l'icône de notification
function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'danger': 'radiation'
    };
    return icons[type] || 'info-circle';
}

// Mettre à jour le compteur d'alertes
function updateAlertCount() {
    const alertCount = document.getElementById('activeAlerts');
    const current = parseInt(alertCount.textContent) || 0;
    alertCount.textContent = current + 1;

    // Animation
    alertCount.parentElement.classList.add('pulse');
    setTimeout(() => {
        alertCount.parentElement.classList.remove('pulse');
    }, 1000);
}

// Formater l'heure
function formatTime(date) {
    return date.toTimeString().slice(0, 8);
}

// Nettoyage à la fermeture
window.addEventListener('beforeunload', function() {
    if (realtimeUpdateInterval) {
        clearInterval(realtimeUpdateInterval);
    }
    socket.disconnect();
});