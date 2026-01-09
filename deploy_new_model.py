"""
Deployer le nouveau modele entraine et tester sa performance
"""

import os
import shutil
import cv2
from pathlib import Path

NEW_MODEL = 'runs/train/epi_detection_v2/weights/best.pt'
BACKUP_MODEL = 'models/best.pt.backup'
PROD_MODEL = 'models/best.pt'

print("=" * 60)
print("DEPLOIEMENT DU NOUVEAU MODELE")
print("=" * 60)

# Verifier que le nouveau modele existe
if not os.path.exists(NEW_MODEL):
    print("\nERR: New model not found at {}".format(NEW_MODEL))
    print("Wait for fast_train.py to complete first!")
    exit(1)

print("\n1. Checking new model size...")
new_size = os.path.getsize(NEW_MODEL) / (1024*1024)
print("   New model: {:.1f} MB".format(new_size))

print("\n2. Backing up current model...")
if os.path.exists(PROD_MODEL):
    shutil.copy(PROD_MODEL, BACKUP_MODEL)
    print("   Backup: {}".format(BACKUP_MODEL))
else:
    print("   No current model to backup")

print("\n3. Deploying new model...")
shutil.copy(NEW_MODEL, PROD_MODEL)
print("   New model deployed: {}".format(PROD_MODEL))

print("\n4. Testing new model...")
try:
    import torch
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=PROD_MODEL, force_reload=True)
    print("   Model loaded successfully!")
    
    # Test sur une image
    if os.path.exists('c.jpg'):
        img = cv2.imread('c.jpg')
        results = model(img)
        detections = results.xyxy[0].cpu().numpy()
        print("   Test detection: {} objects found".format(len(detections)))
        print("   Status: OK")
    
except Exception as e:
    print("   ERR: {}".format(str(e)))
    print("   Rolling back to backup model...")
    shutil.copy(BACKUP_MODEL, PROD_MODEL)
    print("   Rollback complete")
    exit(1)

print("\n" + "=" * 60)
print("DEPLOYMENT SUCCESSFUL!")
print("=" * 60)
print("\nNext steps:")
print("  1. Restart the Flask application")
print("  2. Test with upload.html")
print("  3. Verify improved detection on non-labeled images")
