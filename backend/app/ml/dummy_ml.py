import time
import random
import numpy as np

class DummyML:
    def __init__(self):
        """
        Initializes the Dummy ML module.
        """
        pass

    def set_failure_mode(self, enabled: bool, mode: str = "timeout"):
        """
        Enables or disables failure simulation.
        
        Args:
            enabled (bool): True to active failure.
            mode (str): 'timeout' (sleep > 0.2s) or 'error' (raise Exception).
        """
        self.failure_enabled = enabled
        self.failure_mode = mode

    def run_inference(self, frame: np.ndarray) -> dict:
        """
        Simulates running ML inference on a single frame.
        
        Args:
            frame (np.ndarray): The input RGB frame.
            
        Returns:
            dict: Structured inference result.
        """
        start_time = time.time()
        
        # CHECK FAILURES
        if hasattr(self, 'failure_enabled') and self.failure_enabled:
            if self.failure_mode == 'timeout':
                # Sleep > 0.2s to trigger Safe Mode
                print("[ML] SIMULATING TIMEOUT...")
                time.sleep(0.3)
            elif self.failure_mode == 'error':
                print("[ML] SIMULATING EXCEPTION...")
                raise RuntimeError("Simulated ML Crash")

        # Simulate inference delay (50ms - 100ms)
        delay = random.uniform(0.05, 0.1)
        time.sleep(delay)
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Log inference details (Requirements: Frame ID is not passed here, but Scheduler logs it. 
        # ML logs internal start/end/latency)
        print(f"[ML] Inference Start: {start_time:.4f}")
        print(f"[ML] Inference End: {end_time:.4f} (Latency: {latency:.4f}s)")
        
        return {
            "status": "success",
            "detections": [],
            "visibility_score": 0.95
        }
