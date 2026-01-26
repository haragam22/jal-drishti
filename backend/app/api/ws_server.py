from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Optional

router = APIRouter()

# Global variable to hold the single active connection
active_connection: Optional[WebSocket] = None

# Global Event Loop reference for thread-safe messaging
# We will set this when the server starts in main.py if needed, 
# or we can assume ws handlers run in the main loop.
_event_loop = None

def set_event_loop(loop):
    global _event_loop
    _event_loop = loop

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    global active_connection
    
    # Accept new connection
    await websocket.accept()
    
    # Requirement: Accept exactly one active client at a time
    if active_connection is not None:
        print("[WS] Rejecting secondary connection.")
        # Send JSON error before closing
        await websocket.send_json({
            "type": "system",
            "status": "error",
            "message": "Connection limit reached",
            "payload": None
        })
        await websocket.close()
        return

    active_connection = websocket
    print("[WS] Client connected.")
    
    # Send connection success message
    await websocket.send_json({
        "type": "system",
        "status": "connected",
        "message": "WebSocket connection established",
        "payload": None
    })
    
    try:
        while True:
            # Keep the connection open.
            # We don't expect messages from client, but we must await something to keep loop alive.
            # If client disconnects, this will raise WebSocketDisconnect
            data = await websocket.receive_text()
            # Optional: handle ping/pong or commands
            pass
            
    except WebSocketDisconnect:
        print("[WS] Client disconnected.")
        active_connection = None
    except Exception as e:
        print(f"[WS] Error: {e}")
        active_connection = None


def broadcast(payload: dict):
    """
    Sends data to the active WebSocket connection.
    This function is intended to be called from the Scheduler thread.
    It uses asyncio.run_coroutine_threadsafe to jump to the main event loop.
    """
    global active_connection, _event_loop
    
    if active_connection is None:
        return # No one to send to
        
    if _event_loop is None:
        # Fallback if loop wasn't set explicitly (though it should be)
        try:
            _event_loop = asyncio.get_event_loop()
        except:
             print("[WS] Error: No event loop found for broadcast.")
             return

    async def _send():
        if active_connection:
            try:
                # Wrap payload in standardized JSON structure
                await active_connection.send_json({
                    "type": "data",
                    "status": "success",
                    "message": "New frame data",
                    "payload": payload
                })
            except Exception as e:
                 print(f"[WS] Send Error: {e}")

    # Schedule the send on the main loop
    asyncio.run_coroutine_threadsafe(_send(), _event_loop)
