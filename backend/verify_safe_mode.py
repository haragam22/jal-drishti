import time
import threading
import sys
import os

print("--- DEBUG: Script Started ---", flush=True)

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.scheduler.frame_scheduler import FrameScheduler
from app.video.video_reader import VideoReader
from app.ml.dummy_ml import DummyML

# Mock VideoReader since we might not have a video file
class MockVideoReader:
    def read_video(self):
        import numpy as np
        # Yield fake frames indefinitely
        h, w = 360, 640
        while True:
            yield np.zeros((h, w, 3), dtype='uint8')
            time.sleep(0.03) # 30fps source speed

def result_callback(payload):
    msg_type = payload.get('type')
    status = payload.get('status')
    msg = payload.get('message')
    print(f"\n[CALLBACK] Type: {msg_type}, Status: {status}, Message: {msg}")

def main():
    print("--- STARTING SAFE MODE VERIFICATION ---")
    
    # 1. Setup
    video_reader = MockVideoReader()
    ml_module = DummyML()
    scheduler = FrameScheduler(video_reader, target_fps=5, ml_module=ml_module, result_callback=result_callback)
    
    # 2. Run Scheduler in separate thread
    sched_thread = threading.Thread(target=scheduler.run, daemon=True)
    sched_thread.start()
    
    print(">>> Phase 1: Normal Operation (5s)")
    time.sleep(5)
    
    print("\n>>> Phase 2: Trigger Failure (Timeout)")
    ml_module.set_failure_mode(True, 'timeout')
    
    # Wait for Safe Mode activation
    time.sleep(5)
    
    if scheduler.in_safe_mode:
        print("\n*** VERIFICATION PASS: Scheduler entered SAFE MODE ***")
    else:
        print("\n*** VERIFICATION FAIL: Scheduler did NOT enter SAFE MODE ***")

    print("\n>>> Phase 3: Trigger Recovery")
    ml_module.set_failure_mode(False)
    
    # Wait for recovery check (interval is 5s)
    print("Waiting for recovery check (approx 6s)...")
    time.sleep(6)
    
    if not scheduler.in_safe_mode:
        print("\n*** VERIFICATION PASS: Scheduler RECOVERED from SAFE MODE ***")
    else:
        print("\n*** VERIFICATION FAIL: Scheduler did NOT recover ***")
        
    print("--- TEST COMPLETE ---")

if __name__ == "__main__":
    main()
