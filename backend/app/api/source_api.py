"""
Source API: Runtime Source Selection & Server Info

PHASE-3 CORE: API endpoints for source switching.

Endpoints:
- POST /api/source/select - Switch source (non-blocking)
- POST /api/source/upload - Upload video file
- GET /api/source/status - Current source state
- GET /api/server/info - Server IP and camera URL
"""

from fastapi import APIRouter, Request, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import logging
import os
import shutil

from app.services.source_manager import source_manager, get_lan_ip

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/source", tags=["source"])

# Upload directory
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class SourceSelectRequest(BaseModel):
    type: str  # "video" or "camera"
    video_path: Optional[str] = None  # Optional path for video


class SourceSelectResponse(BaseModel):
    success: bool
    state: Optional[str] = None
    source: Optional[str] = None
    error: Optional[str] = None


class SourceStatusResponse(BaseModel):
    state: str
    source: Optional[str]
    last_frame_ts: Optional[float]


class ServerInfoResponse(BaseModel):
    ip: str
    port: int
    camera_url: str


class VideoUploadResponse(BaseModel):
    success: bool
    file_path: Optional[str] = None
    error: Optional[str] = None


@router.post("/select", response_model=SourceSelectResponse)
async def select_source(request: SourceSelectRequest):
    """
    Switch video source at runtime.
    
    Non-blocking: returns immediately, never waits on ML.
    
    Args:
        type: "video" or "camera"
        video_path: Optional path to video file (for video type)
    """
    logger.info(f"[API] Source select request: {request.type}, path={request.video_path}")
    result = source_manager.switch_source(request.type, video_path=request.video_path)
    return SourceSelectResponse(**result)


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file and optionally switch to it.
    
    File is saved to data/uploads/ directory.
    """
    try:
        # Validate file extension
        if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            return VideoUploadResponse(success=False, error="Invalid file type. Supported: mp4, avi, mov, mkv, webm")
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        logger.info(f"[API] Video uploaded: {file_path}")
        return VideoUploadResponse(success=True, file_path=file_path)
        
    except Exception as e:
        logger.error(f"[API] Video upload error: {e}")
        return VideoUploadResponse(success=False, error=str(e))


@router.get("/status", response_model=SourceStatusResponse)
async def get_source_status():
    """Get current source status."""
    status = source_manager.get_status()
    return SourceStatusResponse(**status)


@router.get("/info")
async def get_server_info(request: Request):
    """
    Get server connection info for phone camera.
    
    IP is derived from active network interface (not hardcoded).
    """
    ip = get_lan_ip()
    # Get port from request (actual server port)
    port = request.url.port or 9000
    camera_url = f"http://{ip}:{port}/static/phone_camera.html"
    
    logger.info(f"[API] Server info: {ip}:{port}")
    return ServerInfoResponse(ip=ip, port=port, camera_url=camera_url)

