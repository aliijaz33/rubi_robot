#!/usr/bin/env python3
"""Test the YOLO detector script directly"""

import cv2
import numpy as np
import json
import subprocess
import tempfile
import os

# Create a dummy image
print("🎨 Creating dummy image...")
dummy_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

# Save to temp file
with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
    image_path = f.name
    cv2.imwrite(image_path, dummy_image)
    print(f"📁 Saved dummy image to {image_path}")

# Run the detector script
print("🔍 Running detector script...")
script_path = "vision/yolo_detector.py"

try:
    result = subprocess.run(
        ["conda", "run", "-n", "rubi_robot", "python", script_path, image_path],
        capture_output=True,
        text=True,
        timeout=10.0
    )
    
    print(f"Exit code: {result.returncode}")
    print(f"Stdout length: {len(result.stdout)}")
    print(f"Stderr: {result.stderr[:200] if result.stderr else 'None'}")
    
    if result.returncode == 0:
        try:
            detected = json.loads(result.stdout.strip())
            print(f"✅ Detected {len(detected)} objects")
            for obj in detected[:5]:
                print(f"  - {obj['name']} ({obj['confidence']}) at {obj['distance']}m")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Output: {result.stdout[:200]}")
    else:
        print(f"❌ Script failed with return code {result.returncode}")
        
except subprocess.TimeoutExpired:
    print("❌ Script timed out after 10 seconds")
except Exception as e:
    print(f"❌ Error running script: {e}")

# Clean up
try:
    os.remove(image_path)
except:
    pass