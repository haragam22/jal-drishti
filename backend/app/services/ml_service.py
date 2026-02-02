import base64
import numpy as np
import cv2
import logging
import requests
import io
import time

logger = logging.getLogger(__name__)


class MLService:
    """HTTP client wrapper around the ml-engine service.

    The backend remains lightweight: all ML model loading and CUDA
    usage occur inside the separate `ml-engine` process.
    
    PHASE-3 CORE: GPU Ownership Rule
    - Backend does NOT import torch or use CUDA
    - All GPU operations happen in ML-engine process
    - Backend communicates via HTTP only
    """

    def __init__(self, url: str = "http://127.0.0.1:8001", timeout: float = 10.0, debug_mode: bool = False):
        self.url = url.rstrip('/')
        # PHASE-3 CORE: Aggressive timeout handling
        # - First inference needs 2-5s for GPU model warmup (cold start)
        # - Normal GPU inference is ~20-80ms
        # - Use high initial timeout, then AGGRESSIVE 500ms timeout
        # - If timeout → SAFE MODE immediately (no cascading stalls)
        self.timeout = timeout  # Initial high timeout for cold start
        self.timeout_normal = 0.5  # AGGRESSIVE: 500ms timeout after warmup
        self.warmed_up = False
        self.debug_mode = debug_mode
        self.frame_count = 0
        self.device_cached = None
        
        # SAFE MODE State Management
        self.ml_available = False
        self.last_health_check = 0.0
        self.health_check_interval = 5.0  # Retry every 5 seconds when unavailable
        self.consecutive_failures = 0
        self.max_failures_before_safe_mode = 2  # Reduced: faster SAFE MODE entry

    def _health(self):
        try:
            r = requests.get(f"{self.url}/health", timeout=self.timeout)
            if r.status_code == 200:
                data = r.json()
                self.device_cached = data.get('device', 'cpu')
                self.ml_available = True
                self.consecutive_failures = 0
                return data
        except Exception:
            logger.debug("MLService: health check failed")
        return None

    def probe(self):
        """Probe ML-engine health and cache device information."""
        data = self._health()
        if data:
            logger.info(f"[MLService] ML-engine connected: device={data.get('device')}, gpu={data.get('gpu_name')}")
        return data

    def _safe_mode_response(self, reason: str = "ML-engine unavailable"):
        """Return SAFE MODE response when ML-engine is unavailable."""
        return {
            'detections': [],
            'max_confidence': 0.0,
            'state': 'SAFE_MODE',
            'latency_ms': 0.0,
            'ml_available': False,
            'safe_mode_reason': reason,
        }

    def run_inference(self, frame: np.ndarray, send_enhanced: bool = False) -> dict:
        """POST frame to ml-engine /infer and return parsed result.

        Synchronous call intended to be executed from scheduler's ML worker.
        
        SAFE MODE Logic:
        - If ML-engine was unavailable, check health before inference
        - Retry health check at intervals to detect recovery
        - Return SAFE_MODE response if ML-engine still unreachable
        """
        # Periodic health check when ML was previously unavailable
        if not self.ml_available:
            now = time.time()
            if now - self.last_health_check > self.health_check_interval:
                self.last_health_check = now
                if self._health():
                    logger.info("[MLService] ML-engine recovered and available")
                else:
                    logger.debug("[MLService] ML-engine still unavailable, staying in SAFE MODE")
                    return self._safe_mode_response("ML-engine unreachable")

        self.frame_count += 1
        try:
            # Encode to JPEG bytes
            _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            buf_bytes = buf.tobytes()

            files = {
                'frame': ('frame.jpg', buf_bytes, 'image/jpeg')
            }
            data = {
                'frame_id': str(self.frame_count),
                'timestamp': str(time.time()),
                'send_enhanced': '1' if send_enhanced or self.debug_mode else '0'
            }

            r = requests.post(f"{self.url}/infer", files=files, data=data, timeout=self.timeout)
            if r.status_code != 200:
                raise RuntimeError(f"ML engine returned {r.status_code}")

            resp = r.json()
            
            # Mark ML as available on successful response
            self.ml_available = True
            self.consecutive_failures = 0
            
            # WARMUP: After first successful inference, reduce timeout
            if not self.warmed_up:
                self.warmed_up = True
                self.timeout = self.timeout_normal
                logger.info(f"[MLService] GPU warmup complete, reducing timeout to {self.timeout}s")
            
            # Cache device
            dev = resp.get('device_used') or resp.get('device')
            if dev:
                self.device_cached = dev

            # Normalize response to previous MLService contract
            if resp.get('status') != 'success':
                return {
                    'detections': [],
                    'max_confidence': 0.0,
                    'state': 'SAFE_MODE',
                    'latency_ms': resp.get('inference_latency_ms', 0.0),
                    'ml_available': True,
                }

            out = {
                'detections': resp.get('detections', []),
                'max_confidence': resp.get('confidence', 0.0),
                'state': resp.get('threat_state', 'NORMAL'),
                'latency_ms': resp.get('inference_latency_ms', 0.0),
                'ml_available': True,
            }

            # Optionally include enhanced image under same key used earlier
            if 'enhanced_image' in resp:
                out['image_data'] = resp['enhanced_image']

            return out

        except requests.exceptions.Timeout:
            self.consecutive_failures += 1
            logger.warning(f"[MLService] Inference timeout (attempt {self.consecutive_failures})")
            if self.consecutive_failures >= self.max_failures_before_safe_mode:
                self.ml_available = False
                self.last_health_check = time.time()
            return self._safe_mode_response("Inference timeout")
            
        except requests.exceptions.ConnectionError:
            self.ml_available = False
            self.last_health_check = time.time()
            logger.warning("[MLService] ML-engine connection failed, entering SAFE MODE")
            return self._safe_mode_response("Connection failed")
            
        except Exception as e:
            self.consecutive_failures += 1
            logger.exception("MLService: inference error: %s", e)
            if self.consecutive_failures >= self.max_failures_before_safe_mode:
                self.ml_available = False
                self.last_health_check = time.time()
            return self._safe_mode_response(str(e))

    def process_frame(self, binary_frame: bytes, send_enhanced: bool = False) -> dict:
        """Compatibility wrapper: accept raw bytes (e.g., from HTTP endpoints)."""
        try:
            nparr = np.frombuffer(binary_frame, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                return {"status": "error", "message": "Image decode failed"}
            resp = self.run_inference(frame, send_enhanced=send_enhanced)
            return {"status": "success", "frame_id": self.frame_count, **resp}
        except Exception as e:
            logger.exception("process_frame error: %s", e)
            return {"status": "error", "message": str(e)}

