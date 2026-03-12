#!/usr/bin/env python3
"""
Test les endpoints API email pour voir lesquels répondent
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("="*70)
print("TEST DES ENDPOINTS API EMAIL")
print("="*70)

endpoints = [
    ("GET", "/api/email/config", None),
    ("GET", "/api/email/recipients", None),
    ("GET", "/api/email/status", None),
    ("POST", "/api/email/send-test", {"recipient": "20firmino09@gmail.com"}),
]

for method, path, data in endpoints:
    print(f"\n{method} {path}")
    try:
        if method == "GET":
            r = requests.get(f"{BASE_URL}{path}", timeout=5)
        else:
            r = requests.post(f"{BASE_URL}{path}", json=data, timeout=5)
        
        print(f"  Status Code: {r.status_code}")
        
        if r.status_code == 200:
            print(f"  ✓ Response: {len(r.text)} bytes")
            try:
                result = r.json()
                print(f"  JSON: {json.dumps(result, indent=2)[:200]}...")
            except:
                print(f"  Text: {r.text[:100]}...")
        else:
            print(f"  ✗ Error: {r.status_code}")
            print(f"  Text: {r.text[:200]}")
    except Exception as e:
        print(f"  ✗ Exception: {e}")

print("\n" + "="*70)
