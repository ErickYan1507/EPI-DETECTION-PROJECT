#!/usr/bin/env python
import sys
from pathlib import Path

try:
    from app.camera import CameraManager, CameraStreamManager
    print("✓ Camera module imported successfully")
    print("✓ CameraManager available")
    print("✓ CameraStreamManager available")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("\n✓ All imports successful!")
