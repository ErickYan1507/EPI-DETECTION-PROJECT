#!/usr/bin/env python3
"""Test upload endpoint"""
import requests
import numpy as np
import cv2

# Create a simple test image with OpenCV
image = np.zeros((100, 100, 3), dtype=np.uint8)
image[:, :] = [0, 255, 0]  # Green
cv2.imwrite('test_image.png', image)

print("✅ Image créée: test_image.png")

# Test POST /upload
print("\n📤 Test POST /upload...")
try:
    with open('test_image.png', 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:5000/upload', files=files, timeout=120)
    
    print(f"✅ HTTP {response.status_code}")
    print(response.text[:500])
except Exception as e:
    print(f"❌ Error: {e}")
