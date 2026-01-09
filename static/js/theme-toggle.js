// Theme Toggle System
class ThemeToggle {
    constructor() {
        this.darkMode = localStorage.getItem('theme-mode') === 'dark' || 
                       (!localStorage.getItem('theme-mode') && window.matchMedia('(prefers-color-scheme: dark)').matches);
        this.init();
    }

    init() {
        // Appliquer le thème au chargement
        this.applyTheme();
        
        // Écouter les changements de préférence système
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme-mode')) {
                this.darkMode = e.matches;
                this.applyTheme();
            }
        });
    }

    toggle() {
        this.darkMode = !this.darkMode;
        localStorage.setItem('theme-mode', this.darkMode ? 'dark' : 'light');
        this.applyTheme();
    }

    applyTheme() {
        const root = document.documentElement;
        
        if (this.darkMode) {
            // Mode Sombre
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');
            
            root.style.setProperty('--bg-primary', '#0F1419');
            root.style.setProperty('--bg-secondary', '#1A1F2E');
            root.style.setProperty('--bg-tertiary', '#252D3D');
            root.style.setProperty('--text-primary', '#FFFFFF');
            root.style.setProperty('--text-secondary', '#D0D0D0');
            root.style.setProperty('--text-tertiary', '#888888');
            root.style.setProperty('--border-color', 'rgba(255,255,255,0.1)');
            root.style.setProperty('--glass-bg', 'rgba(31, 41, 55, 0.7)');
            
        } else {
            // Mode Clair
            document.body.classList.add('light-mode');
            document.body.classList.remove('dark-mode');
            
            root.style.setProperty('--bg-primary', '#F8F9FA');
            root.style.setProperty('--bg-secondary', '#FFFFFF');
            root.style.setProperty('--bg-tertiary', '#F0F2F5');
            root.style.setProperty('--text-primary', '#1A1A1A');
            root.style.setProperty('--text-secondary', '#4A4A4A');
            root.style.setProperty('--text-tertiary', '#999999');
            root.style.setProperty('--border-color', 'rgba(0,0,0,0.1)');
            root.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.8)');
        }
        
        // Déclencher un événement personnalisé
        window.dispatchEvent(new CustomEvent('themechange', { detail: { isDark: this.darkMode } }));
    }

    isDarkMode() {
        return this.darkMode;
    }

    setDarkMode(isDark) {
        this.darkMode = isDark;
        localStorage.setItem('theme-mode', isDark ? 'dark' : 'light');
        this.applyTheme();
    }
}

// Initialisation globale
const themeToggle = new ThemeToggle();

// Fonction accessible globalement
function toggleTheme() {
    themeToggle.toggle();
    updateThemeButton();
}

function updateThemeButton() {
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
        const icon = btn.querySelector('i');
        if (themeToggle.isDarkMode()) {
            icon.className = 'fas fa-sun';
            btn.title = 'Mode Clair';
        } else {
            icon.className = 'fas fa-moon';
            btn.title = 'Mode Sombre';
        }
    }
}

// Mettre à jour le bouton après le chargement du DOM
document.addEventListener('DOMContentLoaded', updateThemeButton);
