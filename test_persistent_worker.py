#!/usr/bin/env python3
"""
Test script to verify persistent YOLO worker reduces detection time
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vision.camera import Camera
import time
import cv2
import numpy as np

def test_persistent_worker():
    """Test that persistent YOLO worker reduces detection time"""
    print("🧪 Testing persistent YOLO worker performance...")
    
    # Create camera instance
    camera = Camera()
    
    # Initialize camera (this should start the persistent worker)
    if not camera.initialize():
        print("❌ Camera initialization failed")
        return False
    
    # Create a test frame (simple colored image)
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    test_frame[:, :] = (100, 150, 200)  # Blue-ish color
    
    # Draw a simple rectangle to simulate an object
    cv2.rectangle(test_frame, (200, 150), (400, 350), (0, 255, 0), 2)
    
    print("📊 Testing detection performance...")
    
    # First detection (should be slower if worker needs to start)
    print("   First detection (may be slow due to worker startup)...")
    start_time = time.time()
    detected = camera._run_yolo_detection(test_frame)
    first_detection_time = time.time() - start_time
    
    if detected is None:
        print("   ⚠️ First detection returned None")
    else:
        print(f"   ✅ First detection took {first_detection_time:.2f} seconds")
        print(f"   Found {len(detected)} objects")
    
    # Second detection (should be much faster with persistent worker)
    print("   Second detection (should be faster)...")
    start_time = time.time()
    detected = camera._run_yolo_detection(test_frame)
    second_detection_time = time.time() - start_time
    
    if detected is None:
        print("   ⚠️ Second detection returned None")
    else:
        print(f"   ✅ Second detection took {second_detection_time:.2f} seconds")
        print(f"   Found {len(detected)} objects")
    
    # Third detection (should be consistent)
    print("   Third detection (should be consistent)...")
    start_time = time.time()
    detected = camera._run_yolo_detection(test_frame)
    third_detection_time = time.time() - start_time
    
    if detected is None:
        print("   ⚠️ Third detection returned None")
    else:
        print(f"   ✅ Third detection took {third_detection_time:.2f} seconds")
        print(f"   Found {len(detected)} objects")
    
    # Calculate improvement
    if first_detection_time > 0 and second_detection_time > 0:
        improvement = first_detection_time - second_detection_time
        print(f"\n📈 Performance improvement: {improvement:.2f} seconds faster")
        
        if second_detection_time < 2.0:
            print("✅ Persistent worker is working! Detection under 2 seconds")
        else:
            print(f"⚠️ Detection still slow: {second_detection_time:.2f} seconds")
    
    # Test worker status
    print(f"\n🔍 Worker status:")
    print(f"   use_persistent_worker: {camera.use_persistent_worker}")
    print(f"   yolo_worker_process: {'Running' if camera.yolo_worker_process and camera.yolo_worker_process.poll() is None else 'Not running'}")
    
    # Clean up - only call stop() if we started capture
    try:
        camera.stop()
    except AttributeError:
        # If capture_thread doesn't exist, just stop the worker
        camera._stop_yolo_worker()
    
    return True

def test_with_real_camera():
    """Test with actual camera if available"""
    print("\n🎥 Testing with real camera...")
    
    camera = Camera()
    
    if not camera.initialize():
        print("❌ Camera initialization failed, skipping real camera test")
        return False
    
    camera.start_capture()
    
    # Wait for a few frames
    print("   Waiting for camera to capture frames...")
    time.sleep(2)
    
    # Get a frame
    frame = camera.get_frame()
    if frame is None:
        print("   ⚠️ No frame captured")
    else:
        print(f"   ✅ Frame captured: {frame.shape}")
        
        # Test detection on real frame
        start_time = time.time()
        detected = camera._run_yolo_detection(frame)
        detection_time = time.time() - start_time
        
        if detected is None:
            print("   ⚠️ Detection on real frame returned None")
        else:
            print(f"   ✅ Detection on real frame took {detection_time:.2f} seconds")
            print(f"   Found {len(detected)} objects")
            for obj in detected[:3]:  # Show first 3 objects
                print(f"     - {obj['name']} ({obj['confidence']:.2f}) at {obj['distance']}m")
    
    camera.stop()
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Persistent YOLO Worker Performance Test")
    print("=" * 60)
    
    # Test 1: Synthetic frame
    test_persistent_worker()
    
    # Test 2: Real camera (if available)
    test_with_real_camera()
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)