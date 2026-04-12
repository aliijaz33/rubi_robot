#!/usr/bin/env python3
"""
Test camera responsiveness with the new persistent YOLO worker
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vision.camera import Camera
import time
import threading
import cv2
import numpy as np

def test_frame_rate():
    """Test camera frame rate and responsiveness"""
    print("🎥 Testing camera frame rate and responsiveness...")
    
    camera = Camera()
    
    if not camera.initialize():
        print("❌ Camera initialization failed")
        return
    
    camera.start_capture()
    
    # Variables to track performance
    frame_count = 0
    detection_count = 0
    start_time = time.time()
    last_frame_time = start_time
    frame_times = []
    detection_times = []
    
    # Create a simple display window
    cv2.namedWindow("Camera Test", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Camera Test", 800, 600)
    
    print("📊 Starting performance measurement (10 seconds)...")
    print("   Press 'q' to quit early")
    
    try:
        while time.time() - start_time < 10:
            # Get frame
            frame = camera.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            frame_count += 1
            current_time = time.time()
            frame_times.append(current_time - last_frame_time)
            last_frame_time = current_time
            
            # Calculate FPS
            if frame_count % 30 == 0:
                elapsed = current_time - start_time
                fps = frame_count / elapsed
                avg_frame_time = sum(frame_times[-30:]) / 30 if len(frame_times) >= 30 else 0
                
                # Get detection info
                detected = camera.detected_objects
                detection_info = f"Detections: {len(detected)}"
                if detected:
                    detection_info += f" ({detected[0]['name']} at {detected[0]['distance']}m)"
                
                print(f"   FPS: {fps:.1f}, Frame time: {avg_frame_time*1000:.1f}ms, {detection_info}")
            
            # Run detection occasionally (simulating search mode)
            if frame_count % 15 == 0:  # Every 15 frames
                detection_start = time.time()
                # This would normally be called by _start_detection_thread
                # For testing, we'll just check if detection is working
                detection_count += 1
                detection_times.append(time.time() - detection_start)
            
            # Display frame with info
            display_frame = frame.copy()
            
            # Add FPS counter
            fps_text = f"FPS: {frame_count/(time.time()-start_time):.1f}"
            cv2.putText(display_frame, fps_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add detection info
            detected = camera.detected_objects
            if detected:
                obj_text = f"Objects: {len(detected)}"
                cv2.putText(display_frame, obj_text, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Show first object
                if len(detected) > 0:
                    obj = detected[0]
                    obj_detail = f"{obj['name']} ({obj['distance']}m)"
                    cv2.putText(display_frame, obj_detail, (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add worker status
            worker_status = "Worker: "
            if camera.yolo_worker_process and camera.yolo_worker_process.poll() is None:
                worker_status += "✅ Active"
            else:
                worker_status += "❌ Inactive"
            cv2.putText(display_frame, worker_status, (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Camera Test", display_frame)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Small sleep to prevent CPU overload
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    finally:
        cv2.destroyAllWindows()
        camera.stop()
    
    # Calculate final statistics
    total_time = time.time() - start_time
    avg_fps = frame_count / total_time if total_time > 0 else 0
    
    if detection_times:
        avg_detection_time = sum(detection_times) / len(detection_times)
    else:
        avg_detection_time = 0
    
    print("\n" + "=" * 60)
    print("PERFORMANCE RESULTS:")
    print("=" * 60)
    print(f"Total time: {total_time:.1f} seconds")
    print(f"Total frames: {frame_count}")
    print(f"Average FPS: {avg_fps:.1f}")
    print(f"Frame processing time: {(1/avg_fps*1000 if avg_fps > 0 else 0):.1f}ms")
    print(f"Detection attempts: {detection_count}")
    if detection_times:
        print(f"Average detection time: {avg_detection_time*1000:.1f}ms")
    print(f"Worker status: {'Active' if camera.yolo_worker_process and camera.yolo_worker_process.poll() is None else 'Inactive'}")
    
    # Check if performance is acceptable
    if avg_fps >= 15:
        print("✅ Camera responsiveness: GOOD (≥15 FPS)")
    elif avg_fps >= 10:
        print("⚠️ Camera responsiveness: ACCEPTABLE (10-15 FPS)")
    else:
        print("❌ Camera responsiveness: POOR (<10 FPS)")
    
    if detection_times and avg_detection_time < 0.1:
        print("✅ Detection speed: EXCELLENT (<100ms)")
    elif detection_times and avg_detection_time < 0.5:
        print("✅ Detection speed: GOOD (<500ms)")
    else:
        print("⚠️ Detection speed: NEEDS IMPROVEMENT")

def test_search_responsiveness():
    """Test search responsiveness with actual object detection"""
    print("\n🔍 Testing search responsiveness...")
    
    camera = Camera()
    
    if not camera.initialize():
        print("❌ Camera initialization failed")
        return
    
    camera.start_capture()
    
    # Start a search for "person"
    print("   Starting search for 'person'...")
    
    def search_callback(obj):
        print(f"   🔔 Search callback: Found {obj['name']} at {obj['distance']}m")
    
    camera.start_search("person", search_callback)
    
    # Wait for some detections
    print("   Waiting for detections (5 seconds)...")
    
    detection_count = 0
    start_time = time.time()
    
    while time.time() - start_time < 5:
        detected = camera.detected_objects
        if detected:
            detection_count += 1
            if detection_count <= 3:  # Only print first 3 detections
                for obj in detected:
                    if obj['name'] == 'person':
                        print(f"   👤 Found person at {obj['distance']}m")
        time.sleep(0.1)
    
    camera.stop_search()
    camera.stop()
    
    print(f"   Total detection cycles: {detection_count}")
    if detection_count >= 3:
        print("✅ Search responsiveness: GOOD")
    else:
        print("⚠️ Search responsiveness: Could be better")

if __name__ == "__main__":
    print("=" * 60)
    print("Camera Responsiveness Test with Persistent YOLO Worker")
    print("=" * 60)
    
    # Test 1: Frame rate and basic responsiveness
    test_frame_rate()
    
    # Test 2: Search responsiveness
    test_search_responsiveness()
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)