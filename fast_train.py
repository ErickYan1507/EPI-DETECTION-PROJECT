"""
Script de retrainement rapide du modele avec augmentation intrinseque YOLO
YOLO gere deja l'augmentation pendant l'entrainnement
"""

import os
import torch
import warnings

warnings.filterwarnings('ignore')

print("=" * 60)
print("RETRAINEMENT DU MODELE YOLO")
print("=" * 60)

# Verifier que le dataset existe
if not os.path.exists('dataset/data.yaml'):
    print("ERR: dataset/data.yaml not found!")
    print("Make sure dataset is configured in dataset/data.yaml")
    exit(1)

print("\nVerifications:")
print("  - Dataset: OK")
print("  - CUDA available:", torch.cuda.is_available())
print("  - PyTorch version:", torch.__version__)

print("\nCharging YOLOv5 model...")
model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/best.pt', force_reload=False)

print("\nConfiguration du retrainement:")
print("  - Epochs: 30")
print("  - Image size: 640")
print("  - Batch size: 8")
print("  - Device: {}".format('cuda' if torch.cuda.is_available() else 'cpu'))
print("  - Augmentation: YOLO built-in")

print("\nDemarrage du retrainement...")
print("  Ceci peut prendre 30-60 minutes...")

try:
    results = model.train(
        data='dataset/data.yaml',
        epochs=50,
        imgsz=640,
        batch=8,
        patience=20,
        device=0 if torch.cuda.is_available() else 'cpu',
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10,
        translate=0.1,
        scale=0.5,
        flipud=0.5,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
        project='runs/train',
        name='epi_detection_v2',
        exist_ok=True,
        save=True,
        cache=True,
        workers=4,
        verbose=True
    )
    
    print("\nRetrainement complete avec succes!")
    print("  Meilleur modele: runs/train/epi_detection_v2/weights/best.pt")
    print("\nPour utiliser le nouveau modele:")
    print("  1. Copier runs/train/epi_detection_v2/weights/best.pt vers models/best.pt")
    print("  2. Redemarrer l'application")
    
except Exception as e:
    print("ERR: Erreur pendant le retrainement: {}".format(str(e)))
    import traceback
    traceback.print_exc()
