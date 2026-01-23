import torch
from pathlib import Path

# Try to import Model from yolov5 to allowlist it
try:
    from yolov5.models.yolo import Model
except Exception as e:
    print('Import Model failed:', e)
    Model = None

weights = Path('yolov5s.pt')
if not weights.exists():
    print('weights file not found:', weights)
    raise SystemExit(1)

# Try to add safe globals and load
try:
    if Model is not None:
        try:
            torch.serialization.add_safe_globals([Model])
            print('add_safe_globals OK')
        except Exception as e:
            print('add_safe_globals error:', e)
    ckpt = torch.load(str(weights), map_location='cpu', weights_only=False)
    print('Loaded ckpt keys:', list(ckpt.keys()))
except Exception as e:
    print('Error loading checkpoint:', repr(e))
    raise
