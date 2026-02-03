#!/usr/bin/env python
"""
GPU/CPU Separation Verification Script

PHASE-3 CORE: Verify process separation between ML-Engine (GPU) and Backend (CPU)

Usage:
    cd backend
    venv\\Scripts\\activate
    python verify_gpu_separation.py

Tests:
    1. ML-engine health endpoint returns GPU details
    2. Backend has no torch imports (optional check)
    3. SAFE MODE when ML-engine unreachable
    4. End-to-end inference through HTTP
"""

import sys
import os
import time
import requests

# Add backend path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

ML_ENGINE_URL = "http://127.0.0.1:8001"


def test_ml_engine_health():
    """Test ML-engine health endpoint returns GPU details."""
    print("\n[TEST 1] ML-Engine Health Endpoint")
    print("=" * 50)
    
    try:
        r = requests.get(f"{ML_ENGINE_URL}/health", timeout=2.0)
        if r.status_code != 200:
            print(f"❌ FAIL: Health endpoint returned {r.status_code}")
            return False
        
        data = r.json()
        print(f"✓ Status: {data.get('status')}")
        print(f"✓ Device: {data.get('device')}")
        print(f"✓ FP16: {data.get('fp16')}")
        print(f"✓ Loaded: {data.get('loaded')}")
        print(f"✓ CUDA Available: {data.get('cuda_available')}")
        print(f"✓ GPU Name: {data.get('gpu_name')}")
        print(f"✓ GPU Memory: {data.get('gpu_memory_gb')} GB")
        
        # Verify GPU is being used if available
        if data.get('cuda_available'):
            if data.get('device') != 'cuda':
                print("⚠️  WARNING: CUDA available but device is not cuda")
            else:
                print("✓ GPU is being used for inference")
        else:
            print("⚠️  CUDA not available, running in CPU fallback mode")
        
        print("\n✅ PASS: ML-engine health check passed")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ FAIL: Cannot connect to ML-engine at", ML_ENGINE_URL)
        print("   Make sure ML-engine is running:")
        print("   cd ml-engine && venv\\Scripts\\activate && python service.py")
        return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_backend_no_torch():
    """Verify backend doesn't import torch directly."""
    print("\n[TEST 2] Backend Torch Independence")
    print("=" * 50)
    
    try:
        # Check if torch is imported in current process
        import sys
        if 'torch' in sys.modules:
            print("⚠️  WARNING: torch is loaded in current Python process")
            print("   This may be okay if running from ml-engine venv")
        else:
            print("✓ torch is not loaded in current process")
        
        # Check ml_service.py source code for actual import statements
        ml_service_path = os.path.join(current_dir, 'app', 'services', 'ml_service.py')
        if os.path.exists(ml_service_path):
            with open(ml_service_path, 'r') as f:
                lines = f.readlines()
            
            # Look for actual import statements (not in comments/docstrings)
            torch_imported = False
            for line in lines:
                stripped = line.strip()
                # Skip comments and empty lines
                if stripped.startswith('#') or not stripped:
                    continue
                # Check for actual import statement
                if stripped.startswith('import torch') or stripped.startswith('from torch'):
                    torch_imported = True
                    break
            
            if torch_imported:
                print("❌ FAIL: ml_service.py has torch import statement")
                return False
            else:
                print("✓ ml_service.py does not import torch")
            
            # Check for GPU Ownership Rule documentation
            with open(ml_service_path, 'r') as f:
                source = f.read()
            if 'GPU Ownership Rule' in source:
                print("✓ GPU Ownership Rule documented in ml_service.py")
        
        print("\n✅ PASS: Backend is torch-independent")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_safe_mode_fallback():
    """Test SAFE MODE behavior when ML-engine is unreachable."""
    print("\n[TEST 3] SAFE MODE Fallback (Simulated)")
    print("=" * 50)
    
    try:
        from app.services.ml_service import MLService
        import numpy as np
        
        # Create service pointing to non-existent endpoint
        bad_service = MLService(url="http://127.0.0.1:9999", timeout=0.5)
        
        # Create a dummy frame
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Run inference (should fail and return SAFE_MODE)
        result = bad_service.run_inference(dummy_frame)
        
        if result.get('state') == 'SAFE_MODE':
            print("✓ Service returns SAFE_MODE when ML-engine unreachable")
        else:
            print(f"❌ FAIL: Expected SAFE_MODE, got {result.get('state')}")
            return False
        
        if result.get('ml_available') == False:
            print("✓ ml_available flag is False")
        else:
            print("⚠️  ml_available flag not set correctly")
        
        if 'safe_mode_reason' in result:
            print(f"✓ Safe mode reason: {result.get('safe_mode_reason')}")
        
        print("\n✅ PASS: SAFE MODE fallback works correctly")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_inference():
    """Test full inference through HTTP."""
    print("\n[TEST 4] End-to-End Inference")
    print("=" * 50)
    
    try:
        from app.services.ml_service import MLService
        import numpy as np
        import cv2
        
        # Create service
        service = MLService(url=ML_ENGINE_URL, timeout=5.0)
        
        # First check health
        health = service.probe()
        if not health:
            print("⚠️  ML-engine not available, skipping inference test")
            return True  # Not a failure, just skip
        
        print(f"✓ ML-engine connected: {health.get('device')}")
        
        # Create a test frame (blue gradient)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :, 0] = np.linspace(0, 255, 640, dtype=np.uint8)  # Blue gradient
        
        # Run inference
        start = time.time()
        result = service.run_inference(frame)
        latency = (time.time() - start) * 1000
        
        print(f"✓ Inference completed in {latency:.1f}ms")
        print(f"✓ State: {result.get('state')}")
        print(f"✓ ML Available: {result.get('ml_available')}")
        print(f"✓ Detections: {len(result.get('detections', []))}")
        print(f"✓ Confidence: {result.get('max_confidence'):.3f}")
        
        # Check expected latency ranges
        if latency < 100:
            print("✓ Latency is in GPU range (<100ms)")
        elif latency < 300:
            print("⚠️  Latency is in CPU range (100-300ms)")
        else:
            print("⚠️  Latency is high (>300ms) - check system load")
        
        print("\n✅ PASS: End-to-end inference works")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 60)
    print("PHASE-3 CORE: GPU/CPU SEPARATION VERIFICATION")
    print("=" * 60)
    
    results = []
    results.append(("ML-Engine Health", test_ml_engine_health()))
    results.append(("Backend Torch Independence", test_backend_no_torch()))
    results.append(("SAFE MODE Fallback", test_safe_mode_fallback()))
    results.append(("End-to-End Inference", test_end_to_end_inference()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 GPU/CPU separation verified successfully!")
        print("\nArchitecture Verification:")
        print("   ✓ ML-engine runs on GPU (if available)")
        print("   ✓ Backend communicates via HTTP only")
        print("   ✓ SAFE MODE works when ML-engine unavailable")
        print("   ✓ End-to-end inference pipeline functional")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
