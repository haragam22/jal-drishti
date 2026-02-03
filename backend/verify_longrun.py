#!/usr/bin/env python3
"""
PHASE-3 CORE: Long-Run Stability Test
Tests system stability over 15+ minutes of continuous operation.

Tests:
- FPS stability
- Memory usage (no leaks)
- GPU memory stability
- Latency consistency
- No crashes or errors
"""

import sys
import os
import time
import psutil
import torch
import numpy as np
import cv2
from datetime import datetime
from pathlib import Path

# Add ml-engine to path
ml_engine_path = os.path.join(os.path.dirname(__file__), "..", "ml-engine")
if ml_engine_path not in sys.path:
    sys.path.append(ml_engine_path)

from core.pipeline import JalDrishtiEngine
from core.config import STATE_SAFE_MODE, STATE_POTENTIAL_ANOMALY, STATE_CONFIRMED_THREAT

class LongRunTest:
    def __init__(self, duration_minutes=15, use_gpu=True, use_fp16=True):
        """
        Initialize long-run stability test.
        
        Args:
            duration_minutes: How long to run the test (default 15 minutes)
            use_gpu: Enable GPU
            use_fp16: Enable FP16
        """
        self.duration_minutes = duration_minutes
        self.duration_seconds = duration_minutes * 60
        self.use_gpu = use_gpu
        self.use_fp16 = use_fp16
        
        print(f"\n{'='*70}")
        print(f"PHASE-3 CORE: LONG-RUN STABILITY TEST")
        print(f"{'='*70}")
        print(f"Duration: {duration_minutes} minutes")
        print(f"GPU Enabled: {use_gpu}")
        print(f"FP16 Enabled: {use_fp16}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Initialize engine
        try:
            self.engine = JalDrishtiEngine(use_gpu=use_gpu, use_fp16=use_fp16)
            print("[Test] Engine initialized successfully\n")
        except Exception as e:
            print(f"[Test] FATAL: Could not initialize engine: {e}")
            sys.exit(1)
        
        # Create synthetic test frame (underwater-like)
        self.test_frame = self._create_test_frame()
        
        # Metrics tracking
        self.metrics = {
            "frame_count": 0,
            "error_count": 0,
            "total_latency_ms": 0.0,
            "max_latency_ms": 0.0,
            "min_latency_ms": float('inf'),
            "fps_history": [],
            "memory_history": [],
            "gpu_memory_history": [],
            "start_time": time.time(),
        }
    
    def _create_test_frame(self, h=480, w=640):
        """Create a synthetic underwater test frame"""
        # Create noisy blue-ish underwater-like frame
        frame = np.random.randint(0, 80, (h, w, 3), dtype=np.uint8)
        # Add some gradient pattern
        for i in range(h):
            frame[i, :] = frame[i, :] + np.linspace(0, 100, w, dtype=np.uint8)[:, np.newaxis]
        # Add some "objects" (bright spots)
        for _ in range(10):
            y, x = np.random.randint(100, h-100), np.random.randint(100, w-100)
            frame[y-20:y+20, x-20:x+20] = np.clip(frame[y-20:y+20, x-20:x+20].astype(int) + 100, 0, 255).astype(np.uint8)
        return frame
    
    def run(self):
        """Run the long-run stability test"""
        start_time = time.time()
        last_fps_check = start_time
        frames_since_last_check = 0
        
        try:
            while time.time() - start_time < self.duration_seconds:
                elapsed = time.time() - start_time
                elapsed_min = elapsed / 60.0
                
                # Run inference
                try:
                    result, enhanced = self.engine.infer(self.test_frame)
                    self.metrics["frame_count"] += 1
                    frames_since_last_check += 1
                    
                    # Track latency
                    latency = result.get("latency_ms", 0)
                    self.metrics["total_latency_ms"] += latency
                    self.metrics["max_latency_ms"] = max(self.metrics["max_latency_ms"], latency)
                    self.metrics["min_latency_ms"] = min(self.metrics["min_latency_ms"], latency)
                    
                except Exception as e:
                    self.metrics["error_count"] += 1
                    print(f"[Test] Inference error at frame {self.metrics['frame_count']}: {e}")
                
                # Calculate and report FPS every 10 seconds
                if time.time() - last_fps_check >= 10.0:
                    elapsed_10s = time.time() - last_fps_check
                    fps = frames_since_last_check / elapsed_10s
                    self.metrics["fps_history"].append(fps)
                    
                    # Get memory info
                    process = psutil.Process(os.getpid())
                    mem_mb = process.memory_info().rss / 1024 / 1024
                    self.metrics["memory_history"].append(mem_mb)
                    
                    # Get GPU memory if available
                    gpu_mem_mb = 0
                    if torch.cuda.is_available():
                        gpu_mem_mb = torch.cuda.memory_allocated() / 1024 / 1024
                        self.metrics["gpu_memory_history"].append(gpu_mem_mb)
                    
                    # Print status
                    print(f"[{elapsed_min:6.2f}m] Frame #{self.metrics['frame_count']:6d} | "
                          f"FPS: {fps:6.2f} | "
                          f"Mem: {mem_mb:7.1f}MB | "
                          f"GPU: {gpu_mem_mb:7.1f}MB | "
                          f"Errors: {self.metrics['error_count']}")
                    
                    last_fps_check = time.time()
                    frames_since_last_check = 0
            
            # Test completed
            self.print_summary()
            return True
            
        except KeyboardInterrupt:
            print("\n[Test] Interrupted by user")
            self.print_summary()
            return False
        except Exception as e:
            print(f"\n[Test] FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        elapsed = time.time() - self.metrics["start_time"]
        elapsed_min = elapsed / 60.0
        
        print(f"\n{'='*70}")
        print(f"LONG-RUN STABILITY TEST SUMMARY")
        print(f"{'='*70}")
        
        print(f"\n[Duration]")
        print(f"  Actual Runtime: {elapsed_min:.2f} minutes")
        print(f"  Total Frames: {self.metrics['frame_count']}")
        
        print(f"\n[Performance]")
        if self.metrics["fps_history"]:
            avg_fps = sum(self.metrics["fps_history"]) / len(self.metrics["fps_history"])
            min_fps = min(self.metrics["fps_history"])
            max_fps = max(self.metrics["fps_history"])
            fps_std = np.std(self.metrics["fps_history"])
            print(f"  Avg FPS: {avg_fps:.2f}")
            print(f"  Min FPS: {min_fps:.2f}")
            print(f"  Max FPS: {max_fps:.2f}")
            print(f"  Stability (StdDev): {fps_std:.2f}")
        
        print(f"\n[Latency]")
        if self.metrics["frame_count"] > 0:
            avg_latency = self.metrics["total_latency_ms"] / self.metrics["frame_count"]
            print(f"  Avg Latency: {avg_latency:.2f}ms")
            print(f"  Max Latency: {self.metrics['max_latency_ms']:.2f}ms")
            print(f"  Min Latency: {self.metrics['min_latency_ms']:.2f}ms")
        
        print(f"\n[Memory]")
        if self.metrics["memory_history"]:
            mem_start = self.metrics["memory_history"][0]
            mem_end = self.metrics["memory_history"][-1]
            mem_peak = max(self.metrics["memory_history"])
            print(f"  Start Memory: {mem_start:.1f}MB")
            print(f"  End Memory: {mem_end:.1f}MB")
            print(f"  Peak Memory: {mem_peak:.1f}MB")
            print(f"  Memory Growth: {mem_end - mem_start:+.1f}MB")
        
        print(f"\n[GPU Memory]")
        if self.metrics["gpu_memory_history"]:
            gpu_start = self.metrics["gpu_memory_history"][0]
            gpu_end = self.metrics["gpu_memory_history"][-1]
            gpu_peak = max(self.metrics["gpu_memory_history"])
            print(f"  Start GPU Memory: {gpu_start:.1f}MB")
            print(f"  End GPU Memory: {gpu_end:.1f}MB")
            print(f"  Peak GPU Memory: {gpu_peak:.1f}MB")
            print(f"  GPU Memory Growth: {gpu_end - gpu_start:+.1f}MB")
        else:
            print(f"  GPU not available or not in use")
        
        print(f"\n[Errors]")
        print(f"  Total Errors: {self.metrics['error_count']}")
        if self.metrics["error_count"] == 0:
            print(f"  Status: ✓ NO ERRORS")
        else:
            print(f"  Status: ✗ {self.metrics['error_count']} errors occurred")
        
        print(f"\n[Success Criteria]")
        criteria_pass = True
        
        # Check FPS stability
        if self.metrics["fps_history"]:
            fps_std = np.std(self.metrics["fps_history"])
            fps_stable = fps_std < 3.0  # Allow ±3 FPS oscillation
            print(f"  {'✓' if fps_stable else '✗'} FPS Stable (StdDev < 3.0): {fps_std:.2f}")
            criteria_pass = criteria_pass and fps_stable
        
        # Check no errors
        no_errors = self.metrics["error_count"] == 0
        print(f"  {'✓' if no_errors else '✗'} No Errors")
        criteria_pass = criteria_pass and no_errors
        
        # Check memory stability
        if len(self.metrics["memory_history"]) > 2:
            mem_growth = self.metrics["memory_history"][-1] - self.metrics["memory_history"][0]
            mem_stable = mem_growth < 100  # Allow max 100MB growth
            print(f"  {'✓' if mem_stable else '✗'} Memory Stable (Growth < 100MB): {mem_growth:+.1f}MB")
            criteria_pass = criteria_pass and mem_stable
        
        # Check GPU memory stability
        if len(self.metrics["gpu_memory_history"]) > 2:
            gpu_growth = self.metrics["gpu_memory_history"][-1] - self.metrics["gpu_memory_history"][0]
            gpu_stable = gpu_growth < 50  # Allow max 50MB growth
            print(f"  {'✓' if gpu_stable else '✗'} GPU Memory Stable (Growth < 50MB): {gpu_growth:+.1f}MB")
            criteria_pass = criteria_pass and gpu_stable
        
        print(f"\n[Overall Result]")
        if criteria_pass:
            print(f"  ✓ TEST PASSED - System is stable for long-run operation")
        else:
            print(f"  ✗ TEST FAILED - System has stability issues")
        
        print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase-3 CORE Long-Run Stability Test")
    parser.add_argument("--duration", type=int, default=15, help="Test duration in minutes (default 15)")
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU")
    parser.add_argument("--no-fp16", action="store_true", help="Disable FP16")
    
    args = parser.parse_args()
    
    test = LongRunTest(
        duration_minutes=args.duration,
        use_gpu=not args.no_gpu,
        use_fp16=not args.no_fp16
    )
    
    success = test.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
