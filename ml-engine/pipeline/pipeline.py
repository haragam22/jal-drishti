"""
Jal-Drishti Unified Perception Pipeline
========================================
Part 4 & 5 Implementation

This module integrates FUnIE-GAN (underwater image enhancement) with 
YOLOv8-Nano (anomaly detection) into a single, unified inference pipeline.

Key Features:
- Normalization bridge between GAN [-1,1] and YOLO [0,1] domains
- Frame validity gate for corrupted/empty frames
- Confidence-driven decision framework
- Safe Mode for poor visibility conditions
- Standardized JSON output schema for backend integration

Author: Jal-Drishti Team
"""

import torch
import torch.nn.functional as F
import cv2
import numpy as np
import os
import sys
import logging
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ultralytics import YOLO
from enhancement.funie_gan.nets.funiegan import GeneratorFunieGAN


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('JalDrishtiPipeline')


class SystemState(Enum):
    """
    Confidence-driven system states for human-in-the-loop design.
    
    The AI system provides confidence-scored suggestions but NEVER initiates
    action independently. Final decisions are made by human operators.
    """
    CONFIRMED_THREAT = "CONFIRMED_THREAT"       # Confidence > 0.75
    POTENTIAL_ANOMALY = "POTENTIAL_ANOMALY"     # Confidence 0.40 - 0.75
    SAFE_MODE = "SAFE_MODE"                     # Confidence < 0.40 or invalid


class JalDrishtiPipeline:
    """
    Unified GAN → YOLO perception pipeline for underwater anomaly detection.
    
    This class bridges two fundamentally different models:
    - FUnIE-GAN: Input [-1,1], Output [-1,1], Resolution 256×256
    - YOLOv8-Nano: Input [0,1], Resolution 640×640
    
    The normalization bridge ensures correct data transitions:
    Raw (0-255) → GAN (-1 to 1) → Bridge (0 to 1) → YOLO (detection)
    
    Attributes:
        gan: FUnIE-GAN generator model
        yolo: YOLOv8-Nano detection model
        device: CUDA or CPU device
        use_fp16: Whether to use half-precision inference
    """
    
    # Confidence thresholds (configurable, conservative by design)
    THRESHOLD_CONFIRMED = 0.75
    THRESHOLD_POTENTIAL = 0.40
    
    def __init__(
        self, 
        gan_weights_path: str = None,
        yolo_weights_path: str = None,
        device: str = None,
        use_fp16: bool = False
    ):
        """
        Initialize the unified pipeline. Models are loaded ONCE at startup.
        
        Args:
            gan_weights_path: Path to FUnIE-GAN weights (.pth)
            yolo_weights_path: Path to YOLOv8 weights (.pt)
            device: 'cuda' or 'cpu' (auto-detected if None)
            use_fp16: Enable half-precision inference for speed
        """
        # Auto-detect device
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.use_fp16 = use_fp16 and self.device == "cuda"
        
        logger.info(f"Initializing JalDrishtiPipeline on {self.device}")
        logger.info(f"FP16 inference: {self.use_fp16}")
        
        # Resolve default paths
        base_path = Path(__file__).parent.parent
        if gan_weights_path is None:
            gan_weights_path = base_path / "enhancement" / "funie_gan" / "weights" / "funie_generator.pth"
        if yolo_weights_path is None:
            yolo_weights_path = base_path / "detection" / "yolov8n.pt"
        
        # Load FUnIE-GAN generator (loaded once, no repeated loading)
        logger.info(f"Loading FUnIE-GAN weights from: {gan_weights_path}")
        self.gan = GeneratorFunieGAN().to(self.device)
        self.gan.load_state_dict(torch.load(str(gan_weights_path), map_location=self.device))
        self.gan.eval()
        
        if self.use_fp16:
            self.gan = self.gan.half()
        
        # Load YOLOv8-Nano (loaded once, no repeated loading)
        logger.info(f"Loading YOLOv8-Nano weights from: {yolo_weights_path}")
        self.yolo = YOLO(str(yolo_weights_path))
        
        logger.info("Pipeline initialization complete ✓")
    
    def _validate_frame(self, image: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Frame Validity Gate: Check if frame is valid before processing.
        
        Prevents:
        - Corrupted frames crashing the pipeline
        - Empty frames from stream glitches
        - Decoder failures
        
        Args:
            image: Input image array
            
        Returns:
            Tuple of (is_valid, error_reason)
        """
        if image is None:
            return False, "Image is None"
        
        if not isinstance(image, np.ndarray):
            return False, f"Invalid type: {type(image)}"
        
        if image.size == 0:
            return False, "Empty image (size=0)"
        
        if len(image.shape) < 3:
            return False, f"Invalid dimensions: {image.shape}"
        
        if image.shape[2] != 3:
            return False, f"Invalid channels: {image.shape[2]} (expected 3)"
        
        return True, None
    
    def preprocess_for_gan(self, image: np.ndarray) -> torch.Tensor:
        """
        Preprocess raw image for FUnIE-GAN input.
        
        Transformation:
        1. BGR → RGB (OpenCV → PyTorch convention)
        2. Resize → 256×256 (GAN resolution)
        3. Normalize → [-1, 1] (GAN expectation via Tanh)
        
        Args:
            image: Raw BGR image from OpenCV [0-255]
            
        Returns:
            Tensor ready for GAN inference [B, C, H, W] in range [-1, 1]
        """
        # BGR to RGB
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize to GAN resolution
        img_resized = cv2.resize(img_rgb, (256, 256))
        
        # Normalize to [-1, 1] (matching Tanh activation)
        img_normalized = (img_resized.astype(np.float32) - 127.5) / 127.5
        
        # Convert to tensor [B, C, H, W]
        tensor = torch.from_numpy(img_normalized).permute(2, 0, 1).unsqueeze(0)
        tensor = tensor.to(self.device)
        
        if self.use_fp16:
            tensor = tensor.half()
        
        return tensor
    
    def gan_inference(self, gan_input: torch.Tensor) -> torch.Tensor:
        """
        Run FUnIE-GAN enhancement inference.
        
        Args:
            gan_input: Preprocessed tensor in GAN domain [-1, 1]
            
        Returns:
            Enhanced tensor in GAN domain [-1, 1], resolution 256×256
        """
        with torch.no_grad():
            enhanced_tensor = self.gan(gan_input)
        
        return enhanced_tensor
    
    def preprocess_for_yolo(self, gan_output: torch.Tensor) -> np.ndarray:
        """
        Bridge normalization: Convert GAN output to YOLO input.
        
        This is the critical normalization bridge that prevents:
        - Black frames (wrong range)
        - Color distortion (clamping issues)
        - Detection failures (YOLO expects [0,1])
        
        Transformation:
        1. Range: [-1, 1] → [0, 1] via (x + 1) / 2
        2. Resolution: 256×256 → 640×640 (bilinear interpolation)
        
        Args:
            gan_output: Enhanced tensor from GAN [-1, 1]
            
        Returns:
            Image array ready for YOLO [0-255] uint8
        """
        # Bridge normalization: [-1, 1] → [0, 1]
        yolo_tensor = (gan_output + 1) / 2
        
        # Upscale to YOLO resolution using bilinear interpolation
        yolo_tensor = F.interpolate(
            yolo_tensor, 
            size=(640, 640), 
            mode='bilinear', 
            align_corners=False
        )
        
        # Convert to numpy for YOLO
        yolo_input = yolo_tensor.squeeze(0).permute(1, 2, 0).cpu()
        if self.use_fp16:
            yolo_input = yolo_input.float()
        yolo_input = (yolo_input.numpy() * 255).clip(0, 255).astype(np.uint8)
        
        return yolo_input
    
    def yolo_inference(self, yolo_input: np.ndarray, conf_threshold: float = 0.25) -> List[Dict]:
        """
        Run YOLOv8-Nano detection inference.
        
        Args:
            yolo_input: Image array [0-255] uint8
            conf_threshold: Minimum confidence threshold
            
        Returns:
            List of detection dictionaries with bbox, confidence, label
        """
        results = self.yolo(yolo_input, conf=conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(confidence, 4),
                    "label": "anomaly"  # All detections treated as anomalies
                })
        
        return detections
    
    def classify_confidence(self, detections: List[Dict]) -> Tuple[SystemState, float]:
        """
        Confidence-driven decision framework.
        
        Thresholds (conservative by design):
        - > 0.75: CONFIRMED_THREAT (immediate operator attention)
        - 0.40 - 0.75: POTENTIAL_ANOMALY (manual verification encouraged)
        - < 0.40: SAFE_MODE (poor visibility, no alerts)
        
        Args:
            detections: List of detection results
            
        Returns:
            Tuple of (SystemState, max_confidence)
        """
        if not detections:
            return SystemState.SAFE_MODE, 0.0
        
        max_confidence = max(d["confidence"] for d in detections)
        
        if max_confidence >= self.THRESHOLD_CONFIRMED:
            return SystemState.CONFIRMED_THREAT, max_confidence
        elif max_confidence >= self.THRESHOLD_POTENTIAL:
            return SystemState.POTENTIAL_ANOMALY, max_confidence
        else:
            return SystemState.SAFE_MODE, max_confidence
    
    def get_enhanced_image(self, gan_output: torch.Tensor) -> np.ndarray:
        """
        Extract enhanced image for visualization (GAN domain → display).
        
        This is semantically separate from YOLO input preparation to maintain
        clarity between enhancement output and detection input.
        
        Args:
            gan_output: Enhanced tensor from GAN [-1, 1]
            
        Returns:
            BGR image for OpenCV display/saving [0-255] uint8
        """
        enhanced = gan_output.squeeze(0).permute(1, 2, 0).cpu()
        if self.use_fp16:
            enhanced = enhanced.float()
        enhanced = enhanced.numpy()
        
        # De-normalize: [-1, 1] → [0, 255]
        enhanced = ((enhanced + 1) * 127.5).clip(0, 255).astype(np.uint8)
        
        # RGB → BGR for OpenCV
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)
        
        return enhanced_bgr
    
    def run(
        self, 
        image_path: str = None, 
        image_array: np.ndarray = None,
        conf_threshold: float = 0.25
    ) -> Dict[str, Any]:
        """
        Run the complete perception pipeline.
        
        Standardized output schema for backend integration:
        {
            "timestamp": "ISO 8601 string",
            "state": "POTENTIAL_ANOMALY",
            "max_confidence": 0.63,
            "detections": [
                {
                    "bbox": [x1, y1, x2, y2],
                    "confidence": 0.63,
                    "label": "anomaly"
                }
            ],
            "enhanced_image": np.ndarray,  # Optional, for visualization
            "detection_image": np.ndarray   # Optional, with boxes drawn
        }
        
        Args:
            image_path: Path to input image (optional)
            image_array: Direct BGR image array (optional)
            conf_threshold: Detection confidence threshold
            
        Returns:
            Standardized detection result dictionary
        """
        timestamp = datetime.now().isoformat()
        
        # Load image if path provided
        if image_path is not None:
            image = cv2.imread(str(image_path))
        else:
            image = image_array
        
        # Frame Validity Gate
        is_valid, error_reason = self._validate_frame(image)
        if not is_valid:
            logger.warning(f"Invalid frame: {error_reason}")
            return {
                "timestamp": timestamp,
                "state": SystemState.SAFE_MODE.value,
                "max_confidence": 0.0,
                "detections": [],
                "error": error_reason,
                "enhanced_image": None,
                "detection_image": None
            }
        
        try:
            # Step 1: Preprocess for GAN
            gan_input = self.preprocess_for_gan(image)
            
            # Step 2: GAN Enhancement (Enhancement Output)
            enhanced_tensor = self.gan_inference(gan_input)
            
            # Step 3: Extract enhanced image for visualization
            enhanced_image = self.get_enhanced_image(enhanced_tensor)
            
            # Step 4: Bridge to YOLO domain (Detection Input - semantically separate)
            yolo_input = self.preprocess_for_yolo(enhanced_tensor)
            
            # Step 5: YOLO Detection
            detections = self.yolo_inference(yolo_input, conf_threshold)
            
            # Step 6: Classify confidence
            state, max_conf = self.classify_confidence(detections)
            
            # Step 7: Draw detection boxes on enhanced image
            detection_image = enhanced_image.copy()
            detection_image = cv2.resize(detection_image, (640, 640))
            
            for det in detections:
                x1, y1, x2, y2 = det["bbox"]
                conf = det["confidence"]
                
                # Color based on confidence/state
                if conf >= self.THRESHOLD_CONFIRMED:
                    color = (0, 0, 255)  # Red for confirmed
                elif conf >= self.THRESHOLD_POTENTIAL:
                    color = (0, 165, 255)  # Orange for potential
                else:
                    color = (0, 255, 0)  # Green for low confidence
                
                cv2.rectangle(detection_image, (x1, y1), (x2, y2), color, 2)
                
                label = f"{state.value}: {conf:.2f}"
                cv2.putText(
                    detection_image, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                )
            
            # Add state indicator
            state_color = {
                SystemState.CONFIRMED_THREAT: (0, 0, 255),
                SystemState.POTENTIAL_ANOMALY: (0, 165, 255),
                SystemState.SAFE_MODE: (0, 255, 0)
            }
            cv2.putText(
                detection_image, f"State: {state.value}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color[state], 2
            )
            cv2.putText(
                detection_image, f"Max Conf: {max_conf:.2f}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color[state], 2
            )
            
            return {
                "timestamp": timestamp,
                "state": state.value,
                "max_confidence": round(max_conf, 4),
                "detections": detections,
                "enhanced_image": enhanced_image,
                "detection_image": detection_image
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return {
                "timestamp": timestamp,
                "state": SystemState.SAFE_MODE.value,
                "max_confidence": 0.0,
                "detections": [],
                "error": str(e),
                "enhanced_image": None,
                "detection_image": None
            }
    
    def run_continuous(
        self, 
        image_paths: List[str], 
        output_dir: str = None,
        save_outputs: bool = True
    ) -> Dict[str, Any]:
        """
        Run pipeline on multiple images for stability testing.
        
        Args:
            image_paths: List of image paths to process
            output_dir: Directory to save outputs
            save_outputs: Whether to save output images
            
        Returns:
            Summary statistics
        """
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        results = []
        start_time = datetime.now()
        
        for idx, path in enumerate(image_paths):
            result = self.run(image_path=path)
            results.append({
                "path": path,
                "state": result["state"],
                "max_confidence": result["max_confidence"],
                "detection_count": len(result["detections"])
            })
            
            if save_outputs and output_dir and result["detection_image"] is not None:
                filename = Path(path).stem
                cv2.imwrite(
                    os.path.join(output_dir, f"{filename}_detected.jpg"),
                    result["detection_image"]
                )
            
            if (idx + 1) % 10 == 0:
                logger.info(f"Processed {idx + 1}/{len(image_paths)} images")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        fps = len(image_paths) / elapsed if elapsed > 0 else 0
        
        # Summary statistics
        state_counts = {state.value: 0 for state in SystemState}
        for r in results:
            state_counts[r["state"]] += 1
        
        return {
            "total_images": len(image_paths),
            "elapsed_seconds": round(elapsed, 2),
            "fps": round(fps, 2),
            "state_distribution": state_counts,
            "results": results
        }


# Convenience function for quick testing
def create_pipeline(**kwargs) -> JalDrishtiPipeline:
    """Create a JalDrishtiPipeline with default settings."""
    return JalDrishtiPipeline(**kwargs)
