"""
Monitorer la progression de l'entrainnement
"""

import os
import time
from pathlib import Path

TRAINING_DIR = 'runs/train/epi_detection_v2'
FINAL_MODEL = os.path.join(TRAINING_DIR, 'weights', 'best.pt')

print("=" * 60)
print("MONITORING TRAINING PROGRESS")
print("=" * 60)

print("\nWaiting for training to start...")
print("Check logs at: {}".format(TRAINING_DIR))

max_checks = 360
check_interval = 10

for check_num in range(max_checks):
    if os.path.exists(FINAL_MODEL):
        model_size = os.path.getsize(FINAL_MODEL) / (1024*1024)
        print("\nOK: Final model found!")
        print("  Size: {:.1f} MB".format(model_size))
        print("\nTraining completed! To deploy:")
        print("  python deploy_new_model.py")
        exit(0)
    
    # Check for training results
    results_file = os.path.join(TRAINING_DIR, 'results.csv')
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            lines = f.readlines()
            last_epoch = len(lines) - 1
            print("  Epoch {}/30 completed...".format(last_epoch), end='\r')
    
    if check_num > 0 and check_num % 6 == 0:
        print("  Still training... ({} minutes elapsed)".format(check_num * check_interval // 60))
    
    time.sleep(check_interval)

print("\nTimeout: Training took too long (> 1 hour)")
print("Check manually at: {}".format(TRAINING_DIR))
