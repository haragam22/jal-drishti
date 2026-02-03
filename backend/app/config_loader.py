"""
Configuration Loader for Jal-Drishti Phase-3 CORE
Loads config.yaml from root or uses sensible defaults
Falls back to JSON if YAML not available
"""

import json
import os
import sys
from pathlib import Path

# Try to import YAML, fallback to JSON only
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

class ConfigLoader:
    """Load and manage configuration from YAML file"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Load configuration on first initialization"""
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """Load config.yaml or config.json from root directory with fallback defaults"""
        config_paths = [
            "config.yaml",
            "config.json",
            os.path.join(os.path.dirname(__file__), "config.yaml"),
            os.path.join(os.path.dirname(__file__), "config.json"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.yaml"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json"),
        ]
        
        self._config = self._get_defaults()
        
        for path in config_paths:
            if os.path.exists(path):
                try:
                    if path.endswith('.yaml') and HAS_YAML:
                        with open(path, 'r') as f:
                            loaded = yaml.safe_load(f) or {}
                            self._deep_merge(self._config, loaded)
                        print(f"[Config] Loaded from: {os.path.abspath(path)}")
                        return
                    elif path.endswith('.json'):
                        with open(path, 'r') as f:
                            loaded = json.load(f) or {}
                            self._deep_merge(self._config, loaded)
                        print(f"[Config] Loaded from: {os.path.abspath(path)}")
                        return
                except Exception as e:
                    print(f"[Config] Error loading {path}: {e}")
        
        print("[Config] Using default configuration (config.yaml/config.json not found)")
    
    def _deep_merge(self, base, override):
        """Recursively merge override dict into base dict"""
        for key, value in override.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _get_defaults(self):
        """Return default configuration"""
        return {
            "device": {
                "use_gpu": True,
                "gpu_fallback_to_cpu": True,
                "fp16_enabled": True,
            },
            "performance": {
                "target_fps": 12,
                "max_fps": 15,
                "latency_target_ms": 80,
                "frame_queue_size": 5,
                "frame_drop_on_ml_busy": True,
            },
            "video": {
                "source_type": "file",
                "file_path": "backend/dummy.mp4",
                "webcam_id": 0,
                "rtsp_url": "",
                "fallback_to_simulation": True,
            },
            "confidence": {
                "yolo_detection_threshold": 0.40,
                "safe_mode_threshold": 0.30,
                "potential_anomaly_threshold": 0.30,
                "confirmed_threat_threshold": 0.70,
            },
            "smoothing": {
                "enabled": True,
                "window_size": 3,
                "state_persistence_frames": 2,
            },
            "event_logging": {
                "enabled": True,
                "log_non_safe_mode": True,
                "max_events_in_memory": 15,
            },
            "backend": {
                "host": "127.0.0.1",
                "port": 9000,
                "ws_broadcast_interval_ms": 83,
            },
            "ml_service": {
                "debug_mode": True,
                "send_enhanced_on_anomaly": True,
            },
            "ml_engine": {
                "gan_model_path": "ml-engine/weights/funie_generator.pth",
                "yolo_model_path": "ml-engine/weights/yolov8n.pt",
                "inference_timeout_ms": 100,
            },
            "logging": {
                "level": "INFO",
                "log_frame_drops": True,
                "log_device_info": True,
                "log_latency": True,
            },
            "features": {
                "live_video_support": True,
                "error_recovery": True,
                "architecture_frozen": False,
            },
        }
    
    def get(self, key_path, default=None):
        """
        Get config value using dot notation
        Example: config.get("device.use_gpu")
        """
        keys = key_path.split(".")
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_section(self, section):
        """Get entire config section"""
        return self._config.get(section, {})
    
    def get_all(self):
        """Get entire configuration"""
        return self._config
    
    def validate(self):
        """Validate configuration consistency"""
        errors = []
        
        # Validate thresholds
        cfg = self._config.get("confidence", {})
        if cfg.get("safe_mode_threshold", 0) > cfg.get("confirmed_threat_threshold", 1):
            errors.append("Confidence threshold ordering invalid")
        
        # Validate FPS
        perf = self._config.get("performance", {})
        if perf.get("target_fps", 0) > perf.get("max_fps", 100):
            errors.append("target_fps cannot exceed max_fps")
        
        if errors:
            print("[Config] Validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def print_summary(self):
        """Print configuration summary for debugging"""
        print("\n[Config] Configuration Summary:")
        print(f"  Device: GPU={self._config['device']['use_gpu']}, FP16={self._config['device']['fp16_enabled']}")
        print(f"  Performance: Target FPS={self._config['performance']['target_fps']}, Latency Target={self._config['performance']['latency_target_ms']}ms")
        print(f"  Video Source: {self._config['video']['source_type']}")
        print(f"  Confidence Thresholds: Safe={self._config['confidence']['safe_mode_threshold']}, Potential={self._config['confidence']['potential_anomaly_threshold']}, Threat={self._config['confidence']['confirmed_threat_threshold']}")
        print()

# Singleton instance
config = ConfigLoader()
