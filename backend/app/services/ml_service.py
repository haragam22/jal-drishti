import random
import base64

class MLService:
    def __init__(self):
        self.frame_count = 0
        # Placeholder base64 image (1x1 pixel black png) to satisfy contract if needed, 
        # or we can use a larger placeholder.
        # This is a small 1x1 black pixel.
        self.placeholder_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        
        # State for moving objects [x, y, dx, dy]
        self.objects = [
            {"x": 100, "y": 100, "vx": 5, "vy": 3, "label": "Suspicious Object"},
            {"x": 300, "y": 200, "vx": -4, "vy": 2, "label": "mine"}
        ]
        self.width = 640
        self.height = 480

    def process_frame(self, binary_frame: bytes) -> dict:
        """
        Simulates processing a video frame.
        Ignores actual binary data.
        Returns a dictionary matching the response schema.
        """
        self.frame_count += 1
        
        # Update object positions
        active_detections = []
        
        # Randomly add/remove objects occasionally
        if random.random() > 0.98 and len(self.objects) < 5:
            self.objects.append({
                "x": random.randint(0, self.width), 
                "y": random.randint(0, self.height), 
                "vx": random.randint(-5, 5), 
                "vy": random.randint(-5, 5),
                "label": random.choice(["Person", "Vehicle", "mine"])
            })
        
        if random.random() > 0.99 and len(self.objects) > 0:
            self.objects.pop(0)

        for obj in self.objects:
            # Move
            obj["x"] += obj["vx"]
            obj["y"] += obj["vy"]
            
            # Bounce
            if obj["x"] < 0 or obj["x"] > self.width - 100: obj["vx"] *= -1
            if obj["y"] < 0 or obj["y"] > self.height - 100: obj["vy"] *= -1
            
            # Create detection
            confidence = random.uniform(0.4, 0.95)
            # Box size roughly 100x100
            bbox = [
                int(obj["x"]), 
                int(obj["y"]), 
                100, 
                100
            ]
            
            active_detections.append({
                "label": obj["label"],
                "confidence": round(confidence, 2),
                "bbox": bbox
            })

        # Simulate visibility
        visibility = 100.0 + random.uniform(-10, 10)

        return {
            "status": "success",
            "frame_id": self.frame_count,
            "image_data": self.placeholder_b64, 
            "detections": active_detections,
            "visibility_score": round(visibility, 1)
        }

ml_service = MLService()
