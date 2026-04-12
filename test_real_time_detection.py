#!/usr/bin/env python3
"""
Test real-time detection with persistent YOLO worker
This test runs without GUI to avoid segmentation faults
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vision.camera import Camera
import time
import numpy as np

def test_real_time_performance():
    """Test real-time detection performance without GUI"""
    print("⚡ Testing real-time detection performance...")
    
    camera = Camera()
    
    if not camera.initialize():
        print("❌ Camera initialization failed")
        return False
    
    print("✅ Camera initialized")
    print(f"   Persistent worker: {'Enabled' if camera.use_persistent_worker else 'Disabled'}")
    
    # Start capture
    camera.start_capture()
    print("✅ Camera capture started")
    
    # Wait for camera to warm up
    time.sleep(1)
    
    # Test parameters
    test_duration = 10  # seconds
    detection_interval = 0.5  # Run detection every 0.5 seconds
    frame_count = 0
    detection_count = 0
    successful_detections = 0
    
    print(f"\n📊 Running real-time test for {test_duration} seconds...")
    print("   Detection interval: every 0.5 seconds")
    print("   Press Ctrl+C to stop early\n")
    
    start_time = time.time()
    last_detection_time = start_time
    
    try:
        while time.time() - start_time < test_duration:
            # Get frame (non-blocking)
            frame = camera.get_frame()
            if frame is not None:
                frame_count += 1
            
            # Run detection at specified interval
            current_time = time.time()
            if current_time - last_detection_time >= detection_interval:
                detection_count += 1
                last_detection_time = current_time
                
                if frame is not None:
                    # Run detection
                    detection_start = time.time()
                    detected = camera._run_yolo_detection(frame)
                    detection_time = time.time() - detection_start
                    
                    if detected is not None:
                        successful_detections += 1
                        
                        # Print detection results (but not too frequently)
                        if detection_count % 2 == 0:  # Every other detection
                            obj_count = len(detected)
                            if obj_count > 0:
                                obj_names = ", ".join([obj['name'] for obj in detected[:3]])
                                if obj_count > 3:
                                    obj_names += f" (+{obj_count-3} more)"
                                print(f"   🔍 Detection {detection_count}: {obj_count} objects in {detection_time*1000:.0f}ms")
                                print(f"      Found: {obj_names}")
                            else:
                                print(f"   🔍 Detection {detection_count}: No objects in {detection_time*1000:.0f}ms")
                    else:
                        print(f"   ⚠️ Detection {detection_count}: Failed")
            
            # Small sleep to prevent CPU overload
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    
    finally:
        # Stop camera
        camera.stop()
    
    # Calculate statistics
    total_time = time.time() - start_time
    avg_fps = frame_count / total_time if total_time > 0 else 0
    
    print("\n" + "=" * 60)
    print("REAL-TIME DETECTION RESULTS:")
    print("=" * 60)
    print(f"Test duration: {total_time:.1f} seconds")
    print(f"Frames captured: {frame_count}")
    print(f"Average FPS: {avg_fps:.1f}")
    print(f"Detection attempts: {detection_count}")
    print(f"Successful detections: {successful_detections}")
    
    if detection_count > 0:
        success_rate = (successful_detections / detection_count) * 100
        print(f"Detection success rate: {success_rate:.1f}%")
    
    # Performance assessment
    print("\n📈 PERFORMANCE ASSESSMENT:")
    
    if avg_fps >= 20:
        print("✅ Frame rate: EXCELLENT (≥20 FPS)")
    elif avg_fps >= 15:
        print("✅ Frame rate: GOOD (15-20 FPS)")
    elif avg_fps >= 10:
        print("⚠️ Frame rate: ACCEPTABLE (10-15 FPS)")
    else:
        print("❌ Frame rate: POOR (<10 FPS)")
    
    if detection_count > 0 and successful_detections > 0:
        print("✅ Detection reliability: GOOD")
    else:
        print("⚠️ Detection reliability: NEEDS IMPROVEMENT")
    
    # Check worker status
    print(f"\n🔧 SYSTEM STATUS:")
    print(f"   Persistent worker: {'✅ Active' if camera.use_persistent_worker else '❌ Disabled'}")
    print(f"   Detection method: {'Persistent worker' if camera.use_persistent_worker and camera.yolo_worker_process else 'Subprocess fallback'}")
    
    return True

def test_object_tracking():
    """Test tracking objects over time"""
    print("\n🎯 Testing object tracking over time...")
    
    camera = Camera()
    
    if not camera.initialize():
        print("❌ Camera initialization failed")
        return
    
    camera.start_capture()
    
    # Track objects over multiple detections
    object_history = {}
    detection_times = []
    
    print("   Tracking objects for 5 seconds...")
    
    start_time = time.time()
    detection_count = 0
    
    while time.time() - start_time < 5:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        
        # Run detection
        detection_start = time.time()
        detected = camera._run_yolo_detection(frame)
        detection_time = time.time() - detection_start
        
        if detected is not None:
            detection_count += 1
            detection_times.append(detection_time)
            
            # Update object history
            for obj in detected:
                obj_name = obj['name']
                if obj_name not in object_history:
                    object_history[obj_name] = {
                        'count': 0,
                        'first_seen': time.time() - start_time,
                        'last_seen': time.time() - start_time,
                        'distances': []
                    }
                
                object_history[obj_name]['count'] += 1
                object_history[obj_name]['last_seen'] = time.time() - start_time
                object_history[obj_name]['distances'].append(obj['distance'])
        
        time.sleep(0.5)  # Detect every 0.5 seconds
    
    camera.stop()
    
    # Print tracking results
    print(f"   Total detections: {detection_count}")
    
    if detection_times:
        avg_detection_time = sum(detection_times) / len(detection_times)
        print(f"   Average detection time: {avg_detection_time*1000:.1f}ms")
    
    if object_history:
        print(f"   Objects detected: {len(object_history)}")
        for obj_name, data in object_history.items():
            avg_distance = sum(data['distances']) / len(data['distances']) if data['distances'] else 0
            print(f"     - {obj_name}: seen {data['count']} times, avg distance: {avg_distance:.1f}m")
    else:
        print("   No objects detected during tracking period")

if __name__ == "__main__":
    print("=" * 60)
    print("Real-Time Detection Test with Persistent YOLO Worker")
    print("=" * 60)
    
    # Test 1: Real-time performance
    test_real_time_performance()
    
    # Test 2: Object tracking
    test_object_tracking()
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)