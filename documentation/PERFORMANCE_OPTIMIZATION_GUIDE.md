# 🚀 Performance Optimization Guide - EPI Detection

## Current Issue
**Your app reports "LES RESPONSES SONT LENT"** (slow responses). Main cause: **CPU-only PyTorch inference**

### Current Status
```
torch version: 2.9.1+cpu  ❌ CPU ONLY - EXTREMELY SLOW
Device: cpu
Model: YOLOv5 (7M parameters)
Inference time: ~2-5 seconds per image on CPU ❌
```

---

## 🎯 Quick Wins (Priority Order)

### 1. **Install GPU PyTorch (HIGHEST PRIORITY)**
If you have an NVIDIA GPU:

```powershell
# Remove current CPU torch
pip uninstall torch torchvision -y

# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify
python -c "import torch; print(torch.cuda.is_available())"  # Should return True
```

**Expected improvement:** ~10-15x faster inference (2s → 150ms per image)

---

### 2. **Enable ONNX Runtime Acceleration (NO GPU REQUIRED)**

ONNX Runtime can provide 2-3x speedup even on CPU with DirectML (GPU) support.

```powershell
# Install ONNX Runtime with GPU support
pip install onnxruntime onnxruntime-gpu==1.17.0

# Convert model to ONNX (run once)
python -c "
import torch
from app.detection import EPIDetector
detector = EPIDetector('models/best.pt')
dummy_input = torch.randn(1, 3, 320, 240)
torch.onnx.export(detector.model, dummy_input, 'models/best.onnx', opset_version=12)
print('ONNX model saved!')
"
```

Then update [detection.py](app/detection.py) to use ONNX:

```python
# Add this import at the top
import onnxruntime as ort

# In EPIDetector.__init__(), add ONNX option:
try:
    sess_options = ort.SessionOptions()
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    self.ort_session = ort.InferenceSession(
        model_path.replace('.pt', '.onnx'),
        providers=['DmlExecutionProvider', 'CPUExecutionProvider'],
        sess_options=sess_options
    )
except Exception as e:
    logger.warning(f"ONNX model not available: {e}")
    self.ort_session = None
```

**Expected improvement:** 2-3x speedup (no GPU required!)

---

### 3. **Reduce Real-Time Processing Load**

Edit [config.py](config.py):

```python
# Current (SLOW)
CAMERA_FPS = 5              # Process every frame at 5 FPS
FRAME_SKIP = 3              # Then skip 3 frames = ~1 FPS actual processing
USE_ENSEMBLE_FOR_CAMERA = False  # Good, keep this

# Optimized (FAST)
CAMERA_FPS = 2              # Reduce to 2 FPS capture (enough for monitoring)
FRAME_SKIP = 5              # Skip more frames = 0.4 FPS processing
USE_ENSEMBLE_FOR_CAMERA = False  # KEEP THIS - don't use ensemble for real-time
```

**Expected improvement:** ~5x less CPU load on camera stream

---

### 4. **Async Database Operations**

Slow database writes are blocking requests. Update [main.py](app/main.py) around line 700:

```python
# CURRENT (BLOCKING)
detection_record = Detection(...)
db.session.add(detection_record)
db.session.commit()  # ⚠️ BLOCKS HERE - Can be 100ms+

# OPTIMIZED (ASYNC)
def save_detection_async(detection_dict):
    try:
        detection_record = Detection(**detection_dict)
        db.session.add(detection_record)
        db.session.commit()
    except Exception as e:
        logger.error(f"DB error: {e}")

# In upload handler:
detection_dict = {...}
threading.Thread(target=save_detection_async, args=(detection_dict,), daemon=True).start()
```

**Expected improvement:** Responses ~100-300ms faster

---

### 5. **Disable Ensemble for Camera (Already Done!)**
Your config already has `USE_ENSEMBLE_FOR_CAMERA = False` ✅

But verify in [main.py](app/main.py) line ~180 that you're respecting this:

```python
# Make sure it's like this:
if use_ensemble and len(multi_detector.models) > 1:
    detections, stats = multi_detector._detect_ensemble(image)
else:
    detections, stats = multi_detector._detect_single(image)
```

**Expected improvement:** If ensemble was running, ~2-3x faster

---

## 📊 Optimization Impact Summary

| Optimization | Effort | Speedup | Notes |
|---|---|---|---|
| **GPU PyTorch** | Medium | **10-15x** ⭐ | Requires NVIDIA GPU |
| **ONNX Runtime** | Low | **2-3x** | Works on CPU/GPU |
| **Reduce FPS** | Very Easy | **2-3x** | Just edit config |
| **Async DB** | Low | **2-3x** | Faster responses |
| **Disable Ensemble Camera** | Already Done | **2-3x** | Already enabled |
| **Model Quantization** | Medium | **1.5-2x** | More work needed |

**Total potential improvement with all optimizations:** ~20-30x faster responses! 🚀

---

## 🔧 Implementation Checklist

- [ ] Check if you have an NVIDIA GPU (run `gpu-z` or check Device Manager)
- [ ] If GPU available: Install CUDA PyTorch (5 min)
- [ ] If no GPU: Install ONNX Runtime (5 min)
- [ ] Reduce CAMERA_FPS to 2 and FRAME_SKIP to 5 (1 min)
- [ ] Implement async database saves (10 min)
- [ ] Test inference time with: `python` then `from app.detection import EPIDetector; import time; d=EPIDetector(); t=time.time(); d.detect(img); print(time.time()-t)`
- [ ] Monitor CPU usage before/after

---

## 🔍 Performance Monitoring

Add this to your app to track response times:

```python
import time
from functools import wraps

def measure_performance(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = f(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        if elapsed > 100:  # Log if > 100ms
            logger.warning(f"{f.__name__} took {elapsed:.0f}ms")
        return result
    return wrapper

@app.route('/api/camera/detect')
@measure_performance
def camera_detect():
    return jsonify(camera_manager.last_detection)
```

---

## 📈 Expected Response Times After Optimization

| Scenario | Before | After (GPU) | After (ONNX) |
|---|---|---|---|
| Screenshot detection | 3-5s | 200-300ms | 800ms-1s |
| Real-time camera | Slow/Laggy | Smooth 5-10 FPS | Smooth 1-2 FPS |
| Dashboard load | Slow | Fast | Fast |
| Upload & detect | 5-10s | 500-800ms | 1-2s |

---

## ⚠️ If Still Slow After Optimizations

1. **Profile your code:**
   ```python
   python -m cProfile -s cumulative app/main.py
   ```

2. **Check database queries:** Enable `SQLALCHEMY_ECHO = True` in [config.py](config.py)

3. **Use Gunicorn with multiple workers:**
   ```powershell
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 "app.main:app"
   ```

4. **Consider using FastAPI instead of Flask** (much faster for real-time apps)

---

## 🎓 Next Steps

1. Start with **GPU PyTorch** install (biggest impact)
2. Then **ONNX Runtime** (as backup acceleration)
3. Then adjust **config.py** parameters
4. Finally, implement **async database saves**

Good luck! 🚀
