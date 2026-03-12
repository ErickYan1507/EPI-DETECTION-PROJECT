// static/js/main.js - FONCTIONS GLOBALES
document.addEventListener('DOMContentLoaded', function() {
    // Mettre à jour l'année automatiquement
    updateCopyrightYear();
    
    // Menu mobile
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navMenu = document.getElementById('navMenu');

    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });
    }

    // Fermer menu en cliquant ailleurs
    document.addEventListener('click', function(event) {
        if (navMenu && mobileMenuToggle && !event.target.closest('.nav-container') && navMenu.classList.contains('active')) {
            navMenu.classList.remove('active');
            const icon = mobileMenuToggle.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
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
            const complianceEl = document.getElementById('footerCompliance');
            const personsEl = document.getElementById('footerPersons');
            if (complianceEl) complianceEl.textContent = `${data.avg_compliance || 85}%`;
            if (personsEl) personsEl.textContent = data.total_persons || 24;
        })
        .catch(err => console.error('Erreur stats footer:', err));
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

// Fonction pour mettre à jour l'année du copyright automatiquement
function updateCopyrightYear() {
    const yearElement = document.getElementById('currentYear');
    if (yearElement) {
        const currentYear = new Date().getFullYear();
        yearElement.textContent = currentYear;
    }
}