import torch
import cv2
from pathlib import Path

model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/best.pt', force_reload=False)

# Tester avec confiance très basse pour voir TOUS les résultats
model.conf = 0.01

img = cv2.imread('a.jpg')
if img is not None:
    print(f"Analyzing a.jpg ({img.shape})")
    
    results = model(img)
    detections = results.xyxy[0].cpu().numpy()
    
    print(f"\nDetections found: {len(detections)}")
    
    if len(detections) > 0:
        # Grouper par confiance
        high = [d for d in detections if d[4] >= 0.5]
        medium = [d for d in detections if 0.3 <= d[4] < 0.5]
        low = [d for d in detections if 0.01 <= d[4] < 0.3]
        
        print(f"\n  HIGH confidence (>= 0.5): {len(high)}")
        for d in high:
            cls_name = model.names[int(d[5])]
            print(f"    - {cls_name}: {d[4]:.3f}")
        
        print(f"\n  MEDIUM confidence (0.3-0.5): {len(medium)}")
        for d in medium:
            cls_name = model.names[int(d[5])]
            print(f"    - {cls_name}: {d[4]:.3f}")
        
        print(f"\n  LOW confidence (0.01-0.3): {len(low)}")
        for d in low:
            cls_name = model.names[int(d[5])]
            print(f"    - {cls_name}: {d[4]:.3f}")
    else:
        print("NO detections found at all, even with very low threshold!")
        print("This image likely contains objects very different from training data")
else:
    print("Could not load a.jpg")
