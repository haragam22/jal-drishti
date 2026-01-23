export const MOCK_Response = {
    "status": "success",
    "frame_id": 12,
    "image_data": "https://i.pinimg.com/1200x/9a/ad/96/9aad968fc365b527f4d12d1a9ff04304.jpg", // Using placeholder for now as requested format was /sample_enhanced.jpg but that file likely doesn't exist.
    "detections": [
        {
            "label": "Suspicious Object",
            "confidence": 0.78,
            "bbox": [120, 80, 300, 260]
        },
        {
            "label": "Suspicious Object",
            "confidence": 0.45,
            "bbox": [360, 140, 480, 300]
        }
    ],
    "visibility_score": 134.2
};
