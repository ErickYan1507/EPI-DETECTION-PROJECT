# API Performance Endpoints Documentation

## Performance Monitoring Endpoints

### 1. Get Real-time Performance Metrics
**Endpoint**: `/api/performance`  
**Method**: `GET`  
**Response**: JSON with performance metrics

#### Response Format
```json
{
  "fps": 4.5,
  "avg_frame_ms": 222.15,
  "avg_inference_ms": 185.32,
  "avg_encoding_ms": 28.45,
  "total_avg_ms": 222.15,
  "timestamp": "2025-12-22T22:11:00"
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `fps` | float | Frames per second (calculated from last 30 frames) |
| `avg_frame_ms` | float | Average total time to process one frame in milliseconds |
| `avg_inference_ms` | float | Average model inference time in milliseconds |
| `avg_encoding_ms` | float | Average JPEG encoding time in milliseconds |
| `total_avg_ms` | float | Total average processing time (same as avg_frame_ms) |
| `timestamp` | string | ISO 8601 timestamp of the response |

#### Example Usage
```bash
# Using curl
curl http://localhost:5000/api/performance

# Using JavaScript
fetch('/api/performance')
  .then(res => res.json())
  .then(data => console.log(`FPS: ${data.fps}, Latency: ${data.total_avg_ms}ms`))

# Using Python
import requests
response = requests.get('http://localhost:5000/api/performance')
metrics = response.json()
print(f"Latency: {metrics['total_avg_ms']}ms")
```

---

### 2. Camera Detection with Timing
**Endpoint**: `/api/camera/detect`  
**Method**: `GET`  
**Response**: Latest detections with timing information

#### Response Format
```json
{
  "detections": [
    {
      "class": "helmet",
      "confidence": 0.95,
      "bbox": [100, 50, 180, 150],
      "color": [0, 255, 0]
    }
  ],
  "statistics": {
    "total_persons": 2,
    "with_helmet": 1,
    "with_vest": 2,
    "with_glasses": 0,
    "with_boots": 0,
    "compliance_rate": 50.0,
    "compliance_level": "partiel",
    "alert_type": "warning",
    "inference_ms": 185.42,
    "total_ms": 215.67
  }
}
```

#### Timing Fields in Statistics
| Field | Description |
|-------|-------------|
| `inference_ms` | Pure model inference time in milliseconds |
| `total_ms` | Total end-to-end detection time in milliseconds |

---

### 3. Upload Image for Detection with Timing
**Endpoint**: `/api/detect`  
**Method**: `POST`  
**Request Body**: JSON with image path

#### Request Format
```json
{
  "image_path": "/path/to/image.jpg"
}
```

#### Response Format
```json
{
  "detections": [...],
  "statistics": {
    "total_persons": 2,
    "with_helmet": 2,
    "with_vest": 1,
    "with_glasses": 0,
    "compliance_rate": 100.0,
    "alert_type": "safe",
    "inference_ms": 192.15,
    "total_ms": 221.43
  },
  "detection_id": 42
}
```

---

## Timing Information Breakdown

### Total Processing Pipeline (in milliseconds)
```
Total Time = Image Loading + Preprocessing + Inference + Postprocessing + Encoding
            ~0-5ms        + ~5-20ms       + ~150-250ms  + ~2-5ms        + ~20-50ms
            = ~180-330ms total
```

### Response Time Categories
- **Fast**: < 150ms (excellent, GPU optimized)
- **Good**: 150-250ms (normal, acceptable real-time)
- **Acceptable**: 250-350ms (usable but slower)
- **Slow**: > 350ms (needs optimization)

### Inference Time Only (Model Execution)
- **GPU (float16)**: 80-150ms
- **GPU (float32)**: 120-200ms
- **CPU**: 1000-5000ms (avoid on CPU)

### Encoding Time (JPEG Compression)
- **Quality 70**: 15-35ms
- **Quality 50**: 10-20ms
- **Quality 30**: 5-10ms

---

## Real-time Monitoring Dashboard

### Example HTML/JavaScript for Performance Dashboard
```html
<div id="performance-metrics">
  <h3>Performance Metrics</h3>
  <p>FPS: <span id="fps">--</span></p>
  <p>Latency: <span id="latency">--</span>ms</p>
  <p>Inference: <span id="inference">--</span>ms</p>
  <p>Encoding: <span id="encoding">--</span>ms</p>
</div>

<script>
// Update metrics every 500ms
setInterval(() => {
  fetch('/api/performance')
    .then(res => res.json())
    .then(data => {
      document.getElementById('fps').textContent = data.fps.toFixed(1);
      document.getElementById('latency').textContent = data.total_avg_ms.toFixed(1);
      document.getElementById('inference').textContent = data.avg_inference_ms.toFixed(1);
      document.getElementById('encoding').textContent = data.avg_encoding_ms.toFixed(1);
    });
}, 500);
</script>
```

---

## Performance Optimization Tips

### Reducing Inference Time
1. **Increase FRAME_SKIP**: Process fewer frames
   ```python
   # In config.py
   FRAME_SKIP = 3  # Process every 3rd frame
   ```

2. **Lower camera resolution**:
   ```python
   CAMERA_FRAME_WIDTH = 480
   CAMERA_FRAME_HEIGHT = 360
   ```

3. **Enable GPU half precision** (usually enabled by default):
   ```python
   ENABLE_HALF_PRECISION = True
   ```

### Reducing Encoding Time
1. **Lower JPEG quality**:
   ```python
   JPEG_QUALITY = 50  # Default is 70
   ```

2. **Reduce camera resolution** (smaller images encode faster)

### Monitoring Performance Over Time
```python
# Sample code to log performance metrics
import time
from collections import deque

metrics_history = deque(maxlen=100)

# In your monitoring loop:
response = requests.get('/api/performance')
metrics = response.json()
metrics['timestamp'] = time.time()
metrics_history.append(metrics)

# Analyze trends
avg_latency = sum(m['total_avg_ms'] for m in metrics_history) / len(metrics_history)
print(f"Average latency over last 100 samples: {avg_latency:.2f}ms")
```

---

## Troubleshooting Timing Issues

### Latency Higher Than Expected

**Check if model is on GPU**:
```bash
# Look at startup logs for:
# "Modèle chargé: ... (Device: cuda)"
# vs
# "Modèle chargé: ... (Device: cpu)"
```

**Verify inference time is reasonable**:
- If `avg_inference_ms` > 300ms: Model running on CPU (slow)
- If `avg_inference_ms` 80-150ms: Normal GPU performance
- If `avg_inference_ms` < 80ms: Excellent GPU optimization

**Check encoding overhead**:
```json
{
  "avg_frame_ms": 250,
  "avg_inference_ms": 180,
  "avg_encoding_ms": 45,
  // The remaining 25ms is preprocessing/postprocessing
}
```

### FPS Is Very Low (< 2 FPS)
1. **Increase FRAME_SKIP** (process fewer frames)
2. **Check GPU utilization** (nvidia-smi on Linux/Windows)
3. **Reduce resolution** significantly
4. **Check system CPU/memory usage**

### FPS Drops During Operation
1. **Database writes blocking stream**: Already mitigated with async saves
2. **Memory leak**: Check if memory usage grows
3. **GPU memory full**: Reduce resolution or increase FRAME_SKIP
4. **System thermal throttling**: Check GPU/CPU temperatures

---

## Expected Performance on Different Hardware

### High-End GPU (RTX 3090)
- **Latency**: 80-120ms
- **FPS**: 8-12 FPS

### Mid-Range GPU (RTX 3060)
- **Latency**: 120-180ms
- **FPS**: 5-8 FPS

### Entry-Level GPU (GTX 1050)
- **Latency**: 180-250ms
- **FPS**: 4-5 FPS

### CPU Only (Not Recommended)
- **Latency**: 2000-5000ms
- **FPS**: 0.2-0.5 FPS

---

## Summary

The optimized detection system provides:
- **Inference times: 80-250ms** depending on GPU
- **Total pipeline latency: 200-300ms**
- **Real-time performance suitable for live monitoring**
- **Easy performance monitoring via API endpoints**
