# 🎯 Unified Monitoring - Complete Integration Guide

## Overview

The **Unified Monitoring** page combines three essential components into a single, synchronized interface:
1. **Live Camera Feed** - Real-time video stream from camera
2. **EPI Detection Statistics** - Detection results with compliance metrics
3. **IoT Simulation (TinkerCad)** - Physical device indicators (LEDs, Buzzer, Sensors)

## Access

- **URL**: `http://localhost:5000/unified` (after starting the application)
- **Navigation**: Use the navbar → "Unified Monitoring" link
- **Direct Link**: Located in the main navigation between "Caméra" and "Realtime"

---

## 📺 Live Camera Feed (Left Panel)

### Features
- Real-time video stream from selected camera
- FPS counter and performance metrics
- Frame capture functionality
- Camera selection and control

### Controls
| Button | Function |
|--------|----------|
| **Start** | Activate camera and detection stream |
| **Stop** | Stop camera feed |
| **Capture** | Download current frame as JPEG |

### Technical Details
- **Endpoint**: `/api/camera/start`, `/api/camera/stop`, `/api/camera/frame`
- **Detection Rate**: ~1 detection per second
- **Frame Format**: MJPEG stream or Canvas fallback
- **Resolution**: Depends on camera capabilities

---

## 📊 Detection Statistics (Center Panel)

### Real-Time Metrics

#### Statistics Grid (4 boxes)
```
┌──────────────────┬──────────────────┐
│ Total Persons    │ With Helmet      │
│       5          │       4          │
├──────────────────┼──────────────────┤
│ With Vest        │ With Glasses     │
│       4          │       3          │
└──────────────────┴──────────────────┘
```

#### Compliance Rate Section
- **Visual Circle Progress**: Animated conic gradient (0-100%)
- **Progress Bar**: Color-coded (red → yellow → green)
- **Status Text**: 
  - ✓ Full Compliance (≥80%)
  - ⚠ Partial Compliance (50-80%)
  - ✗ Non-Compliant (<50%)

#### Latest Detections List
- Shows last 5 detections
- Displays: Class, Confidence %, Timestamp
- Auto-updates every 1 second

### API Endpoints Used
- `/api/camera/detect` - Gets detection data
- `/api/performance` - Gets FPS and timing metrics

---

## 🤖 IoT Simulation (Right Panel)

### System Indicators (4 Visual Lights)

#### 1. Motion Detector
- **Status**: ON/OFF
- **Color**: Green when active
- **Icon**: Arrow/movement symbol

#### 2. Worker Presence
- **Status**: Present/Not Present
- **Color**: Blue when active
- **Icon**: User check mark

#### 3. Green LED
- **Status**: ON/OFF
- **Color**: Green when active
- **Associated with**: Full compliance

#### 4. Red LED
- **Status**: ON/OFF
- **Color**: Red when active
- **Associated with**: Non-compliance alert

### Compliance Slider Control
```
[======================================]  50%
            Apply Compliance Button
```
- **Range**: 0-100%
- **Function**: Force simulation compliance level
- **Effect**: Triggers LED and buzzer states

### Control Buttons
| Button | Function |
|--------|----------|
| **Start** | Begin IoT simulation |
| **Stop** | Stop IoT simulation |
| **Apply Compliance** | Force new compliance level |

### System Status Display
- Current simulation status (Active/Inactive)
- Last update timestamp
- Alert count from sensors

### API Endpoints Used
- `/api/iot/simulation/start` - Start simulation
- `/api/iot/simulation/stop` - Stop simulation
- `/api/iot/simulation/state` - Get current state
- `/api/iot/simulation/force-compliance` - Force compliance level

---

## 📈 Performance Metrics (Bottom Left)

Displays:
- **FPS**: Frames per second (target: 30)
- **Inference Time**: Model inference duration (ms)
- **Latency**: Total processing time (ms)

---

## 📝 System Logs (Bottom Center)

- Real-time system events
- Color-coded by severity:
  - Blue: Info
  - Yellow: Warning
  - Red: Error

---

## 🚨 Alert History (Bottom Right)

Tracks all alerts:
- **Critical Alerts** (Low compliance): Red
- **Warning Alerts** (Medium compliance): Yellow
- **Info Alerts**: Blue

### Alert Triggers
- Compliance < 50% → **Critical**
- Compliance 50-80% → **Warning**
- Red LED activation → **Critical**
- Manual events → **Info**

---

## 🔄 Synchronization Flow

```
Camera Stream
    ↓
Detection API (/api/camera/detect)
    ↓
┌─────────────────────────────────┐
│  Statistics Update (1s)         │
│  - Compliance Rate              │
│  - Equipment Counts             │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  IoT Simulation Sync (2s)       │
│  - LED States                   │
│  - Buzzer Trigger               │
│  - Sensor Data                  │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Alert Generation               │
│  - Compliance-based             │
│  - Threshold-based              │
└─────────────────────────────────┘
```

---

## ⚙️ Configuration

### In `config.py`:
```python
CAMERA_FPS = 30              # Target FPS
CONFIDENCE_THRESHOLD = 0.5   # Detection threshold
IOU_THRESHOLD = 0.5          # NMS IOU threshold
```

### In `app/main.py`:
```python
# Detection interval: 1000ms
# Simulation interval: 2000ms
# Alert update: Real-time
```

---

## 🔐 Security Considerations

1. **Frame Capture**: Frames stored in `/uploads/images/`
2. **Detection Data**: Stored in unified database
3. **Alert History**: Persistent database records
4. **API Authentication**: Inherit from Flask app auth

---

## 📱 Responsive Design

| Device | Layout |
|--------|--------|
| Desktop (>1400px) | 3 columns (video, stats, iot) |
| Tablet (768-1400px) | 2 columns + stacked sections |
| Mobile (<768px) | Single column, stacked |

---

## 🐛 Troubleshooting

### Camera Not Starting
1. Check camera index (`/api/camera/list`)
2. Ensure camera is not used by another application
3. Check camera permissions

### No Detections
1. Verify model is loaded: Check console logs
2. Ensure sufficient lighting
3. Check confidence threshold in config

### Simulation Not Updating
1. Click "Start Simulation" button
2. Check IoT routes are registered
3. Verify database connection

### Alerts Not Appearing
1. Check compliance calculation
2. Ensure alert thresholds are configured
3. Review system logs for errors

---

## 📊 Database Schema

### Detection Table
```sql
CREATE TABLE detection (
    id INTEGER PRIMARY KEY,
    total_persons INTEGER,
    with_helmet INTEGER,
    with_vest INTEGER,
    with_glasses INTEGER,
    compliance_rate FLOAT,
    compliance_level VARCHAR,
    alert_type VARCHAR,
    timestamp DATETIME
);
```

### IoT Sensor Table
```sql
CREATE TABLE iot_sensor (
    sensor_id VARCHAR PRIMARY KEY,
    sensor_name VARCHAR,
    sensor_type VARCHAR,
    led_red BOOLEAN,
    led_green BOOLEAN,
    buzzer_active BOOLEAN,
    motion_detected BOOLEAN,
    worker_present BOOLEAN,
    last_update DATETIME
);
```

---

## 🚀 Performance Tips

1. **Reduce Detection Frequency**: Adjust update intervals if needed
2. **Lower Camera Resolution**: For faster processing
3. **Enable GPU**: Uncomment CUDA settings in config
4. **Close Other Tabs**: Reduce browser resource usage

---

## 📞 Support

For issues or feature requests:
1. Check system logs in the unified monitoring page
2. Review console errors (F12 → Console)
3. Check Flask server output for API errors

---

## 📝 Version Info

- **Created**: 2025-12-30
- **Framework**: Flask + Vanilla JavaScript
- **Styling**: CSS3 Glassmorphism
- **Components**: Camera, Detection, IoT Simulation
