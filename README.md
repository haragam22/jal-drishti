
# Jal-Drishti 

**Advanced Real-Time AI Surveillance Dashboard for Defense**

##  Overview

**Jal-Drishti** is a cutting-edge real-time surveillance system designed for underwater and high-stakes defense environments. It combines state-of-the-art computer vision models with a robust, low-latency dashboard to provide actionable intelligence.

The system features a **Dual-Mode Architecture** separating the core application logic (Backend) from the heavy AI computation (ML Engine), ensuring stability and responsiveness even under heavy load.

## Key Features

- **🔴 Safe Mode Monitoring**: Real-time threat assessment with visual "Safe Mode" / "Threat" indicators.
- **📷 Information Enhancement**: Uses **FUnIE-GAN** to clear up underwater/low-visibility footage in real-time.
- **🎯 Precise Detection**: **YOLOv8** integration for high-accuracy object detection.
- **📱 Multi-Source Support**:
  - Live Webcam
  - Video Files (Simulation)
  - RTSP Streams
  - **Phone Camera Streaming** (continuously integrated)
- **⚡ High Performance**:
  - Decoupled ML Engine (GPU-optimized).
  - WebSockets for real-time telemetry (<80ms latency targets).
  - Graceful frame dropping and error recovery.
- **🖥️ Defense-Grade Dashboard**: Dark-themed, high-contrast UI designed for long-duration monitoring with System Uptime, FPS, and Latency trackers.

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 (Vite)
- **Styling**: Custom Defense-Grade CSS
- **Communication**: WebSocket (Native)

### Backend (Control Plane)
- **Framework**: FastAPI (Python)
- **Role**: WebSocket broadcaster, Frame Scheduler, System State Manager.
- **Concurrency**: AsyncIO

### ML Engine (Compute Plane)
- **Framework**: FastAPI (Python)
- **ML Libraries**: PyTorch, OpenCV, NumPy
- **Models**: YOLOv8 (Detection), FUnIE-GAN (Enhancement)
- **Hardware**: GPU (CUDA) preferred, CPU fallback available.

## 📂 Project Structure

```
jal-drishti/
├── backend/            # Application Logic & WebSocket Server
├── frontend/           # React-based Dashboard
├── ml-engine/          # Independent AI Service (YOLO + GAN)
├── data/               # Datasets and logs
├── config.yaml         # Centralized System Configuration
└── README.md           # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- [Optional] NVidia GPU with CUDA for ML acceleration.

### 1. Start the ML Engine
The ML Engine handles all heavy AI inference.
```bash
cd ml-engine
# Create and activate virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
python service.py
```
*Port: 8001*

### 2. Start the Backend
The Backend coordinates streams and connects to the Frontend.
```bash
cd backend
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 9000
```
*Port: 9000*

### 3. Start the Frontend
The Dashboard UI.
```bash
cd frontend
npm install
npm run dev
```
*Access at: http://localhost:5173*

## ⚙️ Configuration

The system is highly configurable via `config.yaml` in the root directory. Key settings include:

- **`device`**: Toggle `use_gpu` and `fp16_enabled`.
- **`video`**: Switch `source_type` (file/webcam/rtsp).
- **`performance`**: Adjust `target_fps` and `latency_target_ms`.
- **`confidence`**: Tune YOLO and Safe Mode thresholds.

## 🧠 ML Engine

The core of Jal-Drishti is a sophisticated Machine Learning pipeline designed to overcome the optical challenges of underwater vision (color absorption, haze, and low contrast).

### 1. The Dual-Stream Hybrid Pipeline
Instead of relying on a single data source, the system processes two parallel streams for every frame:
1.  **Stream A (Raw Sensor)**: Direct feed from the camera. Best for detecting **Divers** and objects in clear water where texture preservation is key.
2.  **Stream B (AI-Enhanced)**: Processed through a Generative Adversarial Network (GAN) to restore color and remove haze. Best for detecting **Mines** and camouflaged threats.

Both streams are batched together for inference, ensuring **real-time performance (Batch Inference)** without doubling the latency.

### 2. Image Enhancement (FUnIE-GAN + CLAHE)
The enhancement module transforms degraded underwater frames into clear, detector-friendly images:
*   **FUnIE-GAN**: A Fast Underwater Image Enhancement GAN that corrects color balance (restoring red channels) and removes haze.
*   **CLAHE**: Contrast Limited Adaptive Histogram Equalization is applied post-GAN to recover local texture details that might be smoothed out by the generator.

### 3. Object Detection (YOLOv8-Nano)
We use a custom-trained **YOLOv8-Nano** model for high-speed detection.
*   **Classes**:
    *   `0`: Mine (Naval Mines)
    *   `1`: Diver (Human presence)
    *   `2`: Drone (ROVs/AUVs)
    *   `3`: Submarine (Manned submersibles)
*   **Performance**: Optimized with **FP16 (Half-Precision)** inference on CUDA devices.

### 4. Intelligent Logic Layers
The system doesn't just trust the model blindly. It employs "Gatekeeper" logic to minimize false positives:

#### A. Class-Specific Thresholds
Different threats carry different risks. We apply strict confidence cutoffs:
*   **Diver (> 55%)**: High threshold to prevent "Ghost Divers" (fish misclassified as humans).
*   **Mine / Submarine (> 40%)**: Balanced sensitivity.
*   **Drone (> 15%)**: Lower threshold to catch small, faint signatures of distant ROVs.

#### B. Smart NMS (Diver Priority)
Standard Non-Maximum Suppression (NMS) creates conflicts. Our **Smart NMS** resolves them semantically:
*   **The Rule**: If a *Diver* and a *Submarine* are detected in the same location (High IoU), the system **prioritizes the Diver** and removes the Submarine detection.
*   **Reasoning**: Large ROVs or background noise often look like subs, but detecting a human is critical safety info.

### 5. System States
The engine determines the overall threat level based on detection confidence:
*   🔴 **CONFIRMED THREAT**: High confidence detection.
*   🟡 **POTENTIAL ANOMALY**: Moderate confidence detection.
*   🟢 **SAFE MODE**: No significant anomalies detected.

---

## 📱 Mobile Camera Integration

To use your phone as a camera source:
1. Ensure your phone and PC are on the same network.
2. Navigate to the Mobile Stream page (URL displayed in dashboard or `http://<YOUR_PC_IP>:9000/mobile`).
3. Update `config.yaml` or environment variables to accept external streams.

## 🤝 Contributing

1. Fork the repository
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
**Jal-Drishti**: Seeing the unseen.
