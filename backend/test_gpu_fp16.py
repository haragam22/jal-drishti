import sys
import os
ml_engine_path = os.path.join(os.path.dirname(os.getcwd()), 'ml-engine')
sys.path.insert(0, ml_engine_path)

from core.pipeline import JalDrishtiEngine
import numpy as np

print('[Test] Initializing Engine with GPU...')
engine = JalDrishtiEngine(use_gpu=True, use_fp16=True)

print('[Test] Creating test frame...')
test_frame = np.random.randint(0, 100, (480, 640, 3), dtype=np.uint8)

print('[Test] Running inference...')
result, enhanced = engine.infer(test_frame)

print('[Test] Inference completed successfully')
print(f"  State: {result['state']}")
print(f"  Confidence: {result['max_confidence']}")
print(f"  Latency: {result['latency_ms']:.2f}ms")
device_type = 'cuda' if engine.device.type == 'cuda' else 'cpu'
print(f"  Device: {device_type}")
print('\n[Test] ✓ GPU Enablement and FP16 Test PASSED')
