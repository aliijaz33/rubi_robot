"""
Camera and object detection module for Rubi robot
"""

import cv2
import numpy as np
from ultralytics import YOLO
import threading
import time

class Camera:
    """Handles camera capture and object detection"""
    
    def __init__(self):
        self.camera = None
        self.model = None
        self.running = False
        self.last_frame = None
        self.detected_objects = []
        self.frame_lock = threading.Lock()
        
    def initialize(self):
        """Initialize camera and YOLO model"""
        print("📷 Initializing camera...")
        
        # Try different camera indices (0 is usually built-in Mac camera)
        for camera_id in [0, 1]:
            self.camera = cv2.VideoCapture(camera_id)
            if self.camera.isOpened():
                print(f"✅ Camera found at index {camera_id}")
                break
        
        if not self.camera or not self.camera.isOpened():
            print("❌ No camera found")
            return False
            
        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        print("🤖 Loading YOLO model (this may take a moment)...")
        try:
            # Use the smallest YOLO model for better performance
            self.model = YOLO('yolov8n.pt')
            print("✅ YOLO model loaded!")
        except Exception as e:
            print(f"❌ Failed to load YOLO model: {e}")
            return False
            
        return True
        
    def start_capture(self):
        """Start continuous frame capture in background thread"""
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        print("📷 Camera capture started")
        
    def _capture_loop(self):
        """Continuous frame capture and detection loop"""
        frame_count = 0
        while self.running and self.camera:
            ret, frame = self.camera.read()
            if ret:
                with self.frame_lock:
                    self.last_frame = frame.copy()
                
                # Run detection every 5 frames to save CPU
                frame_count += 1
                if frame_count % 5 == 0:
                    self._detect_objects(frame)
            else:
                time.sleep(0.01)
                
    def _detect_objects(self, frame):
        """Run object detection on frame"""
        if not self.model:
            return
            
        try:
            # Run YOLO detection
            results = self.model(frame, verbose=False)
            
            detected = []
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = box.conf[0].item()
                    class_id = int(box.cls[0].item())
                    class_name = self.model.names[class_id]
                    
                    # Calculate position relative to frame center
                    center_x = (x1 + x2) / 2
                    frame_center = frame.shape[1] / 2
                    
                    if center_x < frame_center - 50:
                        direction = "left"
                    elif center_x > frame_center + 50:
                        direction = "right"
                    else:
                        direction = "center"
                    
                    # Estimate distance (simplified - wider = closer)
                    object_width = x2 - x1
                    if object_width > 0:
                        # Rough distance estimation (calibrate for your camera)
                        distance = 500 / object_width
                    else:
                        distance = 0
                    
                    # Only keep high confidence detections
                    if confidence > 0.5:
                        detected.append({
                            'name': class_name,
                            'confidence': round(confidence, 2),
                            'direction': direction,
                            'distance': round(distance, 1),
                            'bbox': (int(x1), int(y1), int(x2), int(y2))
                        })
            
            with self.frame_lock:
                self.detected_objects = detected
                
        except Exception as e:
            print(f"❌ Detection error: {e}")
            
    def get_current_objects(self):
        """Get the latest detected objects"""
        with self.frame_lock:
            return self.detected_objects.copy()
            
    def get_frame(self):
        """Get the latest camera frame"""
        with self.frame_lock:
            if self.last_frame is not None:
                return self.last_frame.copy()
            return None
            
    def describe_scene(self):
        """Generate a text description of current scene"""
        objects = self.get_current_objects()
        
        if not objects:
            return "I don't see anything interesting"
            
        # Count objects by type
        object_counts = {}
        for obj in objects:
            name = obj['name']
            object_counts[name] = object_counts.get(name, 0) + 1
        
        # Build description
        if len(objects) == 1:
            description = f"I see a {objects[0]['name']} "
        else:
            description = f"I see {len(objects)} objects. "
        
        # Describe each unique object
        items = []
        for name, count in object_counts.items():
            if count == 1:
                items.append(f"a {name}")
            else:
                items.append(f"{count} {name}s")
        
        if len(items) == 1:
            description += items[0]
        elif len(items) == 2:
            description += f"{items[0]} and {items[1]}"
        else:
            description += ", ".join(items[:-1]) + f", and {items[-1]}"
        
        description += ". "
        
        # Add closest object info
        if objects:
            closest = min(objects, key=lambda x: x['distance'])
            description += f"The {closest['name']} is closest, to your {closest['direction']}."
            
        return description
        
    def find_object(self, target_name):
        """Find a specific object (like 'chair', 'person', etc.)"""
        objects = self.get_current_objects()
        
        # Filter for target object (partial match)
        matches = [obj for obj in objects if target_name.lower() in obj['name'].lower()]
        
        if not matches:
            return None
            
        # Return the closest match
        return min(matches, key=lambda x: x['distance'])
        
    def draw_detections(self, frame=None):
        """Draw bounding boxes on frame (for debugging)"""
        if frame is None:
            frame = self.get_frame()
        if frame is None:
            return None
            
        objects = self.get_current_objects()
        
        for obj in objects:
            x1, y1, x2, y2 = obj['bbox']
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # Draw label
            label = f"{obj['name']} {obj['confidence']}"
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        return frame
        
    def stop(self):
        """Stop camera capture"""
        self.running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        if self.camera:
            self.camera.release()
        print("📷 Camera stopped")