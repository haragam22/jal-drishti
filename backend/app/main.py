from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import stream, ws_server
from app.auth import auth_router

# Core Modules
from app.video.video_reader import VideoReader
from app.scheduler.frame_scheduler import FrameScheduler
from app.ml.dummy_ml import DummyML
import threading
import asyncio

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

@app.on_event("startup")
async def startup_event():
    # Capture the main event loop for the WS server to use
    loop = asyncio.get_running_loop()
    ws_server.set_event_loop(loop)
    
    # Initialize Core Pipeline
    # Using a dummy video for now as per previous testing context. 
    # Ideally this video path should come from config or request.
    video_path = "backend/dummy.mp4" # Assumption based on verify_video.py location, but we are running from root likely
    # Let's use a safe absolute path or check existence. 
    # For this Milestone, let's look for 'dummy.mp4' in current dir or create one?
    # Actually, verify_video.py created it on Desktop execution context.
    # Let's assume a fixed path for the demo.
    import os
    if not os.path.exists("dummy.mp4"):
        print("[Startup] Warning: dummy.mp4 not found. Please run verify_video.py first or provide video.")
        # Create one if missing for stability? No, simpler to warn.
    
    # Actually, we need to pass a valid video reader.
    # Reusing the one created by verification if available.
    if os.path.exists("dummy.mp4"):
        reader = VideoReader("dummy.mp4")
    else:
        # Fallback to verify logic? Or just fail gracefully?
        print("[Startup] No video source found.")
        return

    ml_module = DummyML()
    
    # Callback to push to WebSocket
    def on_result(payload):
        ws_server.broadcast(payload)

    # Scheduler
    scheduler = FrameScheduler(reader, target_fps=15, ml_module=ml_module, result_callback=on_result)
    
    # Run in background thread
    t = threading.Thread(target=scheduler.run, daemon=True)
    t.start()
    print("[Startup] Scheduler thread started.")


@app.get("/")
def read_root():
    return {"message": "Jal-Drishti Backend is running"}

# Entry point for debugging if run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
