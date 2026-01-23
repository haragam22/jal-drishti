from pydantic import BaseModel
from typing import List, Optional

class Detection(BaseModel):
    label: str
    confidence: float
    bbox: List[int] # [x1, y1, x2, y2]

class AIResponse(BaseModel):
    status: str
    frame_id: int
    image_data: str # base64
    detections: List[Detection]
    visibility_score: float

class ErrorResponse(BaseModel):
    status: str
    message: str
