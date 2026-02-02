"""
Phone Camera Upload WebSocket Endpoint

PHASE-3 CORE: Throttled phone camera upload with feedback.

Key Changes:
1. Only 1 phone connection allowed (kick old)
2. Throttle feedback: accepted=false tells phone to slow down
3. Target ~12 FPS from phone, not unlimited
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import base64
import numpy as np
import cv2
import json
import time

from app.video.phone_source import phone_camera_source

router = APIRouter()

# PHASE-3 CORE: Single phone connection only
_active_phone: WebSocket = None
TARGET_FPS = 12
FRAME_INTERVAL = 1.0 / TARGET_FPS


@router.websocket("/upload")
async def phone_upload_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for receiving phone camera frames.
    
    PHASE-3 CORE Rules:
    1. Only 1 phone allowed (kick old on new connect)
    2. Send throttle feedback to phone
    3. If queue full → tell phone to slow down
    """
    global _active_phone
    
    # Kick old phone connection if exists
    if _active_phone is not None:
        try:
            await _active_phone.close(code=1000, reason="New phone connected")
            print("[PhoneUpload] Kicked old phone for new connection")
        except Exception:
            pass
    
    await websocket.accept()
    _active_phone = websocket
    print("[PhoneUpload] Phone camera connected (1 allowed)")
    
    frames_received = 0
    last_frame_time = 0.0
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if "frame" not in message:
                    continue
                
                # Throttle: Skip if too fast
                now = time.time()
                if last_frame_time > 0 and (now - last_frame_time) < FRAME_INTERVAL * 0.5:
                    # Phone is sending too fast - send throttle feedback
                    await websocket.send_json({
                        "status": "throttle",
                        "wait_ms": int(FRAME_INTERVAL * 1000)
                    })
                    continue
                
                last_frame_time = now
                
                # Decode base64 JPEG to NumPy array
                frame_b64 = message["frame"]
                frame_bytes = base64.b64decode(frame_b64)
                nparr = np.frombuffer(frame_bytes, np.uint8)
                frame_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame_bgr is None:
                    continue
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                
                # Inject frame - check if accepted
                accepted = phone_camera_source.inject_frame(frame_rgb)
                
                frames_received += 1
                
                # Send feedback to phone
                if not accepted:
                    # Queue full - tell phone to slow down
                    await websocket.send_json({
                        "status": "slow_down",
                        "wait_ms": int(FRAME_INTERVAL * 2000)  # Wait 2x interval
                    })
                
                # Log periodically
                if frames_received % 30 == 0:
                    print(f"[PhoneUpload] Received {frames_received} frames (accepted={accepted})")
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"[PhoneUpload] Error processing frame: {e}")
                continue
                
    except WebSocketDisconnect:
        print(f"[PhoneUpload] Phone disconnected after {frames_received} frames")
    except Exception as e:
        print(f"[PhoneUpload] Error: {e}")
    finally:
        if _active_phone == websocket:
            _active_phone = None
        phone_camera_source.stop()
        print("[PhoneUpload] Connection closed")
