**STEP-BY-STEP GUIDE TO BUILD ML PART** 

# **PART 1: DATA ACQUISITION AND PREPARATION**

**Step-by-Step Detailed Execution Plan**

---

## **1\. Purpose of Part 1**

The purpose of Part 1 is to establish a **clean, reproducible, and engineering-correct data foundation** for the Jal-Drishti system.

This stage does **not involve model training, inference, or backend integration**.  
It strictly focuses on:

* Correct dataset selection  
* Logical data separation  
* Proper folder structuring  
* Dataset validation  
* Documentation of assumptions and limitations

A mistake at this stage propagates errors into all later stages; therefore, Part 1 is treated as a **system design task**, not a preprocessing step.

---

## **2\. High-Level Conceptual Flow of Part 1**

Public Underwater Dataset  
        ↓  
Dataset Selection & Filtering  
        ↓  
Logical Separation (Enhancement vs Detection)  
        ↓  
Project-Aligned Folder Structure  
        ↓  
Visual & Structural Validation  
        ↓  
Dataset Strategy Documentation

Only after this flow is complete does the project move to model work.

---

## **3\. Project Root Context**

The Jal-Drishti repository is structured as a **multi-service system**:

JAL-DRISHTI/  
 ├── backend/  
 ├── frontend/  
 ├── ml-engine/  
 └── docs/

All Part-1 activities are **strictly confined to the `ml-engine` directory**.  
No changes are made to backend or frontend during Part-1.

---

## **4\. Folder Structure Required for Part 1**

### **4.1 Base Structure inside `ml-engine`**

The following folder hierarchy must exist before data is added:

ml-engine/  
 ├── data/  
 │   ├── enhancement/  
 │   │   ├── raw/  
 │   │   └── paired/  
 │   └── detection/  
 │       ├── backgrounds/  
 │       └── notes/  
 ├── docs/  
 │   └── part1\_dataset\_strategy.md  
 ├── venv/  
 ├── README.md

### **4.2 Purpose of Each Folder**

| Folder | Purpose |
| ----- | ----- |
| `data/enhancement/raw/` | Stores raw degraded underwater images |
| `data/enhancement/paired/` | Stores target enhanced images (paired with raw) |
| `data/detection/backgrounds/` | Stores natural underwater scenes for detection context |
| `data/detection/notes/` | Stores dataset assumptions or notes |
| `docs/` | Stores documentation files |
| `venv/` | Python virtual environment |

---

## **5\. Dataset Selection**

### **5.1 Selected Dataset**

**EUVP – Enhancement of Underwater Visual Perception Dataset**

Source: Kaggle (publicly available)

The dataset is selected because it:

* Contains real underwater imagery  
* Includes paired degraded and enhanced images  
* Is widely used in underwater vision research  
* Supports reproducibility and documentation

---

## **6\. Dataset Download Procedure**

### **6.1 Download Method**

* The dataset is downloaded **as a ZIP file** from Kaggle  
* Notebook-based imports (KaggleHub, Colab) are intentionally avoided

**Reason**:  
Local file system access is required for:

* Custom pipelines  
* Offline validation  
* Later real-time integration

---

### **6.2 Extracted Dataset Structure (Original)**

After extraction, the dataset appears as:

EUVP/  
 ├── Paired/  
 │   ├── underwater\_scenes/  
 │   │   ├── trainA/  
 │   │   ├── trainB/  
 │   │   └── validation/  
 ├── underwater\_imagenet/  
 ├── Unpaired/  
 ├── test\_samples/  
 └── eval\_data/

---

## **7\. Dataset Filtering for Jal-Drishti**

Only a **specific subset** of EUVP is used in Part-1.

### **7.1 Enhancement Dataset Selection**

**Source Path**:

EUVP/Paired/underwater\_scenes/

| Subfolder | Meaning |
| ----- | ----- |
| `trainA` | Raw degraded underwater images |
| `trainB` | Corresponding enhanced images |

These folders form a **paired dataset**, which is essential for supervised GAN-based enhancement.

---

### **7.2 Detection Background Dataset Selection**

**Source Path**:

EUVP/underwater\_scenes/trainA

These images represent:

* Natural underwater environments  
* No explicit objects of interest  
* Baseline visual context

They are used to understand background appearance and later anomaly contrast.

---

## **8\. Data Copy and Placement (Critical Step)**

### **8.1 Copy for Enhancement (Raw Images)**

**From**:

EUVP/Paired/underwater\_scenes/trainA/

**To**:

ml-engine/data/enhancement/raw/

---

### **8.2 Copy for Enhancement (Paired Targets)**

**From**:

EUVP/Paired/underwater\_scenes/trainB/

**To**:

ml-engine/data/enhancement/paired/

**Important Constraint**:

* Filenames in `raw/` and `paired/` must match exactly  
* This ensures one-to-one image correspondence

---

### **8.3 Copy for Detection Backgrounds**

**From**:

EUVP/underwater\_scenes/trainA/

**To**:h

ml-engine/data/detection/backgrounds/

No labels are created at this stage.

---

## **9\. Data Validation and Sanity Checks**

### **9.1 Visual Validation**

Randomly inspect images from:

* `enhancement/raw/`  
* `enhancement/paired/`

Confirm:

* Raw images show green/blue color cast  
* Paired images show improved color balance  
* Visibility and contrast differences are clear

---

### **9.2 Structural Validation**

Ensure:

* No images are duplicated across enhancement and detection folders  
* No labels or annotations exist  
* File formats are consistent (JPG/PNG)

---

## **10\. Conceptual Separation Enforced in Part 1**

### **10.1 Enhancement vs Detection Data**

| Enhancement Data | Detection Data |
| ----- | ----- |
| Paired images | Unlabeled backgrounds |
| Used by GAN | Used by detector |
| Pixel-level learning | Context understanding |

This separation prevents:

* Data leakage  
* Training bias  
* Overfitting assumptions

---

## **11\. Documentation Requirement**

### **11.1 Required Document**

Create the following file:

ml-engine/docs/part1\_dataset\_strategy.md

### **11.2 Mandatory Content**

The document must clearly explain:

1. Why EUVP dataset was selected  
2. Why paired underwater scenes were used  
3. Why enhancement precedes detection  
4. Why anomaly detection is used instead of weapon classification  
5. Dataset limitations and assumptions

This document is essential for:

* Technical reviews  
* Jury evaluation  
* Ethical justification

---

## **12\. Explicit Non-Goals of Part 1**

During Part-1, the following actions are **strictly prohibited**:

* Training any ML model  
* Writing GAN or YOLO code  
* Creating labels or bounding boxes  
* Modifying backend or frontend code  
* Measuring accuracy or performance

---

## **13\. Completion Criteria for Part 1**

Part 1 is considered complete when:

* All required folders exist and are populated correctly  
* Dataset subsets are copied to their designated locations  
* Visual differences between raw and paired images are verified  
* No code execution has occurred  
* The dataset strategy document is written

---

## **14\. Output of Part 1**

At the end of Part 1, the system has:

* A clean, reproducible dataset layout  
* A clear enhancement-first design philosophy  
* Proper separation between enhancement and detection data  
* A documented dataset strategy  
* A stable foundation for Part-2

---

# **PART 2: UNDERWATER IMAGE ENHANCEMENT**

**Step-by-Step Detailed Execution Plan using FUnIE-GAN**

---

## **1\. Objective of Part 2**

**The objective of Part 2 is to implement and validate the underwater image enhancement module of Jal-Drishti using a pretrained FUnIE-GAN generator.**

**This part ensures that:**

* **Raw underwater images are transformed into visually enhanced images**  
* **Enhancement works independently of detection and backend systems**  
* **The enhancement module is stable, reproducible, and testable**  
* **The output images are suitable for downstream detection**

**No real-time streaming or detection is involved in this stage.**

---

## **2\. Scope and Non-Scope of Part 2**

### **2.1 What Part 2 Includes**

* **Setting up a Python virtual environment for ML**  
* **Integrating pretrained FUnIE-GAN (PyTorch)**  
* **Running enhancement on sample underwater images**  
* **Saving and validating enhanced outputs**

### **2.2 What Part 2 Explicitly Excludes**

* **YOLO or any detection logic**  
* **FastAPI or backend integration**  
* **Model training or fine-tuning**  
* **Performance benchmarking**

---

## **3\. GitHub Repository Used**

**FUnIE-GAN Official Repository**  
**GitHub Link:**  
[**https://github.com/xahidbuffon/FUnIE-GAN**](https://github.com/xahidbuffon/FUnIE-GAN)

**This repository contains multiple implementations. Only one is relevant.**

---

## **4\. Critical Implementation Decision**

### **4.1 PyTorch vs TensorFlow**

**The repository contains:**

* **`TF-Keras/` → TensorFlow implementation (.h5 models)**  
* **`PyTorch/` → PyTorch implementation (.pth model)**

**Jal-Drishti uses PyTorch across the entire ML stack, therefore:**

**Only the PyTorch implementation is used.**  
**All TensorFlow / Keras files are ignored.**

---

## **5\. Python Environment Setup (Mandatory)**

### **5.1 Python Version Requirement**

* **Required Python version: 3.9 or 3.10**  
* **Python 3.13 is not supported by PyTorch and must not be used**

---

### **5.2 Virtual Environment Location**

**The virtual environment must be created inside `ml-engine/`.**

#### **Reason:**

* **ML dependencies are isolated from backend/frontend**  
* **Prevents version conflicts**  
* **Ensures reproducibility**

---

### **5.3 Creating the Virtual Environment**

**From project root:**

**cd ml-engine**  
**python3.10 \-m venv venv**

**Activate:**

**Windows**

**venv\\Scripts\\activate**

**Linux / macOS**

**source venv/bin/activate**

**All subsequent commands are executed with this environment activated.**

---

### **5.4 Installing Required Dependencies**

**pip install torch torchvision torchaudio**  
**pip install opencv-python numpy pillow matplotlib**

**Optional GPU verification:**

**python \-c "import torch; print(torch.cuda.is\_available())"**

---

## **6\. Required Folder Structure for Part 2**

**The following structure must exist inside `ml-engine/`:**

**ml-engine/**  
 **├── enhancement/**  
 **│   ├── funie\_gan/**  
 **│   │   ├── nets/**  
 **│   │   ├── utils/**  
 **│   │   └── weights/**  
 **│   ├── test\_images/**  
 **│   ├── outputs/**  
 **│   └── run\_funie.py**  
 **├── data/**  
 **│   └── enhancement/**  
 **│       └── raw/**  
 **├── docs/**  
 **│   └── part2\_image\_enhancement.md**  
 **├── venv/**  
 **└── README.md**

---

## **7\. Files to Copy from FUnIE-GAN Repository**

**Navigate to the cloned or downloaded repository:**

**FUnIE-GAN/**  
 **└── PyTorch/**

**Only the following files and folders are required.**

---

### **7.1 Generator Network Code**

**Source**

**FUnIE-GAN/PyTorch/nets/**

**Destination**

**ml-engine/enhancement/funie\_gan/nets/**

**This folder contains:**

* **Generator architecture**  
* **Supporting layers**

---

### **7.2 Utility Functions**

**Source**

**FUnIE-GAN/PyTorch/utils/**

**Destination**

**ml-engine/enhancement/funie\_gan/utils/**

**This folder handles:**

* **Image loading**  
* **Tensor transformations**  
* **Utility operations**

---

### **7.3 Pretrained Generator Weights**

**Source**

**FUnIE-GAN/PyTorch/models/funie\_generator.pth**

**Destination**

**ml-engine/enhancement/funie\_gan/weights/funie\_generator.pth**

**This is the pretrained FUnIE-GAN generator model.**

---

### **7.4 Files That Must NOT Be Copied**

**The following files are intentionally excluded:**

* **`TF-Keras/` (TensorFlow implementation)**  
* **`train_funiegan.py`**  
* **`train_ugan.py`**  
* **Discriminator models**  
* **Evaluation scripts**

**Reason:**  
**Training and evaluation are outside the scope of Part 2\.**

---

## **8\. Preparing Test Images**

### **8.1 Selecting a Test Image**

**Copy one raw underwater image from:**

**ml-engine/data/enhancement/raw/**

**Paste it into:**

**ml-engine/enhancement/test\_images/**

**Example:**

**raw\_test.jpg**

**Only one image is used for validation to ensure clarity.**

---

## **9\. Enhancement Execution Script**

### **9.1 Script Location**

**Create the following file:**

**ml-engine/enhancement/run\_funie.py**

---

### **9.2 Script Responsibilities**

**The script performs the following steps:**

1. **Load raw underwater image**  
2. **Convert color space (BGR → RGB)**  
3. **Resize image to `256 × 256`**  
4. **Normalize pixel values to `[-1, 1]`**  
5. **Load pretrained FUnIE-GAN generator**  
6. **Perform inference**  
7. **De-normalize output to `[0, 255]`**  
8. **Save enhanced image to disk**

---

### **9.3 Reference Execution Logic (Conceptual)**

**Raw Image \[0–255\]**  
        **↓**  
**Resize (256×256)**  
        **↓**  
**Normalize → \[-1, 1\]**  
        **↓**  
**FUnIE-GAN Generator**  
        **↓**  
**Output \[-1, 1\]**  
        **↓**  
**De-normalize → \[0–255\]**  
        **↓**  
**Enhanced Image**

---

## **10\. Running the Enhancement Test**

**From terminal:**

**cd ml-engine/enhancement**  
**python run\_funie.py**

---

## **11\. Output Verification**

**The enhanced image must appear in:**

**ml-engine/enhancement/outputs/**

**Example:**

**enhanced\_test.jpg**

### **11.1 Visual Validation Criteria**

**The enhanced image should show:**

* **Reduced green/blue color dominance**  
* **Improved contrast**  
* **Better object visibility**  
* **No black frames or artifacts**

**Exact color accuracy is not required at this stage.**

---

## **12\. Common Errors and Their Causes**

| Issue | Likely Cause |
| ----- | ----- |
| **Black output image** | **Incorrect normalization** |
| **Strange colors** | **BGR/RGB mismatch** |
| **Model load failure** | **Wrong Python version** |
| **CUDA error** | **GPU unsupported (run on CPU)** |

---

## **13\. Documentation Requirement**

**Create the following file:**

**ml-engine/docs/part2\_image\_enhancement.md**

**This document must explain:**

* **Why FUnIE-GAN was selected**  
* **Why pretrained weights were used**  
* **Enhancement input/output flow**  
* **Visual examples (before vs after)**  
* **Limitations of enhancement**

---

## **14\. Completion Criteria for Part 2**

**Part 2 is considered complete when:**

* **FUnIE-GAN generator loads successfully**  
* **At least one underwater image is enhanced**  
* **Output image is visually improved**  
* **No detection or backend code is involved**  
* **Documentation for Part 2 is written**

---

## **15\. Output of Part 2**

**At the end of Part 2, Jal-Drishti has:**

* **A working underwater image enhancement module**  
* **A validated preprocessing stage for detection**  
* **A clean, modular ML architecture**  
* **A reproducible enhancement pipeline**

---

## **TEST SCRIPT (run\_funie.py)**

**`ml-engine/enhancement/run_funie.py`**

### **🧠 Ye script kya karega**

* **Image load**

* **Resize → 256×256**

* **Normalize → \[-1,1\]**

* **Generator run**

* **De-normalize**

* **Output save**

---

### **✅ MINIMAL WORKING TEST CODE**

**`import torch`**  
**`import cv2`**  
**`import numpy as np`**  
**`from nets.funiegan import GeneratorFunieGAN`**

**`# ---------- CONFIG ----------`**  
**`IMAGE_PATH = "test_images/raw_test.jpg"`**  
**`WEIGHTS_PATH = "funie_gan/weights/funie_generator.pth"`**  
**`OUTPUT_PATH = "outputs/enhanced_test.jpg"`**  
**`DEVICE = "cuda" if torch.cuda.is_available() else "cpu"`**  
**`# ----------------------------`**

**`# Load image`**  
**`img = cv2.imread(IMAGE_PATH)`**  
**`img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)`**  
**`img = cv2.resize(img, (256, 256))`**

**`# Normalize to [-1,1]`**  
**`img = (img.astype(np.float32) - 127.5) / 127.5`**  
**`img = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(DEVICE)`**

**`# Load model`**  
**`model = GeneratorFunieGAN().to(DEVICE)`**  
**`model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=DEVICE))`**  
**`model.eval()`**

**`# Inference`**  
**`with torch.no_grad():`**  
    **`out = model(img)`**

**`# De-normalize`**  
**`out = out.squeeze(0).permute(1, 2, 0).cpu().numpy()`**  
**`out = ((out + 1) * 127.5).clip(0, 255).astype(np.uint8)`**

**`# Save output`**  
**`out = cv2.cvtColor(out, cv2.COLOR_RGB2BGR)`**  
**`cv2.imwrite(OUTPUT_PATH, out)`**

**`print("✅ Enhancement done. Saved to:", OUTPUT_PATH)`**

---

## **STEP 5: RUN TEST**

**Terminal:**

**`cd ml-engine/enhancement`**  
**`python run_funie.py`**

---

## **STEP 6: VERIFY OUTPUT**

**Open:**

**`ml-engine/enhancement/outputs/enhanced_test.jpg`**

### **Check:**

* **green tint kam?**

* **contrast better?**

* **visibility improved?**

**👉 Agar YES → PART-2 PRACTICAL DONE 🎯**

# **PART 3: OBJECT / ANOMALY DETECTION**

**Step-by-Step Detailed Execution Plan using YOLOv8-Nano**

---

## **1\. Position of Part 3 in the Overall Execution Flow**

**At this stage of the project:**

* **Part-1 is complete**  
  **Dataset is selected, structured, validated, and documented.**  
* **Part-2 is complete**  
  **Underwater image enhancement using FUnIE-GAN is implemented and validated.**  
  **Raw underwater images can now be converted into enhanced images.**

**Part-3 builds directly on Part-2.**

**In Part-3, the system learns to *perceive objects or anomalies***  
**only on enhanced images, never on raw underwater frames.**

---

## **2\. Objective of Part 3**

**The objective of Part-3 is to integrate and validate a real-time object/anomaly detection model that can:**

* **Take an enhanced underwater image as input**  
* **Detect visually salient or suspicious objects**  
* **Output:**  
  * **Bounding boxes**  
  * **Confidence scores**  
* **Operate independently of backend, streaming, or real-time deployment**

**This stage validates the detection capability in isolation, before pipeline integration.**

---

## **3\. Problem Framing Used in Part 3**

### **3.1 What the System Does**

* **Detects visual anomalies or man-made objects**  
* **Provides confidence-scored localization**  
* **Acts as a decision-support component**

### **3.2 What the System Explicitly Does NOT Do**

* **It does not classify underwater mines**  
* **It does not make autonomous decisions**  
* **It does not guarantee object identity**

**This framing is intentional and necessary due to:**

* **Lack of public military datasets**  
* **Ethical and legal constraints**  
* **Real-world defense AI practices**

---

## **4\. Selection of Detection Model**

### **4.1 Why YOLO-Based Detection**

**YOLO (You Only Look Once) models are selected because they:**

* **Perform detection in a single forward pass**  
* **Are suitable for real-time inference**  
* **Are widely used in safety-critical perception systems**

---

### **4.2 Why YOLOv8-Nano Specifically**

**YOLOv8-Nano is chosen because it provides:**

* **Very low latency**  
* **Small model size**  
* **Low GPU memory usage**  
* **Anchor-free detection (better generalization)**

**This makes it suitable for:**

* **Cloud GPU deployment**  
* **Future edge deployment**  
* **Real-time maritime surveillance scenarios**

---

## **5\. Dependency and Environment Requirements**

### **5.1 Python Environment**

* **Python version: 3.9 or 3.10**  
* **Same virtual environment created in Part-2**  
* **No separate venv is created**

**Reason:**  
**FUnIE-GAN and YOLO must eventually run in the same runtime environment.**

---

### **5.2 Required Library**

**YOLOv8 is provided by the Ultralytics package.**

**Installation (with venv activated inside `ml-engine`):**

**pip install ultralytics**

**Verification:**

**yolo \--version**

**If a version is printed, installation is successful.**

---

## **6\. Folder Structure for Part 3**

**The following structure must be created inside `ml-engine/`:**

**ml-engine/**  
 **├── detection/**  
 **│   ├── yolo/**  
 **│   │   ├── weights/**  
 **│   │   └── outputs/**  
 **│   ├── test\_images/**  
 **│   └── run\_yolo.py**  
 **├── enhancement/**  
 **│   └── outputs/**  
 **├── docs/**  
 **│   └── part3\_detection.md**  
 **├── venv/**  
 **└── README.md**

---

## **7\. YOLOv8-Nano Model Acquisition**

### **7.1 Pretrained Weights**

**YOLOv8-Nano pretrained weights are named:**

**yolov8n.pt**

**There are two valid ways to obtain the weights:**

#### **Option 1 (Recommended)**

**Let Ultralytics automatically download the weights on first run.**

#### **Option 2 (Manual)**

**Place the weights manually in:**

**ml-engine/detection/yolo/weights/yolov8n.pt**

**Both approaches are acceptable.**

---

## **8\. Preparing Input for Detection**

### **8.1 Input Source**

**Detection input must come from Part-2 output only.**

**Copy one enhanced image from:**

**ml-engine/enhancement/outputs/**

**Paste it into:**

**ml-engine/detection/test\_images/**

**Example file:**

**enhanced\_test.jpg**

**Raw underwater images must not be used in Part-3.**

---

## **9\. Detection Execution Script**

### **9.1 Script Location**

**Create the following file:**

**ml-engine/detection/run\_yolo.py**

---

### **9.2 Responsibilities of the Script**

**The script performs the following actions:**

1. **Load YOLOv8-Nano model**  
2. **Load enhanced image**  
3. **Run inference with a confidence threshold**  
4. **Extract bounding boxes and confidence scores**  
5. **Draw detections on the image**  
6. **Save the output image to disk**

---

### **9.3 Minimal Functional Testing Script**

**from ultralytics import YOLO**  
**import cv2**  
**import os**

**\# Configuration**  
**IMAGE\_PATH \= "test\_images/enhanced\_test.jpg"**  
**OUTPUT\_DIR \= "yolo/outputs"**  
**MODEL\_NAME \= "yolov8n.pt"**  
**CONF\_THRESHOLD \= 0.4**

**os.makedirs(OUTPUT\_DIR, exist\_ok=True)**

**\# Load model**  
**model \= YOLO(MODEL\_NAME)**

**\# Run inference**  
**results \= model(IMAGE\_PATH, conf=CONF\_THRESHOLD)**

**\# Load image for visualization**  
**image \= cv2.imread(IMAGE\_PATH)**

**\# Draw detections**  
**for result in results:**  
    **for box in result.boxes:**  
        **x1, y1, x2, y2 \= map(int, box.xyxy\[0\])**  
        **confidence \= float(box.conf\[0\])**

        **cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2\)**  
        **cv2.putText(**  
            **image,**  
            **f"Anomaly {confidence:.2f}",**  
            **(x1, y1 \- 10),**  
            **cv2.FONT\_HERSHEY\_SIMPLEX,**  
            **0.6,**  
            **(0, 255, 0),**  
            **2**  
        **)**

**\# Save output**  
**output\_path \= os.path.join(OUTPUT\_DIR, "detected\_test.jpg")**  
**cv2.imwrite(output\_path, image)**

**print("Detection completed. Output saved to:", output\_path)**

---

## **10\. Running the Detection Test**

**From terminal:**

**cd ml-engine/detection**  
**python run\_yolo.py**

**On first execution:**

* **YOLOv8-Nano weights may download automatically**  
* **This is expected behavior**

---

## **11\. Output Validation**

**The output image must appear at:**

**ml-engine/detection/yolo/outputs/detected\_test.jpg**

### **Expected Observations**

* **One or more bounding boxes may appear**  
* **Confidence values may vary**  
* **Detection accuracy is not evaluated at this stage**

**The only requirement is successful inference and output generation.**

---

## **12\. Important Clarifications**

### **12.1 Random or Incorrect Detections**

**This is expected because:**

* **YOLOv8-Nano is pretrained on COCO dataset**  
* **It has not yet been fine-tuned for underwater anomalies**

**This does not indicate a failure.**

---

### **12.2 Why Training Is Not Done in Part 3**

**Training requires:**

* **Custom labeled datasets**  
* **Careful validation**  
* **Pipeline integration**

**These are addressed in later stages.**  
**Part-3 validates model integration, not accuracy.**

---

## **13\. Common Errors and Their Causes**

| Issue | Cause |
| ----- | ----- |
| **No detections** | **High confidence threshold** |
| **Script crashes** | **Missing ultralytics install** |
| **Weird boxes** | **COCO bias (expected)** |
| **Using raw images** | **Incorrect execution flow** |

---

## **14\. Documentation Requirement**

**Create the following file:**

**ml-engine/docs/part3\_detection.md**

**This document must explain:**

* **Why YOLOv8-Nano was chosen**  
* **Why detection is anomaly-based**  
* **Why enhanced images are mandatory**  
* **Role of confidence scores**  
* **Limitations of pretrained detection**

---

## **15\. Completion Criteria for Part 3**

**Part-3 is considered complete when:**

* **YOLOv8-Nano loads successfully**  
* **Enhanced image inference runs without errors**  
* **Bounding boxes and confidence scores are produced**  
* **Output image is saved correctly**  
* **No backend or real-time logic is involved**  
* **Documentation is written**

---

## **16\. Output of Part 3**

**At the end of Part-3, Jal-Drishti has:**

* **A validated detection module**  
* **A clear separation between enhancement and detection**  
* **Confidence-scored perception output**  
* **A stable foundation for pipeline integration**

---

# **PART 4: UNIFIED GAN → YOLO PIPELINE**

**Step-by-Step Execution Plan (End-to-End Integration)**

---

## **1\. Position of Part 4 in the Overall Execution Flow**

**At this stage:**

* **Part-1 is complete**  
  * **Dataset selected, structured, validated**  
  * **Enhancement and detection data clearly separated**  
* **Part-2 is complete**  
  * **FUnIE-GAN generator works independently**  
  * **Raw underwater image → enhanced image validated**  
* **Part-3 is complete**  
  * **YOLOv8-Nano runs independently**  
  * **Enhanced image → bounding box \+ confidence validated**

**Part-4 integrates Part-2 and Part-3 into a single pipeline.**

**This is the first time the system behaves like a *real perception system* rather than isolated models.**

---

## **2\. Objective of Part 4**

**The objective of Part-4 is to:**

* **Connect FUnIE-GAN and YOLOv8-Nano into one inference flow**  
* **Guarantee correct data transfer between models**  
* **Enforce strict normalization and resolution rules**  
* **Ensure stability, correctness, and debuggability**  
* **Validate the complete ML perception chain on a single input**

**No real-time streaming is introduced yet.**  
**This part focuses on correctness over speed.**

---

## **3\. Why Part 4 Is a Dedicated Execution Stage**

**Most real-world ML systems fail not because of bad models, but because of:**

* **Wrong pixel value ranges**  
* **Color channel mismatches**  
* **Silent tensor shape errors**  
* **Improper resizing**  
* **Framework boundary issues**

**GANs and detectors have fundamentally different assumptions.**

**Part-4 exists to bridge those assumptions safely.**

---

## **4\. Conceptual End-to-End Flow (Authoritative)**

**Raw Underwater Image (BGR, 0–255)**  
            **↓**  
**Color Conversion (BGR → RGB)**  
            **↓**  
**Resize → 256×256**  
            **↓**  
**Normalize → \[-1, 1\]**  
            **↓**  
**FUnIE-GAN Generator**  
            **↓**  
**Output Range \[-1, 1\]**  
            **↓**  
**Bridge Normalization → \[0, 1\]**  
            **↓**  
**Resize → 640×640**  
            **↓**  
**YOLOv8-Nano Detector**  
            **↓**  
**Bounding Boxes \+ Confidence**

**Every arrow above is enforced in code.**

---

## **5\. Folder Structure Required for Part 4**

**The following structure must exist inside `ml-engine/`:**

**ml-engine/**  
 **├── pipeline/**  
 **│   ├── pipeline.py**  
 **│   └── test\_pipeline.py**  
 **├── enhancement/**  
 **│   └── funie\_gan/**  
 **│       ├── nets/**  
 **│       ├── utils/**  
 **│       └── weights/**  
 **├── detection/**  
 **│   └── yolo/**  
 **├── data/**  
 **│   └── enhancement/**  
 **│       └── raw/**  
 **├── outputs/**  
 **│   └── pipeline/**  
 **├── docs/**  
 **│   └── part4\_unified\_pipeline.md**  
 **├── venv/**  
 **└── README.md**

---

## **6\. Environment and Dependency Rules**

### **6.1 Python Environment**

* **Same virtual environment created in Part-2**  
* **No new venv is created**  
* **Reason: GAN and YOLO must run in one runtime context**

---

### **6.2 Required Libraries (Already Installed)**

* **torch**  
* **torchvision**  
* **opencv-python**  
* **numpy**  
* **ultralytics**

**No additional dependencies are introduced in Part-4.**

---

## **7\. Core Engineering Constraint: Single Framework**

**Both models must run in:**

* **Native PyTorch**  
* **Single CUDA / CPU context**  
* **No framework switching**

**This avoids:**

* **GPU memory duplication**  
* **CPU ↔ GPU overhead**  
* **Framework-level instability**

---

## **8\. Pipeline Implementation Strategy**

### **8.1 Single Responsibility Principle**

**Part-4 introduces one new core file:**

**ml-engine/pipeline/pipeline.py**

**This file:**

* **Loads models once**  
* **Defines preprocessing**  
* **Defines normalization bridge**  
* **Runs end-to-end inference**

**No visualization or testing logic lives here.**

---

## **9\. Normalization Bridge (Non-Negotiable)**

### **9.1 Raw Image → GAN Input**

**Raw image properties:**

* **Format: BGR**  
* **Range: \[0, 255\]**  
* **Type: uint8**

**Required transformation:**

1. **Convert BGR → RGB**  
2. **Resize to 256×256**  
3. **Normalize:**

**\[**  
**x\_{GAN} \= \\frac{x\_{raw} \- 127.5}{127.5}**  
**\]**

**Result:**

* **Range: \[-1, 1\]**  
* **Type: float32**

---

### **9.2 GAN Output → YOLO Input**

**GAN output:**

* **Range: \[-1, 1\]**  
* **Resolution: 256×256**

**YOLO requires:**

* **Range: \[0, 1\]**  
* **Resolution: 640×640**

**Bridge normalization:**

**\[**  
**x\_{YOLO} \= \\frac{x\_{GAN\_out} \+ 1}{2}**  
**\]**

**Then:**

* **Resize using bilinear interpolation**  
* **`align_corners = False`**

---

## **10\. Pipeline Implementation File**

### **10.1 File Location**

**ml-engine/pipeline/pipeline.py**

---

### **10.2 Responsibilities of `pipeline.py`**

1. **Load FUnIE-GAN generator**  
2. **Load YOLOv8-Nano model**  
3. **Accept raw image path**  
4. **Apply all preprocessing**  
5. **Run enhancement**  
6. **Run detection**  
7. **Return structured detection results**

---

### **10.3 High-Level Pipeline Code Structure (Conceptual)**

**class JalDrishtiPipeline:**  
    **def \_\_init\_\_(self):**  
        **load\_gan()**  
        **load\_yolo()**

    **def preprocess\_for\_gan(self, image):**  
        **pass**

    **def gan\_inference(self, tensor):**  
        **pass**

    **def preprocess\_for\_yolo(self, gan\_output):**  
        **pass**

    **def yolo\_inference(self, image):**  
        **pass**

    **def run(self, image\_path):**  
        **pass**

**Each step is explicitly separated for debuggability.**

---

## **11\. Testing Strategy for Part 4**

### **11.1 Why Testing Is Mandatory Here**

**This is the first point where:**

* **Multiple models interact**  
* **Silent failures are common**  
* **Debugging becomes difficult later**

**Therefore, testing is mandatory before proceeding.**

---

## **12\. Unified Pipeline Test Script**

### **12.1 Test Script Location**

**ml-engine/pipeline/test\_pipeline.py**

---

### **12.2 Purpose of the Test Script**

**The test script:**

* **Uses a single raw underwater image**  
* **Runs the full pipeline**  
* **Saves:**  
  * **Enhanced image**  
  * **Detection visualization**  
* **Prints confidence values**

---

### **12.3 Test Script Execution Flow**

1. **Load raw image from `data/enhancement/raw/`**  
2. **Pass it through `JalDrishtiPipeline`**  
3. **Draw YOLO bounding boxes**  
4. **Save output to `outputs/pipeline/`**

---

### **12.4 Expected Test Output**

**outputs/pipeline/**  
 **├── enhanced\_output.jpg**  
 **└── detected\_output.jpg**

---

## **13\. Validation Criteria for Part 4**

**Part-4 is considered successful only if:**

* **Enhanced image is generated correctly**  
* **Detection runs on enhanced image**  
* **Bounding boxes appear on output**  
* **Confidence values are printed**  
* **No crashes or silent failures occur**  
* **Pipeline runs multiple times consistently**

---

## **14\. Common Failure Modes and Prevention**

| Failure | Root Cause | Prevention |
| ----- | ----- | ----- |
| **Black frames** | **Wrong normalization** | **Enforce math strictly** |
| **Color distortion** | **BGR/RGB mismatch** | **Explicit conversion** |
| **YOLO crash** | **Wrong input range** | **Apply bridge formula** |
| **Low confidence** | **Enhancement skipped** | **Enforce pipeline order** |
| **Random behavior** | **Models reloaded repeatedly** | **Load once in init** |

---

## **15\. Documentation Requirement**

**Create the following file:**

**ml-engine/docs/part4\_unified\_pipeline.md**

**This document must explain:**

* **Why a normalization bridge is required**  
* **How GAN and YOLO assumptions differ**  
* **End-to-end data flow**  
* **Failure modes and safeguards**  
* **Why integration is a separate stage**

---

## **16\. Completion Criteria for Part 4**

**Part-4 is considered complete when:**

* **One raw underwater image passes end-to-end**  
* **Enhanced \+ detected output is produced**  
* **Pipeline is stable and repeatable**  
* **No backend or streaming logic is used**  
* **Documentation is written**

---

## **17\. Output of Part 4**

**At the end of Part-4, Jal-Drishti has:**

* **A unified perception pipeline**  
* **Mathematically correct data transitions**  
* **A stable GAN → detector flow**  
* **A foundation for real-time deployment**

---

**PART 5: REAL-TIME OPERATION, CONFIDENCE LOGIC, AND SYSTEM SAFETY**

**Final Execution and Validation Plan**

---

## **1\. Position of Part 5 in the Overall System Flow**

**At this point:**

* **Part-1 established a clean and ethical dataset foundation**  
* **Part-2 implemented underwater image enhancement (FUnIE-GAN)**  
* **Part-3 implemented object/anomaly detection (YOLOv8-Nano)**  
* **Part-4 unified GAN → YOLO into a single, stable perception pipeline**

**Part-5 finalizes the system for real-world operation.**

**This is the stage where Jal-Drishti becomes a safe, real-time, decision-support system, not just a working ML pipeline.**

---

## **2\. Objective of Part 5**

**The objective of Part-5 is to:**

1. **Enforce real-time operational constraints**  
2. **Introduce confidence-driven decision logic**  
3. **Guarantee system stability over time**  
4. **Prevent unsafe or misleading AI outputs**  
5. **Prepare the system for human-in-the-loop usage**  
6. **Validate the pipeline under continuous operation**

**This part addresses engineering reliability, safety, and trust, not model accuracy.**

---

## **3\. Core Design Philosophy of Part 5**

**Jal-Drishti follows three non-negotiable principles:**

1. **AI assists, humans decide**  
2. **Uncertainty must be explicitly exposed**  
3. **System must fail safely, not silently**

**All design choices in Part-5 enforce these principles.**

---

## **4\. Real-Time Performance Constraints**

### **4.1 Target Frame Rate**

* **Target: 12–15 FPS**  
* **This is the minimum for smooth human situational awareness**

### **4.2 Latency Budget**

**At 15 FPS:**

**\[**  
**\\text{Max time per frame} \\approx 66 \\text{ ms}**  
**\]**

**This includes:**

* **Frame reception**  
* **Enhancement (GAN)**  
* **Detection (YOLO)**  
* **Result formatting**

**Any system exceeding this budget causes:**

* **Lag**  
* **Operator confusion**  
* **Loss of trust**

---

## **5\. Performance Control Strategies**

**To stay within the latency budget, the following strategies are enforced:**

### **5.1 Lightweight Models**

* **FUnIE-GAN (compact generator)**  
* **YOLOv8-Nano (smallest YOLOv8 variant)**

### **5.2 FP16 Inference**

* **Models run in half-precision where supported**  
* **Reduces memory usage and inference time**

### **5.3 Asynchronous Processing**

* **Frame ingestion**  
* **ML inference**  
* **Output rendering**  
  **are decoupled logically**

### **5.4 Frame Dropping Policy**

* **If processing lags:**  
  * **Older frames are dropped**  
  * **Only the latest frame is processed**

**This prioritizes situational awareness over completeness.**

---

## **6\. Confidence-Driven Decision Framework**

### **6.1 Why Confidence Is Mandatory**

**Binary outputs (“threat / no threat”) are dangerous in maritime environments.**

**Reasons:**

* **Underwater visibility is inconsistent**  
* **Optical illusions are common**  
* **Models can be uncertain**

**Therefore, every detection must include a confidence score.**

---

### **6.2 Confidence Thresholds**

**Jal-Drishti enforces the following interpretation:**

| Confidence Score | System State |
| ----- | ----- |
| **\> 0.75** | **Confirmed Threat** |
| **0.40 – 0.75** | **Potential Anomaly** |
| **\< 0.40** | **Safe Mode** |

**These thresholds are conservative by design.**

---

### **6.3 Meaning of Each State**

**Confirmed Threat**

* **High confidence visual anomaly**  
* **Immediate operator attention required**

**Potential Anomaly**

* **Uncertain detection**  
* **Manual verification encouraged**

**Safe Mode**

* **Visibility too poor or AI uncertainty too high**  
* **System explicitly avoids misleading output**

---

## **7\. Safe Mode Logic (Critical Safety Feature)**

### **7.1 When Safe Mode Is Triggered**

**Safe Mode activates when:**

* **Detection confidence \< 0.40**  
* **Water turbidity is high**  
* **Visual features are unreliable**  
* **Model outputs fluctuate excessively**

---

### **7.2 Behavior in Safe Mode**

* **No threat alerts are raised**  
* **UI displays “Low Confidence / Poor Visibility”**  
* **Operator is informed explicitly**  
* **System continues monitoring without claims**

**This prevents:**

* **False alarms**  
* **Over-trust in AI**  
* **Unsafe decisions**

---

## **8\. Human-in-the-Loop Enforcement**

### **8.1 Role of the AI System**

**The AI system:**

* **Highlights regions of interest**  
* **Provides confidence-scored suggestions**  
* **Never initiates action**

---

### **8.2 Role of the Human Operator**

**The human operator:**

* **Interprets AI outputs**  
* **Confirms or dismisses detections**  
* **Makes final operational decisions**

**This design aligns with:**

* **Defense safety standards**  
* **Ethical AI principles**  
* **Legal accountability requirements**

---

## **9\. System Stability and Long-Duration Operation**

### **9.1 Model Lifecycle Management**

* **Models are loaded once at startup**  
* **No repeated loading per frame**  
* **Inference runs under `no_grad()` mode**

**This prevents:**

* **Memory leaks**  
* **GPU fragmentation**  
* **Performance degradation**

---

### **9.2 Error Handling Strategy**

**The system explicitly handles:**

* **Invalid frames**  
* **Corrupted input**  
* **Temporary data loss**

**Instead of crashing:**

* **Errors are logged**  
* **Frame is skipped**  
* **System continues running**

---

## **10\. Testing Strategy for Part 5**

### **10.1 Continuous Run Test**

**Run the unified pipeline continuously for:**

* **At least 5–10 minutes**  
* **Using multiple raw underwater images**

**Observe:**

* **Memory usage**  
* **FPS stability**  
* **Output consistency**

---

### **10.2 Confidence Behavior Test**

**Test three scenarios:**

1. **Clear underwater image**  
2. **Moderately turbid image**  
3. **Extremely low-visibility image**

**Verify:**

* **Confidence decreases with visibility**  
* **Safe Mode triggers correctly**  
* **No false “Confirmed Threat” in poor visibility**

---

### **10.3 Failure Injection Test**

**Intentionally test:**

* **Invalid image input**  
* **Blank frames**  
* **Noise-only frames**

**System must:**

* **Not crash**  
* **Not hallucinate threats**  
* **Enter Safe Mode if needed**

---

## **11\. Folder Structure Finalization**

**At the end of Part-5, the ML section should look like:**

**ml-engine/**  
 **├── data/**  
 **├── enhancement/**  
 **├── detection/**  
 **├── pipeline/**  
 **├── outputs/**  
 **│   └── pipeline/**  
 **├── docs/**  
 **│   ├── part1\_dataset\_strategy.md**  
 **│   ├── part2\_image\_enhancement.md**  
 **│   ├── part3\_detection.md**  
 **│   ├── part4\_unified\_pipeline.md**  
 **│   └── part5\_system\_safety.md**  
 **├── venv/**  
 **└── README.md**

---

## **12\. Documentation Requirement for Part 5**

**Create:**

**ml-engine/docs/part5\_system\_safety.md**

**This document must explain:**

* **Real-time constraints**  
* **Confidence thresholds**  
* **Safe Mode logic**  
* **Human-in-the-loop design**  
* **Limitations of the system**  
* **Ethical positioning**

**This is mandatory for jury and defense review.**

---

## **13\. Completion Criteria for Part 5**

**Part-5 is considered complete when:**

* **End-to-end pipeline runs continuously**  
* **FPS remains within acceptable limits**  
* **Confidence logic behaves predictably**  
* **Safe Mode triggers correctly**  
* **No autonomous decisions are made**  
* **System does not crash under stress**  
* **All documentation is complete**

---

## **14\. Final System Outcome**

**After Part-5, Jal-Drishti achieves:**

* **A unified, real-time ML perception system**  
* **Explicit uncertainty handling**  
* **Safety-first operational design**  
* **Ethical and realistic defense framing**  
* **Demo-ready and review-ready maturity**

---

## **15\. What You Can Claim After Part-5 (Safely)**

**You can confidently state:**

**“Jal-Drishti is a real-time, AI-assisted underwater perception system that enhances visibility, detects visual anomalies, and supports human decision-making under uncertain maritime conditions.”**

**No over-claiming. No unsafe promises.**

## **After Part-5, Is ML Work Fully Done?**

### **Short answer**

**Core ML is DONE.**

### **What is complete:**

* **Model selection**

* **Enhancement logic**

* **Detection logic**

* **Unified pipeline**

* **Confidence & safety framework**

### **What remains (optional / advanced):**

* **YOLO fine-tuning on custom anomaly data**

* **Temporal smoothing (tracking across frames)**

* **FPS optimization**

* **Edge deployment (Jetson)**

**These are Phase-2 / Phase-3 enhancements, not MVP blockers.**

**This was intentional and correct.**

### **Reasoning:**

| Stage | Focus |
| ----- | ----- |
| **Part-1** | **Data realism** |
| **Part-2** | **Enhancement correctness** |
| **Part-3** | **Detection correctness** |
| **Part-4** | **Mathematical integration** |
| **Part-5** | **Safety & runtime behavior** |

**Video belongs to:**

* **System integration**

* **Transport**

* **Frontend rendering**

**Not to:**

* **Model design**

* **ML correctness**

* **Training logic**

**Including video earlier would:**

* **Blur responsibilities**

* **Confuse reviewers**

* **Mix ML with system plumbing**

