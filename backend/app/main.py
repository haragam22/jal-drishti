from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api import stream, ws_server
from app.auth import auth_router

# Core Modules
from app.video.video_reader import RawVideoSource
from app.scheduler.frame_scheduler import FrameScheduler
from app.ml.dummy_ml import DummyML
from app.services.video_stream_manager import video_stream_manager

import threading
import asyncio
import os

app = FastAPI(title="Jal-Drishti Backend", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
# app.include_router(stream.router, prefix="/ws", tags=["stream"]) # Keeping old one for now if needed?
app.include_router(ws_server.router, prefix="/ws", tags=["websocket"])

# --- RAW FEED WEBSOCKET ---
@app.websocket("/ws/raw_feed")
async def raw_feed_endpoint(websocket: WebSocket):
    await video_stream_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for any client messages (ignore them or handle control)
            data = await websocket.receive_text()
            # Optional: Heartbeat or keepalive logic
    except WebSocketDisconnect:
        video_stream_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error in raw_feed: {e}")
        video_stream_manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    # Capture the main event loop for the WS server to use
    loop = asyncio.get_running_loop()
    ws_server.set_event_loop(loop)
    import os
    # Initialize Core Pipeline
    from app.services.ml_service import ml_service
    
    video_path = "backend/dummy.mp4"
    if not os.path.exists(video_path):
        # Check relative to root as well
        if os.path.exists("dummy.mp4"):
            video_path = "dummy.mp4"
        else:
            print(f"[Startup] Warning: {video_path} not found.")
            return
    
    reader = RawVideoSource(video_path)

    # Callback to push to WebSocket
    def on_result(envelope):
        """
        Flatten the payload for the frontend.
        The frontend expects 'state', 'image_data', etc. at the top level.
        """
        if envelope.get("type") == "data" and "payload" in envelope:
            flat_payload = {
                "type": "data",
                **envelope["payload"]
            }
            ws_server.broadcast(flat_payload)
        else:
            ws_server.broadcast(envelope)

    # Scheduler
    # Raw frame callback: schedule the coroutine on the main loop
    def raw_frame_callback(frame, frame_id, timestamp):
        try:
            # Use run_coroutine_threadsafe to schedule async broadcast from scheduler thread
            asyncio.run_coroutine_threadsafe(
                video_stream_manager.broadcast_raw_frame(frame, frame_id, timestamp),
                loop
            )
        except Exception as e:
            print(f"[Startup] Error scheduling raw frame broadcast: {e}")

    scheduler = FrameScheduler(reader, target_fps=5, ml_module=ml_service, result_callback=on_result, raw_callback=raw_frame_callback)
    
    # Run in background thread
    t = threading.Thread(target=scheduler.run, daemon=True)
    t.start()
    print("[Startup] Scheduler thread started with real ML Engine.")


@app.get("/")
def read_root():
    return {"message": "Jal-Drishti Backend is running"}

# Entry point for debugging if run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
