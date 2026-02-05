from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Set, Dict

router = APIRouter()

# PHASE-3: Viewer-aware connections
# Map: viewer_id -> WebSocket
active_connections: Dict[str, WebSocket] = {}
_event_loop = None


def set_event_loop(loop):
    global _event_loop
    _event_loop = loop


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    PHASE-3 CORE: Viewer-aware WebSocket endpoint.
    
    Client must send viewer_id on connect.
    Only allowed viewers receive frames (others stay connected but get no data).
    """
    from app.services.viewer_manager import viewer_manager
    
    await websocket.accept()
    
    # Wait for viewer_id from client
    viewer_id = None
    try:
        # Expect first message to be viewer registration
        init_msg = await asyncio.wait_for(websocket.receive_json(), timeout=5.0)
        viewer_id = init_msg.get("viewer_id")
        label = init_msg.get("label", "Unknown Device")
        
        if not viewer_id:
            # Generate one if client didn't provide
            import uuid
            viewer_id = str(uuid.uuid4())
            
    except asyncio.TimeoutError:
        # No viewer_id sent, generate one
        import uuid
        viewer_id = str(uuid.uuid4())
        label = "Unknown Device"
    except Exception as e:
        print(f"[WS] Error getting viewer_id: {e}")
        import uuid
        viewer_id = str(uuid.uuid4())
        label = "Unknown Device"
    
    # Register viewer
    active_connections[viewer_id] = websocket
    viewer_manager.register_viewer(viewer_id, websocket, label)
    print(f"[WS] Viewer connected: {viewer_id[:8]}... Total: {len(active_connections)}")
    
    # Send connection success with assigned viewer_id
    await websocket.send_json({
        "type": "system",
        "status": "connected",
        "message": "WebSocket connection established",
        "viewer_id": viewer_id,
        "allowed": viewer_manager.is_allowed(viewer_id)
    })
    
    try:
        while True:
            # Passive subscriber: keep connection alive
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
            # Ignore other messages
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS] Error: {e}")
    finally:
        active_connections.pop(viewer_id, None)
        viewer_manager.unregister_viewer(viewer_id)
        print(f"[WS] Viewer disconnected: {viewer_id[:8]}... Total: {len(active_connections)}")


def broadcast(message: dict):
    """
    PHASE-3: Send ML result to ALLOWED viewers only.
    
    Blocked viewers stay connected but receive no frames.
    """
    from app.services.viewer_manager import viewer_manager
    
    global active_connections, _event_loop
    
    if not active_connections:
        return
        
    if _event_loop is None:
        try:
            _event_loop = asyncio.get_event_loop()
        except:
            return

    send_message = message.copy()

    async def _send():
        if not active_connections:
            return
        
        # Send only to ALLOWED viewers
        for viewer_id, connection in list(active_connections.items()):
            # Check if viewer is allowed
            if not viewer_manager.is_allowed(viewer_id):
                continue  # Skip blocked viewers (WS stays open)
            
            try:
                if isinstance(send_message, dict) and "type" in send_message:
                    await asyncio.wait_for(
                        connection.send_json(send_message),
                        timeout=0.1
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
                pass
            except Exception:
                active_connections.pop(viewer_id, None)
                viewer_manager.unregister_viewer(viewer_id)

    asyncio.run_coroutine_threadsafe(_send(), _event_loop)

