#!/usr/bin/env python3
"""
🔍 EPI Detection Performance Diagnostic
Identify bottlenecks and provide personalized recommendations
"""

import os
import sys
import time
import psutil
import platform
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from config import config

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_system_specs():
    """Check hardware specifications"""
    print_section("1️⃣  SYSTEM SPECIFICATIONS")
    
    print(f"\n🖥️  Hardware:")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  CPU: {platform.processor()}")
    print(f"  CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical")
    print(f"  RAM: {psutil.virtual_memory().total / 1024**3:.1f}GB")
    print(f"  Available RAM: {psutil.virtual_memory().available / 1024**3:.1f}GB")
    
    print(f"\n📊 GPU Status:")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  ✅ GPU: {torch.cuda.get_device_name(0)}")
            print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
            print(f"  CUDA Version: {torch.version.cuda}")
        else:
            print(f"  ❌ GPU: Not Available (using CPU)")
            print(f"  PyTorch: {torch.__version__}")
            print(f"  ℹ️  Install CUDA PyTorch for 10-30x speedup!")
    except Exception as e:
        print(f"  ❌ Error checking GPU: {e}")

def check_model_info():
    """Check loaded model information"""
    print_section("2️⃣  MODEL INFORMATION")
    
    print(f"\n📁 Model Path: {config.MODEL_PATH}")
    if Path(config.MODEL_PATH).exists():
        size_mb = Path(config.MODEL_PATH).stat().st_size / 1024 / 1024
        print(f"  Size: {size_mb:.1f}MB")
        print(f"  ✅ Model file exists")
    else:
        print(f"  ❌ Model file NOT FOUND!")
    
    print(f"\n⚙️  Model Configuration:")
    print(f"  CONFIDENCE_THRESHOLD: {config.CONFIDENCE_THRESHOLD}")
    print(f"  IOU_THRESHOLD: {config.IOU_THRESHOLD}")
    print(f"  MAX_DETECTIONS: {config.MAX_DETECTIONS}")
    
    print(f"\n🎯 Performance Settings:")
    print(f"  CAMERA_FPS: {config.CAMERA_FPS}")
    print(f"  FRAME_SKIP: {config.FRAME_SKIP}")
    print(f"  Effective FPS: {config.CAMERA_FPS / (config.FRAME_SKIP + 1):.1f}")
    print(f"  ENABLE_GPU: {config.ENABLE_GPU}")
    print(f"  ENABLE_HALF_PRECISION: {config.ENABLE_HALF_PRECISION}")
    print(f"  USE_ENSEMBLE_FOR_CAMERA: {config.USE_ENSEMBLE_FOR_CAMERA}")
    
    print(f"\n🔍 Ensemble Settings:")
    print(f"  MULTI_MODEL_ENABLED: {config.MULTI_MODEL_ENABLED}")
    print(f"  ENSEMBLE_STRATEGY: {config.ENSEMBLE_STRATEGY}")
    
    # Count available models
    try:
        import glob
        models = glob.glob(os.path.join(config.MODELS_FOLDER, '*.pt'))
        print(f"  Models Available: {len(models)}")
        for m in models:
            size = Path(m).stat().st_size / 1024 / 1024
            print(f"    - {Path(m).name}: {size:.1f}MB")
    except Exception as e:
        print(f"  Models: Error - {e}")

def benchmark_inference():
    """Quick inference benchmark"""
    print_section("3️⃣  INFERENCE BENCHMARK")
    
    try:
        import cv2
        import numpy as np
        from app.detection import EPIDetector
        
        print("\n📸 Creating test image...")
        dummy_img = np.random.randint(0, 255, (config.CAMERA_FRAME_HEIGHT, config.CAMERA_FRAME_WIDTH, 3), dtype=np.uint8)
        
        print("🔧 Loading detector...")
        detector = EPIDetector()
        
        print("🔥 Warm-up inference (1 run)...")
        detector.detect(dummy_img)
        
        print("⏱️  Measuring inference time (3 runs)...")
        times = []
        for i in range(3):
            start = time.perf_counter()
            detections, stats = detector.detect(dummy_img)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            print(f"  Run {i+1}: {elapsed:6.0f}ms")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 Results:")
        print(f"  Average: {avg_time:.0f}ms")
        print(f"  Min: {min_time:.0f}ms")
        print(f"  Max: {max_time:.0f}ms")
        print(f"  Estimated RTT: {avg_time/1000:.1f}s")
        
        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        if avg_time < 100:
            print(f"  ✅ EXCELLENT (Real-time/interactive)")
        elif avg_time < 500:
            print(f"  ✅ GOOD (Near real-time)")
        elif avg_time < 1000:
            print(f"  ⚠️  MODERATE (Acceptable)")
        elif avg_time < 3000:
            print(f"  ❌ SLOW (Sluggish)")
        else:
            print(f"  ❌❌ VERY SLOW (Critical)")
        
        return avg_time
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_database():
    """Check database performance"""
    print_section("4️⃣  DATABASE PERFORMANCE")
    
    try:
        from app.database_unified import db, Detection
        import time
        
        print(f"\n📊 Database Configuration:")
        print(f"  Type: {config.DB_TYPE}")
        print(f"  URI: {config.DATABASE_URI.split('@')[0]}...")  # Hide password
        
        # Test connection
        print(f"\n🔗 Testing database connection...")
        start = time.perf_counter()
        
        # Quick query
        result = Detection.query.limit(1).all()
        elapsed = (time.perf_counter() - start) * 1000
        
        print(f"  ✅ Connected in {elapsed:.0f}ms")
        print(f"  Total records: {Detection.query.count()}")
        
        if elapsed > 100:
            print(f"  ⚠️  Database response slow ({elapsed:.0f}ms)")
            print(f"     Consider: indexing, query optimization, or MySQL/PostgreSQL")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

def get_recommendations(avg_inference_time):
    """Get personalized recommendations based on diagnosis"""
    print_section("5️⃣  PERSONALIZED RECOMMENDATIONS")
    
    try:
        import torch
        has_gpu = torch.cuda.is_available()
    except:
        has_gpu = False
    
    recommendations = []
    priority = 1
    
    # GPU check
    if not has_gpu:
        recommendations.append({
            'priority': priority,
            'action': '⭐ Install GPU PyTorch',
            'impact': '10-30x faster',
            'time': '5 min',
            'command': 'pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118'
        })
        priority += 1
    
    # Inference time check
    if avg_inference_time and avg_inference_time > 1000:
        recommendations.append({
            'priority': priority,
            'action': 'Install ONNX Runtime',
            'impact': '2-3x faster',
            'time': '3 min',
            'command': 'pip install onnxruntime-gpu'
        })
        priority += 1
    
    if config.CAMERA_FPS > 2:
        recommendations.append({
            'priority': priority,
            'action': 'Lower CAMERA_FPS to 2',
            'impact': '2-3x faster',
            'time': '1 min',
            'command': 'Edit config.py: CAMERA_FPS = 2'
        })
        priority += 1
    
    if config.FRAME_SKIP < 5:
        recommendations.append({
            'priority': priority,
            'action': 'Increase FRAME_SKIP to 5',
            'impact': '2-3x faster',
            'time': '1 min',
            'command': 'Edit config.py: FRAME_SKIP = 5'
        })
        priority += 1
    
    if config.USE_ENSEMBLE_FOR_CAMERA:
        recommendations.append({
            'priority': priority,
            'action': 'Disable ensemble for camera',
            'impact': '2-3x faster',
            'time': '1 min',
            'command': 'Edit config.py: USE_ENSEMBLE_FOR_CAMERA = False'
        })
        priority += 1
    
    if not recommendations:
        print("\n✅ System is already optimized!")
        return
    
    print("\n🎯 Top Actions (in priority order):\n")
    for rec in recommendations:
        print(f"{rec['priority']}. {rec['action']}")
        print(f"   Impact: {rec['impact']} | Time: {rec['time']}")
        print(f"   Run: {rec['command']}")
        print()
    
    print("\n💡 Combined Impact:")
    if len(recommendations) >= 2:
        combined_impact = 5 * len([r for r in recommendations if 'GPU' not in r['action']])
        if any('GPU' in r['action'] for r in recommendations):
            combined_impact = 30
        print(f"   If you implement top 3: ~{combined_impact}x faster ✨")

def main():
    """Run all diagnostics"""
    print("\n" + "="*60)
    print("  🔍 EPI DETECTION PERFORMANCE DIAGNOSTIC")
    print("="*60)
    
    # Run diagnostics
    check_system_specs()
    check_model_info()
    avg_time = benchmark_inference()
    check_database()
    
    # Get recommendations
    if avg_time:
        get_recommendations(avg_time)
    
    print("\n" + "="*60)
    print("  📖 For detailed optimization guide, see:")
    print("     PERFORMANCE_OPTIMIZATION_GUIDE.md")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Diagnostic interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
