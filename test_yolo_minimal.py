#!/usr/bin/env python3
"""Minimal YOLO test to isolate segmentation fault"""

import sys
import signal
import traceback
import numpy as np
from ultralytics import YOLO

def signal_handler(sig, frame):
    print(f"\n⚠️  Received signal {sig}")
    sys.exit(1)

def test_yolo_inference():
    """Test YOLO inference with a dummy image"""
    print("🧪 Starting minimal YOLO test...")
    
    try:
        # Load model
        print("📦 Loading YOLO model...")
        model = YOLO('yolov8n.pt')
        print("✅ Model loaded successfully")
        
        # Create dummy image
        print("🎨 Creating dummy image...")
        dummy_image = np.random.randint(0, 255, (640, 480, 3), dtype=np.uint8)
        
        # Run inference
        print("🔍 Running inference...")
        results = model(dummy_image, verbose=False)
        print(f"✅ Inference completed, {len(results)} results")
        
        # Process results
        for i, r in enumerate(results):
            boxes = r.boxes
            if boxes is not None:
                print(f"  Result {i}: {len(boxes)} detections")
        
        print("🧹 Cleaning up...")
        del results
        del model
        print("✅ Cleanup complete")
        
    except Exception as e:
        print(f"❌ Exception during inference: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGSEGV, signal_handler)
    signal.signal(signal.SIGABRT, signal_handler)
    
    print("🚀 Starting test...")
    success = test_yolo_inference()
    
    if success:
        print("🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("💥 Test failed!")
        sys.exit(1)