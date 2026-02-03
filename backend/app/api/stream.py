from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.schemas.response import AIResponse
from app.core.security import verify_token
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn")

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # 1. Verify Token
    payload = verify_token(token)
    if not payload:
        # Close with Policy Violation (1008) if invalid
        logger.warning("Unauthenticated WebSocket connection attempt rejected.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user = payload.get("sub")
    logger.info(f"Authenticated client '{user}' connected to stream")

    await websocket.accept()
    
    try:
        while True:
            # Receive binary frame (bytes)
            # We use receive_bytes to accept raw image data
            data = await websocket.receive_bytes()

            # Retrieve the ML service instance from the app state
            ml_service = getattr(websocket.app.state, 'ml_service', None)
            if ml_service is None:
                logger.error("ML service not available on app.state")
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
                return

            # Process frame via the ML service
            result = ml_service.process_frame(data)

            # Validate against schema (optional, but good for safety)
            response = AIResponse(**result)

            # Send JSON response
            await websocket.send_json(response.model_dump())

    except WebSocketDisconnect:
        logger.info(f"Client '{user}' disconnected")
    except Exception as e:
        # Suppress noisy errors during shutdown or normal closes
        error_msg = str(e).lower()
        if "close message has been sent" in error_msg or "connection closed" in error_msg:
            pass  # Normal close, don't log
        else:
            logger.error(f"Error in stream: {type(e).__name__}: {e}")
        try:
            await websocket.close()
        except:
            pass
