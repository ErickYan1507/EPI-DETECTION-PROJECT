#!/usr/bin/env python3
"""
🚀 EPI Detection Performance Optimization Script
Automatically applies recommended optimizations
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from config import config
from app.logger import logger

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_gpu():
    """Check if CUDA is available"""
    print("📊 Checking GPU availability...")
    try:
        import torch
        has_cuda = torch.cuda.is_available()
        if has_cuda:
            print(f"✅ GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA Version: {torch.version.cuda}")
            return True
        else:
            print(f"❌ GPU not available (torch: {torch.__version__})")
            print(f"   Using CPU inference (slow)")
            return False
    except Exception as e:
        print(f"❌ Error checking GPU: {e}")
        return False

def test_inference_speed():
    """Test current inference speed"""
    print("\n⏱️  Testing inference speed...")
    try:
        import cv2
        import numpy as np
        from app.detection import EPIDetector
        
        # Create dummy image
        dummy_img = np.zeros((config.CAMERA_FRAME_HEIGHT, config.CAMERA_FRAME_WIDTH, 3), dtype=np.uint8)
        dummy_img[:] = (255, 200, 100)  # Add some content
        
        detector = EPIDetector()
        
        # Warm up
        detector.detect(dummy_img)
        
        # Measure
        times = []
        for i in range(3):
            start = time.perf_counter()
            detections, stats = detector.detect(dummy_img)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            print(f"  Run {i+1}: {elapsed:.0f}ms")
        
        avg_time = sum(times) / len(times)
        print(f"\n📈 Average inference time: {avg_time:.0f}ms")
        
        if avg_time > 1000:
            print("⚠️  SLOW - Inference takes >1 second!")
            print("   Recommended: Install GPU PyTorch or use ONNX Runtime")
        elif avg_time > 500:
            print("⚠️  MODERATE - Could be faster")
        else:
            print("✅ GOOD inference speed")
            
        return avg_time
    except Exception as e:
        logger.error(f"Error testing inference: {e}")
        print(f"❌ Error: {e}")
        return None

def install_onnx_runtime():
    """Install ONNX Runtime with GPU support"""
    print("\n📦 Installing ONNX Runtime...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "onnxruntime-gpu==1.17.0", "-q"
        ])
        print("✅ ONNX Runtime GPU installed")
        
        # Test import
        import onnxruntime
        print(f"   Available providers: {onnxruntime.get_available_providers()}")
        return True
    except Exception as e:
        print(f"⚠️  ONNX GPU install failed: {e}")
        print("   Trying CPU version...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "onnxruntime==1.17.0", "-q"
            ])
            print("✅ ONNX Runtime (CPU) installed")
            return True
        except Exception as e2:
            print(f"❌ ONNX install failed: {e2}")
            return False

def convert_to_onnx():
    """Convert PyTorch model to ONNX"""
    print("\n🔄 Converting model to ONNX...")
    try:
        import torch
        import numpy as np
        
        model_path = config.MODEL_PATH
        onnx_path = model_path.replace('.pt', '.onnx')
        
        if Path(onnx_path).exists():
            print(f"✅ ONNX model already exists: {onnx_path}")
            return True
        
        print(f"   Source: {model_path}")
        print(f"   Target: {onnx_path}")
        
        # Load PyTorch model
        print("   Loading PyTorch model...")
        from app.detection import EPIDetector
        detector = EPIDetector(model_path)
        
        # Create dummy input
        dummy_input = torch.randn(1, 3, 320, 240)
        if torch.cuda.is_available():
            dummy_input = dummy_input.cuda()
            detector.model = detector.model.cuda()
        
        # Export to ONNX
        print("   Exporting to ONNX (this may take 30-60 seconds)...")
        torch.onnx.export(
            detector.model,
            dummy_input,
            onnx_path,
            opset_version=12,
            input_names=['images'],
            output_names=['output'],
            dynamic_axes={'images': {0: 'batch_size'}}
        )
        
        print(f"✅ ONNX model created: {onnx_path}")
        print(f"   Size: {Path(onnx_path).stat().st_size / 1024 / 1024:.1f}MB")
        return True
        
    except Exception as e:
        logger.error(f"✅ ONNX conversion skipped: {e}")
        print(f"⚠️  ONNX conversion: {e}")
        print("   (Not critical - app will still work with PyTorch)")
        return False

def optimize_config():
    """Suggest config optimizations"""
    print("\n⚙️  Config Optimization Recommendations:")
    
    config_changes = []
    
    # Check current settings
    if config.CAMERA_FPS > 2:
        config_changes.append({
            'current': config.CAMERA_FPS,
            'setting': 'CAMERA_FPS',
            'recommended': 2,
            'reason': 'Lower FPS = Less processing load'
        })
    
    if config.FRAME_SKIP < 5:
        config_changes.append({
            'current': config.FRAME_SKIP,
            'setting': 'FRAME_SKIP',
            'recommended': 5,
            'reason': 'Skip more frames = Faster processing'
        })
    
    if config.CONFIDENCE_THRESHOLD < 0.3:
        config_changes.append({
            'current': config.CONFIDENCE_THRESHOLD,
            'setting': 'CONFIDENCE_THRESHOLD',
            'recommended': 0.3,
            'reason': 'Higher threshold = Fewer false positives + Faster NMS'
        })
    
    if config.USE_ENSEMBLE_FOR_CAMERA:
        config_changes.append({
            'current': True,
            'setting': 'USE_ENSEMBLE_FOR_CAMERA',
            'recommended': False,
            'reason': 'Ensemble = Multiple inference passes (slow)'
        })
    
    if not config_changes:
        print("✅ Config already optimized!")
        return
    
    print(f"\nFound {len(config_changes)} optimization opportunities:\n")
    for i, change in enumerate(config_changes, 1):
        print(f"{i}. {change['setting']}")
        print(f"   Current: {change['current']}")
        print(f"   Recommended: {change['recommended']}")
        print(f"   Reason: {change['reason']}")
        print()
    
    # Ask user
    response = input("Apply recommended changes? (y/n): ").lower().strip()
    if response == 'y':
        apply_config_changes(config_changes)

def apply_config_changes(changes):
    """Apply config changes"""
    print("\n✏️  Applying config changes...")
    
    config_path = project_root / 'config.py'
    config_content = config_path.read_text()
    
    for change in changes:
        old_pattern = f"{change['setting']} = {change['current']}"
        new_pattern = f"{change['setting']} = {change['recommended']}"
        
        if old_pattern in config_content:
            config_content = config_content.replace(old_pattern, new_pattern)
            print(f"✅ Updated {change['setting']}: {change['current']} → {change['recommended']}")
        else:
            print(f"⚠️  Could not find {change['setting']} = {change['current']}")
    
    config_path.write_text(config_content)
    print("✅ Config saved!")

def main():
    """Main optimization flow"""
    print_header("🚀 EPI Detection Performance Optimization")
    
    print("This script will:")
    print("  1. Diagnose current performance")
    print("  2. Check GPU availability")
    print("  3. Install accelerators (ONNX Runtime)")
    print("  4. Test inference speed")
    print("  5. Recommend config optimizations")
    print()
    
    # Step 1: Check GPU
    has_gpu = check_gpu()
    
    # Step 2: Test current speed
    print_header("STEP 1: Current Performance")
    before_speed = test_inference_speed()
    
    # Step 3: Install ONNX
    print_header("STEP 2: Install ONNX Runtime")
    response = input("\nInstall ONNX Runtime? (y/n): ").lower().strip()
    if response == 'y':
        if install_onnx_runtime():
            convert_to_onnx()
    
    # Step 4: Config recommendations
    print_header("STEP 3: Config Optimization")
    optimize_config()
    
    # Summary
    print_header("📊 Optimization Summary")
    print("✅ Next steps:")
    print()
    if not has_gpu:
        print("1. ⭐ GPU PyTorch (if you have NVIDIA GPU):")
        print("   pip uninstall torch torchvision -y")
        print("   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        print()
    print("2. Restart Flask app to apply changes")
    print("   python app/main.py")
    print()
    print("3. Test inference speed again")
    print("   This script can be re-run to compare performance")
    print()
    print("Expected improvements:")
    if has_gpu:
        print("  - With GPU: 10-30x faster inference")
    else:
        print("  - With ONNX: 2-3x faster on CPU")
    print("  - With config changes: 2-5x faster camera processing")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Optimization cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Optimization error: {e}")
        sys.exit(1)
