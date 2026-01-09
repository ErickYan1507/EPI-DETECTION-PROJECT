import torch
import cv2
from pathlib import Path

model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/best.pt', force_reload=False)

print("=" * 60)
print("DIAGNOSTIC DU MODÈLE")
print("=" * 60)

print(f"\nNoms de classes: {model.names}")
print(f"Seuil de confiance: {model.conf}")
print(f"Seuil IOU: {model.iou}")

# Tester avec plusieurs images
test_images = [f for f in Path('.').glob('*.jpg') if f.exists()][:3]

print(f"\nTest sur {len(test_images)} images...")

for img_path in test_images:
    print(f"\n--- {img_path.name} ---")
    img = cv2.imread(str(img_path))
    
    if img is None:
        print("  ❌ Impossible de charger")
        continue
    
    print(f"  Image shape: {img.shape}")
    
    results = model(img)
    detections = results.xyxy[0].cpu().numpy()
    
    print(f"  Détections (confiance >= {model.conf}): {len(detections)}")
    
    if len(detections) > 0:
        for det in detections:
            x1, y1, x2, y2, conf, cls_idx = det
            cls_name = model.names[int(cls_idx)]
            print(f"    - {cls_name}: {conf:.2f}")
    
    # Afficher TOUTES les détections même avec faible confiance
    print(f"\n  Détections avec confiance basse (< 0.3):")
    low_conf_dets = [d for d in detections if d[4] < 0.3]
    if low_conf_dets:
        for det in low_conf_dets:
            x1, y1, x2, y2, conf, cls_idx = det
            cls_name = model.names[int(cls_idx)]
            print(f"    - {cls_name}: {conf:.2f}")
    else:
        print("    Aucune")

print("\n" + "=" * 60)
