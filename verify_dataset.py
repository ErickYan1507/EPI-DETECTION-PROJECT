"""
Verifier que le dataset est correct pour l'entrainnement
"""

import os
from pathlib import Path

DATASET_PATH = 'dataset'

print("=" * 60)
print("VERIFICATION DU DATASET")
print("=" * 60)

# Verifier data.yaml
if os.path.exists(os.path.join(DATASET_PATH, 'data.yaml')):
    print("\n1. data.yaml: OK")
else:
    print("\n1. data.yaml: MISSING")

# Verifier train
train_imgs = os.path.join(DATASET_PATH, 'images', 'train')
train_labels = os.path.join(DATASET_PATH, 'labels', 'train')

if os.path.exists(train_imgs):
    train_count = len([f for f in os.listdir(train_imgs) if f.endswith(('.jpg', '.png'))])
    print("\n2. Train images: {} files".format(train_count))
else:
    print("\n2. Train images: MISSING")
    train_count = 0

if os.path.exists(train_labels):
    label_count = len([f for f in os.listdir(train_labels) if f.endswith('.txt')])
    print("   Train labels: {} files".format(label_count))
else:
    print("   Train labels: MISSING")
    label_count = 0

if train_count > 0 and label_count > 0:
    if train_count == label_count:
        print("   Match: OK")
    else:
        print("   Match: MISMATCH ({} images, {} labels)".format(train_count, label_count))

# Verifier test
test_imgs = os.path.join(DATASET_PATH, 'images', 'test')
test_labels = os.path.join(DATASET_PATH, 'labels', 'test')

if os.path.exists(test_imgs):
    test_count = len([f for f in os.listdir(test_imgs) if f.endswith(('.jpg', '.png'))])
    print("\n3. Test images: {} files".format(test_count))
else:
    print("\n3. Test images: MISSING")
    test_count = 0

if os.path.exists(test_labels):
    test_label_count = len([f for f in os.listdir(test_labels) if f.endswith('.txt')])
    print("   Test labels: {} files".format(test_label_count))
else:
    print("   Test labels: MISSING")
    test_label_count = 0

# Verifier val
val_imgs = os.path.join(DATASET_PATH, 'images', 'val')
if os.path.exists(val_imgs):
    val_count = len([f for f in os.listdir(val_imgs) if f.endswith(('.jpg', '.png'))])
    print("\n4. Val images: {} files".format(val_count))
else:
    print("\n4. Val images: MISSING (will use test as val)")
    val_count = test_count

print("\n" + "=" * 60)
print("RESUME:")
print("  Total training: {}".format(train_count))
print("  Total test: {}".format(test_count))
print("  Total validation: {}".format(val_count if val_count > 0 else test_count))
print("=" * 60)

if train_count >= 50 and label_count >= 50:
    print("\nStatus: OK - Dataset is ready for training")
    print("Execute: python fast_train.py")
else:
    print("\nStatus: INSUFFICIENT DATA")
    print("Need at least 50 images with labels for training")
