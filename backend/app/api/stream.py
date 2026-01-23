from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.ml_service import ml_service
from app.schemas.response import AIResponse
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn")

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected to stream")
    
    try:
        while True:
            # Receive binary frame (bytes)
            # We use receive_bytes to accept raw image data
            data = await websocket.receive_bytes()
            
            # Process frame (Dummy ML)
            result = ml_service.process_frame(data)
            
            # Validate against schema (optional, but good for safety)
            response = AIResponse(**result)
            
            # Send JSON response
            await websocket.send_json(response.model_dump())
            
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error in stream: {e}")
        try:
            await websocket.close()
        except:
            pass
