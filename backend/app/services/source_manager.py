"""
SourceManager: Runtime Source Switching Service

PHASE-3 CORE: Singleton service managing video source lifecycle.

States: IDLE -> VIDEO_ACTIVE | CAMERA_WAITING -> CAMERA_ACTIVE | ERROR

Key behaviors:
- Scheduler created once, sources hot-swapped
- Single active source only
- Non-blocking API (never waits on ML)
- Camera timeout: 15s waiting -> stays IDLE
- Phone disconnect -> IDLE (no auto-fallback)
"""

import threading
import time
import socket
import logging
from enum import Enum
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


class SourceState(Enum):
    IDLE = "IDLE"
    VIDEO_ACTIVE = "VIDEO_ACTIVE"
    CAMERA_WAITING = "CAMERA_WAITING"
    CAMERA_ACTIVE = "CAMERA_ACTIVE"
    ERROR = "ERROR"


class SourceManager:
    """
    Singleton service for runtime source switching.
    
    The scheduler is created once and reused. On switch:
    1. Stop old source
    2. Reset frame timestamp
    3. Attach new source to existing scheduler
    
    CRITICAL FIX: Scheduler and ML worker are NEVER destroyed on switch!
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._state = SourceState.IDLE
        self._current_source_type: Optional[str] = None
        self._current_source = None
        self._scheduler = None
        self._scheduler_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._state_lock = threading.Lock()
        
        # Frame-driven timeout tracking (CRITICAL FIX)
        self._camera_timeout_seconds = 15.0
        self._camera_timeout_thread: Optional[threading.Thread] = None
        self._timeout_active = False
        
        # Last frame timestamp - FRAME-DRIVEN, not wall-clock
        self._last_frame_ts: Optional[float] = None
        
        # Callbacks
        self._on_result_callback: Optional[Callable] = None
        self._on_raw_callback: Optional[Callable] = None
        self._ml_service = None
        self._event_loop = None
        
        # Config
        self._video_path = "backend/dummy.mp4"
        self._target_fps = 12
        
        logger.info("[SourceManager] Initialized in IDLE state")
    
    @property
    def state(self) -> SourceState:
        with self._state_lock:
            return self._state
    
    @property
    def source_type(self) -> Optional[str]:
        return self._current_source_type
    
    @property
    def last_frame_ts(self) -> Optional[float]:
        return self._last_frame_ts
    
    def configure(self, 
                  ml_service,
                  on_result_callback: Callable,
                  on_raw_callback: Callable,
                  event_loop,
                  video_path: str = "backend/dummy.mp4",
                  target_fps: int = 12):
        """Configure manager with callbacks and ML service."""
        self._ml_service = ml_service
        self._on_result_callback = on_result_callback
        self._on_raw_callback = on_raw_callback
        self._event_loop = event_loop
        self._video_path = video_path
        self._target_fps = target_fps
        logger.info("[SourceManager] Configured with ML service and callbacks")
    
    def switch_source(self, source_type: str, video_path: str = None) -> dict:
        """
        Switch to a new source. Non-blocking, returns immediately.
        
        Args:
            source_type: "video" or "camera"
            video_path: Optional path to video file (overrides default)
            
        Returns:
            dict with status and message
        """
        logger.info(f"[SourceManager] Switch requested: {source_type} (path={video_path})")
        
        if source_type not in ("video", "camera"):
            return {"success": False, "error": "Invalid source type. Use 'video' or 'camera'"}
        
        # Detach current source first
        self._detach_current_source()
        
        # Reset counters
        self._last_frame_ts = None
        
        try:
            if source_type == "video":
                return self._attach_video_source(custom_path=video_path)
            else:
                return self._attach_camera_source()
        except Exception as e:
            logger.error(f"[SourceManager] Error switching source: {e}")
            with self._state_lock:
                self._state = SourceState.ERROR
            return {"success": False, "error": str(e), "state": "ERROR"}
    
    def _detach_current_source(self):
        """Gracefully stop current source without destroying scheduler."""
        logger.info("[SourceManager] Detaching current source...")
        
        # Stop timeout monitoring
        self._timeout_active = False
        
        # Stop source (NOT scheduler!)
        if self._current_source:
            try:
                if hasattr(self._current_source, 'stop'):
                    self._current_source.stop()
            except Exception as e:
                logger.warning(f"[SourceManager] Error stopping source: {e}")
        
        self._current_source = None
        self._current_source_type = None
        self._last_frame_ts = None
        
        with self._state_lock:
            self._state = SourceState.IDLE
        
        logger.info("[SourceManager] Source detached, now IDLE (scheduler kept alive)")
    
    def _attach_video_source(self, custom_path: str = None) -> dict:
        """Attach video file source."""
        from app.video.video_reader import RawVideoSource
        import os
        
        # Use custom path if provided, otherwise use default
        video_path = custom_path if custom_path else self._video_path
        
        if not os.path.exists(video_path):
            # Check relative paths for default
            for alt_path in ["dummy.mp4", "backend/dummy.mp4"]:
                if os.path.exists(alt_path):
                    video_path = alt_path
                    break
            else:
                with self._state_lock:
                    self._state = SourceState.ERROR
                return {"success": False, "error": f"Video file not found: {video_path}", "state": "ERROR"}
        
        try:
            reader = RawVideoSource(video_path)
            self._current_source = reader
            self._current_source_type = "video"
            
            # Start scheduler with new source
            self._start_scheduler(reader)
            
            with self._state_lock:
                self._state = SourceState.VIDEO_ACTIVE
            
            logger.info(f"[SourceManager] Video source active: {video_path}")
            return {"success": True, "state": "VIDEO_ACTIVE", "source": "video"}
            
        except Exception as e:
            with self._state_lock:
                self._state = SourceState.ERROR
            return {"success": False, "error": str(e), "state": "ERROR"}
    
    def _attach_camera_source(self) -> dict:
        """Attach phone camera source (waiting for connection)."""
        from app.video.phone_source import phone_camera_source
        
        self._current_source = phone_camera_source
        self._current_source_type = "camera"
        
        # Reset frame timestamp for timeout tracking
        self._last_frame_ts = time.time()  # Start fresh
        
        with self._state_lock:
            self._state = SourceState.CAMERA_WAITING
        
        # Start scheduler with phone source
        self._start_scheduler(phone_camera_source)
        
        # Start FRAME-DRIVEN timeout monitor
        self._timeout_active = True
        self._camera_timeout_thread = threading.Thread(
            target=self._monitor_camera_timeout_frame_driven,
            daemon=True
        )
        self._camera_timeout_thread.start()
        
        logger.info("[SourceManager] Camera source waiting for phone connection...")
        return {"success": True, "state": "CAMERA_WAITING", "source": "camera"}
    
    def _monitor_camera_timeout_frame_driven(self):
        """
        CRITICAL FIX: Frame-driven timeout monitoring.
        
        Timeout triggers only if no frames received for 15s.
        NOT based on wall-clock from start.
        """
        logger.info("[SourceManager] Starting frame-driven timeout monitor (15s)")
        
        while self._timeout_active:
            time.sleep(2.0)  # Check every 2 seconds
            
            with self._state_lock:
                current_state = self._state
            
            # Don't timeout if already active or not in camera mode
            if current_state == SourceState.CAMERA_ACTIVE:
                continue  # Camera working, keep monitoring for stalls
            if current_state not in (SourceState.CAMERA_WAITING, SourceState.CAMERA_ACTIVE):
                return  # State changed externally
            
            # Check frame-driven timeout
            if self._last_frame_ts is not None:
                time_since_frame = time.time() - self._last_frame_ts
                if time_since_frame > self._camera_timeout_seconds:
                    logger.warning(f"[SourceManager] Camera stalled ({time_since_frame:.1f}s since last frame). Going to IDLE.")
                    self._timeout_active = False
                    self._detach_current_source()
                    return
        
        logger.info("[SourceManager] Timeout monitor stopped")
    
    def on_frame_received(self):
        """
        CRITICAL: Called by PhoneCameraSource when a frame arrives.
        This updates last_frame_ts for frame-driven timeout.
        """
        self._last_frame_ts = time.time()
        
        # Transition from WAITING to ACTIVE on first frame
        with self._state_lock:
            if self._state == SourceState.CAMERA_WAITING:
                self._state = SourceState.CAMERA_ACTIVE
                logger.info("[SourceManager] First frame received! State: CAMERA_ACTIVE")
    
    def notify_camera_disconnected(self):
        """Called when phone camera disconnects."""
        logger.info("[SourceManager] Camera disconnected. Going to IDLE.")
        self._timeout_active = False
        self._detach_current_source()
    
    def update_frame_timestamp(self, ts: float):
        """Update last frame timestamp."""
        self._last_frame_ts = ts
    
    def _start_scheduler(self, source):
        """Start or rebind scheduler with new source."""
        from app.scheduler.frame_scheduler import FrameScheduler
        
        # Stop existing scheduler thread if running
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._shutdown_event.set()
            self._scheduler_thread.join(timeout=2.0)
            self._shutdown_event.clear()
        
        # Create new scheduler with source
        self._scheduler = FrameScheduler(
            video_source=source,
            target_fps=self._target_fps,
            ml_module=self._ml_service,
            result_callback=self._on_result_callback,
            raw_callback=self._on_raw_callback,
            shutdown_event=self._shutdown_event
        )
        
        # Start in background thread
        self._scheduler_thread = threading.Thread(
            target=self._scheduler.run,
            daemon=True
        )
        self._scheduler_thread.start()
        logger.info("[SourceManager] Scheduler started with new source")
    
    def get_status(self) -> dict:
        """Get current source status."""
        return {
            "state": self.state.value,
            "source": self._current_source_type,
            "last_frame_ts": self._last_frame_ts
        }
    
    def shutdown(self):
        """Graceful shutdown."""
        logger.info("[SourceManager] Shutting down...")
        self._detach_current_source()
        self._shutdown_event.set()
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=5.0)


def get_lan_ip() -> str:
    """
    Get the LAN IP address of this machine.
    Derived from active network interface (not hardcoded).
    """
    try:
        # Create a socket to determine the outbound IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        # Connect to a public DNS server (doesn't actually send data)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback to localhost
        return "127.0.0.1"


# Global singleton instance
source_manager = SourceManager()
