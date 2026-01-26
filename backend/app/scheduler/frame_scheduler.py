import time
from app.video.video_reader import VideoReader

class FrameScheduler:
    def __init__(self, video_reader: VideoReader, target_fps: int = 15, simulate_processing_delay: float = 0.0, ml_module = None, result_callback = None):
        """
        Initializes the FrameScheduler.

        Args:
            video_reader (VideoReader): Instance of VideoReader source.
            target_fps (int): Target frames per second. Default 15.
            simulate_processing_delay (float): Artificial delay in seconds if no ML module is present.
            ml_module (object): Optional ML module with run_inference method.
            result_callback (callable): Optional callback for ML results. signature: (dict) -> None.
        """
        self.video_reader = video_reader
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        self.simulate_processing_delay = simulate_processing_delay
        self.ml_module = ml_module
        self.result_callback = result_callback

    def run(self):
        """
        Runs the scheduler loop.
        Reads frames from the video reader, enforces FPS, and handles logical drops.
        """
        print(f"[Scheduler] Starting at Target FPS={self.target_fps}, Interval={self.frame_interval:.4f}s")
        if self.ml_module:
            print("[Scheduler] ML Module detected. Using synchronous inference.")
        
        # SAFE MODE State
        self.in_safe_mode = False
        self.safe_mode_reason = None
        self.last_recovery_check = 0.0
        self.recovery_interval = 5.0 # Seconds
        
        start_time = time.time()
        frames_processed_in_window = 0
        last_fps_log_time = start_time
        current_fps = 0.0 # Store for payload

        # We iterate through all frames from the reader
        # logical_frame_index tracks the index in the video source
        try:
            for frame in self.video_reader.read_video():
                current_time = time.time()
                elapsed_total = current_time - start_time
                
                if not hasattr(self, '_internal_frame_counter'):
                    self._internal_frame_counter = 0
                
                expected_time_for_frame = self._internal_frame_counter * self.frame_interval
                self._internal_frame_counter += 1

                # Reset start_time on first frame to align
                if self._internal_frame_counter == 1:
                    start_time = time.time()
                    elapsed_total = 0
                    expected_time_for_frame = 0

                # Drift check
                drift = elapsed_total - expected_time_for_frame 
                
                if drift > self.frame_interval:
                    # We are behind by more than one frame. Drop this frame.
                    print(f"[Scheduler] Frame {self._internal_frame_counter-1}: Status=DROPPED (Drift={drift:.4f}s)")
                else:
                    # Process the frame
                    print(f"[Scheduler] Frame {self._internal_frame_counter-1}: Status=PROCESSED")
                    
                    # SAFE MODE CHECK / RECOVERY
                    should_run_ml = False
                    
                    if self.in_safe_mode:
                        # Periodically check for recovery
                        if current_time - self.last_recovery_check >= self.recovery_interval:
                            print("[Scheduler] Safe Mode: Attempting recovery check...")
                            should_run_ml = True # Try one inference
                            self.last_recovery_check = current_time
                        else:
                            # Skip ML, send Safe Mode status
                            if self.result_callback:
                                self.result_callback({
                                    "type": "system",
                                    "status": "safe_mode",
                                    "message": f"System in Safe Mode: {self.safe_mode_reason}",
                                    "payload": None
                                })
                    else:
                        should_run_ml = True # Normal operation

                    # ML PROCESSING
                    if self.ml_module and should_run_ml:
                        try:
                            # Blocking call to ML with timeout measurement
                            print(f"[Scheduler] Frame {self._internal_frame_counter-1}: Sending to ML...")
                            
                            ml_start = time.time()
                            result = self.ml_module.run_inference(frame)
                            ml_end = time.time()
                            ml_duration = ml_end - ml_start
                            
                            print(f"[Scheduler] Frame {self._internal_frame_counter-1}: ML Result Received. Duration={ml_duration:.4f}s")
                            
                            # CHECK FOR SLOW INFERENCE
                            if ml_duration > 0.2:
                                raise TimeoutError(f"ML inference too slow: {ml_duration:.4f}s > 0.2s")
                            
                            # If we were in safe mode and succeeded quickly, recover
                            if self.in_safe_mode:
                                print(f"[Scheduler] Recovery Successful! (Duration: {ml_duration:.4f}s)")
                                self.in_safe_mode = False
                                self.safe_mode_reason = None
                                if self.result_callback:
                                    self.result_callback({
                                        "type": "system",
                                        "status": "recovered",
                                        "message": "System recovered",
                                        "payload": None
                                    })

                            # CALLBACK FOR WEBSOCKET (Normal Data)
                            if self.result_callback:
                                payload = result.copy()
                                payload['frame_id'] = self._internal_frame_counter - 1
                                payload['system'] = {
                                    "fps": current_fps,
                                    "latency_ms": ml_duration * 1000
                                }
                                # Normal data format
                                self.result_callback({
                                    "type": "data",
                                    "status": "success",
                                    "message": "New frame data",
                                    "payload": payload
                                })

                        except Exception as e:
                            print(f"[Scheduler] Frame {self._internal_frame_counter-1}: ML Error: {e}")
                            
                            # ENTER SAFE MODE
                            if not self.in_safe_mode:
                                self.in_safe_mode = True
                                self.safe_mode_reason = str(e)
                                self.last_recovery_check = time.time() # Start timer
                                print(f"[Scheduler] !!! ENTERING SAFE MODE !!! Reason: {e}")
                                
                                if self.result_callback:
                                    self.result_callback({
                                        "type": "system",
                                        "status": "safe_mode",
                                        "message": str(e),
                                        "payload": None
                                    })
                                    
                    elif self.simulate_processing_delay > 0:
                        # Fallback simulation if no ML module
                        time.sleep(self.simulate_processing_delay)
                    
                    frames_processed_in_window += 1
                    
                    # Check if we processed too fast, need to sleep to maintain FPS
                    post_process_time = time.time()
                    post_elapsed = post_process_time - start_time
                    next_frame_expected_time = (self._internal_frame_counter) * self.frame_interval
                    
                    sleep_duration = next_frame_expected_time - post_elapsed
                    if sleep_duration > 0:
                        time.sleep(sleep_duration)

                # FPS Calculation (every 1 second)
                now = time.time()
                if now - last_fps_log_time >= 1.0:
                    current_fps = frames_processed_in_window # Update for payload
                    print(f"[Scheduler] Actual FPS: {frames_processed_in_window}")
                    frames_processed_in_window = 0
                    last_fps_log_time = now
        
        except Exception as e:
            # Catch unexpected Video loop errors (VideoReader failure propagation)
             print(f"[Scheduler] CRITICAL LOOP ERROR: {e}")
             # We can't really "recover" the loop if it crashed, but we can try to stay alive or notify.
             # Requirements say "VideoReader fails to read frame" -> Safe Mode.
             # If read_video() raises, we are here.
             # But if read_video() yields None (handled inside checks?), usually it just stops yielding.
             # If we want to keep running, we'd need the loop inside a try/except, but the generator...
             # The generator throws? 
             pass

if __name__ == "__main__":
    # Test Block
    from app.video.video_reader import VideoReader
    import sys
    
    video_path = "dummy.mp4" # Default for quick test if exists
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        
    print(f"Testing Scheduler with {video_path}")
    reader = VideoReader(video_path)
    scheduler = FrameScheduler(reader, target_fps=15, simulate_processing_delay=0.02) # 20ms processing
    scheduler.run()
