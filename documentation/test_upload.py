import requests
import os
from pathlib import Path

BASE_URL = 'http://localhost:5000'
TEST_IMAGE = 'c.jpg'

if not os.path.exists(TEST_IMAGE):
    print(f"Image {TEST_IMAGE} not found")
    exit(1)

with open(TEST_IMAGE, 'rb') as f:
    files = {'file': f}
    data = {'type': 'image'}
    
    print(f"Uploading {TEST_IMAGE}...")
    response = requests.post(f'{BASE_URL}/upload', files=files, data=data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
