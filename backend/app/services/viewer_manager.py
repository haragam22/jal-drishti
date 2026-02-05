"""
ViewerManager: Multi-Viewer Streaming Control

PHASE-3 CORE: Selective streaming to authorized viewers.

Features:
- Track connected viewers by viewer_id
- Allow/deny list for frame delivery
- Blocked viewers keep WS open but receive no frames
"""

import threading
import logging
from typing import Dict, Set, Optional
from dataclasses import dataclass
from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass
class ViewerInfo:
    viewer_id: str
    websocket: WebSocket
    label: str = "Unknown Device"
    connected_at: float = 0.0


class ViewerManager:
    """
    Manages connected viewers and their streaming permissions.
    
    Rules:
    - Each viewer has unique viewer_id (UUID from client)
    - Blocked viewers stay connected but receive no frames
    - Operator can toggle allow/block per viewer
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._viewers: Dict[str, ViewerInfo] = {}  # viewer_id -> ViewerInfo
        self._allowed_viewers: Set[str] = set()  # viewer_ids that can receive frames
        self._viewers_lock = threading.Lock()
        
        # By default, allow all new viewers (operator can block later)
        self._auto_allow_new = True
        
        logger.info("[ViewerManager] Initialized")
    
    def register_viewer(self, viewer_id: str, websocket: WebSocket, label: str = "Unknown Device") -> bool:
        """
        Register a new viewer connection.
        
        Args:
            viewer_id: Unique client identifier (UUID)
            websocket: The WebSocket connection
            label: Human-readable device label
            
        Returns:
            True if registered successfully
        """
        import time
        
        with self._viewers_lock:
            self._viewers[viewer_id] = ViewerInfo(
                viewer_id=viewer_id,
                websocket=websocket,
                label=label,
                connected_at=time.time()
            )
            
            # Auto-allow if configured
            if self._auto_allow_new:
                self._allowed_viewers.add(viewer_id)
                logger.info(f"[ViewerManager] Viewer registered and allowed: {viewer_id[:8]}...")
            else:
                logger.info(f"[ViewerManager] Viewer registered (blocked by default): {viewer_id[:8]}...")
            
            return True
    
    def unregister_viewer(self, viewer_id: str):
        """Remove viewer on disconnect."""
        with self._viewers_lock:
            if viewer_id in self._viewers:
                del self._viewers[viewer_id]
            self._allowed_viewers.discard(viewer_id)
            logger.info(f"[ViewerManager] Viewer unregistered: {viewer_id[:8]}...")
    
    def is_allowed(self, viewer_id: str) -> bool:
        """Check if viewer is allowed to receive frames."""
        with self._viewers_lock:
            return viewer_id in self._allowed_viewers
    
    def allow_viewer(self, viewer_id: str) -> bool:
        """Allow a viewer to receive frames."""
        with self._viewers_lock:
            if viewer_id in self._viewers:
                self._allowed_viewers.add(viewer_id)
                logger.info(f"[ViewerManager] Viewer allowed: {viewer_id[:8]}...")
                return True
            return False
    
    def revoke_viewer(self, viewer_id: str) -> bool:
        """Block a viewer from receiving frames (WS stays open)."""
        with self._viewers_lock:
            self._allowed_viewers.discard(viewer_id)
            logger.info(f"[ViewerManager] Viewer blocked: {viewer_id[:8]}...")
            return True
    
    def get_connected_viewers(self) -> list:
        """Get list of all connected viewers with their status."""
        with self._viewers_lock:
            return [
                {
                    "viewer_id": v.viewer_id,
                    "label": v.label,
                    "allowed": v.viewer_id in self._allowed_viewers,
                    "connected_at": v.connected_at
                }
                for v in self._viewers.values()
            ]
    
    def get_allowed_websockets(self) -> list:
        """Get WebSocket connections of allowed viewers only."""
        with self._viewers_lock:
            return [
                self._viewers[vid].websocket
                for vid in self._allowed_viewers
                if vid in self._viewers
            ]
    
    def get_viewer_count(self) -> dict:
        """Get viewer statistics."""
        with self._viewers_lock:
            return {
                "total": len(self._viewers),
                "allowed": len(self._allowed_viewers),
                "blocked": len(self._viewers) - len(self._allowed_viewers)
            }


# Global singleton instance
viewer_manager = ViewerManager()
