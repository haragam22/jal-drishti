# **PHASE-3 (CORE): REAL-TIME OPTIMIZATION & DEPLOYMENT-READY EXECUTION PLAN**

**Project: Jal-Drishti (AI-Powered Maritime Perception System)**

---

## **1\. Background and Context**

Jal-Drishti has already completed its foundational and integration phases.

### **Phase-1 established correctness**

* Underwater dataset strategy finalized  
* FUnIE-GAN for image enhancement validated  
* YOLOv8-Nano for anomaly detection integrated  
* Ethical framing adopted: anomaly detection, not weapon classification

### **Phase-2 established system integration**

* Backend, ML engine, and frontend connected  
* Frame-based video simulation implemented  
* Unified GAN → YOLO pipeline verified  
* Confidence-based safety logic introduced  
* End-to-end real-time prototype demonstrated (primarily CPU-based)

Phase-2 successfully proved that the **system works functionally**.

---

## **2\. Purpose of Phase-3 (CORE)**

Phase-3 CORE exists to **transform a working prototype into a deployment-ready, real-world usable system**, without changing its validated architecture.

### **Phase-3 CORE is NOT about**

* Improving benchmark accuracy  
* Training new models  
* Advanced research features  
* Heavy visual polish  
* Architectural redesign

### **Phase-3 CORE IS about**

* Real-time performance  
* Stability over long runs  
* Hardware realism (GPU execution)  
* Safe and predictable behavior  
* Deployment readiness

In simple terms:

**Phase-3 CORE focuses on execution quality, not new capability.**

---

## **3\. Definition of Success for Phase-3 CORE**

Phase-3 CORE is considered successful when the system:

* Runs correctly on **GPU (CUDA)**  
* Maintains **stable 12–15 FPS**  
* Keeps **end-to-end latency below \~80 ms**  
* Works with **at least one real live video source**  
* Runs continuously for extended periods without crashes  
* Preserves all confidence and safety logic  
* Has a frozen, stable architecture suitable for demonstration and evaluation

---

## **4\. Core Design Principles (Non-Negotiable)**

The following principles govern all Phase-3 CORE work:

1. **No architectural rewrites**  
2. **No new ML models introduced**  
3. **One change at a time**  
4. **Stability over optimization**  
5. **Correctness over perfection**  
6. **Graceful degradation over hard failure**

These principles exist to prevent late-stage system breakage.

---

## **5\. System Architecture (Unchanged)**

The overall system architecture remains identical to Phase-2.  
Phase-3 CORE only optimizes execution and behavior.

Video / Live Source

        ↓

Backend Frame Extraction

        ↓

Frame Scheduler (Drop Old Frames)

        ↓

ML Engine (GPU)

   ├─ FUnIE-GAN (FP16)

   └─ YOLOv8-Nano (FP16)

        ↓

Confidence & Safety Logic

        ↓

Frontend Visualization

**Component responsibilities do not change in Phase-3 CORE.**

---

## **6\. Phase-3 CORE Execution Plan (Detailed)**

---

### **Step 1: GPU Enablement**

#### **Objective**

Enable GPU acceleration safely for the entire ML pipeline.

#### **Work to be Done**

* Install CUDA-enabled PyTorch  
* Detect GPU availability at runtime  
* Load GAN and YOLO models on GPU **once at startup**  
* Ensure inference runs under `torch.no_grad()`

#### **Important Refinement**

GPU acceleration is an **optimization**, not a hard dependency.

* If GPU is available → system runs faster  
* If GPU is not available → system still runs (CPU fallback), but slower

The system must **never fail due to missing GPU**.

#### **Validation Criteria**

* Logs clearly indicate active device (`cuda` or `cpu`)  
* Output behavior remains identical to Phase-2  
* Only performance changes, not logic

---

### **Step 2: FP16 (Half-Precision) Inference**

#### **Objective**

Reduce latency and GPU memory usage while preserving correctness.

#### **Work to be Done**

* Enable FP16 inference for GAN and YOLO  
* Use automatic mixed precision on GPU  
* Keep preprocessing steps in FP32 for numerical safety

#### **Why This Matters**

* FP16 leverages modern GPU tensor cores  
* Improves FPS significantly  
* Industry-standard for real-time vision systems

#### **Validation Criteria**

* No NaN values or corrupted outputs  
* No visible change in enhanced images or detections  
* Measurable performance improvement

---

### **Step 3: Stable FPS and Latency Control**

#### **Objective**

Achieve **consistent real-time performance**, not peak speed.

#### **Target**

* FPS: **12–15 (stable)**  
* Latency: **\< 80 ms per frame**

#### **Work to be Done**

* Tune backend frame scheduler  
* Enforce “latest-frame-only” processing  
* Drop old frames aggressively under load

#### **Key Refinement**

Consistency is more important than maximum FPS.

Surveillance and monitoring systems prioritize **fresh information**, not completeness.

#### **Validation Criteria**

* FPS does not oscillate heavily  
* Latency does not increase over time  
* Frame dropping is controlled and logged

---

### **Step 4: Real Live Video Source Integration**

#### **Objective**

Demonstrate real-world realism beyond offline video simulation.

#### **Allowed Sources**

* Mobile phone used as camera  
* USB webcam  
* IP / RTSP stream  
* Network video feed

#### **Critical Rule**

The **ML engine never handles video decoding**.

* Backend handles all video ingestion  
* ML engine receives frames only

#### **Refinement (Important)**

* Video simulation remains the **default mode**  
* Live streaming is **optional**, not mandatory  
* Lack of live camera must never break the demo

#### **Validation Criteria**

* Continuous live feed works  
* Performance remains within limits  
* No memory leaks or crashes

---

### **Step 5: Long-Run Stability Testing**

#### **Objective**

Ensure the system survives real operational conditions.

#### **Test Conditions**

* Continuous runtime: **10–15 minutes minimum**  
* Live or simulated input  
* No restarts

#### **What to Observe**

* FPS stability  
* Memory usage  
* GPU utilization  
* No performance degradation

#### **Why This Matters**

Most real-world failures occur **over time**, not immediately.

#### **Validation Criteria**

* No crashes  
* No FPS decay  
* No memory growth

---

### **Step 6: Confidence & Safety Behavior Finalization**

#### **Objective**

Make system behavior predictable and conservative.

#### **Work to be Done**

* Finalize confidence thresholds  
* Smooth confidence fluctuations  
* Prevent alert spamming  
* Ensure SAFE MODE dominates during uncertainty

#### **Refinement**

The AI must **never over-claim certainty**.

When visibility or confidence is low:

* The system must clearly indicate uncertainty  
* No aggressive alerts should be raised

---

### **Step 7: Configuration-Driven Control**

#### **Objective**

Remove hard-coded behavior.

#### **Work to be Done**

* Move parameters to configuration:  
  * FPS limits  
  * Confidence thresholds  
  * Live vs simulation mode  
* Allow behavior changes without code modification

#### **Benefit**

* Easier testing  
* Safer tuning  
* More professional deployment behavior

---

### **Step 8: Failure Handling and Defensive Design**

#### **Expected Failure Scenarios**

* ML inference slowdown  
* GPU unavailable  
* Corrupted video frames  
* Network disconnects

#### **Required Behavior**

* System must not crash  
* SAFE MODE must be activated  
* Operator must be clearly informed

The system should **fail safely, not silently**.

---

### **Step 9: Architecture Freeze**

#### **Objective**

Prevent last-minute instability.

#### **Work to be Done**

* Freeze pipeline structure  
* Freeze data flow  
* Freeze interfaces

After this point:

* Only parameter tuning allowed  
* No refactors  
* No feature additions

---

## **7\. Explicit Exclusions from Phase-3 CORE**

The following are intentionally excluded:

* YOLO fine-tuning  
* GAN retraining  
* Object tracking  
* Multi-camera fusion  
* Hardware-specific kernel optimization

These may be addressed in future phases or documented as extensions.

---

## 

## 

## 

## **8\. Risks and Mitigation**

| Risk | Mitigation |
| ----- | ----- |
| GPU issues | Enable incrementally |
| Performance regression | Benchmark after each step |
| System instability | One change at a time |
| Over-optimization | Architecture freeze |

---

## **9\. Final Deliverables of Phase-3 CORE**

At completion, Jal-Drishti will have:

* GPU-accelerated ML pipeline  
* Stable real-time performance  
* Live video capability with fallback  
* Conservative, safety-aware outputs  
* Long-run stability  
* Deployment-ready, review-ready system

---

## **10\. Final Statement**

**Phase-3 CORE focuses on execution quality, stability, and real-world readiness without altering the validated system architecture.**  
It transforms the Phase-2 prototype into a stable, GPU-accelerated, real-time underwater perception system suitable for deployment, demonstration, and evaluation.

## **Phase-3 CORE Addition: Visual Anomaly Event Logging**

### **Objective**

Introduce visual anomaly event logging in the frontend to ensure **traceability, transparency, and auditability** of detected anomalies during real-time operation.

This enhancement ensures that whenever the system flags an anomaly, a visual snapshot of that moment is preserved and made accessible to the operator.

---

### **Rationale for Inclusion in Phase-3 CORE**

Visual event logging is considered **core system behavior**, not a cosmetic UI feature, because:

* Safety-critical systems must provide **evidence of detection events**

* Operators and reviewers must be able to verify:

  * *When* an anomaly was detected

  * *What the system saw* at that moment

* It supports debugging, demonstration, and post-analysis

* It increases trust in AI-assisted decision-support systems

Therefore, anomaly image logging is treated as a **mandatory Phase-3 CORE capability**.

---

### **Functional Description**

Whenever the system enters a non-safe state:

* `POTENTIAL_ANOMALY`

* `CONFIRMED_THREAT`

the frontend must automatically capture and store the corresponding **enhanced frame** as a visual log entry.

Each anomaly event generates a single log entry containing:

* Timestamp of detection

* Enhanced image frame (snapshot)

* System state

* Confidence score

No logging occurs while the system is in `SAFE_MODE`.

---

### **System Behavior Flow**

1. **ML Engine Output**  
    The ML engine already produces:

   * System state

   * Confidence score

   * Enhanced frame (encoded as image data)

2. **Backend Forwarding**  
    The backend forwards this data to the frontend **without modification**.

3. **Frontend Event Capture**  
    The frontend monitors incoming system states.

   * If the state is not `SAFE_MODE`, the event is added to the anomaly log.

   * The log is maintained locally in frontend memory.

---

### **Frontend Log Management Rules**

To ensure stability and performance:

* Only the **latest N anomaly events** (e.g., 10–20) are retained

* Older entries are automatically discarded

* Logs are **visual references only**, not persistent storage

* No database or backend storage is required

---

### **User Interface Expectations**

* An “Anomaly Event Log” panel is displayed in the dashboard

* Each log entry includes:

  * A small image thumbnail

  * Timestamp

  * System state (Potential / Confirmed)

  * Confidence percentage

* Clicking an entry allows the operator to visually review the anomaly

---

### **Safety and Stability Considerations**

* SAFE\_MODE frames are never logged

* Logging does not affect inference speed

* Logging does not block the real-time pipeline

* Memory usage is bounded and predictable

---

### **Outcome of This Core Addition**

At the end of Phase-3 CORE:

* Every anomaly has **visual evidence**

* Operators gain historical awareness of detections

* The system becomes **traceable and review-ready**

* The dashboard behaves like a real monitoring console rather than a live video viewer

