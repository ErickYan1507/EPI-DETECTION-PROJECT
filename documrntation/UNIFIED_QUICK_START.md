# 🚀 UNIFIED MONITORING - QUICK REFERENCE

## 📌 Access Point
```
URL: http://localhost:5000/unified
Navbar: "Unified Monitoring" link
```

## 🎮 Control Panel Quick Guide

### Left Panel: Camera Control
```
┌─────────────────────┐
│   START BUTTON      │  ← Activate camera
│   STOP BUTTON       │  ← Deactivate camera
│   CAPTURE BUTTON    │  ← Download frame
└─────────────────────┘
```

### Center Panel: Detection Info
```
Displays in Real-Time:
├─ Total Persons Detected
├─ Count with Helmet
├─ Count with Vest
├─ Count with Glasses
├─ Compliance %
└─ Latest 5 Detections
```

### Right Panel: IoT Simulation
```
┌─────────────────────┐
│   START BUTTON      │  ← Begin simulation
│   STOP BUTTON       │  ← End simulation
├─────────────────────┤
│ 🟢 Motion Indicator │
│ 🔵 Worker Indicator │
│ 🟢 Green LED        │
│ 🔴 Red LED          │
├─────────────────────┤
│ Compliance: [50%]   │  ← Adjust slider
│ APPLY COMPLIANCE    │  ← Force new value
└─────────────────────┘
```

## 📊 Status Indicators Legend

| Color | Meaning | When Active |
|-------|---------|------------|
| 🟢 Green | Normal/Active | Detection found, LED ON, Compliance OK |
| 🔵 Blue | Info | Worker detected, system ready |
| 🟠 Orange | Warning | Low compliance (50-80%) |
| 🔴 Red | Critical | Non-compliant (<50%), Alert triggered |
| ⚪ Gray | Inactive | System OFF, no detection |

## ⚡ Quick Workflow

### Start Monitoring
1. **Open Page**: `/unified`
2. **Click "Start"** (Camera panel) → Wait 1-2 seconds
3. **Click "Start"** (IoT panel) → Simulation begins
4. **Observe**: Real-time updates appear

### Stop Monitoring
1. **Click "Stop"** (Camera) → Camera stops
2. **Click "Stop"** (IoT) → Simulation stops
3. **Clear Alerts**: Click "Clear All" button

## 🔄 Update Rates

| Component | Update Rate | Latency |
|-----------|------------|---------|
| Detection Stats | 1 sec | ~50ms |
| IoT State | 2 sec | ~100ms |
| Performance | Per frame | ~16ms |
| Alerts | Real-time | <100ms |

## 🎯 Key Metrics Explained

### Compliance Rate
```
< 50%   = 🔴 CRITICAL (Red, Buzzer on)
50-80%  = 🟠 WARNING  (Yellow, Alert)
> 80%   = 🟢 OK       (Green, Safe)
```

### Detection Counts
```
Total Persons = All people detected
With Helmet   = People wearing helmets
With Vest     = People wearing vests
With Glasses  = People wearing safety glasses
```

## 💾 Data Persistence

### Auto-Saved Data
✓ All detections → Database
✓ Compliance rates → Database
✓ Alert history → Database
✓ Sensor readings → Database

### Downloaded Data
- Frame captures (via "Capture" button)
- Can be downloaded to local machine

## 🌐 API Endpoints Quick Reference

```
GET  /api/camera/list              → List available cameras
POST /api/camera/start             → Start camera
POST /api/camera/stop              → Stop camera
GET  /api/camera/detect            → Get detections
GET  /api/camera/frame             → Download latest frame
GET  /api/performance              → Get FPS metrics

POST /api/iot/simulation/start     → Start IoT simulation
POST /api/iot/simulation/stop      → Stop simulation
GET  /api/iot/simulation/state     → Get current state
POST /api/iot/simulation/force-compliance → Force compliance
```

## 🎨 Color Scheme

- **Primary Gradient**: Purple (#667eea) → Dark Purple (#764ba2)
- **Accent**: Maroon (#8B1538)
- **Success**: Green (#27ae60)
- **Warning**: Orange (#f39c12)
- **Danger**: Red (#e74c3c)
- **Background**: Dark gradient

## 📱 Responsive Breakpoints

| Device | Layout |
|--------|--------|
| Desktop (>1400px) | 3 columns |
| Tablet (768-1400px) | 2 columns + bottom |
| Mobile (<768px) | Single column |

## 🔐 What Data Is Collected?

| Data Type | Storage | Purpose |
|-----------|---------|---------|
| Detections | Database | Compliance tracking |
| Compliance % | Database | Statistics |
| Alerts | Database | Audit trail |
| Images | Disk | Reference |
| Sensor Data | Database | IoT monitoring |

## ⚙️ Common Adjustments

### Lower CPU Usage
```
1. Reduce CAMERA_FPS to 15
2. Increase detection interval to 2s
3. Lower confidence threshold
```

### Increase Detection Speed
```
1. Raise CAMERA_FPS to 60
2. Decrease detection interval to 500ms
3. Use GPU (if available)
```

### Change Alert Threshold
```
Edit config.py:
COMPLIANCE_ALERT_THRESHOLD = 80  # Alert when below this %
```

## 🆘 Emergency Controls

| Issue | Quick Fix |
|-------|-----------|
| Page frozen | Refresh browser (F5) |
| Camera stuck | Click "Stop", wait 2s, click "Start" |
| High CPU | Close other apps, reduce FPS |
| No detections | Check lighting, increase confidence slider |
| IoT not responding | Restart simulation (Stop → Start) |

## 📞 Debug Mode

### Check Console
- Press `F12` → Console tab
- Watch for error messages
- Check network requests (Network tab)

### Check Server Logs
```bash
# Monitor server output for:
# - Detection errors
# - API failures
# - Database issues
```

## ✅ Verification Checklist

Before going live:
- [ ] Camera detected and working
- [ ] Detections appearing within 2 seconds
- [ ] Compliance percentage updating
- [ ] IoT simulation responding to compliance
- [ ] LEDs lighting up correctly
- [ ] Alerts generating on low compliance
- [ ] Performance metrics reasonable
- [ ] No console errors (F12)

## 🎓 Example Scenarios

### Scenario 1: Perfect Compliance
```
Total Persons: 5
With Helmet: 5
With Vest: 5
→ Compliance: 100% 🟢
→ LEDs: Green ON, Red OFF
→ Status: ✓ SAFE
```

### Scenario 2: Partial Compliance
```
Total Persons: 5
With Helmet: 3
With Vest: 5
→ Compliance: 60% 🟠
→ LEDs: Both blinking
→ Status: ⚠ WARNING
```

### Scenario 3: Non-Compliance
```
Total Persons: 5
With Helmet: 1
With Vest: 2
→ Compliance: 20% 🔴
→ LEDs: Red ON, buzzer active
→ Status: 🚨 CRITICAL
```

## 📈 Typical Performance

| Metric | Expected Value |
|--------|----------------|
| Page Load | 1-2 seconds |
| First Detection | 2-3 seconds |
| FPS Average | 25-30 |
| API Response | 50-100ms |
| Memory Usage | 300-400MB |
| CPU Usage | 15-25% (idle), 40-60% (active) |

## 🔄 Data Flow Summary

```
Camera Input
    ↓
YOLOv5 Detection
    ↓
Statistics Calculation
    ↓
Database Storage + UI Update
    ↓
IoT Simulation Feedback
    ↓
Alert Generation
    ↓
Real-time Display
```

## 💡 Pro Tips

1. **Use External Camera**: Better quality than webcam
2. **Optimal Lighting**: 300-500 lux for best detection
3. **Clear Background**: Reduces false positives
4. **Proper Distance**: 1-5 meters for best accuracy
5. **Save Frames**: Use Capture button for documentation

## 📞 Support

- Check: `UNIFIED_MONITORING_GUIDE.md` for detailed docs
- Test: `test_unified_monitoring.py` to verify installation
- Logs: Check `logs/` directory for errors

---

**Quick Start**: 
1. Open `/unified` 
2. Click "Start" on camera 
3. Click "Start" on simulation 
4. Watch real-time detection and IoT sync!

✨ **Happy Monitoring!** ✨
