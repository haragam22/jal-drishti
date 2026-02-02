import time
import base64
import requests
import cv2

URL = "http://127.0.0.1:8001/infer"

if __name__ == '__main__':
    img = cv2.imread('ml-engine/test_images/sample.jpg') if cv2.haveImageReader('ml-engine/test_images/sample.jpg') else None
    if img is None:
        # generate black image
        import numpy as np
        img = np.zeros((480,600,3), dtype=np.uint8)
    _, buf = cv2.imencode('.jpg', img)
    start = time.time()
    files = {'frame': ('frame.jpg', buf.tobytes(), 'image/jpeg')}
    data = {'frame_id': '1', 'timestamp': str(time.time()), 'send_enhanced': '0'}
    try:
        r = requests.post(URL, files=files, data=data, timeout=5.0)
        elapsed = (time.time() - start) * 1000.0
        print('HTTP RTT ms:', elapsed)
        print('Status:', r.status_code)
        print('Response:', r.json())
    except Exception as e:
        print('Error calling ML engine:', e)
