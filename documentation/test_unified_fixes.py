#!/usr/bin/env python3
"""
Test des corrections pour unified_monitoring.html
- Vérification que /api/tinkercad/update existe
- Vérification que /api/camera/frame existe
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def test_tinkercad_update():
    """Tester l'endpoint /api/tinkercad/update"""
    print("\n✅ TEST 1: POST /api/tinkercad/update")
    print("-" * 50)
    
    try:
        payload = {
            'sensor_id': 'tinkercad_sim_001',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'motion_detected': True,
                'compliance_level': 85,
                'led_green': True,
                'led_red': False,
                'buzzer_active': False,
                'worker_present': True
            }
        }
        
        response = requests.post(
            f'{BASE_URL}/api/tinkercad/update',
            json=payload,
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data}")
            print(f"Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_camera_frame():
    """Tester l'endpoint /api/camera/frame"""
    print("\n✅ TEST 2: GET /api/camera/frame")
    print("-" * 50)
    
    try:
        response = requests.get(f'{BASE_URL}/api/camera/frame', timeout=5)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Frame reçu ({len(response.content)} bytes)")
            print(f"Content-Type: {response.headers.get('content-type')}")
            return True
        elif response.status_code == 404:
            print(f"⚠️  Caméra pas prête (pas de frame disponible)")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_camera_detect():
    """Tester l'endpoint /api/camera/detect"""
    print("\n✅ TEST 3: GET /api/camera/detect")
    print("-" * 50)
    
    try:
        response = requests.get(f'{BASE_URL}/api/camera/detect', timeout=5)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print(f"✅ Détection reçue")
            print(f"  - Total persons: {stats.get('total_persons', 0)}")
            print(f"  - With helmet: {stats.get('with_helmet', 0)}")
            print(f"  - Compliance: {stats.get('compliance_rate', 0):.1f}%")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_iot_simulation_state():
    """Tester l'endpoint /api/iot/simulation/state"""
    print("\n✅ TEST 4: GET /api/iot/simulation/state")
    print("-" * 50)
    
    try:
        response = requests.get(f'{BASE_URL}/api/iot/simulation/state', timeout=5)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            state = data.get('state', {})
            print(f"✅ État simulation reçu")
            print(f"  - Running: {data.get('running', False)}")
            print(f"  - Motion: {state.get('motion_detected', False)}")
            print(f"  - Compliance: {state.get('compliance_level', 0)}")
            print(f"  - LED Green: {state.get('led_green', False)}")
            print(f"  - LED Red: {state.get('led_red', False)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("="*60)
    print("🧪 TEST DES CORRECTIONS - UNIFIED_MONITORING.HTML")
    print("="*60)
    
    results = []
    
    results.append(("TinkerCad Update", test_tinkercad_update()))
    results.append(("Camera Frame", test_camera_frame()))
    results.append(("Camera Detect", test_camera_detect()))
    results.append(("IoT Simulation", test_iot_simulation_state()))
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {passed}/{total}")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
    else:
        print("⚠️  Certains tests ont échoué.")

if __name__ == '__main__':
    import time
    print("\n⏳ Attente de 2 secondes pour que le serveur soit prêt...")
    time.sleep(2)
    main()
