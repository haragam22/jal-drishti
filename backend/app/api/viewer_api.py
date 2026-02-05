"""
Viewer API: Multi-Viewer Streaming Control

PHASE-3 CORE: API endpoints for viewer management.

Endpoints:
- GET /api/viewers/connected - List connected viewers
- POST /api/viewers/allow - Allow viewer to receive frames
- POST /api/viewers/revoke - Block viewer from receiving frames
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.services.viewer_manager import viewer_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/viewers", tags=["viewers"])


class ViewerActionRequest(BaseModel):
    viewer_id: str


class ViewerInfo(BaseModel):
    viewer_id: str
    label: str
    allowed: bool
    connected_at: float


class ViewerListResponse(BaseModel):
    viewers: List[ViewerInfo]
    total: int
    allowed: int
    blocked: int


class ViewerActionResponse(BaseModel):
    success: bool
    viewer_id: str
    message: str


@router.get("/connected", response_model=ViewerListResponse)
async def get_connected_viewers():
    """Get list of all connected dashboard viewers."""
    viewers = viewer_manager.get_connected_viewers()
    stats = viewer_manager.get_viewer_count()
    
    return ViewerListResponse(
        viewers=[ViewerInfo(**v) for v in viewers],
        total=stats["total"],
        allowed=stats["allowed"],
        blocked=stats["blocked"]
    )


@router.post("/allow", response_model=ViewerActionResponse)
async def allow_viewer(request: ViewerActionRequest):
    """Allow a viewer to receive video frames."""
    success = viewer_manager.allow_viewer(request.viewer_id)
    return ViewerActionResponse(
        success=success,
        viewer_id=request.viewer_id,
        message="Viewer allowed" if success else "Viewer not found"
    )


@router.post("/revoke", response_model=ViewerActionResponse)
async def revoke_viewer(request: ViewerActionRequest):
    """
    Block a viewer from receiving frames.
    
    Note: WebSocket stays open, viewer just stops receiving frames.
    UI should show "View disabled" state.
    """
    success = viewer_manager.revoke_viewer(request.viewer_id)
    return ViewerActionResponse(
        success=success,
        viewer_id=request.viewer_id,
        message="Viewer blocked" if success else "Error"
    )
