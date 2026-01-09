import torch
import sys
import psutil
import cv2

print("=" * 60)
print("SYSTEM DIAGNOSTICS")
print("=" * 60)

print(f"\nPython: {sys.version}")
print(f"PyTorch: {torch.__version__}")
print(f"OpenCV: {cv2.__version__}")

print(f"\nCUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("GPU: NOT AVAILABLE - Running on CPU (VERY SLOW)")

cpu_count = psutil.cpu_count()
ram = psutil.virtual_memory().total / (1024**3)
print(f"\nCPU Cores: {cpu_count}")
print(f"Total RAM: {ram:.1f} GB")

try:
    model = torch.hub.load('ultralytics/yolov5', 'custom', 
                          path='models/best.pt', force_reload=False)
    print(f"\nModel loaded successfully")
    print(f"Model device: {next(model.parameters()).device}")
except Exception as e:
    print(f"\nModel loading ERROR: {e}")

print("=" * 60)
