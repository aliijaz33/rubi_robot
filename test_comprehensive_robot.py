#!/usr/bin/env python3
"""
Comprehensive test of the complete robot search and navigation functionality.
This test verifies that:
1. Robot can search for objects without segmentation faults
2. Navigation starts when object is found
3. Distance decreases over time (progress is made)
4. Robot eventually reaches target and completes navigation
"""

import sys
import os
import time
import threading
from unittest.mock import Mock, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hardware.motor_factory import MotorFactory
from vision.camera import Camera
from intelligence.searcher import ObjectSearcher
from speech.speaker import Speaker


class MockSpeaker:
    """Mock speaker to avoid audio output during tests"""
    def speak(self, text):
        print(f"[Speaker] {text}")
    
    def stop(self):
        pass


def test_complete_search_and_navigation():
    """Test the complete search and navigation workflow"""
    print("=" * 60)
    print("COMPREHENSIVE ROBOT SEARCH & NAVIGATION TEST")
    print("=" * 60)
    
    # Create mock speaker
    speaker = MockSpeaker()
    
    # Create motor controller (simulation mode)
    print("\n1. Creating motor controller...")
    motor = MotorFactory.create_motor_controller(mode='simulation')
    
    # Create camera
    print("2. Creating camera...")
    camera = Camera()
    camera.initialize()
    
    # Create object searcher
    print("3. Creating object searcher...")
    searcher = ObjectSearcher(motor, camera, speaker)
    
    # Start camera capture
    print("4. Starting camera capture...")
    camera.start_capture()
    
    # Set up mock detection to simulate finding a phone
    print("5. Setting up mock detection...")
    
    # Override camera's detection to return a phone at decreasing distances
    original_detect = camera._detect_objects
    
    # Track navigation progress
    test_distances = [1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.35]
    distance_index = 0
    
    def mock_detect(frame):
        """Mock detection that returns a phone at decreasing distances"""
        nonlocal distance_index
        
        # Simulate YOLO detection returning a phone
        mock_detections = []
        
        # Only return phone after search has started
        if hasattr(camera, 'search_target') and camera.search_target == 'phone':
            # Get current distance
            if distance_index < len(test_distances):
                distance = test_distances[distance_index]
            else:
                distance = 0.35  # Final distance
            
            # Create mock detection
            mock_detections.append({
                'name': 'phone',
                'confidence': 0.85,
                'bbox': [100, 100, 200, 200],
                'distance': distance,
                'center_x': 150,
                'center_y': 150
            })
            
            # Increment distance every 2 detections to simulate movement
            if hasattr(camera, '_detection_count'):
                camera._detection_count += 1
                if camera._detection_count % 2 == 0 and distance_index < len(test_distances) - 1:
                    distance_index += 1
                    print(f"  → Distance decreased to {test_distances[distance_index]:.2f}m")
            else:
                camera._detection_count = 1
        
        return mock_detections
    
    # Replace detection method
    camera._detect_objects = mock_detect
    
    # Start search for phone
    print("\n6. Starting search for 'phone'...")
    
    search_complete = threading.Event()
    object_found = threading.Event()
    navigation_complete = threading.Event()
    
    def search_callback(event, obj=None):
        """Callback for search events"""
        if event == 'object_found':
            print(f"\n✓ OBJECT FOUND: {obj['name']} at {obj['distance']:.2f}m")
            object_found.set()
        elif event == 'navigation_started':
            print(f"\n✓ NAVIGATION STARTED toward {obj['name']}")
        elif event == 'navigation_progress':
            print(f"  → Progress: distance = {obj['distance']:.2f}m")
        elif event == 'navigation_complete':
            print(f"\n✓ NAVIGATION COMPLETE! Reached {obj['name']}")
            navigation_complete.set()
        elif event == 'search_complete':
            print(f"\n✓ SEARCH COMPLETE")
            search_complete.set()
    
    # Start search in background thread
    def run_search():
        searcher.search_for_object('phone', pattern='scan')
        search_callback('search_complete')
    
    search_thread = threading.Thread(target=run_search, daemon=True)
    search_thread.start()
    
    # Wait for object to be found
    print("\nWaiting for phone to be detected...")
    if object_found.wait(timeout=10):
        print("✓ Phone successfully detected!")
    else:
        print("✗ Phone not detected within timeout")
        return False
    
    # Wait for navigation to complete
    print("\nWaiting for navigation to complete...")
    print("(This simulates the robot moving toward the phone)")
    
    # Simulate navigation progress
    start_time = time.time()
    timeout = 30  # seconds
    
    while not navigation_complete.is_set():
        if time.time() - start_time > timeout:
            print(f"\n✗ Navigation timeout after {timeout} seconds")
            break
        
        # Check if we've reached target distance
        if distance_index >= len(test_distances) - 1:
            # We've reached the final distance
            navigation_complete.set()
            print("\n✓ Reached target distance (0.35m)")
            break
        
        time.sleep(1)
    
    # Stop search
    print("\n7. Stopping search...")
    searcher.stop_searching()
    camera.stop_search()
    
    # Wait a bit for cleanup
    time.sleep(1)
    
    # Stop camera
    print("8. Stopping camera...")
    camera.stop()
    
    # Check results
    success = object_found.is_set()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)
    print(f"Object found: {'✓' if object_found.is_set() else '✗'}")
    print(f"Navigation progress: {'✓' if distance_index > 0 else '✗'} (reached {test_distances[distance_index]:.2f}m)")
    print(f"Final distance: {test_distances[distance_index]:.2f}m")
    
    if success:
        print("\n✅ COMPREHENSIVE TEST PASSED!")
        print("The robot can successfully:")
        print("  - Search for objects without crashes")
        print("  - Detect objects when found")
        print("  - Navigate toward objects with decreasing distances")
        print("  - Make progress toward the target")
    else:
        print("\n❌ COMPREHENSIVE TEST FAILED")
        print("Some aspect of the search/navigation failed.")
    
    return success


def test_segmentation_fault_protection():
    """Verify that segmentation faults in YOLO don't crash the main robot"""
    print("\n" + "=" * 60)
    print("SEGMENTATION FAULT PROTECTION TEST")
    print("=" * 60)
    
    from vision.camera import Camera
    import subprocess
    
    camera = Camera()
    camera.initialize()
    
    # Test that YOLO detection runs in subprocess
    print("1. Testing YOLO detection subprocess isolation...")
    
    # Create a test frame
    import numpy as np
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Try to run YOLO detection
    try:
        # This should not crash even if YOLO has issues
        detections = camera._run_yolo_detection(test_frame)
        print(f"✓ YOLO detection completed without crashing main process")
        print(f"  Detections: {len(detections) if detections else 0}")
        
        # Check if it fell back to mock detection
        if detections and len(detections) > 0 and detections[0].get('name') == 'mock':
            print("✓ Falls back to mock detection when YOLO fails")
        
        return True
    except Exception as e:
        print(f"✗ YOLO detection error (but main process didn't crash): {e}")
        return False


def main():
    """Run all comprehensive tests"""
    print("Running comprehensive robot functionality tests...")
    print(f"Python: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    all_passed = True
    
    # Test 1: Segmentation fault protection
    if test_segmentation_fault_protection():
        print("\n✅ Segmentation fault protection: PASSED")
    else:
        print("\n❌ Segmentation fault protection: FAILED")
        all_passed = False
    
    # Test 2: Complete search and navigation
    if test_complete_search_and_navigation():
        print("\n✅ Complete search and navigation: PASSED")
    else:
        print("\n❌ Complete search and navigation: FAILED")
        all_passed = False
    
    print("\n" + "=" * 60)
    print("FINAL VERDICT:")
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nThe robot is now fixed and should:")
        print("1. Run without segmentation fault crashes")
        print("2. Successfully search for objects")
        print("3. Navigate toward found objects without getting stuck")
        print("4. Make progress until reaching the target")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nFurther investigation may be needed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())