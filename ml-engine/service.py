import time
import base64
import io
import logging
from typing import Optional

import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form

app = FastAPI(title="JalDrishti ML Engine")
logger = logging.getLogger("ml-engine")


class EngineWrapper:
    def __init__(self):
        self.engine = None
        self.device = "cpu"
        self.fp16 = False

    def initialize(self):
        try:
            from core.pipeline import JalDrishtiEngine
            self.engine = JalDrishtiEngine()
            # Try to read device info from engine if available
            dev = getattr(self.engine, 'device', None)
            if dev is not None:
                self.device = str(dev)
            # FP16 detection best-effort
            self.fp16 = getattr(self.engine, 'use_fp16', False) or ('cuda' in self.device and hasattr(self.engine, 'use_fp16'))
            logger.info(f"[ML Engine] Initialized on device={self.device}, fp16={self.fp16}")
        except Exception as e:
            logger.exception("[ML Engine] Failed to initialize engine: %s", e)
            self.engine = None

    def infer(self, frame: np.ndarray, send_enhanced: bool = False):
        if self.engine is None:
            raise RuntimeError("Engine not initialized")
        # engine.infer returns (result_json, enhanced_frame)
        return self.engine.infer(frame)


engine_wrapper = EngineWrapper()


@app.on_event("startup")
def startup_event():
    """
    ML-Engine Startup Sequence:
    1. Detect CUDA availability
    2. Log device details (GPU name, memory)
    3. Initialize engine with models
    """
    import torch
    
    logger.info("[ML Engine] Starting up...")
    
    # GPU Detection and Logging
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        logger.info(f"[ML Engine] GPU Detected: {gpu_name}")
        logger.info(f"[ML Engine] GPU Memory: {gpu_memory_gb:.2f} GB")
        logger.info("[ML Engine] CUDA acceleration enabled")
    else:
        logger.warning("[ML Engine] CUDA not available, using CPU fallback")
        logger.warning("[ML Engine] Performance will be significantly reduced")
    
    # Initialize Engine (loads FUnIE-GAN + YOLO)
    logger.info("[ML Engine] Loading models...")
    engine_wrapper.initialize()


@app.get("/health")
def health():
    """
    Health check endpoint with GPU status.
    Used by backend to verify ML-engine availability.
    """
    import torch
    
    cuda_available = torch.cuda.is_available()
    
    return {
        "status": "ok",
        "device": engine_wrapper.device,
        "fp16": engine_wrapper.fp16,
        "loaded": engine_wrapper.engine is not None,
        "cuda_available": cuda_available,
        "gpu_name": torch.cuda.get_device_name(0) if cuda_available else None,
        "gpu_memory_gb": round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2) if cuda_available else None,
    }


@app.post("/infer")
def infer(frame: UploadFile = File(...), frame_id: Optional[int] = Form(None), timestamp: Optional[float] = Form(None), send_enhanced: Optional[bool] = Form(False)):
    start = time.time()
    if engine_wrapper.engine is None:
        return {"status": "error", "error_message": "Engine not initialized", "frame_id": frame_id}

    try:
        data = frame.file.read()
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"status": "error", "error_message": "Image decode failed", "frame_id": frame_id}

        # Run inference
        result_json, enhanced = engine_wrapper.infer(img, send_enhanced=send_enhanced)

        latency_ms = (time.time() - start) * 1000.0

        response = {
            "status": "success",
            "device_used": engine_wrapper.device,
            "inference_latency_ms": latency_ms,
            "frame_id": frame_id,
            "detections": result_json.get('detections', []),
            "confidence": result_json.get('max_confidence', 0.0),
            "threat_state": result_json.get('state', 'NORMAL'),
        }

        if send_enhanced:
            try:
                _, buf = cv2.imencode('.jpg', enhanced)
                response['enhanced_image'] = base64.b64encode(buf).decode('utf-8')
            except Exception:
                logger.exception("Failed to encode enhanced image")

        return response

    except Exception as e:
        logger.exception("Error during inference: %s", e)
        return {"status": "error", "error_message": str(e), "frame_id": frame_id}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)
