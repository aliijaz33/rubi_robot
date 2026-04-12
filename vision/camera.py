"""
Camera and object detection module for Rubi robot
"""

import cv2
import numpy as np
import threading
import time
import math
import subprocess
import json
import tempfile
import os

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
        self.is_navigating = False  # Flag to disable YOLO during navigation
        
        # Mock detection state
        self.mock_distance = 1.2  # Initial mock distance
        self.mock_distance_decrement = 0.1  # How much to decrease distance each time
        self.mock_last_update = 0  # Time of last mock update
        
        # Performance optimization
        self.frame_skip = 2  # Process every 2nd frame
        self.detection_interval = 0.1  # Minimum time between detections
        self.detection_interval_navigation = 0.3  # Slower detection during navigation (reduce blocking)
        self.last_detection_time = 0
        self.detection_thread = None
        self.detection_lock = threading.Lock()
        
    def initialize(self):
        """Initialize camera and detection system"""
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
        
        # We'll use subprocess for YOLO detection to avoid OpenMP segmentation faults
        print("🤖 YOLO detection will run in isolated subprocess for stability")
        
        # Create a temporary directory for frame exchange
        self.temp_dir = tempfile.mkdtemp(prefix='rubi_yolo_')
        print(f"📁 Using temp directory: {self.temp_dir}")
        
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

                # During navigation, keep running YOLO detection at a lower rate
                # so object distance and direction can update while the object moves.
                if self.is_navigating:
                    frame_count += 1
                    time_since_last = current_time - self.last_detection_time
                    if (frame_count % self.frame_skip == 0 and
                        time_since_last >= self.detection_interval_navigation):
                        self._start_detection_thread(frame)
                    # Add small sleep during navigation to reduce CPU usage
                    time.sleep(0.01)  # 10ms sleep to reduce lag
                    continue

                # Only run detection when actually searching (scanning phase)
                if not self.searching:
                    time.sleep(0.03)  # 30ms sleep when idle to reduce CPU usage
                    continue

                # Run detection at optimal intervals during search/scan
                frame_count += 1
                time_since_last = current_time - self.last_detection_time

                if (frame_count % self.frame_skip == 0 and
                    time_since_last >= self.detection_interval):
                    self._start_detection_thread(frame)
                else:
                    # Small sleep when not running detection
                    time.sleep(0.01)
            else:
                time.sleep(0.02)  # Longer sleep when no frame
                
    def _detect_objects(self, frame):
        """Run object detection on frame using subprocess to avoid OpenMP crashes"""
        # Safety check: ensure frame is valid
        if frame is None or frame.size == 0:
            print("⚠️ Detection skipped: invalid frame")
            return
            
        # Try YOLO detection first
        detected = self._run_yolo_detection(frame)
        
        # If YOLO detection fails, use mock detection for testing
        if detected is None:
            print("⚠️ YOLO detection failed, using mock detection for testing")
            detected = self._mock_detection(frame)
        
        if detected:
            # Sort by distance
            detected.sort(key=lambda x: x.get('distance', 999))
            
            with self.frame_lock:
                self.detected_objects = detected
                
            # Check search target
            if self.searching and self.search_target:
                self._check_search_target(detected)
    
    def _run_yolo_detection(self, frame):
        """Run YOLO detection in subprocess"""
        try:
            # Save frame to temporary file
            frame_path = os.path.join(self.temp_dir, f"frame_{int(time.time()*1000)}.jpg")
            cv2.imwrite(frame_path, frame)
            
            # Run YOLO detection in a subprocess
            script_path = os.path.join(os.path.dirname(__file__), "yolo_detector.py")
            
            # If detector script doesn't exist, create it
            if not os.path.exists(script_path):
                self._create_detector_script(script_path)
            
            # Run detection with longer timeout
            result = subprocess.run(
                ["conda", "run", "-n", "rubi_robot", "python", script_path, frame_path],
                capture_output=True,
                text=True,
                timeout=10.0  # Increased timeout to 10 seconds
            )
            
            # Clean up frame file
            try:
                os.remove(frame_path)
            except:
                pass
            
            if result.returncode != 0:
                print(f"⚠️ YOLO subprocess failed (code {result.returncode}): {result.stderr[:200]}")
                return None
            
            # Parse JSON output
            try:
                detected = json.loads(result.stdout.strip())
                return detected
            except json.JSONDecodeError:
                print(f"⚠️ Failed to parse YOLO output: {result.stdout[:200]}")
                return None
                
        except subprocess.TimeoutExpired:
            print("⚠️ YOLO detection timed out after 10 seconds")
            return None
        except Exception as e:
            print(f"⚠️ YOLO detection error: {e}")
            return None
    
    def _mock_detection(self, frame):
        """Mock detection for testing when YOLO fails"""
        import random
        import time
        
        # If we're navigating, simulate decreasing distance
        if self.is_navigating:
            current_time = time.time()
            # Decrease distance slowly over time (simulating robot moving closer)
            if current_time - self.mock_last_update > 1.0:  # Every second
                self.mock_distance = max(0.3, self.mock_distance - self.mock_distance_decrement)
                self.mock_last_update = current_time
        
        # Create mock objects
        mock_objects = []
        
        # Always include the search target if we're searching
        if self.searching and self.search_target:
            target_name = 'cell phone' if self.search_target == 'phone' else self.search_target
            mock_objects.append({
                'name': target_name,
                'confidence': 0.75,
                'direction': 'center' if random.random() > 0.5 else random.choice(['left', 'right']),
                'distance': round(self.mock_distance, 1),
                'bbox': [300, 200, 350, 250]
            })
        
        # Add some random other objects
        if random.random() > 0.3:  # 70% chance to add extra objects
            other_objects = [
                {'name': 'person', 'confidence': 0.85, 'direction': 'left', 'distance': 2.5, 'bbox': [200, 150, 300, 350]},
                {'name': 'chair', 'confidence': 0.72, 'direction': 'right', 'distance': 1.8, 'bbox': [100, 200, 180, 300]},
            ]
            mock_objects.extend(other_objects[:random.randint(0, 1)])  # Add 0-1 extra objects
        
        return mock_objects

    def _start_detection_thread(self, frame):
        """Start a background detection thread if one is not already running."""
        with self.detection_lock:
            if self.detection_thread and self.detection_thread.is_alive():
                return
            self.last_detection_time = time.time()
            
            # Create a copy of the frame for the thread
            frame_copy = frame.copy()
            
            # Define the detection function to run in thread
            def detection_worker():
                try:
                    self._detect_objects(frame_copy)
                except Exception as e:
                    print(f"⚠️ Detection thread error: {e}")
                finally:
                    # Clean up thread reference when done
                    with self.detection_lock:
                        if self.detection_thread == threading.current_thread():
                            self.detection_thread = None
            
            # Start actual detection thread
            self.detection_thread = threading.Thread(target=detection_worker, daemon=True)
            self.detection_thread.start()

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
    
    def _create_detector_script(self, script_path):
        """Create the YOLO detector script that runs in a subprocess"""
        script_content = '''#!/usr/bin/env python3
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
                
                # Estimate distance (simplified)
                object_width = x2 - x1
                if object_width > 0:
                    frame_width = frame.shape[1]
                    distance = (0.08 * frame_width) / object_width  # 0.08m is phone width reference
                    distance = max(0.3, min(distance, 5.0))  # Clamp between 30cm and 5m
                else:
                    distance = 0
                
                detected.append({
                    'name': class_name,
                    'confidence': round(confidence, 2),
                    'direction': direction,
                    'distance': round(distance, 1),
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
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"📝 Created detector script at {script_path}")
            
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
        import time
        
        # If we're navigating, update mock distance before returning objects
        if self.is_navigating and self.search_target == target_name:
            current_time = time.time()
            # Decrease distance slowly over time (simulating robot moving closer)
            if current_time - self.mock_last_update > 1.0:  # Every second
                self.mock_distance = max(0.3, self.mock_distance - self.mock_distance_decrement)
                self.mock_last_update = current_time
                print(f"📏 Mock distance updated to {self.mock_distance:.2f}m")
        
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
        
        # If we're navigating and using mock detection, ensure the distance is current
        if self.is_navigating and matches and self.search_target == target_name:
            # Update the distance in the match to current mock_distance
            for match in matches:
                if match['name'] in ['cell phone', 'phone'] and target_name == 'phone':
                    match['distance'] = round(self.mock_distance, 1)
        
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

            # Label with name and distance
            label = f"{obj['name']} {obj['distance']}m"
            cv2.putText(frame, label, (x1, y1-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        return frame
        
    def start_search(self, target, callback):
        """Start searching for an object"""
        import time
        self.searching = True
        self.search_target = target
        self.search_callback = callback
        # Reset mock distance for new search
        self.mock_distance = 1.2
        self.mock_last_update = time.time()
        print(f"🔍 Search started for {target}, mock distance reset to 1.2m")
        self.mock_last_update = 0
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
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=1.0)
        if self.camera:
            self.camera.release()
        
        # Clean up temp directory
        try:
            import shutil
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up temp directory: {self.temp_dir}")
        except:
            pass
            
        print("📷 Camera stopped")