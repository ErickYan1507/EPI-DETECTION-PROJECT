# Frontend Architecture

## 🎨 Structure

```
templates/
└── unified_monitoring.html   # Application complète (one-file)

static/
├── css/
│   ├── styles.css           # Styles principaux
│   └── dark-mode.css        # Variables dark mode
└── js/
    ├── app.js               # Logique principale
    ├── api-client.js        # Calls API
    ├── charts.js            # Graphiques
    └── utils.js             # Fonctions utilitaires
```

## 🏗️ Architecture One-File

Le dashboard est contenus dans **unified_monitoring.html** avec:
- HTML5 structure
- CSS3 inline + variables
- JavaScript ES6+ inline

Avantages:
- ✅ Déploiement simple
- ✅ Pas de dépendances build
- ✅ Rapide à charger

## 📺 Interface Utilisateur

### Layout Principal
```
┌─────────────────────────────────────┐
│ Header (Logo + Mode Toggle)         │
├─────────────────────────────────────┤
│ ┌──────────────┐ ┌────────────────┐ │
│ │              │ │   Stats &      │ │
│ │  Webcam      │ │  Détections    │ │
│ │  Canvas      │ │  Charts        │ │
│ │  H5          │ │  Graphiques    │ │
│ │              │ │                │ │
│ └──────────────┘ └────────────────┘ │
├─────────────────────────────────────┤
│ Boutons Controls + Info              │
└─────────────────────────────────────┘
```

## 📹 Capture Webcam

### HTML5 Media API
```javascript
// Accès webcam
navigator.mediaDevices.getUserMedia({
  video: {
    width: { ideal: 1280 },
    height: { ideal: 720 }
  },
  audio: false
})
.then(stream => {
  video.srcObject = stream
  startDetection()
})
.catch(err => console.error('Permission refusée:', err))
```

### Frame Capture
```javascript
function captureFrame() {
  const canvas = document.getElementById('canvas')
  const ctx = canvas.getContext('2d')
  
  // Mirror horizontalement
  ctx.scale(-1, 1)
  ctx.translate(-canvas.width, 0)
  ctx.drawImage(video, 0, 0)
  
  return canvas.toDataURL('image/jpeg', 0.8)
}
```

## 🔗 API Integration

### Envoi à Backend
```javascript
async function detectEPI(imageSrc) {
  const base64 = imageSrc.split(',')[1]
  
  const response = await fetch('/api/detect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image: base64,
      confidence_threshold: 0.5
    })
  })
  
  const data = await response.json()
  return data.detections
}
```

## 🎯 Rendu Détections

### Canvas Drawing
```javascript
function drawDetections(detections, frame) {
  const canvas = document.getElementById('canvas')
  const ctx = canvas.getContext('2d')
  
  // Effacer canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Redessiner frame
  ctx.drawImage(frame, 0, 0)
  
  // Dessiner boîtes englobantes
  detections.forEach(det => {
    const [x, y, x2, y2] = det.bbox
    const color = getColorByClass(det.class)
    
    // Boîte
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.strokeRect(x, y, x2-x, y2-y)
    
    // Label
    ctx.fillStyle = color
    ctx.fillRect(x, y-25, 150, 25)
    ctx.fillStyle = 'white'
    ctx.font = '12px Arial'
    ctx.fillText(
      `${det.class} ${(det.confidence*100).toFixed(0)}%`,
      x+5, y-8
    )
  })
}
```

### Color Mapping
```javascript
const CLASS_COLORS = {
  'helmet': '#FF6B6B',      // Rouge
  'vest': '#4ECDC4',        // Turquoise
  'glasses': '#FFE66D',     // Jaune
  'boots': '#95E1D3',       // Menthe
  'person': '#C7CEEA'       // Violet
}
```

## 📊 Graphiques en Temps Réel

### Détections par Classe
```javascript
const ctx = document.getElementById('classChart').getContext('2d')
const chart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Helmet', 'Vest', 'Glasses', 'Boots'],
    datasets: [{
      label: 'Détections',
      data: [45, 38, 25, 17],
      backgroundColor: ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3']
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false
  }
})
```

### FPS en Temps Réel
```javascript
const fpsChart = new Chart(
  document.getElementById('fpsChart').getContext('2d'),
  {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'FPS',
        data: [],
        borderColor: '#4ECDC4',
        fill: false
      }]
    },
    options: { scales: { y: { min: 0, max: 30 } } }
  }
)

// Update FPS
setInterval(() => {
  fpsChart.data.labels.push(new Date().toLocaleTimeString())
  fpsChart.data.datasets[0].data.push(currentFPS)
  if (fpsChart.data.labels.length > 60) {
    fpsChart.data.labels.shift()
    fpsChart.data.datasets[0].data.shift()
  }
  fpsChart.update()
}, 1000)
```

## 🎨 Mode Sombre

### CSS Variables
```css
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-primary: #000000;
  --text-secondary: #666666;
  --border-color: #ddd;
  --shadow: 0 2px 8px rgba(0,0,0,0.1);
}

[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2a2a2a;
  --text-primary: #ffffff;
  --text-secondary: #aaa;
  --border-color: #444;
  --shadow: 0 2px 8px rgba(0,0,0,0.3);
}
```

### Toggle Implementation
```javascript
function toggleDarkMode() {
  const html = document.documentElement
  const isDark = html.getAttribute('data-theme') === 'dark'
  
  html.setAttribute('data-theme', isDark ? 'light' : 'dark')
  localStorage.setItem('theme', isDark ? 'light' : 'dark')
}

// Restaurer depuis localStorage
window.addEventListener('load', () => {
  const saved = localStorage.getItem('theme') || 'light'
  document.documentElement.setAttribute('data-theme', saved)
})
```

## 📱 Responsive Design

### Breakpoints
```css
/* Mobile */
@media (max-width: 640px) {
  .dashboard { flex-direction: column; }
  canvas { max-width: 100%; }
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
  .dashboard { grid-template-columns: 1fr 1fr; }
}

/* Desktop */
@media (min-width: 1025px) {
  .dashboard { grid-template-columns: 2fr 1fr; }
}
```

## ⌨️ Contrôles

### Boutons
```javascript
document.getElementById('startBtn').addEventListener('click', () => {
  startDetection()
  this.disabled = true
  stopBtn.disabled = false
})

document.getElementById('stopBtn').addEventListener('click', () => {
  stopDetection()
  this.disabled = true
  startBtn.disabled = false
})
```

### Clavier
```javascript
document.addEventListener('keydown', (e) => {
  if (e.key === ' ') startDetection()    // Espace
  if (e.key === 'Escape') stopDetection() // Échap
  if (e.key === 'd') toggleDarkMode()     // 'd' pour dark
})
```

## 🔄 Update Loop

```javascript
async function detectionLoop() {
  while (isDetecting) {
    const frame = captureFrame()
    const detections = await detectEPI(frame)
    
    drawDetections(detections, videoFrame)
    updateStats(detections)
    updateCharts(detections)
    
    // ~30 FPS
    await sleep(33)
  }
}

// Lancer boucle
function startDetection() {
  isDetecting = true
  detectionLoop()
}

function stopDetection() {
  isDetecting = false
}
```

## 📈 Statistiques en Temps Réel

```javascript
let stats = {
  totalDetections: 0,
  detectionsByClass: {},
  averageConfidence: 0,
  sessionStart: new Date(),
  lastUpdate: new Date()
}

function updateStats(detections) {
  stats.totalDetections += detections.length
  
  detections.forEach(det => {
    stats.detectionsByClass[det.class] = 
      (stats.detectionsByClass[det.class] || 0) + 1
  })
  
  const allConfidences = detections.map(d => d.confidence)
  stats.averageConfidence = 
    allConfidences.reduce((a,b) => a+b, 0) / allConfidences.length
  
  stats.lastUpdate = new Date()
  
  // Afficher stats
  document.getElementById('totalDetections').textContent = 
    stats.totalDetections
}
```

## 🔌 Arduino Communication

Envoi des données via API à Flask, qui transmet à Arduino:

```javascript
async function sendToArduino(detection) {
  await fetch('/api/send-arduino', {
    method: 'POST',
    body: JSON.stringify({
      class: detection.class,
      confidence: detection.confidence
    })
  })
}
```

## 🚀 Performance Optimization

1. **Canvas Rendering**
```javascript
// Utiliser requestAnimationFrame
let animationId
function draw() {
  drawDetections(...)
  animationId = requestAnimationFrame(draw)
}
```

2. **Image Compression**
```javascript
// JPEG 80% quality
canvas.toDataURL('image/jpeg', 0.8)  // vs. 1.0
```

3. **Throttling API Calls**
```javascript
let lastCall = 0
const THROTTLE_MS = 100  // Max 10 calls/sec

async function detect() {
  if (Date.now() - lastCall < THROTTLE_MS) return
  lastCall = Date.now()
  
  const result = await detectEPI(...)
}
```
