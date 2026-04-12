#!/usr/bin/env python3
"""
Test YOLO detection performance to identify bottlenecks
"""

import sys
import os
import time
import subprocess
import tempfile
import cv2
import numpy as np

def test_subprocess_startup():
    """Test how long it takes to start a Python subprocess"""
    print("🧪 Testing subprocess startup time...")
    
    python_path = "/Users/macbook/miniforge3/envs/rubi_robot/bin/python"
    
    # Simple test script
    test_script = "import time; print('Hello from subprocess')"
    
    times = []
    for i in range(3):
        start = time.time()
        result = subprocess.run([python_path, "-c", test_script], 
                              capture_output=True, text=True, timeout=5.0)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Run {i+1}: {elapsed:.3f}s")
    
    avg = sum(times) / len(times)
    print(f"  Average subprocess startup: {avg:.3f}s")
    return avg

def test_yolo_model_loading():
    """Test how long it takes to load YOLO model"""
    print("\n🧪 Testing YOLO model loading time...")
    
    python_path = "/Users/macbook/miniforge3/envs/rubi_robot/bin/python"
    
    test_script = """
import time
start = time.time()
from ultralytics import YOLO
load_start = time.time()
model = YOLO('yolov8n.pt')
load_end = time.time()
print(f'IMPORT_TIME:{load_start-start:.3f}')
print(f'LOAD_TIME:{load_end-load_start:.3f}')
print(f'TOTAL_TIME:{load_end-start:.3f}')
"""
    
    start = time.time()
    result = subprocess.run([python_path, "-c", test_script], 
                          capture_output=True, text=True, timeout=30.0)
    elapsed = time.time() - start
    
    if result.returncode == 0:
        import_time = 0
        load_time = 0
        for line in result.stdout.split('\n'):
            if 'IMPORT_TIME:' in line:
                import_time = float(line.split(':')[1])
            elif 'LOAD_TIME:' in line:
                load_time = float(line.split(':')[1])
            elif 'TOTAL_TIME:' in line:
                total_time = float(line.split(':')[1])
        
        print(f"  Import time: {import_time:.3f}s")
        print(f"  Model load time: {load_time:.3f}s")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Subprocess total: {elapsed:.3f}s")
        return total_time
    else:
        print(f"  Error: {result.stderr}")
        return None

def test_yolo_inference():
    """Test YOLO inference time on a test image"""
    print("\n🧪 Testing YOLO inference time...")
    
    # Create a test image
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (100, 100), (200, 200), (0, 255, 0), -1)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        image_path = f.name
        cv2.imwrite(image_path, test_image)
    
    python_path = "/Users/macbook/miniforge3/envs/rubi_robot/bin/python"
    
    test_script = f"""
import time
import cv2
from ultralytics import YOLO

# Load image
start = time.time()
frame = cv2.imread('{image_path}')
load_time = time.time()

# Load model
model = YOLO('yolov8n.pt')
model_load_time = time.time()

# Run inference
results = model(frame, verbose=False, imgsz=320)
inference_time = time.time()

print(f'IMAGE_LOAD:{load_time-start:.3f}')
print(f'MODEL_LOAD:{model_load_time-load_time:.3f}')
print(f'INFERENCE:{inference_time-model_load_time:.3f}')
print(f'TOTAL:{inference_time-start:.3f}')

# Count detections
detections = 0
for r in results:
    for box in r.boxes:
        if box.conf[0].item() > 0.5:
            detections += 1
print(f'DETECTIONS:{detections}')
"""
    
    start = time.time()
    result = subprocess.run([python_path, "-c", test_script], 
                          capture_output=True, text=True, timeout=30.0)
    elapsed = time.time() - start
    
    if result.returncode == 0:
        image_load = 0
        model_load = 0
        inference = 0
        total = 0
        detections = 0
        
        for line in result.stdout.split('\n'):
            if 'IMAGE_LOAD:' in line:
                image_load = float(line.split(':')[1])
            elif 'MODEL_LOAD:' in line:
                model_load = float(line.split(':')[1])
            elif 'INFERENCE:' in line:
                inference = float(line.split(':')[1])
            elif 'TOTAL:' in line:
                total = float(line.split(':')[1])
            elif 'DETECTIONS:' in line:
                detections = int(line.split(':')[1])
        
        print(f"  Image load: {image_load:.3f}s")
        print(f"  Model load: {model_load:.3f}s")
        print(f"  Inference: {inference:.3f}s")
        print(f"  Total in script: {total:.3f}s")
        print(f"  Subprocess total: {elapsed:.3f}s")
        print(f"  Detections found: {detections}")
        return total
    else:
        print(f"  Error: {result.stderr}")
        return None
    
    # Clean up
    if os.path.exists(image_path):
        os.remove(image_path)

def test_full_yolo_detector():
    """Test the full yolo_detector.py script"""
    print("\n🧪 Testing full yolo_detector.py script...")
    
    # Create a test image
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (100, 100), (200, 200), (0, 255, 0), -1)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        image_path = f.name
        cv2.imwrite(image_path, test_image)
    
    python_path = "/Users/macbook/miniforge3/envs/rubi_robot/bin/python"
    script_path = os.path.join(os.path.dirname(__file__), "vision", "yolo_detector.py")
    
    start = time.time()
    result = subprocess.run([python_path, script_path, image_path],
                          capture_output=True, text=True, timeout=30.0)
    elapsed = time.time() - start
    
    if result.returncode == 0:
        print(f"  Full script execution: {elapsed:.3f}s")
        print(f"  Output: {result.stdout[:200]}...")
        return elapsed
    else:
        print(f"  Error (code {result.returncode}): {result.stderr[:500]}")
        return None
    
    # Clean up
    if os.path.exists(image_path):
        os.remove(image_path)

def test_disk_io_overhead():
    """Test disk I/O overhead (saving/loading frames)"""
    print("\n🧪 Testing disk I/O overhead...")
    
    # Create a test frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Test saving to disk
    times_save = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            path = f.name
            start = time.time()
            cv2.imwrite(path, frame)
            elapsed = time.time() - start
            times_save.append(elapsed)
            os.remove(path)
    
    avg_save = sum(times_save) / len(times_save)
    print(f"  Average image save time: {avg_save:.3f}s")
    return avg_save

def main():
    print("=" * 70)
    print("YOLO Performance Analysis")
    print("=" * 70)
    
    print("\n🔍 Analyzing performance bottlenecks...")
    
    # Run tests
    subprocess_time = test_subprocess_startup()
    model_load_time = test_yolo_model_loading()
    inference_time = test_yolo_inference()
    full_script_time = test_full_yolo_detector()
    disk_io_time = test_disk_io_overhead()
    
    print("\n" + "=" * 70)
    print("PERFORMANCE BOTTLENECK ANALYSIS")
    print("=" * 70)
    
    print("\n📊 Breakdown of 10.54s YOLO detection:")
    print("  (Based on test_real_detection.py results)")
    
    if all(v is not None for v in [subprocess_time, model_load_time, inference_time, full_script_time, disk_io_time]):
        print(f"\n  Subprocess startup: ~{subprocess_time:.2f}s")
        print(f"  Model loading: ~{model_load_time:.2f}s")
        print(f"  Inference: ~{inference_time:.2f}s")
        print(f"  Disk I/O (save/load): ~{disk_io_time:.2f}s")
        print(f"  Other overhead: ~{full_script_time - (subprocess_time + model_load_time + inference_time + disk_io_time):.2f}s")
        print(f"  Total estimated: ~{full_script_time:.2f}s")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("  1. Cache model loading - Load once and reuse")
    print("  2. Reduce subprocess overhead - Use shared memory or pipes")
    print("  3. Optimize image transfer - Pass frames via stdin/stdout instead of disk")
    print("  4. Use smaller model or lower resolution")
    print("  5. Implement detection caching - Show previous results while new detection runs")
    
    print("\n💡 QUICK FIXES:")
    print("  • Reduce detection frequency (every 2-3 seconds instead of every frame)")
    print("  • Implement detection result caching")
    print("  • Show 'processing...' indicator in vision window")
    
    return True

if __name__ == "__main__":
    main()