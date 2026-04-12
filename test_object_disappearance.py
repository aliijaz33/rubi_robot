#!/usr/bin/env python3
"""
Test object disappearance scenario to ensure detection boxes clear properly
when objects are removed from camera view.
"""

import sys
import os
import time
import threading

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vision.camera import Camera
from vision.debug_window import VisionDebugWindow
import tkinter as tk

def test_object_disappearance():
    """Test that detection boxes clear when objects disappear"""
    print("🧪 Testing object disappearance scenario")
    print("=" * 60)
    
    # Initialize camera
    camera = Camera()
    if not camera.initialize():
        print("❌ Failed to initialize camera")
        return False
    
    camera.start_capture()
    
    # Create debug window
    root = tk.Tk()
    root.title("Object Disappearance Test")
    debug_window = VisionDebugWindow(camera, root)
    
    print("\n📋 Test Steps:")
    print("1. Camera will start capturing frames")
    print("2. Detection will run every 0.3 seconds (reduced frequency)")
    print("3. Initially, there may be objects detected")
    print("4. After 5 seconds, we'll stop search to simulate object removal")
    print("5. Detection boxes should clear within 1-2 seconds")
    print("6. Test will run for 10 seconds total")
    
    # Start a search for phone to trigger detection
    def search_callback(obj):
        print(f"🔍 Search callback: Found {obj['name']} at {obj['distance']}m")
    
    camera.start_search("phone", search_callback)
    
    # Run Tkinter in background thread
    def run_tkinter():
        root.mainloop()
    
    tk_thread = threading.Thread(target=run_tkinter, daemon=True)
    tk_thread.start()
    
    # Test sequence
    test_start = time.time()
    
    # Phase 1: Let detection run for 5 seconds
    print(f"\n⏱️  Phase 1: Detection running (0-5 seconds)")
    while time.time() - test_start < 5:
        objects = camera.get_current_objects()
        if objects:
            print(f"   Detected objects: {[obj['name'] for obj in objects]}")
        time.sleep(1)
    
    # Phase 2: Stop search to simulate object removal
    print(f"\n⏱️  Phase 2: Stopping search (5-7 seconds)")
    camera.stop_search()
    print("   Search stopped - detection boxes should clear soon")
    
    # Wait for detection to clear
    clear_check_start = time.time()
    objects_after_stop = []
    
    while time.time() - clear_check_start < 3:
        objects = camera.get_current_objects()
        if objects:
            objects_after_stop = objects
        time.sleep(0.5)
    
    # Phase 3: Final check
    print(f"\n⏱️  Phase 3: Final verification (7-10 seconds)")
    final_objects = camera.get_current_objects()
    
    # Stop everything
    camera.stop()
    root.quit()
    
    # Results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    
    if objects_after_stop:
        print(f"❌ FAIL: Objects still detected after search stopped: {[obj['name'] for obj in objects_after_stop]}")
        print("   Detection boxes are not clearing properly when search stops")
        return False
    else:
        print("✅ PASS: No objects detected after search stopped")
        print("   Detection boxes cleared properly when search stopped")
    
    if final_objects:
        print(f"⚠️  WARNING: Final objects list not empty: {[obj['name'] for obj in final_objects]}")
        print("   Some objects may still be in memory")
    else:
        print("✅ PASS: Final objects list is empty")
    
    print(f"\n⏱️  Total test time: {time.time() - test_start:.1f} seconds")
    print("✅ Object disappearance test completed")
    return True

def test_detection_frequency():
    """Test that detection frequency is optimized (not too frequent)"""
    print("\n" + "=" * 60)
    print("🧪 Testing detection frequency optimization")
    
    camera = Camera()
    
    print(f"\n📊 Camera configuration:")
    print(f"   - detection_interval: {camera.detection_interval}s (min time between detections)")
    print(f"   - detection_interval_navigation: {camera.detection_interval_navigation}s (navigation)")
    print(f"   - frame_skip: {camera.frame_skip} (process every Nth frame)")
    
    # Calculate expected detection rate
    max_detections_per_second = 1.0 / camera.detection_interval
    print(f"\n📈 Expected maximum detection rate:")
    print(f"   - During search: {max_detections_per_second:.1f} detections/second")
    print(f"   - During navigation: {1.0/camera.detection_interval_navigation:.1f} detections/second")
    
    # With persistent worker, each detection takes ~0.06-0.1 seconds
    detection_time = 0.08  # Average detection time with persistent worker
    cpu_usage_percent = (detection_time / camera.detection_interval) * 100
    print(f"   - CPU usage estimate: {cpu_usage_percent:.1f}% (based on {detection_time*1000:.0f}ms detection time)")
    
    if cpu_usage_percent < 30:
        print("✅ PASS: Detection frequency is optimized (CPU usage < 30%)")
        return True
    else:
        print(f"⚠️  WARNING: Detection frequency may be too high (CPU usage {cpu_usage_percent:.1f}%)")
        return False

if __name__ == "__main__":
    print("🚀 Starting object disappearance and detection frequency tests")
    print("=" * 60)
    
    # Run frequency test first
    freq_result = test_detection_frequency()
    
    # Run disappearance test
    print("\n" + "=" * 60)
    print("Starting object disappearance test...")
    print("Note: This test requires camera access and will open a window")
    print("=" * 60)
    
    try:
        disappear_result = test_object_disappearance()
    except Exception as e:
        print(f"❌ Error during test: {e}")
        disappear_result = False
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY:")
    print(f"   Detection frequency optimization: {'PASS' if freq_result else 'FAIL/WARNING'}")
    print(f"   Object disappearance clearing: {'PASS' if disappear_result else 'FAIL'}")
    
    if freq_result and disappear_result:
        print("\n✅ ALL TESTS PASSED")
        print("   Detection frequency is optimized and objects clear properly")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        print("   See details above for issues")
        sys.exit(1)