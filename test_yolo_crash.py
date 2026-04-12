#!/usr/bin/env python3
"""
Test YOLO detection alone to see if it causes segmentation fault.
"""
import os
os.environ['KMP_WARNINGS'] = '0'
os.environ['OMP_NUM_THREADS'] = '1'

import sys
import traceback
from vision.camera import Camera

def main():
    print("=== Testing YOLO detection ===")
    
    # Initialize camera
    cam = Camera()
    if not cam.initialize():
        print("Camera init failed")
        return 1
    
    cam.start_capture()
    print("Camera capture started")
    
    # Wait for a frame
    import time
    time.sleep(1)
    
    frame = cam.get_frame()
    if frame is None:
        print("No frame captured")
        cam.stop()
        return 1
    
    print(f"Frame shape: {frame.shape}")
    
    # Run detection directly (bypass threading)
    print("Running YOLO detection...")
    try:
        # Use the model directly
        if not cam.model:
            print("Model not loaded")
            return 1
        
        # Run inference
        results = cam.model(frame, verbose=False, imgsz=320)
        print(f"Detection succeeded, number of results: {len(results)}")
        for r in results:
            print(f"  - {len(r.boxes)} boxes")
        
    except Exception as e:
        print(f"Detection raised exception: {e}")
        traceback.print_exc()
    
    cam.stop()
    print("Test completed.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)