// static/js/chart.js - Configuration Chart.js
let charts = {};

function initComplianceChart(ctx, data) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Taux de conformité',
                data: data.values,
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function initEPIDistributionChart(ctx, data) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Casques', 'Gilets', 'Lunettes', 'Manquants'],
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#E7E9ED'
                ]
            }]
        }
    });
}