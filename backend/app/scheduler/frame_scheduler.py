import time
import threading
import queue
from app.video.video_reader import RawVideoSource


class FrameScheduler:
    """
    PHASE-3 CORE REFACTORED SCHEDULER v2
    
    CRITICAL FIXES:
    1. PACE-DRIVEN timing (NOT timestamp-driven)
    2. ML admission control (1 in-flight request MAX)
    3. ML is BEST-EFFORT async (never blocks raw stream)
    4. Phone/live source clock is UNTRUSTED
    """
    
    def __init__(self, video_source: RawVideoSource, target_fps: int = 12, 
                 ml_module=None, result_callback=None, raw_callback=None, shutdown_event=None):
        """
        Initializes the FrameScheduler with background ML worker.
        PHASE-3: Target 12-15 FPS for stable real-time performance.
        """
        self.video_source = video_source
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        self.ml_module = ml_module
        self.result_callback = result_callback
        self.raw_callback = raw_callback
        self.shutdown_event = shutdown_event
        
        # ========== ML ADMISSION CONTROL ==========
        # Only 1 in-flight ML request allowed at any time
        self.ml_ready = threading.Event()
        self.ml_ready.set()  # Initially ready
        self.latest_frame = None  # Keep only latest frame
        self.latest_frame_lock = threading.Lock()
        
        # ML worker thread
        self.ml_worker_thread = None
        self.ml_stop = threading.Event()
        
        # SAFE MODE state
        self.in_safe_mode = False
        self.safe_mode_reason = None
        
        # Last enhanced result for reuse
        self.last_ml_result = None
        
    def _ml_worker(self):
        """
        BACKGROUND WORKER: Processes ML inference without blocking scheduler.
        
        KEY: Only 1 request in flight. Process latest frame, drop older.
        """
        print("[ML Worker] Background worker started (admission control enabled)")
        
        while not self.ml_stop.is_set():
            # Wait until a frame is available
            self.ml_ready.wait(timeout=1.0)
            if self.ml_stop.is_set():
                break
            
            # Grab latest frame (drop any older frames)
            with self.latest_frame_lock:
                if self.latest_frame is None:
                    continue
                frame, frame_id, timestamp = self.latest_frame
                self.latest_frame = None
            
            try:
                # EXECUTE ML INFERENCE
                ml_start = time.time()
                result = self.ml_module.run_inference(frame)
                ml_duration = time.time() - ml_start
                
                # Metrics: Calculate ML FPS
                ml_fps = 0.0
                if hasattr(self, '_last_ml_time'):
                    delta = time.time() - self._last_ml_time
                    if delta > 0:
                        ml_fps = 1.0 / delta
                self._last_ml_time = time.time()
                
                # Store last result for reuse
                self.last_ml_result = result.copy()
                self.last_ml_result['frame_id'] = frame_id
                self.last_ml_result['ml_latency_ms'] = ml_duration * 1000
                self.last_ml_result['ml_fps'] = ml_fps
                self.last_ml_result['completion_timestamp'] = time.time() # For cache age check
                
                # STABILIZATION: Worker does NOT emit directly.
                # It just updates self.last_ml_result (stored above).
                # The Scheduler Loop picks it up and emits at strict 12 FPS.
                pass
                
                # RECOVERY CHECK
                if self.in_safe_mode and ml_duration < 0.5:
                    self.in_safe_mode = False
                    self.safe_mode_reason = None
                    print("[ML Worker] System recovered from safe mode")
                    
            except Exception as e:
                print(f"[ML Worker] Error processing frame {frame_id}: {e}")
                
                # ENTER SAFE MODE
                if not self.in_safe_mode:
                    self.in_safe_mode = True
                    self.safe_mode_reason = str(e)
                    print(f"[Scheduler] ENTERING SAFE MODE: {e}")
                    
                    if self.result_callback:
                        self.result_callback({
                            "type": "system",
                            "status": "safe_mode",
                            "message": str(e),
                            "payload": {"ml_available": False}
                        })
            
            finally:
                # SIGNAL: Ready for next frame
                self.ml_ready.set()
        
        print("[ML Worker] Background worker stopped")

    def run(self):
        """
        MAIN SCHEDULER LOOP (PACE-DRIVEN)
        
        Contract: 
        1. ALWAYS emit raw frames immediately
        2. Sleep for frame_interval between frames (pace-driven)
        3. Submit to ML only if ready (admission control)
        4. NEVER calculate drift or compare timestamps
        """
        print(f"[Scheduler] PHASE-3 CORE v2: Target FPS={self.target_fps}, Interval={self.frame_interval:.4f}s")
        print("[Scheduler] Mode: PACE-DRIVEN (no drift accumulation)")
        
        # Start background worker if ML module present
        if self.ml_module:
            self.ml_worker_thread = threading.Thread(target=self._ml_worker, daemon=True)
            self.ml_worker_thread.start()
            print("[Scheduler] ML worker started (1 in-flight max)")
        
        frame_count = 0
        last_fps_log = time.time()
        last_frame_time = time.time()
        
        try:
            for frame, frame_id, source_timestamp in self.video_source.read():
                # Check shutdown
                if self.shutdown_event and self.shutdown_event.is_set():
                    print("[Scheduler] Shutdown signal received")
                    break
                
                current_time = time.time()
                
                # ========== STEP 1: EMIT RAW FRAME IMMEDIATELY ==========
                if self.raw_callback:
                    self.raw_callback(frame, frame_id, current_time)
                
                # ========== STEP 2: SUBMIT TO ML (ADMISSION CONTROL) ==========
                if self.ml_module:
                    # A. Submitting new frames to ML Worker
                    if self.ml_ready.is_set():
                        # ML is ready, submit this frame
                        with self.latest_frame_lock:
                            self.latest_frame = (frame, frame_id, current_time)
                        self.ml_ready.clear()  # Mark ML as busy
                    else:
                        # ML busy, update latest frame (drop older)
                        with self.latest_frame_lock:
                            self.latest_frame = (frame, frame_id, current_time)

                    # B. SCHEDULER-PACED EMISSION (Force 12 FPS output)
                    # Emit enhanced frame EVERY scheduler tick using best available data
                    # FIX: Always emit - removed MAX_CACHE_AGE gating that was dropping 90% of frames
                    # image_data is already encoded in last_ml_result (no re-encoding)
                    if self.result_callback and self.last_ml_result:
                        try:
                            # Rebuild payload with FRESH timestamps, reuse cached image
                            enhanced_payload = {
                                "frame_id": frame_id,
                                "timestamp": current_time,
                                # Reuse cached image/detections from last ML result
                                "detections": self.last_ml_result.get("detections", []),
                                "max_confidence": self.last_ml_result.get("max_confidence", 0.0),
                                "state": self.last_ml_result.get("state", "NORMAL"),
                                # image_data is already base64 encoded - no re-encoding needed
                                "image_data": self.last_ml_result.get("image_data"),
                                # Re-attach system metrics
                                "system": {
                                    "fps": self.target_fps,
                                    "latency_ms": self.last_ml_result.get("ml_latency_ms", 0.0),
                                    "ml_fps": self.last_ml_result.get("ml_fps", 0.0),
                                    "ml_available": True
                                },
                                "is_cached": not self.ml_ready.is_set()
                            }

                            self.result_callback({
                                "type": "data",
                                "status": "success",
                                "message": "Enhanced frame (paced)",
                                "payload": enhanced_payload
                            })
                        except Exception as e:
                            print(f"[Scheduler] Error sending paced frame: {e}")
                
                # ========== STEP 3: PACE-DRIVEN SLEEP ==========
                frame_count += 1
                
                # Calculate sleep based on LAST frame time, not absolute
                elapsed_since_last = current_time - last_frame_time
                sleep_duration = self.frame_interval - elapsed_since_last
                
                if sleep_duration > 0:
                    time.sleep(sleep_duration)
                
                last_frame_time = time.time()
                
                # ========== STEP 4: LOG FPS (every second) ==========
                now = time.time()
                if now - last_fps_log >= 1.0:
                    print(f"[Scheduler] FPS={frame_count}, Mode={'GPU' if self.ml_module else 'SAFE'}")
                    frame_count = 0
                    last_fps_log = now
        
        except Exception as e:
            print(f"[Scheduler] CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        # Cleanup
        self.ml_stop.set()
        if self.shutdown_event:
            self.shutdown_event.set()
        
        if self.ml_worker_thread:
            self.ml_worker_thread.join(timeout=2.0)
            print("[Scheduler] Graceful shutdown complete")


if __name__ == "__main__":
    from app.video.video_reader import RawVideoSource
    
    print("Testing PHASE-3 CORE Scheduler v2...")
    source = RawVideoSource()
    scheduler = FrameScheduler(source, target_fps=12) 
    scheduler.run()
