#!/usr/bin/env python3
"""Test camera with subprocess-based YOLO detection"""

import sys
import time
from vision.camera import Camera

def test_camera_detection():
    """Test camera initialization and basic detection"""
    print("🧪 Testing camera with subprocess-based YOLO...")
    
    camera = Camera()
    
    # Initialize camera
    if not camera.initialize():
        print("❌ Camera initialization failed")
        return False
    
    print("✅ Camera initialized")
    
    # Start capture
    camera.start_capture()
    print("✅ Camera capture started")
    
    # Wait for a few frames to be captured
    print("⏳ Waiting for frames...")
    time.sleep(2)
    
    # Try to get a frame
    frame = camera.get_frame()
    if frame is None:
        print("❌ No frame captured")
        camera.stop()
        return False
    
    print(f"✅ Frame captured: {frame.shape}")
    
    # Try detection
    print("🔍 Testing detection...")
    camera._detect_objects(frame)
    
    # Check detected objects
    objects = camera.get_current_objects()
    print(f"✅ Detection completed, found {len(objects)} objects")
    
    if objects:
        for obj in objects[:3]:  # Show first 3 objects
            print(f"  - {obj['name']} ({obj['confidence']}) at {obj['distance']}m to the {obj['direction']}")
    
    # Stop camera
    camera.stop()
    print("✅ Camera stopped")
    
    return True

if __name__ == "__main__":
    success = test_camera_detection()
    
    if success:
        print("🎉 Camera test passed!")
        sys.exit(0)
    else:
        print("💥 Camera test failed!")
        sys.exit(1)