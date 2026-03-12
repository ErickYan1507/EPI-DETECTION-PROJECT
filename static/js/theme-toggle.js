// Theme Toggle System
const LIGHT_TEXT_PALETTE = [
    { name: 'rouge', hex: '#FF0000', rgb: [255, 0, 0] },
    { name: 'bleu', hex: '#4169E1', rgb: [65, 105, 225] },
    { name: 'grenat', hex: '#8B1538', rgb: [139, 21, 56] },
    { name: 'noir', hex: '#000000', rgb: [0, 0, 0] },
    { name: 'cyan', hex: '#06B6D4', rgb: [6, 182, 212] },
    { name: 'marron', hex: '#A52A2A', rgb: [165, 42, 42] }
];

function parseRgbColor(colorValue) {
    const match = (colorValue || '').match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([0-9.]+))?\)/i);
    if (!match) {
        return null;
    }

    return {
        r: Number(match[1]),
        g: Number(match[2]),
        b: Number(match[3]),
        a: match[4] === undefined ? 1 : Number(match[4])
    };
}

function colorDistanceSq(c1, c2) {
    const dr = c1.r - c2[0];
    const dg = c1.g - c2[1];
    const db = c1.b - c2[2];
    return (dr * dr) + (dg * dg) + (db * db);
}

function getNearestAllowedColor(color) {
    let nearest = LIGHT_TEXT_PALETTE[0];
    let minDist = Number.POSITIVE_INFINITY;

    LIGHT_TEXT_PALETTE.forEach((entry) => {
        const dist = colorDistanceSq(color, entry.rgb);
        if (dist < minDist) {
            minDist = dist;
            nearest = entry;
        }
    });

    return nearest.hex;
}

function mapTextColorToPalette(element) {
    if (!(element instanceof HTMLElement)) {
        return;
    }

    const computed = window.getComputedStyle(element);
    const parsed = parseRgbColor(computed.color);
    if (!parsed || parsed.a === 0) {
        return;
    }

    const isAllowed = LIGHT_TEXT_PALETTE.some((entry) => (
        parsed.r === entry.rgb[0] &&
        parsed.g === entry.rgb[1] &&
        parsed.b === entry.rgb[2]
    ));
    if (isAllowed) {
        return;
    }

    const mappedHex = getNearestAllowedColor(parsed).toLowerCase();
    const currentInline = (element.style.getPropertyValue('color') || '').trim().toLowerCase();
    const currentPriority = element.style.getPropertyPriority('color');
    if (currentInline === mappedHex && currentPriority === 'important') {
        return;
    }

    element.style.setProperty('color', mappedHex, 'important');
}

function applyGlobalLightTextPalette() {
    if (!document.body || !document.body.classList.contains('light-mode')) {
        return;
    }

    mapTextColorToPalette(document.body);
    document.querySelectorAll('body *').forEach(mapTextColorToPalette);
}

class ThemeToggle {
    constructor() {
        const savedTheme = localStorage.getItem('theme-mode') || localStorage.getItem('theme');
        this.darkMode = savedTheme ? savedTheme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.lightModeObserver = null;
        this.paletteRafId = null;
        if (savedTheme) {
            localStorage.setItem('theme-mode', savedTheme);
        }
        this.init();
    }

    init() {
        // Apply theme on load
        this.applyTheme();

        // Track OS preference changes
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
            // Dark mode
            root.setAttribute('data-bs-theme', 'dark');
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');

            root.style.setProperty('--bg-primary', '#0F1419');
            root.style.setProperty('--bg-secondary', '#1A1F2E');
            root.style.setProperty('--bg-tertiary', '#252D3D');
            root.style.setProperty('--text-primary', '#ffffff');
            root.style.setProperty('--text-secondary', '#D0D0D0');
            root.style.setProperty('--text-tertiary', '#888888');
            root.style.setProperty('--border-color', 'rgba(255,255,255,0.1)');
            root.style.setProperty('--glass-bg', 'rgba(31, 41, 55, 0.7)');
            this.stopLightPaletteObserver();
        } else {
            // Light mode
            root.setAttribute('data-bs-theme', 'light');
            document.body.classList.add('light-mode');
            document.body.classList.remove('dark-mode');

            root.style.setProperty('--bg-primary', '#ffe599');
            root.style.setProperty('--bg-secondary', '#ffe599');
            root.style.setProperty('--bg-tertiary', '#f5db8f');
            root.style.setProperty('--text-primary', '#000000');
            root.style.setProperty('--text-secondary', '#8B1538');
            root.style.setProperty('--text-tertiary', '#A52A2A');
            root.style.setProperty('--border-color', 'rgba(31, 41, 55, 0.22)');
            root.style.setProperty('--glass-bg', 'rgba(255, 229, 153, 0.92)');

            applyGlobalLightTextPalette();
            this.startLightPaletteObserver();
        }

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('themechange', { detail: { isDark: this.darkMode } }));
    }

    schedulePaletteApply() {
        if (this.paletteRafId !== null) {
            return;
        }

        this.paletteRafId = window.requestAnimationFrame(() => {
            this.paletteRafId = null;
            applyGlobalLightTextPalette();
        });
    }

    startLightPaletteObserver() {
        if (this.lightModeObserver || !document.body) {
            return;
        }

        this.lightModeObserver = new MutationObserver(() => this.schedulePaletteApply());
        this.lightModeObserver.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class']
        });
    }

    stopLightPaletteObserver() {
        if (this.lightModeObserver) {
            this.lightModeObserver.disconnect();
            this.lightModeObserver = null;
        }
        if (this.paletteRafId !== null) {
            window.cancelAnimationFrame(this.paletteRafId);
            this.paletteRafId = null;
        }
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

// Global initialization
const themeToggle = new ThemeToggle();

// Function available globally
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

// Update button after DOM load
document.addEventListener('DOMContentLoaded', () => {
    updateThemeButton();
    applyGlobalLightTextPalette();
});
