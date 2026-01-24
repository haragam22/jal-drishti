# Jal-Drishti ML Engine: Testing Guide

## Overview

This guide provides comprehensive testing procedures for the Jal-Drishti unified perception pipeline. Use this document to validate that the system meets its ideal conditions and operates correctly.

---

## Quick Start

### Single Image Test

```bash
cd c:\Users\Hp\Desktop\JalDrishti\Jal-Drishti\ml-engine\pipeline
python test_pipeline.py
```

### Multi-Image Test (5 images)

```bash
cd c:\Users\Hp\Desktop\JalDrishti\Jal-Drishti\ml-engine\pipeline
python test_pipeline.py --multi 5
```

---

## Ideal Conditions to Achieve

Based on the ML Execution Plan, the system should meet these targets:

| Metric | Target | How to Verify |
|--------|--------|---------------|
| Pipeline runs end-to-end | ✓ Without crashes | Run test_pipeline.py |
| Enhanced image quality | Visible improvement over raw | Compare raw vs enhanced output |
| Detection stability | Consistent bounding boxes | Run multi-image test |
| FPS (on GPU) | ≥ 15 FPS | Check FPS output in multi-image test |
| Latency per frame | < 100ms | Check inference time output |
| Memory leaks | None after 10+ min | Monitor with continuous test |
| Safe Mode trigger | Correct on low-visibility | Test with dark/turbid images |
| Confidence logic | Predictable thresholds | Check state classification |

---

## Test Procedures

### Test 1: Basic Pipeline Execution

**Purpose**: Verify the pipeline runs without crashes

**Steps**:
1. Navigate to `ml-engine/pipeline/`
2. Run: `python test_pipeline.py`
3. Observe the output

**Expected Results**:
- ✅ No Python exceptions
- ✅ "PIPELINE TEST COMPLETE" message appears
- ✅ Two output files created in `outputs/pipeline/`:
  - `enhanced_output.jpg`
  - `detected_output.jpg`

**Failure Indicators**:
- ❌ ImportError → Check dependencies installed
- ❌ FileNotFoundError → Check model weights exist
- ❌ CUDA error → Switch to CPU mode

---

### Test 2: Visual Enhancement Quality

**Purpose**: Verify GAN enhancement produces visible improvement

**Steps**:
1. Run the basic pipeline test
2. Open both images:
   - Raw input from `data/enhancement/raw/`
   - Enhanced output from `outputs/pipeline/enhanced_output.jpg`
3. Compare visually

**Expected Results**:
- ✅ Enhanced image has reduced green/blue color cast
- ✅ Improved contrast and visibility
- ✅ Objects are more distinguishable
- ✅ No black frames or artifacts

**Quality Checklist**:
| Aspect | Pass | Fail |
|--------|------|------|
| Color balance improved | □ | □ |
| Contrast enhanced | □ | □ |
| No black regions | □ | □ |
| No color artifacts | □ | □ |
| Edges preserved | □ | □ |

---

### Test 3: Detection Output Validation

**Purpose**: Verify YOLO detection produces valid outputs

**Steps**:
1. Run the basic pipeline test
2. Open `outputs/pipeline/detected_output.jpg`
3. Examine the JSON output printed to console

**Expected Results**:
- ✅ Image displays correctly (not black/corrupted)
- ✅ State indicator visible in top-left corner
- ✅ Bounding boxes (if any) are reasonable
- ✅ JSON output follows standardized schema

**JSON Output Validation**:
```json
{
  "timestamp": "ISO-8601 format",
  "state": "SAFE_MODE | POTENTIAL_ANOMALY | CONFIRMED_THREAT",
  "max_confidence": 0.0 to 1.0,
  "detections": [
    {
      "bbox": [x1, y1, x2, y2],
      "confidence": 0.0 to 1.0,
      "label": "anomaly"
    }
  ]
}
```

---

### Test 4: Confidence Threshold Verification

**Purpose**: Verify confidence classification works correctly

**Steps**:
1. Run pipeline on multiple images
2. Observe the state classification for each

**Expected Behavior**:

| Confidence Range | Expected State |
|:---:|:---:|
| 0.00 - 0.39 | SAFE_MODE |
| 0.40 - 0.74 | POTENTIAL_ANOMALY |
| 0.75 - 1.00 | CONFIRMED_THREAT |

**Verification**:
- [ ] Images with no detections → SAFE_MODE
- [ ] Low-confidence detections → SAFE_MODE
- [ ] Medium-confidence detections → POTENTIAL_ANOMALY
- [ ] High-confidence detections → CONFIRMED_THREAT

---

### Test 5: Multi-Image Stability Test

**Purpose**: Verify pipeline stability across many images

**Steps**:
1. Run: `python test_pipeline.py --multi 50`
2. Monitor the output

**Expected Results**:
- ✅ All images process without crashes
- ✅ FPS remains consistent
- ✅ No memory-related warnings
- ✅ State distribution is reasonable

**Metrics to Record**:
| Metric | Value |
|--------|-------|
| Total images processed | ____ |
| Total time (seconds) | ____ |
| Average FPS | ____ |
| SAFE_MODE count | ____ |
| POTENTIAL_ANOMALY count | ____ |
| CONFIRMED_THREAT count | ____ |

---

### Test 6: Frame Validity Gate

**Purpose**: Verify invalid frames don't crash the pipeline

**Steps**:
1. Create a test script that passes invalid inputs:

```python
from pipeline import JalDrishtiPipeline
import numpy as np

pipeline = JalDrishtiPipeline()

# Test 1: None input
result = pipeline.run(image_array=None)
assert result['state'] == 'SAFE_MODE'
assert 'error' in result
print("✅ None input handled correctly")

# Test 2: Empty array
result = pipeline.run(image_array=np.array([]))
assert result['state'] == 'SAFE_MODE'
assert 'error' in result
print("✅ Empty array handled correctly")

# Test 3: Wrong dimensions
result = pipeline.run(image_array=np.zeros((100, 100)))
assert result['state'] == 'SAFE_MODE'
assert 'error' in result
print("✅ Wrong dimensions handled correctly")

print("\n🎉 All frame validity tests passed!")
```

**Expected Results**:
- ✅ All invalid inputs return SAFE_MODE
- ✅ No exceptions raised
- ✅ Error messages are descriptive

---

### Test 7: Performance Benchmarking

**Purpose**: Measure inference latency

**Steps**:
1. Modify test to measure individual step times:

```python
import time
from pipeline import JalDrishtiPipeline

pipeline = JalDrishtiPipeline()
image_path = "../data/enhancement/raw/<sample_image>.jpg"

# Warm-up run
_ = pipeline.run(image_path=image_path)

# Timed run
start = time.time()
for i in range(10):
    result = pipeline.run(image_path=image_path)
elapsed = time.time() - start

avg_time = elapsed / 10
fps = 10 / elapsed

print(f"Average time per frame: {avg_time * 1000:.2f} ms")
print(f"Effective FPS: {fps:.2f}")
```

**Target Metrics**:
| Device | Target FPS | Target Latency |
|--------|------------|----------------|
| GPU (CUDA) | ≥ 15 FPS | < 66 ms |
| CPU | ≥ 2 FPS | < 500 ms |

---

### Test 8: Continuous Operation (Stability)

**Purpose**: Verify no memory leaks during extended operation

**Steps**:
1. Run multi-image test with large count: `python test_pipeline.py --multi 200`
2. Monitor system memory during execution
3. Check for increasing memory usage

**Expected Results**:
- ✅ Memory usage stays constant
- ✅ No GPU memory errors
- ✅ Processing speed doesn't degrade

**Memory Monitoring (Windows)**:
```bash
# Open Task Manager and observe Python process memory
# Or use:
Get-Process python | Select-Object WorkingSet64
```

---

### Test 9: Safe Mode Trigger Conditions

**Purpose**: Verify Safe Mode activates appropriately

**Test Cases**:

| Scenario | Expected State |
|----------|----------------|
| Clear underwater image | Depends on detections |
| Very dark/low-light image | SAFE_MODE (low confidence) |
| High turbidity/hazy image | SAFE_MODE (poor visibility) |
| Image with no detectable objects | SAFE_MODE (no detections) |
| Image with clear object | POTENTIAL_ANOMALY or higher |

**Manual Verification**:
1. Find or create test images for each scenario
2. Run pipeline on each
3. Verify state matches expectations

---

### Test 10: Output File Integrity

**Purpose**: Verify output files are valid images

**Steps**:
1. Run pipeline test
2. Verify output files:

```python
import cv2
import os

output_dir = "../outputs/pipeline/"

# Check enhanced output
enhanced = cv2.imread(os.path.join(output_dir, "enhanced_output.jpg"))
assert enhanced is not None, "Enhanced image not readable"
assert enhanced.shape == (256, 256, 3), f"Wrong shape: {enhanced.shape}"
print("✅ Enhanced output valid")

# Check detection output
detected = cv2.imread(os.path.join(output_dir, "detected_output.jpg"))
assert detected is not None, "Detection image not readable"
assert detected.shape == (640, 640, 3), f"Wrong shape: {detected.shape}"
print("✅ Detection output valid")

print("\n🎉 Output file integrity verified!")
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: CUDA Out of Memory

**Symptoms**: 
```
RuntimeError: CUDA out of memory
```

**Solutions**:
1. Use CPU mode: Set `device="cpu"` in pipeline init
2. Enable FP16: Set `use_fp16=True`
3. Close other GPU applications

---

#### Issue: Model Loading Fails

**Symptoms**:
```
FileNotFoundError: No such file or directory
```

**Solutions**:
1. Verify model paths exist:
   - `enhancement/funie_gan/weights/funie_generator.pth`
   - `detection/yolov8n.pt`
2. Re-download weights if missing

---

#### Issue: Black Output Images

**Symptoms**: Enhanced or detected images are completely black

**Solutions**:
1. Verify normalization is correct
2. Check input image is valid (not corrupted)
3. Verify color conversion BGR→RGB is applied

---

#### Issue: No Detections Found

**Symptoms**: All images return empty detections

**Notes**: 
- This is often **expected behavior** for underwater images
- YOLOv8n is pretrained on COCO, not underwater anomalies
- Low/no detections indicate Safe Mode is working correctly

---

## Test Results Template

Use this template to record your test results:

```
=================================================
JAL-DRISHTI PIPELINE TEST RESULTS
=================================================
Date: _______________
Tester: _______________
Device: □ CPU  □ GPU (Model: _____________)

BASIC TESTS
-----------
[ ] Test 1: Basic Pipeline Execution    PASS / FAIL
[ ] Test 2: Visual Enhancement Quality  PASS / FAIL
[ ] Test 3: Detection Output Validation PASS / FAIL
[ ] Test 4: Confidence Thresholds       PASS / FAIL
[ ] Test 5: Multi-Image Stability       PASS / FAIL

ADVANCED TESTS
--------------
[ ] Test 6: Frame Validity Gate         PASS / FAIL
[ ] Test 7: Performance Benchmarking    PASS / FAIL
    - Average FPS: ______
    - Average Latency: ______ ms
[ ] Test 8: Continuous Operation        PASS / FAIL
    - Duration: ______ minutes
    - Memory stable: YES / NO
[ ] Test 9: Safe Mode Triggers          PASS / FAIL
[ ] Test 10: Output File Integrity      PASS / FAIL

OVERALL RESULT: PASS / FAIL

NOTES:
_________________________________________________
_________________________________________________
_________________________________________________
=================================================
```

---

## Comparison: Ideal vs Actual

After running tests, compare your results to the ideal conditions:

| Metric | Ideal | Actual | Status |
|--------|-------|--------|--------|
| Runs end-to-end | ✓ | | □ Pass □ Fail |
| No crashes | ✓ | | □ Pass □ Fail |
| Enhanced visible improvement | ✓ | | □ Pass □ Fail |
| Consistent detections | ✓ | | □ Pass □ Fail |
| FPS ≥ 15 (GPU) | ✓ | ______ | □ Pass □ Fail |
| Latency < 100ms | ✓ | ______ ms | □ Pass □ Fail |
| No memory leaks | ✓ | | □ Pass □ Fail |
| Safe Mode works | ✓ | | □ Pass □ Fail |
| Confidence correct | ✓ | | □ Pass □ Fail |
| JSON schema valid | ✓ | | □ Pass □ Fail |

---

## Conclusion

Once all tests pass, the Jal-Drishti ML pipeline is verified as:

- ✅ **Functional**: End-to-end processing works
- ✅ **Stable**: No crashes under extended operation
- ✅ **Safe**: Confidence logic and Safe Mode work correctly
- ✅ **Performant**: Meets real-time constraints on GPU
- ✅ **Integrated**: Ready for backend/frontend connection

The system is now ready for deployment and demonstration.
