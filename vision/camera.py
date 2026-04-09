"""
Camera and object detection module for Rubi robot
"""

import cv2
import numpy as np
from ultralytics import YOLO
import threading
import time
import math

class Camera:
    """Handles camera capture and object detection"""
    
    def __init__(self):
        self.camera = None
        self.model = None
        self.running = False
        self.last_frame = None
        self.detected_objects = []
        self.frame_lock = threading.Lock()
        
        # Search state
        self.searching = False
        self.search_target = None
        self.search_callback = None
        
        # Performance optimization
        self.frame_skip = 2  # Process every 2nd frame
        self.detection_interval = 0.1  # Minimum time between detections
        self.last_detection_time = 0
        
    def initialize(self):
        """Initialize camera and YOLO model"""
        print("📷 Initializing camera...")
        
        # Try different camera indices
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
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size for lower latency
        
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
                current_time = time.time()
                
                with self.frame_lock:
                    self.last_frame = frame.copy()
                
                # Run detection at optimal intervals
                frame_count += 1
                time_since_last = current_time - self.last_detection_time
                
                if (frame_count % self.frame_skip == 0 and 
                    time_since_last >= self.detection_interval):
                    self._detect_objects(frame)
                    self.last_detection_time = current_time
            else:
                time.sleep(0.001)  # Very short sleep when no frame
                
    def _detect_objects(self, frame):
        """Run object detection on frame"""
        if not self.model:
            return
            
        try:
            # Run YOLO detection with smaller image size for speed
            results = self.model(frame, verbose=False, imgsz=320)  # Reduced from 640
            
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
                    
                    # Calculate position relative to frame center
                    center_x = (x1 + x2) / 2
                    frame_center = frame.shape[1] / 2
                    frame_height = frame.shape[0]
                    
                    # Direction (left/right/center)
                    if center_x < frame_center - 50:
                        direction = "left"
                    elif center_x > frame_center + 50:
                        direction = "right"
                    else:
                        direction = "center"
                    
                    # Estimate distance (simplified)
                    object_width = x2 - x1
                    if object_width > 0:
                        # More realistic distance formula with bounds
                        # Assuming a phone is roughly 8cm wide, project to distance
                        distance = (0.08 * 320) / object_width  # imgsz=320
                        distance = max(0.3, min(distance, 5.0))  # Clamp between 30cm and 5m
                    else:
                        distance = 0
                    
                    detected.append({
                        'name': class_name,
                        'confidence': round(confidence, 2),
                        'direction': direction,
                        'distance': round(distance, 1),
                        'bbox': (int(x1), int(y1), int(x2), int(y2))
                    })
            
            # Sort by distance
            detected.sort(key=lambda x: x['distance'])
            
            with self.frame_lock:
                self.detected_objects = detected
                
            # Check search target
            if self.searching and self.search_target:
                self._check_search_target(detected)
                
        except Exception as e:
            print(f"❌ Detection error: {e}")
            
    def _check_search_target(self, detected):
        """Check if we found what we're searching for"""
        target_map = {
            'chair': ['chair', 'stool', 'seat'],
            'person': ['person'],
            'table': ['table', 'dining table', 'desk'],
            'couch': ['couch', 'sofa'],
            'bottle': ['bottle'],
            'cup': ['cup', 'mug'],
            'phone': ['cell phone'],
            'book': ['book'],
            'laptop': ['laptop']
        }
        
        possible_names = target_map.get(self.search_target, [self.search_target])
        
        for obj in detected:
            if obj['name'] in possible_names:
                if self.search_callback:
                    self.search_callback(obj)
                break
            
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
            
        object_counts = {}
        for obj in objects:
            name = obj['name']
            object_counts[name] = object_counts.get(name, 0) + 1
        
        items = []
        for name, count in object_counts.items():
            if count == 1:
                items.append(f"a {name}")
            else:
                items.append(f"{count} {name}s")
        
        if len(items) == 1:
            description = f"I see {items[0]}"
        elif len(items) == 2:
            description = f"I see {items[0]} and {items[1]}"
        else:
            description = f"I see {', '.join(items[:-1])}, and {items[-1]}"
        
        if objects:
            closest = min(objects, key=lambda x: x['distance'])
            description += f". The {closest['name']} is closest, to your {closest['direction']}."
            
        return description
        
    def find_object(self, target_name):
        """Find a specific object"""
        objects = self.get_current_objects()
        
        target_map = {
            'chair': ['chair', 'stool', 'seat'],
            'person': ['person'],
            'table': ['table', 'dining table', 'desk'],
            'couch': ['couch', 'sofa'],
            'bottle': ['bottle'],
            'cup': ['cup', 'mug'],
            'phone': ['cell phone'],
            'book': ['book'],
            'laptop': ['laptop']
        }
        
        possible_names = target_map.get(target_name, [target_name])
        matches = [obj for obj in objects if obj['name'] in possible_names]
        
        if not matches:
            return None
        return min(matches, key=lambda x: x['distance'])
        
    def draw_detections(self, frame=None):
        """Draw bounding boxes on frame (optimized)"""
        if frame is None:
            frame = self.get_frame()
        if frame is None:
            return None
            
        objects = self.get_current_objects()
        
        # Draw only the most confident objects (max 5)
        for obj in objects[:5]:
            x1, y1, x2, y2 = obj['bbox']
            
            # Simple coloring
            if obj['name'] == 'person':
                color = (0, 255, 0)
            elif obj['name'] in ['chair', 'couch']:
                color = (255, 165, 0)
            elif 'phone' in obj['name']:
                color = (0, 255, 255)
            else:
                color = (255, 0, 0)
            
            # Draw box (simpler, no extra text for speed)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Simple label
            label = f"{obj['name']}"
            cv2.putText(frame, label, (x1, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return frame
        
    def start_search(self, target, callback):
        """Start searching for an object"""
        self.searching = True
        self.search_target = target
        self.search_callback = callback
        print(f"🔍 Started searching for {target}")
        
    def stop_search(self):
        """Stop searching"""
        self.searching = False
        self.search_target = None
        self.search_callback = None
        print("🔍 Search stopped")
        
    def stop(self):
        """Stop camera capture"""
        self.running = False
        self.searching = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        if self.camera:
            self.camera.release()
        print("📷 Camera stopped")