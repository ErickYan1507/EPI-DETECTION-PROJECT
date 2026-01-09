// static/js/main.js - FONCTIONS GLOBALES
document.addEventListener('DOMContentLoaded', function() {
    // Menu mobile
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navMenu = document.getElementById('navMenu');

    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.querySelector('i').classList.toggle('fa-bars');
            this.querySelector('i').classList.toggle('fa-times');
        });
    }

    // Fermer menu en cliquant ailleurs
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.nav-container') && navMenu.classList.contains('active')) {
            navMenu.classList.remove('active');
            mobileMenuToggle.querySelector('i').classList.remove('fa-times');
            mobileMenuToggle.querySelector('i').classList.add('fa-bars');
        }
    });

    // Mettre à jour les stats du footer
    updateFooterStats();

    // Initialiser les tooltips
    initTooltips();
});

function updateFooterStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('footerCompliance').textContent = `${data.avg_compliance || 85}%`;
            document.getElementById('footerPersons').textContent = data.total_persons || 24;
        })
        .catch(console.error);
}

function initTooltips() {
    // Initialiser les tooltips Bootstrap si présents
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Fonction pour afficher les chargements
function showLoading(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Chargement...</div>';
    }
}

// Fonction pour formater les dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR');
}