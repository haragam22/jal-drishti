from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Optional, Set

router = APIRouter()

# Global variable to hold active connections
active_connections: Set[WebSocket] = set()

# Global Event Loop reference for thread-safe messaging
_event_loop = None

def set_event_loop(loop):
    global _event_loop
    _event_loop = loop

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
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
            # Keep the connection open.
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
            # Handle other messages if needed
            
    except WebSocketDisconnect:
        print("[WS] Client disconnected (exception).")
    except Exception as e:
        print(f"[WS] Error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(active_connections)}")


def broadcast(message: dict):
    """
    Sends a dictionary message to ALL active WebSocket connections.
    """
    global active_connections, _event_loop
    
    if not active_connections:
        return # No one to send to
        
    if _event_loop is None:
        try:
            _event_loop = asyncio.get_event_loop()
        except:
             print("[WS] Error: No event loop found for broadcast.")
             return

    async def _send():
        if active_connections:
            # Create a copy to avoid runtime errors if set changes during iteration
            for connection in list(active_connections):
                try:
                    if isinstance(message, dict) and "type" in message:
                         await connection.send_json(message)
                    else:
                        await connection.send_json({
                            "type": "data",
                            "status": "success",
                            "message": "New frame data",
                            "payload": message
                        })
                except RuntimeError as re:
                    # Catch ASGI "Unexpected message" errors which happen when sending to closed socket
                    # This is common during rapid disconnects/reconnects
                    if "websocket.close" in str(re) or "response already completed" in str(re):
                        pass 
                    else:
                         print(f"[WS] Send Runtime Error: {re}")
                except Exception as e:
                     print(f"[WS] Send Error: {e}")

    # Schedule the send on the main loop
    asyncio.run_coroutine_threadsafe(_send(), _event_loop)
