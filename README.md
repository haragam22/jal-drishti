# Jal-Drishti: Underwater Anomaly Detection System

**Jal-Drishti** is an advanced AI-powered underwater surveillance system designed to detect anomalies (Mines, Divers, Drones, Submarines) in real-time. It leverages a **Dual-Stream Hybrid Pipeline** that fuses raw optical data with GAN-enhanced imagery to ensure high accuracy even in turbid, low-visibility underwater environments.

---

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
