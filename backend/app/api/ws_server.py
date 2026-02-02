from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Set

router = APIRouter()

# STABILIZATION FIX: Allow MULTIPLE concurrent clients (Issue 1 & 4)
# Different WS endpoints are NOT same client - allow many subscribers
active_connections: Set[WebSocket] = set()
_event_loop = None

# Enhanced image control - don't send every frame
_last_enhanced_frame_id = -1
ENHANCED_IMAGE_INTERVAL = 6  # Send image every Nth ML result


def set_event_loop(loop):
    global _event_loop
    _event_loop = loop


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    STABILIZATION FIX: Multiple WebSocket clients allowed.
    
    FIX FOR Issues 1 & 4:
    - DO NOT kick existing clients
    - Allow multiple concurrent subscribers
    - Backend is producer, frontend is passive subscriber
    """
    global active_connections
    
    await websocket.accept()
    active_connections.add(websocket)
    print(f"[WS] Client connected. Total: {len(active_connections)}")
    
    # Send connection success message
    await websocket.send_json({
        "type": "system",
        "status": "connected",
        "message": "WebSocket connection established",
        "payload": None
    })
    
    try:
        while True:
            # Passive subscriber: just keep connection alive
            # FIX Issue 2: Ignore any client messages - backend drives timing
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
            # Ignore all other messages - frontend should NOT drive backend
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS] Error: {e}")
    finally:
        active_connections.discard(websocket)
        print(f"[WS] Client disconnected. Total: {len(active_connections)}")


def broadcast(message: dict):
    """
    Send ML result to ALL active WebSocket connections.
    
    STABILIZATION FIX:
    - Send to all clients (not just one)
    - Non-blocking sends with timeout
    - Drop slow clients silently
    """
    global active_connections, _event_loop, _last_enhanced_frame_id
    
    if not active_connections:
        return
        
    if _event_loop is None:
        try:
            _event_loop = asyncio.get_event_loop()
        except:
            return

    # Check if we should include enhanced image
    # STABILIZATION FIX: Never strip image data (Fix #1)
    # The frontend expects a continuous feed. Removing image_data causes "No Signal" flicker.
    # While this increases bandwidth, it is necessary for visual stability until frontend has interpolation.
    should_send_image = True 
    # _last_enhanced_frame_id update removed to prevent NameError
    
    send_message = message.copy()

    async def _send():
        if not active_connections:
            return
        
        # Send to ALL clients (copy to avoid modification during iteration)
        for connection in list(active_connections):
            try:
                if isinstance(send_message, dict) and "type" in send_message:
                    await asyncio.wait_for(
                        connection.send_json(send_message),
                        timeout=0.1  # 100ms max wait
                    )
                else:
                    await asyncio.wait_for(
                        connection.send_json({
                            "type": "data",
                            "status": "success",
                            "message": "New frame data",
                            "payload": send_message
                        }),
                        timeout=0.1
                    )
            except asyncio.TimeoutError:
                # Client too slow, drop this frame for them
                pass
            except Exception:
                # Silently remove failed clients
                active_connections.discard(connection)

    asyncio.run_coroutine_threadsafe(_send(), _event_loop)
