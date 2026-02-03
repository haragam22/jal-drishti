import base64
import cv2
import numpy as np
import asyncio
from typing import List
from fastapi import WebSocket, WebSocketDisconnect


class VideoStreamManager:
    """
    STABILIZATION FIX: Raw Frame WebSocket Manager
    
    FIX FOR Issues 1 & 4:
    - Allow MULTIPLE concurrent clients
    - DO NOT kick existing clients
    - Non-blocking sends with timeout
    - Drop frames for slow clients, don't disconnect them
    """
    
    def __init__(self):
        # STABILIZATION: Allow multiple clients (was single connection)
        self.active_connections: List[WebSocket] = []
        self.is_shutting_down = False
        self.frames_sent = 0
        self.frames_dropped = 0
        
    async def connect(self, websocket: WebSocket):
        """
        STABILIZATION FIX: Accept new connection WITHOUT kicking old ones.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[VideoStreamManager] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[VideoStreamManager] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast_raw_frame(self, frame: np.ndarray, frame_id: int, timestamp: float):
        """
        STABILIZATION FIX:
        - Send to ALL clients
        - Non-blocking with timeout
        - Drop frames for slow clients, don't disconnect
        """
        if not self.active_connections or self.is_shutting_down:
            return

        try:
            # Encode Frame (RGB -> BGR for OpenCV encoding -> JPEG)
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Encode to JPEG with quality reduction for speed
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 70]
            success, buffer = cv2.imencode(".jpg", bgr_frame, encode_params)
            if not success:
                return
            
            # Base64 Encode
            b64_image = base64.b64encode(buffer).decode("utf-8")
            
            # Construct Payload
            payload = {
                "type": "RAW_FRAME",
                "frame_id": frame_id,
                "timestamp": timestamp,
                "image": b64_image,
                "resolution": [frame.shape[0], frame.shape[1]]
            }
            
            # Send to ALL clients (copy list to allow modification)
            for connection in self.active_connections[:]:
                try:
                    await asyncio.wait_for(
                        connection.send_json(payload),
                        timeout=0.1  # 100ms max wait
                    )
                    self.frames_sent += 1
                except asyncio.TimeoutError:
                    # Client too slow - drop this frame for them, don't disconnect
                    self.frames_dropped += 1
                except WebSocketDisconnect:
                    self.disconnect(connection)
                except Exception as e:
                    if not self.is_shutting_down:
                        error_msg = str(e).lower()
                        if "closed" in error_msg or "disconnect" in error_msg:
                            self.disconnect(connection)
                        # Don't print every error - too noisy
                    
        except Exception as e:
            if not self.is_shutting_down:
                print(f"[VideoStreamManager] Broadcasting error: {e}")


# Global instance
video_stream_manager = VideoStreamManager()
