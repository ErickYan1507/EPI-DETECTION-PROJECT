// Exemples d'intégration du système de thème avec Chart.js

// ===== EXEMPLE 1: Adapter les couleurs des graphiques au thème =====

function getChartColors() {
    const isDark = themeToggle.isDarkMode();
    
    return {
        textColor: isDark ? '#D0D0D0' : '#4A4A4A',
        gridColor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
        primaryColor: 'rgba(139, 21, 56, 0.8)',
        secondaryColor: 'rgba(65, 105, 225, 0.8)',
        successColor: 'rgba(75, 192, 117, 0.8)',
        warningColor: 'rgba(255, 165, 0, 0.8)',
        dangerColor: 'rgba(255, 107, 107, 0.8)',
    };
}

// ===== EXEMPLE 2: Créer un graphique avec support du thème =====

let chartInstance = null;

function createResponsiveChart() {
    const ctx = document.getElementById('myChart').getContext('2d');
    const colors = getChartColors();
    
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Conformité',
                data: [65, 78, 82, 88, 85, 92],
                borderColor: colors.primaryColor,
                backgroundColor: 'rgba(139, 21, 56, 0.1)',
                fill: true,
                tension: 0.4,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: colors.textColor,
                    }
                }
            },
            scales: {
                y: {
                    ticks: { color: colors.textColor },
                    grid: { color: colors.gridColor }
                },
                x: {
                    ticks: { color: colors.textColor },
                    grid: { color: colors.gridColor }
                }
            }
        }
    });
}

// ===== EXEMPLE 3: Mettre à jour les graphiques lors du changement de thème =====

window.addEventListener('themechange', (event) => {
    // Détruire les anciennes instances
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    // Recréer avec les nouvelles couleurs
    setTimeout(createResponsiveChart, 100);
    
    // Ou simplement mettre à jour les options
    if (chartInstance) {
        const colors = getChartColors();
        chartInstance.options.plugins.legend.labels.color = colors.textColor;
        chartInstance.options.scales.y.ticks.color = colors.textColor;
        chartInstance.options.scales.x.ticks.color = colors.textColor;
        chartInstance.update();
    }
});

// ===== EXEMPLE 4: Graphique multi-dataset avec thème =====

function createMultiDatasetChart() {
    const ctx = document.getElementById('complianceChart').getContext('2d');
    const colors = getChartColors();
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Zone A', 'Zone B', 'Zone C', 'Zone D'],
            datasets: [
                {
                    label: 'Casques',
                    data: [85, 78, 92, 88],
                    backgroundColor: colors.primaryColor,
                },
                {
                    label: 'Gilets',
                    data: [72, 88, 85, 79],
                    backgroundColor: colors.secondaryColor,
                },
                {
                    label: 'Lunettes',
                    data: [68, 75, 82, 70],
                    backgroundColor: colors.warningColor,
                }
            ]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    labels: { color: colors.textColor }
                }
            },
            scales: {
                x: {
                    ticks: { color: colors.textColor },
                    grid: { color: colors.gridColor }
                },
                y: {
                    ticks: { color: colors.textColor },
                    grid: { color: colors.gridColor }
                }
            }
        }
    });
}

// ===== EXEMPLE 5: Initialiser les graphiques au démarrage =====

document.addEventListener('DOMContentLoaded', () => {
    // Créer les graphiques
    createResponsiveChart();
    
    // Attendre que le thème initial soit appliqué
    setTimeout(() => {
        console.log('✅ Graphiques avec thème appliqué');
    }, 200);
});

// ===== EXEMPLE 6: Utiliser les variables CSS dans le JavaScript =====

function getThemeVariable(varName) {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(varName)
        .trim();
}

// Usage:
// const bgColor = getThemeVariable('--bg-primary');
// const textColor = getThemeVariable('--text-primary');

// ===== EXEMPLE 7: Logger les changements de thème =====

window.addEventListener('themechange', (event) => {
    const isDark = event.detail.isDark;
    console.log(`🎨 Thème changé: ${isDark ? 'Sombre' : 'Clair'}`);
    console.log('Variables CSS mises à jour');
    console.log('Graphiques recalculés');
});

// ===== EXEMPLE 8: Animation de transition entre thèmes =====

function animateThemeTransition() {
    document.body.style.opacity = '0.9';
    
    setTimeout(() => {
        toggleTheme();
    }, 150);
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 300);
}

// ===== EXEMPLE 9: Synchroniser plusieurs graphiques =====

const charts = {
    compliance: null,
    epi: null,
    alerts: null,
    performance: null
};

function initializeAllCharts() {
    charts.compliance = createComplianceChart();
    charts.epi = createEPIChart();
    charts.alerts = createAlertsChart();
    charts.performance = createPerformanceChart();
}

function updateAllChartsTheme() {
    Object.values(charts).forEach(chart => {
        if (chart) {
            chart.destroy();
        }
    });
    
    setTimeout(initializeAllCharts, 100);
}

window.addEventListener('themechange', updateAllChartsTheme);

// ===== EXEMPLE 10: Exporter graphiques avec thème correct =====

function exportChartAsImage(chartInstance, filename) {
    const canvas = chartInstance.canvas;
    const image = canvas.toDataURL('image/png');
    
    const link = document.createElement('a');
    link.href = image;
    link.download = `${filename}-${themeToggle.isDarkMode() ? 'dark' : 'light'}.png`;
    link.click();
}

// Usage: exportChartAsImage(myChart, 'compliance-chart');

// ===== Palette de couleurs réutilisable =====

const THEME_COLORS = {
    dark: {
        text: '#D0D0D0',
        textPrimary: '#FFFFFF',
        grid: 'rgba(255,255,255,0.05)',
        primary: 'rgba(139, 21, 56, 0.8)',
        secondary: 'rgba(65, 105, 225, 0.8)',
        success: 'rgba(75, 192, 117, 0.8)',
        warning: 'rgba(255, 165, 0, 0.8)',
        danger: 'rgba(255, 107, 107, 0.8)',
    },
    light: {
        text: '#4A4A4A',
        textPrimary: '#1A1A1A',
        grid: 'rgba(0,0,0,0.05)',
        primary: 'rgba(139, 21, 56, 0.8)',
        secondary: 'rgba(65, 105, 225, 0.8)',
        success: 'rgba(75, 192, 117, 0.8)',
        warning: 'rgba(255, 165, 0, 0.8)',
        danger: 'rgba(255, 107, 107, 0.8)',
    }
};

function getColors() {
    return THEME_COLORS[themeToggle.isDarkMode() ? 'dark' : 'light'];
}

// ===== Template de graphique réutilisable =====

function createChartWithTheme(ctx, type, data, title) {
    const colors = getColors();
    
    return new Chart(ctx, {
        type: type,
        data: {
            ...data,
            datasets: data.datasets.map(dataset => ({
                ...dataset,
                borderColor: dataset.borderColor || colors.primary,
                backgroundColor: dataset.backgroundColor || 'rgba(139, 21, 56, 0.1)',
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: { display: true, text: title, color: colors.textPrimary },
                legend: { labels: { color: colors.text } }
            },
            scales: {
                y: { ticks: { color: colors.text }, grid: { color: colors.grid } },
                x: { ticks: { color: colors.text }, grid: { color: colors.grid } }
            }
        }
    });
}
