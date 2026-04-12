#!/usr/bin/env python3
"""Test YOLO with ONNX format to avoid PyTorch/OpenMP issues"""

import os
import sys
import signal
import traceback
import numpy as np

# Set environment variables before importing anything
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

print(f"🔧 Environment set: OMP_NUM_THREADS={os.environ.get('OMP_NUM_THREADS')}")

def signal_handler(sig, frame):
    print(f"\n⚠️  Received signal {sig}")
    sys.exit(1)

def test_onnx_inference():
    """Test YOLO inference using ONNX format"""
    print("🧪 Starting YOLO ONNX test...")
    
    try:
        # Try to import ONNX Runtime
        import onnxruntime as ort
        print("✅ ONNX Runtime imported successfully")
        
        # Check if ONNX model exists, otherwise convert
        onnx_model_path = 'yolov8n.onnx'
        if not os.path.exists(onnx_model_path):
            print("📦 Converting PyTorch model to ONNX...")
            from ultralytics import YOLO
            model = YOLO('yolov8n.pt')
            model.export(format='onnx')
            print("✅ Model converted to ONNX")
        
        # Load ONNX model
        print("📥 Loading ONNX model...")
        session = ort.InferenceSession(onnx_model_path)
        print(f"✅ ONNX model loaded, inputs: {session.get_inputs()}")
        
        # Create dummy input
        print("🎨 Creating dummy input...")
        input_name = session.get_inputs()[0].name
        dummy_input = np.random.randn(1, 3, 640, 640).astype(np.float32)
        
        # Run inference
        print("🔍 Running ONNX inference...")
        outputs = session.run(None, {input_name: dummy_input})
        print(f"✅ Inference completed, {len(outputs)} outputs")
        
        print("🧹 Cleaning up...")
        del session
        print("✅ Cleanup complete")
        
    except ImportError as e:
        print(f"❌ ONNX Runtime not available: {e}")
        print("💡 Try: pip install onnxruntime")
        return False
    except Exception as e:
        print(f"❌ Exception during ONNX inference: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGSEGV, signal_handler)
    signal.signal(signal.SIGABRT, signal_handler)
    
    print("🚀 Starting ONNX test...")
    success = test_onnx_inference()
    
    if success:
        print("🎉 ONNX test completed successfully!")
        sys.exit(0)
    else:
        print("💥 ONNX test failed!")
        sys.exit(1)