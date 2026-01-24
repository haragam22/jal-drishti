# Jal-Drishti ML Engine: The Simple Guide

**Version**: 1.1  
**Last Updated**: January 2026  
**Repository**: [Jal-Drishti on GitHub](https://github.com/your-repo/Jal-Drishti)

This guide explains how to **setup, run, and test** the Jal-Drishti ML Engine in the simplest way possible.

---

## ⚡ Quick Start Checklist

1. **Install Python 3.9 or 3.10**
2. **Setup Environment**: `cd ml-engine` → `python -m venv venv` → `activate`
3. **Install Deps**: `pip install torch torchvision torchaudio opencv-python numpy ultralytics matplotlib`
4. **Get Data**: Download EUVP from Kaggle → Extract to `data/` folder
5. **Run**: Execute the scripts for each part

---

## 📂 Project Structure (What goes where)

```
ml-engine/
├── data/                       # 1. DATASET
│   ├── enhancement/
│   │   ├── raw/                # extract 'trainA' here
│   │   └── paired/             # extract 'trainB' here
│   └── detection/
│       └── backgrounds/        # extract 'trainA' (again) here
│
├── enhancement/                # 2. ENHANCE
│   └── run_funie.py            # Script to enhance images
│
├── detection/                  # 3. DETECT
│   └── run_yolo.py             # Script to detect anomalies
│
└── pipeline/                   # 4. & 5. UNIFIED PIPE
    ├── test_pipeline.py        # Run the full system
    ├── framevalidity.py        # Test safety checks
    └── performbench.py         # Check speed
```

---

## 🛠️ Step-by-Step Execution

### Part 1: Dataset Setup (The Foundation)

**Goal**: Get the underwater images ready.

1.  **Download**: [EUVP Dataset from Kaggle](https://www.kaggle.com/datasets/pamuduranasinghe/euvp-dataset?resource=download) (Download ZIP)
2.  **Extract**: Unzip the folder.
3.  **Copy Files**:
    *   Copy images from `EUVP/Paired/underwater_scenes/trainA/` ➔ `ml-engine/data/enhancement/raw/`
    *   Copy images from `EUVP/Paired/underwater_scenes/trainB/` ➔ `ml-engine/data/enhancement/paired/`
    *   Copy images from `EUVP/underwater_scenes/trainA/` ➔ `ml-engine/data/detection/backgrounds/`

*That's it! No code to run for Part 1.*

---

### Part 2: Image Enhancement (FUnIE-GAN)

**Goal**: Turn "green/hazy" images into "clear/balanced" images.

1.  **Navigate**: `cd ml-engine/enhancement`
2.  **Run**:
    ```bash
    python run_funie.py
    ```
3.  **Result**: Check `ml-engine/enhancement/outputs/` to see the clear images.

---

### Part 3: Anomaly Detection (YOLOv8)

**Goal**: Find objects in the water.

1.  **Navigate**: `cd ml-engine/detection`
2.  **Run**:
    ```bash
    python run_yolo.py
    ```
    
    > **✨ AUTOMATIC SETUP**: 
    > When you run this command, the system will **automatically download** or create the necessary YOLO model weights (`yolov8n.pt` or configured weight file) if they are missing. You do NOT need to manually download model files.

3.  **Result**: Check `ml-engine/detection/yolo/outputs/` to see images with green bounding boxes.

---

### Part 4: Unified Pipeline (Connecting 2 & 3)

**Goal**: Process a single raw image through both steps (Enhance → Detect) seamlessly.

1.  **Navigate**: `cd ml-engine`
2.  **Run**:
    ```bash
    python pipeline/test_pipeline.py
    ```
3.  **Result**: 
    *   Console shows detection details (Confidences, Boxes).
    *   Check `ml-engine/outputs/pipeline/` for the final images.

---

### Part 5: Real-Time Safety & Benchmarks

**Goal**: Verify the system is fast and safe for deployment.

#### 1. Frame Validity Check
Tests if the system safely handles bad input (empty frames, glitches).
```bash
python pipeline/framevalidity.py
```
*Expected: "🎉 All frame validity tests passed!"*

#### 2. Performance Benchmark
Tests how many Frames Per Second (FPS) the system runs at.
```bash
python pipeline/performbench.py
```
*Expected: ~10 FPS (CPU) or ~20+ FPS (GPU)*

---

## 🛑 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install <missing-module>` (e.g., `pip install opencv-python`) |
| `FileNotFoundError` (Dataset) | You forgot **Part 1**! Download and put the images in `data/` folder. |
| `FileNotFoundError` (Model) | **Part 2**: Ensure `funie_generator.pth` is in `enhancement/funie_gan/weights/`.<br>**Part 3**: Just run the script again, it usually auto-downloads. |
| Black Images | Likely a normalization issue. Ensure you didn't change the pipeline code logic. |
| Slow Speed | You are likely on CPU. This is normal. A GPU makes it 10x faster. |

---

## 📝 Simple Documentation of Logic

*   **Logic**: Raw Image ➔ **GAN** (Enhance) ➔ **Bridge** (Adjust pixel values) ➔ **YOLO** (Detect) ➔ **Safety Check** (Decide if threat).
*   **Safety**:
    *   **High Confidence (>75%)**: 🔴 Threat
    *   **Medium (40-75%)**: 🟠 Potential Anomaly
    *   **Low (<40%)**: 🟢 Sage Mode / Poor Visibility
*   **Why use this?**: It makes sure we only alert when the AI is sure, and we handle murky water better than standard cameras.

---

*Verified for Jal-Drishti v1.0*
