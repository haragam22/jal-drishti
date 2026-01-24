Official Dataset (EUVP- **Enhancing Underwater Visual Perception**): [https://www.kaggle.com/datasets/pamuduranasinghe/euvp-dataset](https://www.kaggle.com/datasets/pamuduranasinghe/euvp-dataset)

**Deep Reinforcement Learning Based Latency Minimization for Mobile Edge Computing With Virtualization in Maritime UAV Communication Network-**  
[**https://ieeexplore.ieee.org/document/9678008**](https://ieeexplore.ieee.org/document/9678008)

---

# **Jal-Drishti: ML Execution Plan (Detailed Technical Breakdown)**

## **Overview of the 5 Execution Parts**

1. **Data Acquisition & Preparation (Underwater Vision Readiness)**  
2. **Underwater Image Enhancement (Visibility Restoration using GANs)**  
3. **Object / Anomaly Detection (Real-Time Threat Perception)**  
4. **Unified GAN → Detector Pipeline Integration (Normalization & Stability)**  
5. **Real-Time Deployment, Confidence Logic & System Safety**

Each part is **independent**, **testable**, and **incrementally deployable**, which is critical for a beginner-level but safety-critical system.

---

## **PART 1: DATA ACQUISITION & PREPARATION**

### **1.1 What is Done**

* Collect **real underwater images/videos** representing:  
  1. High turbidity  
  2. Color attenuation (red channel loss)  
  3. Low contrast and haze  
* Use **EUVP dataset** as the primary visual backbone.  
* Prepare data for **two parallel learning objectives**:  
  1. Image enhancement (GAN)  
  2. Object/anomaly detection (YOLO)

---

### **1.2 Why This Is Required**

Underwater environments violate almost every assumption made by standard computer vision models:

* Light absorption removes red wavelengths.  
* Scattering causes haze.  
* Contrast is non-uniform and depth-dependent.

Research consistently shows that **raw underwater frames reduce detection accuracy drastically**, even for state-of-the-art detectors .

---

### **1.3 Dataset Selection & Justification**

#### **EUVP Dataset (Primary Choice)**

* Contains **paired underwater images**:  
  * `trainA`: degraded underwater images  
  * `trainB`: enhanced/clear counterparts  
* Enables **supervised GAN training**, which is faster and more stable than unpaired methods.

This dataset has been repeatedly used in underwater enhancement benchmarks and GAN-based pipelines .

---

### **1.4 How to Use the Dataset**

* **Download locally** (recommended):  
  * Kaggle import is only for notebooks; local ML pipelines require filesystem access.  
* Use:  
  * `Paired/underwater_dark` → GAN training  
  * Enhanced outputs → detector input

---

### **1.5 Challenges Solved**

| Challenge | Mitigation |
| ----- | ----- |
| Lack of real mine data | Treat problem as **anomaly detection**, not mine classification |
| Domain bias | Use **real underwater backgrounds**, not synthetic-only images |
| Beginner constraints | Public, well-documented dataset with reproducible results |

---

### **1.6 Output of Part 1**

Clean directory structure:  
data/  
  ├── gan/  
  │   ├── trainA  
  │   └── trainB  
  └── detection/  
      └── frames/

*   
* Dataset sanity-checked and visualized.  
* Ready for GAN training.

**Part-1 Completion Criteria**

* You can load images.  
* You can visually verify degraded vs enhanced pairs.  
* No model training yet.

---

## **PART 2: UNDERWATER IMAGE ENHANCEMENT (FUnIE-GAN)**

### **2.1 What is Done**

* Train **FUnIE-GAN** to:  
  * Restore color balance  
  * Improve contrast  
  * Reduce haze  
* Convert underwater frames into **detector-friendly images**.

---

### **2.2 Why GAN-Based Enhancement Is Mandatory**

Traditional enhancement (CLAHE, white balance):

* Works locally  
* Fails under extreme turbidity  
* Breaks color consistency

GAN-based enhancement:

* Learns **non-linear underwater distortion**  
* Preserves structural integrity  
* Improves downstream detection accuracy significantly

---

### **2.3 Why FUnIE-GAN (Specifically)**

FUnIE-GAN was chosen because:

* **Lightweight**  
* **Real-time capable**  
* U-Net based generator  
* Designed explicitly for underwater images

It outperforms heavy GANs while maintaining inference speed, which is critical for real-time systems .

---

### **2.4 How It Is Implemented**

#### **Input Processing**

* Resize to `256 × 256`

Normalize:  
x\_gan \= (x\_raw − 127.5) / 127.5   → range \[-1, 1\]

* 

#### **Training Objective**

* Adversarial loss  
* Content consistency  
* Perceptual structure preservation

---

### **2.5 Engineering Constraints**

* **RGB ordering enforced**  
* Avoid histogram-based post-processing  
* FP16 inference to reduce latency

---

### **2.6 Challenges Solved**

| Challenge | How GAN Solves |
| ----- | ----- |
| Color loss | Learns wavelength attenuation |
| Haze | Adversarial learning restores contrast |
| Detection failure | Cleaner edges and textures |
| Real-time need | Lightweight generator |

---

### **2.7 Output of Part 2**

* Trained `funie_gan.pth`  
* Enhanced frames visually verified  
* PSNR / UIQM improvement observed (qualitative OK for MVP)

**Part-2 Completion Criteria**

* Raw vs Enhanced frames clearly distinguishable  
* GAN runs under real-time constraints on GPU  
* No NaNs or color artifacts

---

## **PART 3: OBJECT / ANOMALY DETECTION (YOLOv8-Nano)**

### **3.1 What is Done**

* Use **YOLOv8-Nano** for:  
  * Real-time inference  
  * Low GPU memory  
  * Small object sensitivity

---

### **3.2 Why YOLOv8-Nano**

YOLOv8-Nano:

* Anchor-free  
* Faster convergence  
* Excellent FPS on edge-class GPUs  
* Proven in real-time safety systems

---

### **3.3 Detection Philosophy**

**No mine classification claim**.

Instead:

* Detect **man-made or anomalous shapes**  
* Output bounding box \+ confidence  
* Human operator makes final call

This aligns with real defense-grade AI systems and avoids ethical over-claiming .

---

### **3.4 How Detection Is Performed**

#### **Input Preparation**

From GAN output:

x\_yolo \= (x\_gan\_out \+ 1\) / 2   → range \[0, 1\]  
Resize → 640 × 640 (bilinear)

#### **Classes**

* `anomaly`  
* `object_of_interest`

---

### **3.5 Challenges Solved**

| Challenge | Solution |
| ----- | ----- |
| Small objects | YOLOv8 multi-scale heads |
| Low contrast | GAN-enhanced input |
| Latency | Nano backbone |
| False certainty | Confidence-based logic |

---

### **3.6 Output of Part 3**

* Bounding boxes  
* Confidence scores  
* JSON-serializable detections

**Part-3 Completion Criteria**

* Stable detections on enhanced frames  
* No bounding box explosion  
* FPS ≥ 15 on GPU

---

## **PART 4: UNIFIED GAN → YOLO PIPELINE**

### **4.1 What is Done**

* Integrate GAN and YOLO into **one PyTorch runtime**  
* Implement **strict normalization bridge**  
* Prevent color, range, and resolution mismatches

---

### **4.2 Why This Part Is Critical**

Most real-world failures occur here:

* Black frames  
* Over-saturated colors  
* Silent detector failure

These failures are due to **incorrect datatype transitions** .

---

### **4.3 The Normalization Bridge (Non-Negotiable)**

Raw Image (0–255)  
   ↓  
\[-1, 1\]  → FUnIE-GAN  
   ↓  
\[0, 1\]   → YOLOv8

Resolution:

256×256 → 640×640 (bilinear)

Color:

BGR (OpenCV) → RGB (Model)

---

### **4.4 Challenges Solved**

| Issue | Mitigation |
| ----- | ----- |
| Black frames | Correct range remapping |
| Model instability | Single PyTorch context |
| Latency | Shared GPU memory |
| Debug difficulty | Stepwise validation |

---

### **4.5 Output of Part 4**

* `JalDrishtiPipeline` class  
* Unified inference call  
* Deterministic outputs

**Part-4 Completion Criteria**

* End-to-end frame passes through pipeline  
* No crashes after 10+ minutes  
* Outputs stable under load

---

## **PART 5: REAL-TIME DEPLOYMENT & SAFETY LOGIC**

### **5.1 What is Done**

* Stream frames via WebSocket  
* Run async inference  
* Apply **confidence-driven decision logic**

---

### **5.2 Why Safety Logic Is Mandatory**

In maritime defense:

* False positives \= operational chaos  
* False negatives \= mission risk

Therefore, AI **assists**, not decides .

---

### **5.3 Confidence Framework**

| Confidence | System State |
| :---: | :---: |

0.75 | Confirmed Threat |  
0.40 – 0.75 | Potential Anomaly |  
\< 0.40 | Safe Mode |

---

### **5.4 Real-Time Constraints**

* Target latency: **\< 100 ms**  
* Async frame dropping  
* FP16 inference

WebSocket chosen due to low-latency characteristics and cloud compatibility .

---

### **5.5 Output of Part 5**

* Real-time dashboard  
* Operator-readable alerts  
* Stable streaming system

**Final Completion Criteria**

* Continuous streaming  
* No memory leaks  
* Clear operator interpretation

---

# **PART 1: DATA ACQUISITION AND PREPARATION**

*(Underwater Vision Readiness)*

---

## **1\. Objective of Part 1**

The objective of Part 1 is to **establish a reliable, realistic, and research-grounded visual data foundation** for the Jal-Drishti system.  
This stage does **not involve model training**. Instead, it defines:

* What visual data the system will see  
* How underwater conditions are represented  
* How the problem is framed from a defense and engineering perspective

A correct dataset strategy is critical because underwater environments violate most assumptions of conventional computer vision systems.

---

## **2\. Why Data Preparation Is a Critical Challenge in Underwater AI**

Unlike terrestrial vision systems, underwater imagery suffers from multiple physical and optical degradations:

1. **Wavelength-dependent light absorption**  
   Red light attenuates rapidly, causing dominant blue/green color casts.  
2. **Forward and backward scattering**  
   Suspended particles introduce haze and blur.  
3. **Non-uniform illumination**  
   Light intensity decays exponentially with depth.  
4. **Low signal-to-noise ratio**  
   Objects often occupy very few pixels and blend into the background.

Research literature consistently shows that **raw underwater images severely degrade detection accuracy**, even for state-of-the-art deep learning models. This is why data preparation and enhancement are treated as a **separate engineering stage**, not a preprocessing afterthought.

---

## **3\. Problem Framing: Detection vs Weapon Classification**

A key design decision in Jal-Drishti is **how the problem is defined**.

### **3.1 What Jal-Drishti Does NOT Do**

* It does **not claim “mine detection” or “weapon classification”**  
* It does **not perform autonomous lethal decision-making**

### **3.2 What Jal-Drishti Actually Does**

* Detects **visual anomalies or man-made objects** in underwater scenes  
* Provides **confidence-based alerts** for human operators

This framing aligns with:

* Real-world defense AI practice  
* Ethical AI deployment principles  
* The lack of publicly available classified datasets

Hence, the dataset is designed for **anomaly perception**, not weapon labeling.

---

## **4\. Dataset Requirements Defined for Jal-Drishti**

The dataset must satisfy the following conditions:

1. Represent **real underwater optical degradation**  
2. Include **high-turbidity and low-visibility scenes**  
3. Be **publicly accessible and reproducible**  
4. Support **image enhancement research**  
5. Be suitable for **real-time system constraints**

---

## **5\. Selected Dataset: EUVP (Enhancement of Underwater Visual Perception)**

### **5.1 Why EUVP Was Selected**

The EUVP dataset is chosen as the primary data source because it satisfies all project constraints:

* Contains **real underwater images**  
* Includes **paired degraded and enhanced images**  
* Widely used in underwater image enhancement research  
* Supports supervised GAN-based enhancement  
* Publicly available and well-documented

This dataset has been used extensively in research focused on underwater image restoration and real-time perception systems.

---

### **5.2 Structure of the EUVP Dataset**

The dataset is organized into four major components:

* **Paired/**  
  * `trainA`: degraded underwater images  
  * `trainB`: corresponding enhanced images  
* **Unpaired/**  
* **eval\_data/**  
* **test\_samples/**

For Jal-Drishti, the **Paired underwater\_dark subset** is the most relevant.

---

## **6\. How the Dataset Is Used in Jal-Drishti**

### **6.1 Dual-Pipeline Data Strategy**

The Jal-Drishti ML system contains **two independent perception stages**, each requiring data differently:

| Pipeline Stage | Dataset Usage |
| ----- | ----- |
| Image Enhancement (GAN) | Uses paired EUVP images |
| Object / Anomaly Detection | Uses enhanced outputs \+ background frames |

This separation prevents data leakage and ensures modular design.

---

### **6.2 Dataset Usage for Image Enhancement**

* **Input**: Raw underwater images (`trainA`)  
* **Target**: Enhanced images (`trainB`)  
* **Purpose**: Learn a mapping from degraded to visually restored frames

No object labels are required at this stage.

---

### **6.3 Dataset Usage for Detection (Later Stages)**

* Detection models are **not trained on raw EUVP images**  
* They consume **GAN-enhanced frames**  
* This simulates real operational conditions where enhancement precedes detection

---

## **7\. Dataset Acquisition Method**

### **7.1 Download Strategy**

* Dataset is downloaded **locally as a ZIP file**  
* Kaggle notebook imports are avoided

**Reason**:  
Local filesystem access is required for:

* Custom pipelines  
* Real-time streaming simulation  
* Integration with FastAPI and WebSockets

---

### **7.2 Recommended Directory Structure**

ml-engine/  
 └── data/  
     ├── enhancement/  
     │   ├── trainA/  
     │   └── trainB/  
     └── detection/  
         └── backgrounds/

This structure enforces clean separation between enhancement and detection data.

---

## **8\. Data Validation and Sanity Checks**

Before proceeding to Part 2, the following checks are mandatory:

1. Visual inspection of random samples  
   * Strong green/blue color cast present  
   * Low contrast and haze visible  
2. Resolution consistency  
   * Images are resized only during model processing  
   * Original data remains untouched  
3. No labels introduced prematurely  
   * Avoids bias and incorrect assumptions

---

## **9\. Challenges Addressed by Part 1**

| Challenge | How Part 1 Solves It |
| ----- | ----- |
| Lack of real mine data | Reframes task as anomaly detection |
| Underwater optical distortion | Uses real degraded imagery |
| Dataset bias | Avoids synthetic-only data |
| Ethical & legal risks | No weapon classification claims |
| Beginner feasibility | Public, reproducible dataset |

---

## **10\. Deliverables of Part 1**

At the completion of Part 1, the following are ready:

1. Downloaded and structured EUVP dataset  
2. Clear separation between enhancement and detection data  
3. Written dataset strategy for documentation  
4. Visual understanding of underwater degradation  
5. Zero model training performed (by design)

---

## **11\. Completion Criteria for Part 1**

Part 1 is considered complete when:

* The dataset is locally available and organized  
* You can clearly explain:  
  * Why EUVP was chosen  
  * Why enhancement is mandatory  
  * Why the system is anomaly-based  
* No ML model has been trained yet  
* The next step (image enhancement) can start immediately

---

# **PART 2: UNDERWATER IMAGE ENHANCEMENT**

*(Visibility Restoration using FUnIE-GAN)*

---

## **1\. Objective of Part 2**

The objective of Part 2 is to **restore visual usability of underwater imagery** before any object or anomaly detection is attempted.

This stage transforms **optically degraded underwater frames** into **perceptually and statistically improved images** that are suitable for downstream computer vision tasks.

This part explicitly addresses the fact that **detection models fail when applied directly to raw underwater images** due to severe color distortion, haze, and contrast loss.

---

## **2\. Why Image Enhancement Is a Separate System Component**

Underwater image degradation is governed by **physical water properties**, not camera quality. These include:

* Wavelength-dependent light absorption  
* Backscattering caused by suspended particles  
* Depth-dependent illumination decay  
* Non-linear color attenuation

Traditional object detectors assume:

* Stable color distribution  
* High local contrast  
* Clear edges and textures

These assumptions are violated underwater. Therefore, enhancement must be treated as a **dedicated perception module**, not a preprocessing trick.

Research consistently demonstrates that **enhancement-before-detection significantly improves detection accuracy and robustness** in underwater environments.

---

## **3\. Selection of Enhancement Approach**

### **3.1 Why Traditional Enhancement Methods Are Insufficient**

Conventional image enhancement techniques such as:

* Histogram equalization  
* CLAHE  
* White balance correction  
* Dark channel prior

operate using **fixed mathematical rules** and fail to generalize across varying underwater conditions such as turbidity, salinity, and depth.

They often:

* Over-amplify noise  
* Distort colors  
* Destroy texture consistency  
* Fail under extreme haze

---

### **3.2 Why GAN-Based Enhancement Is Used**

Generative Adversarial Networks (GANs) are capable of learning **non-linear mappings** between degraded and restored images directly from data.

Advantages:

* Learn real underwater degradation patterns  
* Preserve structural integrity  
* Restore perceptual color balance  
* Adapt to diverse underwater conditions

GAN-based enhancement has become the dominant approach in modern underwater vision research.

---

## **4\. Why FUnIE-GAN Is Selected**

### **4.1 Design Goals of FUnIE-GAN**

FUnIE-GAN (Fast Underwater Image Enhancement GAN) is specifically designed for:

* **Real-time inference**  
* **Low computational overhead**  
* **Underwater color restoration**  
* **Edge and texture preservation**

Unlike heavy GAN architectures, FUnIE-GAN is optimized for **deployment in real-time systems**, making it suitable for defense and maritime surveillance applications.

---

### **4.2 Architectural Overview**

FUnIE-GAN consists of two main components:

1. **Generator**  
   * Fully convolutional  
   * U-Net architecture  
   * Encoder-decoder with skip connections  
   * Captures both global color correction and local texture details  
2. **Discriminator**  
   * PatchGAN-based  
   * Evaluates local texture realism  
   * Encourages spatial consistency rather than global similarity

For Jal-Drishti, **only the Generator is used during inference**.

---

## **5\. Input and Output Specifications**

### **5.1 Input Image Characteristics**

* Source: EUVP degraded underwater images  
* Format: RGB images  
* Value range: `[0, 255]`  
* Data type: `uint8`

---

### **5.2 Preprocessing and Normalization**

Before passing images to FUnIE-GAN, strict normalization is applied:

\[  
x\_{GAN} \= \\frac{x\_{raw} \- 127.5}{127.5}  
\]

This maps pixel values from:

* `[0, 255]` → `[-1, 1]`

This normalization is **mandatory**. Any deviation results in:

* Black outputs  
* Color saturation  
* Model instability

---

### **5.3 Output Characteristics**

* Output range: `[-1, 1]`  
* Output resolution: `256 × 256`  
* Represents visually restored underwater imagery

The output is later re-mapped for detection usage in Part 4\.

---

## **6\. Training Strategy**

### **6.1 Training Data**

* Paired images from EUVP dataset:  
  * Input: degraded underwater images  
  * Target: corresponding enhanced images

This supervised setup:

* Improves convergence stability  
* Reduces training time  
* Produces consistent visual quality

---

### **6.2 Training Objective**

The generator is trained to minimize:

* Adversarial loss (realism)  
* Content preservation loss  
* Texture consistency loss

The goal is **visual usability**, not photorealistic reconstruction.

---

### **6.3 Training Constraints**

* Resolution fixed at `256 × 256`  
* Batch size kept small for stability  
* Training performed offline  
* No online learning during deployment

---

## **7\. Inference Mode (Deployment Configuration)**

During deployment:

* Only the **generator network** is loaded  
* Model runs in `eval()` mode  
* FP16 precision is enabled where supported  
* No gradients are computed

This ensures:

* Low latency  
* Reduced GPU memory usage  
* Stable real-time inference

---

## **8\. Engineering Constraints and Best Practices**

1. **Color Space Consistency**  
   * Ensure RGB ordering before model input  
   * Avoid OpenCV BGR-to-RGB mismatches  
2. **Resolution Handling**  
   * Resize only at model boundaries  
   * Preserve aspect ratio where possible  
3. **No Post-Processing Hacks**  
   * Avoid histogram stretching after GAN output  
   * Trust the learned mapping  
4. **Isolation from Detection**  
   * Enhancement and detection remain modular  
   * Failures are easier to debug

---

## **9\. Challenges Addressed by Part 2**

| Challenge | Mitigation |
| ----- | ----- |
| Color attenuation | Learned wavelength restoration |
| Haze and blur | Adversarial texture learning |
| Low contrast | Global \+ local feature correction |
| Detection failure | Produces detector-friendly images |
| Real-time constraint | Lightweight GAN architecture |

---

## **10\. Deliverables of Part 2**

At the completion of Part 2, the following artifacts are ready:

1. Trained FUnIE-GAN generator weights  
2. Inference-ready enhancement module  
3. Raw vs enhanced image comparisons  
4. Stable enhancement pipeline  
5. Clear separation from detection logic

---

## **11\. Completion Criteria for Part 2**

Part 2 is considered complete when:

* Enhanced images show visible improvement over raw frames  
* No color artifacts or black outputs appear  
* Inference runs stably for extended durations  
* Output images are suitable for object detection  
* The enhancement module can operate independently

---

# **PART 3: OBJECT / ANOMALY DETECTION**

*(Real-Time Underwater Threat Perception using YOLOv8-Nano)*

---

## **1\. Objective of Part 3**

The objective of Part 3 is to **identify visually suspicious or man-made objects in underwater scenes** after image enhancement has been performed.

This stage provides:

* Spatial localization (bounding boxes)  
* Class indication (anomaly/object of interest)  
* Confidence scores

The output of this stage is **decision-support information**, not an autonomous threat decision.

---

## **2\. Why Detection Is Performed After Enhancement**

Underwater object detection on raw frames is unreliable due to:

* Poor edge definition  
* Severe color distortion  
* Low contrast between object and background

Multiple studies show that **enhanced underwater images significantly improve downstream detection and perception performance**.  
Therefore, Jal-Drishti enforces a strict design rule:

**No detection is performed on raw underwater images.**

The detector only operates on **GAN-enhanced frames** generated in Part 2\.

---

## **3\. Problem Framing: Anomaly Detection, Not Weapon Identification**

### **3.1 Rationale**

There are no publicly available, large-scale, labeled datasets for real underwater mines or military-grade threats.  
Training a classifier to explicitly identify weapons would be:

* Technically unreliable  
* Ethically questionable  
* Legally risky

---

### **3.2 Adopted Detection Philosophy**

Jal-Drishti frames the problem as:

**Underwater anomaly detection and object-of-interest localization**

This means the system detects:

* Man-made shapes  
* Unusual geometry  
* Objects visually inconsistent with natural underwater terrain

Final interpretation and action remain with the human operator.

---

## **4\. Selection of Detection Model**

### **4.1 Why YOLO-Based Detection**

YOLO (You Only Look Once) models are well-suited for:

* Real-time inference  
* Single-stage detection  
* Streaming video pipelines

They offer an optimal balance between:

* Speed  
* Accuracy  
* Engineering simplicity

---

### **4.2 Why YOLOv8-Nano Specifically**

YOLOv8-Nano is selected due to:

* Lightweight architecture  
* High inference speed  
* Low GPU memory footprint  
* Anchor-free detection (improved small-object handling)  
* Proven performance in real-time applications

This makes it suitable for both:

* Cloud GPU deployment  
* Future edge deployment (Jetson-class devices)

---

## **5\. Input Specifications for the Detector**

### **5.1 Source of Input Images**

* Input to YOLOv8 is **not raw EUVP images**  
* Input is the **enhanced output** from FUnIE-GAN

This simulates real operational conditions.

---

### **5.2 Input Normalization and Resolution**

The detector expects:

* RGB images  
* Pixel range: `[0, 1]`  
* Resolution: `640 × 640`

Enhanced GAN outputs are therefore:

1. Rescaled from `[-1, 1]` to `[0, 1]`  
2. Upscaled from `256 × 256` to `640 × 640` using bilinear interpolation

This conversion is handled explicitly in the pipeline to avoid silent failures.

---

## **6\. Dataset Strategy for Detection**

### **6.1 Detection Dataset Composition**

The detection dataset is intentionally small and carefully curated, consisting of:

1. **Natural underwater backgrounds**  
   * Rocks  
   * Sand  
   * Coral  
   * Water plants  
2. **Generic underwater objects**  
   * Debris  
   * Cables  
   * Containers  
   * Man-made shapes  
3. **Synthetic anomalies**  
   * Simple geometric shapes  
   * Cylindrical or spherical objects  
   * Overlaid onto real underwater backgrounds

This strategy avoids dependence on classified data while remaining realistic.

---

### **6.2 Class Definitions**

To minimize complexity and false confidence:

* Single primary class: `anomaly`  
* Optional secondary class: `object_of_interest`

Avoiding fine-grained labels improves robustness and reduces overfitting.

---

## **7\. Training and Inference Strategy**

### **7.1 Training (Optional for MVP)**

For a minimum viable prototype:

* Pretrained YOLOv8-Nano can be used directly  
* Fine-tuning is optional and limited

If fine-tuning is performed:

* Only a small number of epochs  
* Emphasis on generalization, not accuracy metrics

---

### **7.2 Inference Configuration**

During inference:

* Confidence threshold is configurable  
* Non-Maximum Suppression (NMS) is applied  
* Outputs are converted to structured metadata

Each detection includes:

* Bounding box coordinates  
* Confidence score  
* Class label

---

## **8\. Confidence Scores and Their Role**

Confidence scores are a **core safety mechanism**, not just a metric.

They allow the system to:

* Express uncertainty  
* Avoid binary decisions  
* Support operator judgment

Confidence values are used later in Part 5 for system-level safety logic.

---

## **9\. Engineering Constraints**

1. **Real-Time Performance**  
   * Detector must operate within the time budget  
   * YOLOv8-Nano supports real-time inference at 15+ FPS  
2. **Stability Over Accuracy**  
   * Avoid aggressive thresholds  
   * Prefer consistent behavior over peak precision  
3. **Modular Design**  
   * Detection module can be disabled independently  
   * Simplifies debugging and testing

---

## **10\. Challenges Addressed by Part 3**

| Challenge | How It Is Addressed |
| ----- | ----- |
| Lack of labeled mine data | Anomaly-based detection framing |
| Small object visibility | GAN-enhanced inputs \+ YOLOv8 |
| False certainty | Confidence-based outputs |
| Real-time constraints | Lightweight Nano architecture |
| Ethical deployment | Human-in-the-loop design |

---

## **11\. Deliverables of Part 3**

At the end of Part 3, the system includes:

1. YOLOv8-Nano model loaded and configured  
2. Detection inference on enhanced images  
3. Bounding box visualization  
4. Confidence-scored detection outputs  
5. Clean separation from enhancement logic

---

## **12\. Completion Criteria for Part 3**

Part 3 is considered complete when:

* Detector runs reliably on enhanced frames  
* Outputs bounding boxes and confidence values  
* No crashes or unstable behavior observed  
* Detection logic can be explained clearly  
* No autonomous threat claims are made

---

# **PART 4: UNIFIED GAN → DETECTOR PIPELINE**

*(Normalization, Stability, and End-to-End Integration)*

---

## **1\. Objective of Part 4**

The objective of Part 4 is to **safely and reliably integrate the image enhancement module (FUnIE-GAN) with the detection module (YOLOv8-Nano)** into a single, unified inference pipeline.

This part ensures that:

* Data flows correctly between models  
* Mathematical assumptions of each model are respected  
* Real-time stability is maintained  
* Silent failures (black frames, false detections) are avoided

This stage transforms **independent ML components** into a **deployable perception system**.

---

## **2\. Why a Dedicated Integration Stage Is Necessary**

In real-time AI systems, failures rarely occur due to model architecture.  
They occur due to:

* Incorrect data ranges  
* Color space mismatches  
* Resolution incompatibilities  
* Framework-level tensor conversions  
* GPU ↔ CPU memory transfers

GANs and detectors are **not naturally compatible**.  
Without a carefully designed integration layer, the system may appear to run but produce meaningless outputs.

---

## **3\. The Core Integration Challenge**

The Jal-Drishti pipeline integrates **two fundamentally different models**:

| Component | FUnIE-GAN | YOLOv8 |
| ----- | ----- | ----- |
| Input range | `[-1, 1]` | `[0, 1]` |
| Resolution | `256 × 256` | `640 × 640` |
| Objective | Perceptual restoration | Object localization |
| Output type | Image tensor | Bounding boxes \+ scores |

Bridging these differences is the primary goal of Part 4\.

---

## **4\. The Normalization Bridge (Critical Design Element)**

### **4.1 Raw Image to GAN Input**

Raw underwater images arrive as:

* Range: `[0, 255]`  
* Type: `uint8`  
* Format: BGR (OpenCV default)

Before FUnIE-GAN inference:

1. Convert BGR → RGB  
2. Resize to `256 × 256`  
3. Normalize using:

\[  
x\_{GAN} \= \\frac{x\_{raw} \- 127.5}{127.5}  
\]

This maps values to `[-1, 1]`, matching the GAN’s Tanh activation.

Failure at this stage leads to:

* Black outputs  
* Color inversion  
* GAN instability

---

### **4.2 GAN Output to Detector Input**

FUnIE-GAN outputs:

* Range: `[-1, 1]`  
* Resolution: `256 × 256`

YOLOv8 expects:

* Range: `[0, 1]`  
* Resolution: `640 × 640`

Therefore, the **bridge transformation** is:

\[  
x\_{YOLO} \= \\frac{x\_{GAN\_out} \+ 1}{2}  
\]

This ensures:

* No clipping  
* No loss of contrast  
* Correct statistical distribution

---

### **4.3 Resolution Alignment**

GAN output is upscaled using:

* Bilinear interpolation  
* `align_corners = False`

This preserves:

* Edge continuity  
* Object boundaries  
* Small feature geometry

Naive resizing methods cause:

* Blurring of thin objects  
* Loss of small anomaly features

---

## **5\. Color Space Management**

### **5.1 Why Color Order Matters**

* OpenCV uses **BGR**  
* PyTorch models expect **RGB**

If color channels are not swapped:

* Red channel restoration (critical underwater) fails  
* Detector confidence degrades  
* Outputs become visually misleading

Therefore, a **mandatory channel reordering** is enforced:

img \= img\[:, :, \[2, 1, 0\]\]

This step is non-negotiable.

---

## **6\. Unified Runtime Design**

### **6.1 Single-Framework Constraint**

Both FUnIE-GAN and YOLOv8 are executed in:

* **Native PyTorch**  
* **Single CUDA context**

This avoids:

* Framework conflicts (TensorFlow vs PyTorch)  
* GPU memory duplication  
* Expensive CPU-GPU transfers

---

### **6.2 Zero-Copy Tensor Flow**

Once decoded:

* The image tensor remains on the GPU  
* GAN output feeds directly into YOLO  
* Data returns to CPU only at final output stage

This design significantly improves throughput and stability.

---

## **7\. Error Isolation and Debug Strategy**

Part 4 enforces **stepwise validation**:

1. Raw image → GAN output  
2. GAN output → visualization  
3. GAN output → YOLO input  
4. YOLO inference → detection metadata

Each stage can be independently tested and logged.

This prevents:

* Compound failures  
* Untraceable bugs  
* Silent inference errors

---

## **8\. Engineering Constraints for Real-Time Stability**

1. **Batch size fixed to 1**  
   * Streaming context  
   * Predictable latency  
2. **No dynamic graph construction**  
   * Models loaded once  
   * Inference-only mode  
3. **FP16 inference (where supported)**  
   * Reduced memory usage  
   * Faster execution  
4. **Asynchronous handling**  
   * Frame ingestion  
   * Inference  
   * Encoding handled separately

---

## **9\. Challenges Addressed by Part 4**

| Challenge | How Part 4 Solves It |
| ----- | ----- |
| Black or corrupted frames | Strict normalization bridge |
| Color distortion | Explicit BGR → RGB handling |
| Detection instability | Resolution and range alignment |
| Latency spikes | Zero-copy GPU pipeline |
| Debug complexity | Modular validation stages |

---

## **10\. Deliverables of Part 4**

At the completion of Part 4, the system includes:

1. A unified GAN → YOLO inference pipeline  
2. Explicit normalization and interpolation logic  
3. Stable end-to-end tensor flow  
4. Consistent detection outputs  
5. Debug-ready modular architecture

---

## **11\. Completion Criteria for Part 4**

Part 4 is considered complete when:

* A single frame can pass end-to-end through the pipeline  
* Enhanced image and detections are produced together  
* No black frames or invalid outputs occur  
* Pipeline runs continuously without memory leaks  
* All datatype and range transitions are documented and enforced

---

# **PART 5: REAL-TIME DEPLOYMENT, CONFIDENCE LOGIC, AND SYSTEM SAFETY**

*(Operational Readiness and Human-in-the-Loop Design)*

---

## **1\. Objective of Part 5**

The objective of Part 5 is to transform the unified ML pipeline into a **stable, real-time, and safety-aware operational system**.

This stage ensures that:

* The system works under continuous video streams  
* Latency remains within real-time limits  
* AI outputs are interpreted safely  
* Human operators retain final authority

Part 5 is where Jal-Drishti moves from a “working ML model” to a **deployable decision-support system**.

---

## **2\. Why Real-Time Constraints Are Critical in Maritime Security**

Maritime surveillance and underwater threat monitoring are **time-sensitive operations**. Delayed perception can result in:

* Missed threats  
* Incorrect situational awareness  
* Loss of operator trust

Human perception considers video to be “real-time” at approximately **12–15 FPS**.  
For Jal-Drishti, this translates to a strict **per-frame processing budget**.

---

## **3\. Real-Time Performance Targets**

### **3.1 Latency Budget**

For a target of 15 FPS:

\[  
\\text{Time per frame} \= \\frac{1000}{15} \\approx 66.6 \\text{ ms}  
\]

This includes:

* Frame reception  
* Image decoding  
* GAN inference  
* Detector inference  
* Encoding and transmission

Exceeding this budget causes perceptible lag.

---

### **3.2 Performance Strategy**

To remain within the time budget, Jal-Drishti adopts:

1. **Lightweight models**  
   * FUnIE-GAN (compact generator)  
   * YOLOv8-Nano  
2. **FP16 inference**  
   * Reduces computation cost  
   * Lowers GPU memory usage  
3. **Asynchronous pipeline**  
   * Frame ingestion  
   * Inference  
   * Output transmission handled independently  
4. **Frame skipping logic**  
   * Older frames dropped during congestion  
   * Only the most recent frame is processed

This prioritizes **situational awareness over frame completeness**.

---

## **4\. Streaming and Deployment Architecture**

### **4.1 Streaming Mechanism**

The system uses **WebSocket-based streaming** to enable:

* Low-latency bi-directional communication  
* Continuous frame transmission  
* Real-time feedback to the frontend

Frames are transmitted as:

* Binary blobs or base64-encoded images  
* Decoded and processed immediately on arrival

---

### **4.2 Deployment Environment**

For the MVP and demonstration phase:

* Cloud-based GPU deployment (e.g., NVIDIA T4)  
* Persistent inference server  
* No per-request model loading

This ensures:

* Predictable latency  
* Stable memory usage  
* Reproducible results

Edge deployment (Jetson, AUV integration) is identified as **future work**, not part of the current scope.

---

## **5\. Confidence-Driven Decision Framework**

### **5.1 Why Confidence Is Central to Safety**

In safety-critical environments:

* False positives cause unnecessary alarms  
* False negatives can be dangerous

Binary outputs (“threat / no threat”) are unsafe.

Therefore, Jal-Drishti uses **confidence-driven interpretation**, not hard decisions.

---

### **5.2 Confidence Threshold Design**

Each detection returned by the system includes a confidence score.

The system behavior is defined as follows:

| Confidence Range | System Interpretation |
| :---: | :---: |

0.75 | Confirmed Threat |  
0.40 – 0.75 | Potential Anomaly |  
\< 0.40 | Safe Mode |

These thresholds are configurable and conservative by design.

---

### **5.3 Operational Meaning**

* **Confirmed Threat**  
  * High-confidence anomaly  
  * Immediate operator attention required  
* **Potential Anomaly**  
  * Uncertain detection  
  * Manual verification encouraged  
* **Safe Mode**  
  * Visibility too poor or confidence too low  
  * System explicitly avoids misleading output

This prevents over-trust in AI predictions.

---

## **6\. Human-in-the-Loop Design**

### **6.1 Role of the AI System**

Jal-Drishti is designed as:

* A **decision-support system**  
* Not an autonomous defense weapon

The AI:

* Highlights regions of interest  
* Provides confidence-scored suggestions  
* Never initiates action independently

---

### **6.2 Role of the Human Operator**

The human operator:

* Interprets AI outputs  
* Confirms or dismisses detections  
* Retains final authority

This design aligns with:

* Defense safety norms  
* Ethical AI principles  
* Legal accountability requirements

---

## **7\. Long-Term Stability and Reliability Considerations**

### **7.1 Memory Management**

To ensure continuous operation:

* Models are loaded once at startup  
* Inference runs under `no_grad` mode  
* GPU memory usage is monitored  
* No dynamic tensor accumulation

---

### **7.2 Failure Handling**

The system explicitly handles:

* Poor visibility conditions  
* Low confidence detections  
* Temporary stream interruptions

Instead of failing silently, the system:

* Switches to Safe Mode  
* Alerts the operator  
* Preserves system integrity

---

## **8\. Challenges Addressed by Part 5**

| Challenge | How Part 5 Addresses It |
| ----- | ----- |
| Real-time lag | Strict latency budgeting and async processing |
| Operator overload | Confidence-based categorization |
| False positives | Conservative thresholds |
| Over-trust in AI | Human-in-the-loop enforcement |
| Long-duration instability | Controlled inference lifecycle |

---

## **9\. Deliverables of Part 5**

At the completion of Part 5, the system provides:

1. Continuous real-time video processing  
2. Confidence-scored detection outputs  
3. Safe-mode handling for low visibility  
4. Operator-friendly alerts and visualization  
5. Stable, long-running inference behavior

---

## **10\. Completion Criteria for Part 5**

Part 5 is considered complete when:

* The system processes streaming video continuously  
* End-to-end latency remains within acceptable limits  
* Confidence thresholds behave predictably  
* The operator clearly understands system outputs  
* The system never makes autonomous decisions

---

## **Final System Outcome**

With Part 5 complete, Jal-Drishti achieves:

* A scientifically grounded ML pipeline  
* Real-time operational feasibility  
* Safety-first design philosophy  
* Ethical and realistic defense positioning

This completes the **full 5-part ML execution pipeline** for Jal-Drishti.

---

