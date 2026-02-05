## **PHASE-3 CORE – SOURCE CONTROL, STREAMING STABILITY & UX OPTIMIZATION**

---

## **OBJECTIVE**

Enable **runtime source switching** (Video ↔ External Camera) **without restarting backend**, ensure **smooth raw & enhanced streaming**, and eliminate **frame drops & flickering**, while keeping the UX simple and production-ready.

---

## **FINAL USER EXPERIENCE (TARGET)**

1. User starts backend **once**  
2. Opens dashboard  
3. Chooses:  
   * 🎞️ **Video File**  
   * 📱 **Camera (External Device Only)**  
4. If **Video**:  
   * User uploads any video  
   * Streaming starts immediately  
5. If **Camera**:  
   * System shows **instructions**  
   * System shows **auto-generated URL with correct IP**  
   * User opens URL on phone  
   * Camera permission → streaming starts automatically  
6. No server restart, no env vars, no flicker

---

## **PART 1: BACKEND – REMOVE STARTUP SOURCE BINDING**

### **(Critical Architecture Fix)**

### **❌ OLD (Problematic)**

$env:INPUT\_SOURCE=phone  
python \-m uvicorn app.main:app

### **✅ NEW (Correct)**

* Backend **never decides source at startup**  
* Backend always starts in **IDLE mode**  
* Source is selected **at runtime via API**

### **Tasks**

* Remove all logic depending on `INPUT_SOURCE`  
* On startup:  
  * Scheduler starts  
  * No source attached  
  * ML engine warms up only

---

## **PART 2: SOURCE SELECTION API (CONTROL PLANE)**

### **New API**

POST /api/source/select

### **Payload**

{  
  "type": "video" | "camera",  
  "video\_file": "optional"  
}

### **Backend Logic**

* If a source is already active:  
  * Gracefully stop it  
  * Flush scheduler queues  
  * Reset counters  
* Attach new source  
* Resume scheduler

---

## **PART 3: VIDEO SOURCE FLOW (UPLOAD & PLAY)**

### **Frontend**

* File picker → upload video  
* Call `/api/source/select` with `{ type: "video" }`

### **Backend**

* Initialize `VideoReader`  
* Feed frames into scheduler  
* ML \+ streaming continue as usual

---

## **PART 4: CAMERA SOURCE (EXTERNAL DEVICE ONLY)**

### **Key Change (As Requested)**

❌ No laptop camera  
✅ **ONLY external device (phone) camera**

---

### **Backend – Auto IP Detection**

Create utility function:

def get\_lan\_ip():  
    \# returns something like 192.168.1.11

Expose API:

GET /api/server/info

Response:

{  
  "ip": "192.168.1.11",  
  "port": 9000,  
  "camera\_url": "http://192.168.1.11:9000/static/phone\_camera.html"  
}

**Purpose**

* No hardcoded IPs  
* Fixes “URL suddenly stopped working” issue permanently

---

### **Frontend – Camera Selection UX**

When user selects **Camera**:

Show:

* Step-by-step instructions  
* Auto-generated URL (copy button)  
* Optional QR code (future enhancement)

Example:

1\. Connect your phone to the same Wi-Fi  
2\. Open this URL on your phone:  
   http://192.168.1.11:9000/static/phone\_camera.html  
3\. Allow camera permission  
4\. Streaming will start automatically

---

### **Phone Camera Behavior**

* Browser requests camera permission  
* Streams frames via WebSocket `/ws/upload`  
* Backend detects first frame  
* Automatically activates phone camera source

---

## **PART 5: FRAME DROPS – ROOT CAUSE & FIXES**

### **Root Causes (Confirmed)**

| Cause | Status |
| ----- | ----- |
| MAX\_CACHE\_AGE \= 0.25s dropping frames | ✅ FIXED |
| Target FPS set too low | ✅ FIXED |
| ML single in-flight causing skips | ⚠️ PARTIALLY FIXED |
| Emission tied to ML availability | ⚠️ PARTIALLY FIXED |

---

### **Backend Fixes (Final)**

#### **1\. Scheduler Emission Rule**

* **Emit on every tick**  
* Even if ML is busy, reuse last enhanced frame  
* Never stall raw feed

#### **2\. ML Admission Control**

* Keep **1 in-flight ML task**  
* If busy:  
  * Skip inference  
  * Do NOT skip emission

#### **3\. Timestamp Discipline**

* Frame timestamp \= capture time  
* Latency \= `now - timestamp`  
* No recalculation on resend

**Status:**

* MAX\_CACHE\_AGE → ✅ DONE  
* Target FPS → ✅ DONE  
* Remaining logic → ⬜ To be refined

---

## **PART 6: SMOOTH STREAMING (MOST IMPORTANT VISUAL FIX)**

### **Why Flicker Happens (Truth)**

* WebSocket frames arrive in bursts  
* Browser render loop ≠ backend FPS  
* Canvas cleared when no new frame arrives

---

### **Frontend Fix (Required)**

#### **1\. Frame Buffer**

Maintain:

let lastRawFrame \= null;  
let lastEnhancedFrame \= null;

#### **2\. Render Loop (Decoupled)**

* Use `requestAnimationFrame`  
* Always render last available frame  
* Do NOT wait for new WS frame

#### **3\. Never Clear Canvas**

* If no new frame → redraw last frame

#### **4\. Display FPS ≠ Backend FPS**

* UI FPS can be 60  
* Actual ML FPS remains 12 (correct)

**Result**

* No flicker  
* No black frames  
* Perceived smoothness

---

## **PART 7: CONNECTION STABILITY RULES**

### **Backend**

* Allow **single client per feed**  
* Do NOT kick on reconnect unless idle timeout exceeded  
* Graceful WS close handling

### **Frontend**

* Reconnect only if disconnected for \> X ms  
* Do not spam reconnects

**Status:** ⚠️ Needs minor tuning

---

## **FINAL DELIVERABLE – WORK COMPLETION DOC**

### **📄 PHASE-3 CORE – COMPLETION SUMMARY**

#### **✅ Completed**

* GPU ML engine separation  
* ML FPS stabilization (≈12)  
* MAX\_CACHE\_AGE frame drop fix  
* Target FPS correction  
* Phone camera streaming  
* Raw \+ enhanced dual feed

#### **🟡 In Progress / To Do**

* Runtime source switching (no restart)  
* Auto IP \+ camera URL generation  
* Frontend smooth streaming buffer  
* Camera-only external device UX

#### **❌ Deprecated / Removed**

* INPUT\_SOURCE env variable  
* Startup source binding  
* Laptop camera path

