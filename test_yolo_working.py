#!/usr/bin/env python3
"""
Test if YOLO detection works with the installed dependencies.
"""

import cv2
import torch
from ultralytics import YOLO
import numpy as np
import time
import sys
import os

print("🧪 Testing YOLO detection with installed dependencies...")
print("=" * 60)

# Test 1: Check imports
print("1. Checking imports...")
try:
    print(f"   ✅ OpenCV version: {cv2.__version__}")
    print(f"   ✅ PyTorch version: {torch.__version__}")
    print(f"   ✅ CUDA available: {torch.cuda.is_available()}")
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Create a test image
print("\n2. Creating test image...")
try:
    # Create a simple test image (red square on black background)
    test_image = np.zeros((300, 300, 3), dtype=np.uint8)
    test_image[100:200, 100:200] = [0, 0, 255]  # Red square
    print("   ✅ Test image created")
except Exception as e:
    print(f"   ❌ Image creation error: {e}")
    sys.exit(1)

# Test 3: Try to load YOLO model
print("\n3. Loading YOLO model...")
try:
    start_time = time.time()
    # Try to load the YOLOv8n model (smallest, should download automatically)
    model = YOLO('yolov8n.pt')
    load_time = time.time() - start_time
    print(f"   ✅ YOLO model loaded in {load_time:.2f} seconds")
    print(f"   ✅ Model: {model.__class__.__name__}")
except Exception as e:
    print(f"   ❌ YOLO model loading error: {e}")
    print("   ℹ️  Trying alternative model...")
    try:
        # Try with yolov8n if yolov8n.pt fails
        model = YOLO('yolov8n')
        print("   ✅ YOLO model loaded (alternative)")
    except Exception as e2:
        print(f"   ❌ Alternative model also failed: {e2}")
        sys.exit(1)

# Test 4: Run inference
print("\n4. Running inference on test image...")
try:
    start_time = time.time()
    results = model(test_image, verbose=False)
    inference_time = time.time() - start_time
    
    print(f"   ✅ Inference completed in {inference_time:.2f} seconds")
    
    # Check if any objects were detected
    if len(results) > 0:
        result = results[0]
        if len(result.boxes) > 0:
            print(f"   ✅ Detected {len(result.boxes)} objects")
            for i, box in enumerate(result.boxes[:3]):  # Show first 3
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                cls_name = result.names[cls_id]
                print(f"      {i+1}. {cls_name} (confidence: {conf:.2f})")
        else:
            print("   ⚠️  No objects detected (expected for simple test image)")
    else:
        print("   ⚠️  No results returned")
        
except Exception as e:
    print(f"   ❌ Inference error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test the subprocess call that the camera uses
print("\n5. Testing subprocess detection (like camera.py does)...")
try:
    import subprocess
    import json
    import tempfile
    
    # Save test image to temp file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        temp_path = f.name
        cv2.imwrite(temp_path, test_image)
    
    # Run the yolo_detector.py script
    script_path = os.path.join(os.path.dirname(__file__), "vision", "yolo_detector.py")
    
    if os.path.exists(script_path):
        print(f"   ✅ Found detector script: {script_path}")
        
        # Run with timeout
        start_time = time.time()
        result = subprocess.run(
            ["python", script_path, temp_path],
            capture_output=True,
            text=True,
            timeout=5.0
        )
        subprocess_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ Subprocess completed in {subprocess_time:.2f} seconds")
            try:
                detected = json.loads(result.stdout.strip())
                print(f"   ✅ Parsed JSON output: {len(detected)} objects")
                for obj in detected[:3]:
                    print(f"      - {obj['name']} (conf: {obj['confidence']:.2f})")
            except json.JSONDecodeError:
                print(f"   ❌ Failed to parse JSON: {result.stdout[:100]}")
        else:
            print(f"   ❌ Subprocess failed (code {result.returncode}): {result.stderr[:200]}")
    else:
        print(f"   ❌ Detector script not found at {script_path}")
    
    # Clean up
    os.unlink(temp_path)
    
except Exception as e:
    print(f"   ❌ Subprocess test error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🎯 TEST SUMMARY:")
print("YOLO detection should now work with the robot.")
print("The camera will use real object detection instead of mock data.")
print("\nNext steps:")
print("1. Run the robot: python test_robot.py")
print("2. Say 'Rubi, find a phone'")
print("3. With phone present: Should detect real phone")
print("4. Without phone: Should not detect phone (no mock detection)")
print("=" * 60)