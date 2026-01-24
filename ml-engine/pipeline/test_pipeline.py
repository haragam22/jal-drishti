"""
Jal-Drishti Pipeline Test Script
================================

This script validates the unified GAN → YOLO pipeline by:
1. Loading a raw underwater image
2. Running the full JalDrishtiPipeline
3. Saving enhanced and detected outputs
4. Printing confidence values and detection results

Usage:
    cd ml-engine/pipeline
    python test_pipeline.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
from pipeline import JalDrishtiPipeline, SystemState


def run_pipeline_test():
    """Run a single test through the pipeline."""
    
    print("=" * 70)
    print("🌊 JAL-DRISHTI UNIFIED PIPELINE TEST")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Paths
    base_path = Path(__file__).parent.parent
    input_dir = base_path / "data" / "enhancement" / "raw"
    output_dir = base_path / "outputs" / "pipeline"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find test images
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [f for f in input_dir.iterdir() if f.suffix.lower() in image_extensions]
    
    if not image_files:
        print(f"❌ No images found in: {input_dir}")
        print("Please ensure Part-1 dataset is properly set up.")
        return
    
    # Use first available image
    test_image = image_files[0]
    print(f"📁 Input directory: {input_dir}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📷 Test image: {test_image.name}")
    print()
    
    # Initialize pipeline
    print("-" * 70)
    print("🔧 INITIALIZING PIPELINE")
    print("-" * 70)
    
    try:
        pipeline = JalDrishtiPipeline()
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        return
    
    print()
    
    # Run inference
    print("-" * 70)
    print("🚀 RUNNING INFERENCE")
    print("-" * 70)
    
    start_time = datetime.now()
    result = pipeline.run(image_path=str(test_image))
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print(f"⏱️  Inference time: {elapsed:.3f} seconds")
    print()
    
    # Display results
    print("-" * 70)
    print("📊 DETECTION RESULTS")
    print("-" * 70)
    
    print(f"📅 Timestamp: {result['timestamp']}")
    print(f"🎯 System State: {result['state']}")
    print(f"📈 Max Confidence: {result['max_confidence']:.4f}")
    print(f"🔍 Detections Found: {len(result['detections'])}")
    print()
    
    # Check for errors
    if "error" in result:
        print(f"⚠️  Error: {result['error']}")
        return
    
    # Display individual detections
    if result['detections']:
        print("📋 Detection Details:")
        for idx, det in enumerate(result['detections'], 1):
            bbox = det['bbox']
            print(f"   {idx}. Label: {det['label']}")
            print(f"      Confidence: {det['confidence']:.4f}")
            print(f"      BBox: [{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]")
            print()
    else:
        print("ℹ️  No detections above threshold (this is expected for many underwater images)")
        print()
    
    # Display state interpretation
    print("-" * 70)
    print("🔐 CONFIDENCE INTERPRETATION")
    print("-" * 70)
    
    state = result['state']
    if state == SystemState.CONFIRMED_THREAT.value:
        print("🔴 CONFIRMED THREAT")
        print("   → High confidence visual anomaly detected")
        print("   → Immediate operator attention required")
    elif state == SystemState.POTENTIAL_ANOMALY.value:
        print("🟠 POTENTIAL ANOMALY")
        print("   → Uncertain detection")
        print("   → Manual verification encouraged")
    else:
        print("🟢 SAFE MODE")
        print("   → Low confidence or no detections")
        print("   → System continues monitoring without alerts")
    
    print()
    
    # Save outputs
    print("-" * 70)
    print("💾 SAVING OUTPUTS")
    print("-" * 70)
    
    if result['enhanced_image'] is not None:
        enhanced_path = output_dir / "enhanced_output.jpg"
        cv2.imwrite(str(enhanced_path), result['enhanced_image'])
        print(f"✅ Enhanced image saved: {enhanced_path}")
    
    if result['detection_image'] is not None:
        detected_path = output_dir / "detected_output.jpg"
        cv2.imwrite(str(detected_path), result['detection_image'])
        print(f"✅ Detection image saved: {detected_path}")
    
    print()
    
    # Summary
    print("=" * 70)
    print("✨ PIPELINE TEST COMPLETE")
    print("=" * 70)
    print()
    print("📝 JSON Output Schema (for backend integration):")
    print()
    
    # Print JSON-compatible output (without numpy arrays)
    json_output = {
        "timestamp": result['timestamp'],
        "state": result['state'],
        "max_confidence": result['max_confidence'],
        "detections": result['detections']
    }
    
    import json
    print(json.dumps(json_output, indent=2))
    print()
    
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return result


def run_multi_image_test(num_images: int = 5):
    """Run test on multiple images."""
    
    print("\n" + "=" * 70)
    print("🔄 MULTI-IMAGE STABILITY TEST")
    print("=" * 70 + "\n")
    
    base_path = Path(__file__).parent.parent
    input_dir = base_path / "data" / "enhancement" / "raw"
    output_dir = base_path / "outputs" / "pipeline" / "multi_test"
    
    # Find images
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [str(f) for f in input_dir.iterdir() if f.suffix.lower() in image_extensions]
    
    # Limit to requested number
    test_images = image_files[:num_images]
    
    if not test_images:
        print(f"❌ No images found in: {input_dir}")
        return
    
    print(f"📷 Testing with {len(test_images)} images")
    print()
    
    # Initialize pipeline
    pipeline = JalDrishtiPipeline()
    
    # Run continuous test
    summary = pipeline.run_continuous(
        image_paths=test_images,
        output_dir=str(output_dir),
        save_outputs=True
    )
    
    # Display summary
    print("\n" + "-" * 70)
    print("📊 TEST SUMMARY")
    print("-" * 70)
    print(f"Total images processed: {summary['total_images']}")
    print(f"Total time: {summary['elapsed_seconds']:.2f} seconds")
    print(f"Average FPS: {summary['fps']:.2f}")
    print()
    print("State Distribution:")
    for state, count in summary['state_distribution'].items():
        pct = (count / summary['total_images']) * 100 if summary['total_images'] > 0 else 0
        print(f"  - {state}: {count} ({pct:.1f}%)")
    
    print()
    print(f"📁 Outputs saved to: {output_dir}")
    print("=" * 70 + "\n")
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Jal-Drishti Pipeline")
    parser.add_argument('--multi', type=int, default=0, 
                        help='Run multi-image test with N images')
    
    args = parser.parse_args()
    
    if args.multi > 0:
        run_multi_image_test(num_images=args.multi)
    else:
        run_pipeline_test()
