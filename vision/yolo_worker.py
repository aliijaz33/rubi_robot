#!/usr/bin/env python3
"""
Persistent YOLO worker process that stays alive and processes frames.
This avoids the 12-second import overhead of ultralytics on each detection.
"""

import os
import sys
import json
import base64
import numpy as np
import cv2
from ultralytics import YOLO

# Set environment variables for OpenMP stability
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

class YOLOWorker:
    def __init__(self):
        print("🚀 YOLO worker starting up...", file=sys.stderr)
        # Load model once (this takes time but only happens once)
        print("📦 Loading YOLOv8n model...", file=sys.stderr)
        self.model = YOLO('yolov8n.pt')
        print("✅ YOLO model loaded, ready for inference", file=sys.stderr)
        
    def process_frame(self, frame_data):
        """Process a frame and return detections"""
        try:
            # Decode base64 frame data
            frame_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return []
            
            # Run detection
            results = self.model(frame, verbose=False, imgsz=320)
            
            detected = []
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = box.conf[0].item()
                    class_id = int(box.cls[0].item())
                    class_name = self.model.names[class_id]
                    
                    # Skip low confidence detections
                    if confidence < 0.5:
                        continue
                    
                    # Calculate direction based on bounding box position
                    frame_width = frame.shape[1]
                    bbox_center_x = (x1 + x2) / 2
                    
                    if bbox_center_x < frame_width * 0.4:
                        direction = 'left'
                    elif bbox_center_x > frame_width * 0.6:
                        direction = 'right'
                    else:
                        direction = 'center'
                    
                    # Estimate distance (simplified - based on bounding box size)
                    bbox_area = (x2 - x1) * (y2 - y1)
                    frame_area = frame.shape[0] * frame.shape[1]
                    area_ratio = bbox_area / frame_area
                    
                    # Simple distance estimation: larger object = closer
                    if area_ratio > 0.1:  # Covers >10% of frame
                        distance = 0.3  # Very close
                    elif area_ratio > 0.05:  # 5-10%
                        distance = 0.8
                    elif area_ratio > 0.02:  # 2-5%
                        distance = 1.5
                    else:
                        distance = 2.5  # Far away
                    
                    detected.append({
                        'name': class_name,
                        'confidence': round(confidence, 3),
                        'direction': direction,
                        'distance': round(distance, 1),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)]
                    })
            
            return detected
            
        except Exception as e:
            print(f"❌ Error in YOLO worker: {e}", file=sys.stderr)
            return []

def main():
    """Main loop for persistent worker"""
    worker = YOLOWorker()
    
    print("🔄 YOLO worker ready, waiting for frames...", file=sys.stderr)
    
    # Read frames from stdin (base64 encoded)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        if line == "EXIT":
            print("👋 YOLO worker shutting down", file=sys.stderr)
            break
            
        # Process frame
        detections = worker.process_frame(line)
        
        # Send results as JSON
        result = json.dumps(detections)
        print(result, flush=True)

if __name__ == "__main__":
    main()