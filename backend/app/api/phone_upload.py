"""
Phone Camera Upload WebSocket Endpoint

This module provides the /ws/upload endpoint that receives base64-encoded JPEG frames
from the phone camera page and feeds them into the PhoneCameraSource.

Integration Notes:
- This endpoint receives frames from phone_camera.html
- Frames are decoded from base64 JPEG to NumPy RGB arrays
- Frames are injected into phone_camera_source, which is consumed by FrameScheduler
- The existing FrameScheduler, ML Bridge, and SAFE MODE logic are UNCHANGED
- This is purely an INPUT adapter - it replaces VideoReader, not the pipeline
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import base64
import numpy as np
import cv2
import json

from app.video.phone_source import phone_camera_source

router = APIRouter()


@router.websocket("/upload")
async def phone_upload_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for receiving phone camera frames.
    
    Protocol:
        - Phone sends JSON: {"frame": "<base64-encoded-jpeg>"}
        - Server decodes and injects frame into PhoneCameraSource
        - Server responds with acknowledgment (optional)
    
    This endpoint does NOT:
        - Bypass FrameScheduler
        - Send frames directly to ML
        - Modify SAFE MODE logic
        - Affect /ws/stream endpoint
    """
    await websocket.accept()
    print("[PhoneUpload] Phone camera connected")
    
    frames_received = 0
    
    try:
        while True:
            # Receive message from phone
            data = await websocket.receive_text()
            
            try:
                # Parse JSON message
                message = json.loads(data)
                
                if "frame" not in message:
                    # Heartbeat or other message - ignore
                    continue
                
                # Decode base64 JPEG to NumPy array
                frame_b64 = message["frame"]
                frame_bytes = base64.b64decode(frame_b64)
                
                # Decode JPEG to BGR array
                nparr = np.frombuffer(frame_bytes, np.uint8)
                frame_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame_bgr is None:
                    print("[PhoneUpload] Warning: Failed to decode frame")
                    continue
                
                # Convert BGR to RGB (OpenCV loads as BGR, we need RGB for consistency)
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                
                # Inject frame into PhoneCameraSource
                # The FrameScheduler will consume this via phone_camera_source.read()
                accepted = phone_camera_source.inject_frame(frame_rgb)
                
                frames_received += 1
                
                # Log periodically
                if frames_received % 30 == 0:
                    print(f"[PhoneUpload] Received {frames_received} frames (accepted={accepted})")
                
                # Optional: Send acknowledgment to phone
                # Disabled for performance - phone doesn't need confirmation
                # await websocket.send_json({"status": "ok", "frame_id": frames_received})
                
            except json.JSONDecodeError:
                print("[PhoneUpload] Warning: Invalid JSON received")
                continue
            except Exception as e:
                print(f"[PhoneUpload] Error processing frame: {e}")
                continue
                
    except WebSocketDisconnect:
        print(f"[PhoneUpload] Phone disconnected after {frames_received} frames")
    except Exception as e:
        print(f"[PhoneUpload] Error: {e}")
    finally:
        # Signal PhoneCameraSource that phone has disconnected
        # This will cause read() to eventually stop or handle gracefully
        phone_camera_source.stop()
        print("[PhoneUpload] Connection closed")
