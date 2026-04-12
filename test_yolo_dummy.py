#!/usr/bin/env python3
"""
Test YOLO with dummy image to isolate camera issues.
"""
import os
os.environ['KMP_WARNINGS'] = '0'
os.environ['OMP_NUM_THREADS'] = '1'

import sys
import traceback
import numpy as np
from ultralytics import YOLO

def main():
    print("=== Testing YOLO with dummy image ===")
    
    # Load model
    print("Loading YOLO model...")
    try:
        model = YOLO('yolov8n.pt')
        print("Model loaded.")
    except Exception as e:
        print(f"Failed to load model: {e}")
        return 1
    
    # Create dummy image (640x480, 3 channels, uint8)
    dummy = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    print(f"Dummy image shape: {dummy.shape}")
    
    # Run inference
    print("Running inference...")
    try:
        results = model(dummy, verbose=False, imgsz=320)
        print(f"Inference succeeded, number of results: {len(results)}")
        for r in results:
            print(f"  - {len(r.boxes)} boxes")
    except Exception as e:
        print(f"Inference raised exception: {e}")
        traceback.print_exc()
        return 1
    
    print("Test completed.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)