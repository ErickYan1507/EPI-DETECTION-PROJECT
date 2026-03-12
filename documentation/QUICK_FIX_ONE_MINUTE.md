# ⚡ ONE-MINUTE QUICK FIX

## Fastest way to improve performance: Change config parameters

### Make these 3 changes to `config.py`:

**Find and replace these lines:**

#### 1. Reduce camera FPS (line ~126)
```python
# BEFORE:
CAMERA_FPS = 5

# AFTER:
CAMERA_FPS = 2  # Process only 2 frames per second
```

#### 2. Skip more frames (line ~134)
```python
# BEFORE:
FRAME_SKIP = 3

# AFTER:
FRAME_SKIP = 5  # Skip 5 frames between processing
```

#### 3. Increase confidence threshold (line ~37)
```python
# BEFORE:
CONFIDENCE_THRESHOLD = 0.2

# AFTER:
CONFIDENCE_THRESHOLD = 0.35  # Fewer detections = Faster NMS
```

#### 4. Ensure ensemble is OFF for camera (line ~54)
```python
# This should ALREADY be False (good!)
USE_ENSEMBLE_FOR_CAMERA = False  ✅ Keep this!
```

### Save and restart

```powershell
# Kill running app (Ctrl+C in terminal)
# Then restart:
python app/main.py
```

## Expected Result

Response time improvement: **~2-3x faster** 🚀

## Why This Works

- `CAMERA_FPS = 2` → Process 2 frames/sec instead of 5
  - Less inference = Less CPU load

- `FRAME_SKIP = 5` → Skip 5 frames between detections
  - Only 1 detection every ~3 seconds = Huge CPU savings

- `CONFIDENCE_THRESHOLD = 0.35` → Higher threshold
  - Fewer false positives to process
  - Faster NMS (Non-Maximum Suppression) 
  - Still catches real helmets/vests

## What You Lose

- Real-time camera stream becomes 0.4 Hz (1 detection every ~2.5 seconds)
- **But:** You gain **3-5x faster response times**

## If Still Slow

Next steps (in order of impact):
1. **Install GPU PyTorch** (10-30x faster)
2. Install ONNX Runtime (2-3x faster)
3. Implement async database saves
4. Use ONNX quantized model

See `PERFORMANCE_OPTIMIZATION_GUIDE.md` for detailed instructions.
