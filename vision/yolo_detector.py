#!/usr/bin/env python3
"""
YOLO detector script that runs in isolated subprocess to avoid OpenMP crashes
"""
import os
import sys
import json
import numpy as np

# Set environment variables before importing anything
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

try:
    import cv2
    from ultralytics import YOLO
except ImportError as e:
    print(f"{{'error': 'Import failed: {e}'}}")
    sys.exit(1)

def detect_objects(image_path):
    """Run YOLO detection on an image"""
    try:
        # Load image
        frame = cv2.imread(image_path)
        if frame is None:
            return []
        
        # Load model (cached in global scope for performance)
        if not hasattr(detect_objects, 'model'):
            detect_objects.model = YOLO('yolov8n.pt')
        
        # Run detection
        results = detect_objects.model(frame, verbose=False, imgsz=320)
        
        detected = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = box.conf[0].item()
                class_id = int(box.cls[0].item())
                class_name = detect_objects.model.names[class_id]
                
                # Skip low confidence detections
                if confidence < 0.5:
                    continue
                
                # Calculate position relative to frame center
                center_x = (x1 + x2) / 2
                frame_center = frame.shape[1] / 2
                
                # Direction (left/right/center)
                if center_x < frame_center - 50:
                    direction = "left"
                elif center_x > frame_center + 50:
                    direction = "right"
                else:
                    direction = "center"
                
                # Estimate distance (continuous based on bounding box size)
                bbox_area = (x2 - x1) * (y2 - y1)
                frame_area = frame.shape[0] * frame.shape[1]
                area_ratio = bbox_area / frame_area
                
                # Continuous distance estimation: distance ∝ 1/sqrt(area_ratio)
                # Same formula as in yolo_worker.py for consistency
                if area_ratio > 0.001:  # Avoid division by very small numbers
                    k = 0.057
                    distance = k / (area_ratio ** 0.5)
                    
                    # Add object-type specific adjustments
                    if 'phone' in class_name.lower():
                        distance = distance * 0.9
                    elif 'person' in class_name.lower():
                        distance = distance * 1.1
                    
                    # Clamp to reasonable range (0.08m to 5.0m)
                    distance = max(0.08, min(distance, 5.0))
                else:
                    distance = 5.0  # Very far away
                
                # Round to 2 decimal places for smoother changes
                distance_rounded = round(distance, 2)
                
                detected.append({
                    'name': class_name,
                    'confidence': round(confidence, 2),
                    'direction': direction,
                    'distance': distance_rounded,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })
        
        return detected
        
    except Exception as e:
        print(f"{{'error': 'Detection failed: {e}'}}")
        return []

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{"error": "Usage: python yolo_detector.py <image_path>"}')
        sys.exit(1)
    
    image_path = sys.argv[1]
    results = detect_objects(image_path)
    print(json.dumps(results))
