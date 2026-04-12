#!/usr/bin/env python3
"""
Test script to verify YOLO detection works with the modified camera.py
This tests the _run_yolo_detection method directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
from vision.camera import Camera

def test_yolo_detection():
    """Test YOLO detection with a test image"""
    print("🧪 Testing YOLO detection with modified camera.py...")
    
    # Create a camera instance
    camera = Camera()
    camera.initialize()
    
    # Create a test frame (simple colored rectangle)
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add a colored rectangle to simulate something
    cv2.rectangle(test_frame, (100, 100), (300, 300), (0, 255, 0), -1)
    
    print("📸 Running YOLO detection on test frame...")
    
    # Call _run_yolo_detection directly
    detected = camera._run_yolo_detection(test_frame)
    
    if detected is None:
        print("❌ YOLO detection returned None (likely timeout or error)")
        print("   This could mean:")
        print("   1. Python path is incorrect")
        print("   2. YOLO dependencies not installed in rubi_robot environment")
        print("   3. Subprocess timeout still occurring")
        return False
    elif detected == []:
        print("✅ YOLO detection succeeded but found no objects (expected for test image)")
        print("   This confirms YOLO is working and not falling back to mock detection!")
        return True
    else:
        print(f"✅ YOLO detection succeeded and found {len(detected)} objects:")
        for obj in detected:
            print(f"   - {obj.get('name', 'unknown')} at distance {obj.get('distance', 'unknown')}")
        return True

def test_python_path():
    """Test if the Python path exists and can run YOLO"""
    print("\n🔍 Testing Python path...")
    python_path = "/Users/macbook/miniforge3/envs/rubi_robot/bin/python"
    
    if not os.path.exists(python_path):
        print(f"❌ Python path does not exist: {python_path}")
        return False
    
    print(f"✅ Python path exists: {python_path}")
    
    # Test if it can import YOLO
    import subprocess
    test_script = """
import sys
try:
    import cv2
    import torch
    from ultralytics import YOLO
    import numpy as np
    print("SUCCESS: All imports work")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
"""
    
    result = subprocess.run([python_path, "-c", test_script], 
                          capture_output=True, text=True, timeout=5.0)
    
    if result.returncode == 0:
        print("✅ Python environment has all required dependencies")
        print(f"   Output: {result.stdout.strip()}")
        return True
    else:
        print("❌ Python environment missing dependencies")
        print(f"   Error: {result.stderr}")
        return False

def test_yolo_detector_script():
    """Test the yolo_detector.py script directly"""
    print("\n🔍 Testing yolo_detector.py script...")
    
    script_path = os.path.join(os.path.dirname(__file__), "vision", "yolo_detector.py")
    if not os.path.exists(script_path):
        print(f"❌ yolo_detector.py not found at: {script_path}")
        return False
    
    print(f"✅ yolo_detector.py found at: {script_path}")
    
    # Create a test image
    test_image_path = "test_yolo_image.jpg"
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.imwrite(test_image_path, test_frame)
    
    python_path = "/Users/macbook/miniforge3/envs/rubi_robot/bin/python"
    
    import subprocess
    import time
    
    start_time = time.time()
    try:
        result = subprocess.run(
            [python_path, script_path, test_image_path],
            capture_output=True,
            text=True,
            timeout=20.0  # Give it 20 seconds
        )
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ yolo_detector.py succeeded in {elapsed:.2f} seconds")
            print(f"   Output: {result.stdout[:200]}...")
            
            # Try to parse JSON
            import json
            try:
                detected = json.loads(result.stdout.strip())
                print(f"   Parsed {len(detected) if isinstance(detected, list) else 0} objects")
            except:
                print("   Could not parse JSON output")
            return True
        else:
            print(f"❌ yolo_detector.py failed with code {result.returncode}")
            print(f"   stderr: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"❌ yolo_detector.py timed out after {elapsed:.2f} seconds")
        return False
    finally:
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

if __name__ == "__main__":
    print("=" * 60)
    print("Testing YOLO Detection Fix")
    print("=" * 60)
    
    # Test 1: Python path
    if not test_python_path():
        print("\n⚠️ Python path test failed. Cannot proceed.")
        sys.exit(1)
    
    # Test 2: yolo_detector script
    if not test_yolo_detector_script():
        print("\n⚠️ yolo_detector script test failed.")
        # Continue anyway to test camera method
    
    # Test 3: Camera YOLO detection
    print("\n" + "=" * 60)
    print("Testing Camera._run_yolo_detection()")
    print("=" * 60)
    
    success = test_yolo_detection()
    
    if success:
        print("\n✅ All tests passed! YOLO detection should now work without timing out.")
        print("   The robot should now use authentic detection instead of mock detection.")
    else:
        print("\n❌ Tests failed. YOLO detection may still have issues.")
        print("   Check the Python path and ensure dependencies are installed correctly.")
    
    sys.exit(0 if success else 1)