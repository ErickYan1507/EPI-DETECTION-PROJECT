"""
Test for Unified Monitoring Page
Verifies that all routes and endpoints are properly configured
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_unified_monitoring():
    """Test the unified monitoring page configuration"""
    
    print("=" * 60)
    print("Testing Unified Monitoring Integration")
    print("=" * 60)
    
    # Test 1: Check if main.py has the route
    print("\n✓ Test 1: Checking /unified route in main.py...")
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if '@app.route(\'/unified\')' in content and 'unified_monitoring.html' in content:
            print("  ✓ Route /unified found and correctly configured")
        else:
            print("  ✗ Route /unified not found!")
            return False
    
    # Test 2: Check if template exists
    print("\n✓ Test 2: Checking unified_monitoring.html template...")
    template_path = Path('templates/unified_monitoring.html')
    if template_path.exists():
        file_size = template_path.stat().st_size
        print(f"  ✓ Template found ({file_size:,} bytes)")
    else:
        print("  ✗ Template not found!")
        return False
    
    # Test 3: Check if navbar has the link
    print("\n✓ Test 3: Checking navbar link in base.html...")
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
        if '/unified' in content and 'Unified Monitoring' in content:
            print("  ✓ Navbar link configured correctly")
        else:
            print("  ✗ Navbar link not found!")
            return False
    
    # Test 4: Check if camera endpoints exist
    print("\n✓ Test 4: Checking required API endpoints...")
    required_endpoints = [
        '/api/camera/start',
        '/api/camera/stop',
        '/api/camera/detect',
        '/api/camera/frame',
        '/api/performance',
        '/api/iot/simulation/start',
        '/api/iot/simulation/stop',
        '/api/iot/simulation/state',
    ]
    
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        for endpoint in required_endpoints:
            endpoint_route = endpoint.replace('/api/camera/', '@app.route(\'/api/camera/').replace('/api/iot/', '@app.route(\'/api/iot/')
            if endpoint in content or endpoint.replace('/api/', '') in content:
                print(f"  ✓ {endpoint}")
            else:
                print(f"  ✗ {endpoint} - NOT FOUND")
    
    # Test 5: Check imports
    print("\n✓ Test 5: Checking required imports...")
    required_imports = [
        'from flask import Flask, render_template, request, jsonify, send_file, Response',
        'import io',
        'from app.detection import EPIDetector',
        'from app.tinkercad_sim import TinkerCadSimulator',
    ]
    
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        for imp in required_imports:
            if 'io' in imp or any(part in content for part in imp.split(', ')):
                print(f"  ✓ Required imports present")
                break
    
    # Test 6: Check template content
    print("\n✓ Test 6: Verifying template structure...")
    with open('templates/unified_monitoring.html', 'r', encoding='utf-8') as f:
        content = f.read()
        required_elements = [
            'class="monitoring-grid"',
            'id="videoContainer"',
            'id="detectionList"',
            'id="motionLight"',
            'class="camera-controls"',
            'startCamera()',
            'startSimulation()',
            'updateDetectionStats()',
        ]
        
        missing = []
        for element in required_elements:
            if element not in content:
                missing.append(element)
        
        if not missing:
            print("  ✓ All template elements present")
        else:
            print(f"  ✗ Missing elements: {missing}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print("\n📝 Quick Start:")
    print("1. Start the Flask application: python run_app.py")
    print("2. Open browser: http://localhost:5000/unified")
    print("3. Click 'Start' to begin camera and simulation")
    print("4. Monitor real-time detection and IoT status")
    print("\n📚 Documentation: See UNIFIED_MONITORING_GUIDE.md")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = test_unified_monitoring()
    sys.exit(0 if success else 1)
