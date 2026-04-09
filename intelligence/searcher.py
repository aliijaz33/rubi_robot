"""
Search and navigation module for Rubi robot
"""

import time
import threading

class ObjectSearcher:
    """Handles autonomous searching for objects"""
    
    def __init__(self, motor_controller, camera, speaker):
        self.motor = motor_controller
        self.camera = camera
        self.speaker = speaker
        self.searching = False
        self.search_thread = None
        self.search_target = None
        self.navigating = False
        
        # Search patterns
        self.search_patterns = {
            'scan': self._scan_pattern,
            'spiral': self._spiral_pattern
        }
        
    def search_for_object(self, target, pattern='scan'):
        """Start searching for an object"""
        if self.searching:
            self.speaker.speak("Already searching")
            return
            
        self.searching = True
        self.navigating = False
        self.search_target = target
        self.found_object = None
        
        # Register callback with camera
        self.camera.start_search(target, self._object_found)
        
        # Start search in background
        self.search_thread = threading.Thread(
            target=self.search_patterns.get(pattern, self._scan_pattern)
        )
        self.search_thread.daemon = True
        self.search_thread.start()
        
        self.speaker.speak(f"Searching for {target}")
        
    def stop_searching(self):
        """Stop the current search immediately"""
        if self.searching:
            print("🛑 Stopping search immediately")
            self.searching = False
            self.navigating = False
            self.camera.stop_search()
            self.motor.stop()
            self.speaker.speak("Search stopped")
            return True
        return False
        
    def _object_found(self, obj):
        """Called when camera finds the target"""
        if not self.searching or self.navigating:
            return
            
        self.found_object = obj
        self.speaker.speak(f"I found a {obj['name']}!")
        
        # Small pause to let speech complete
        time.sleep(0.5)
        
        # Navigate to the object
        self._navigate_to_object(obj)
        
    def _scan_pattern(self):
        """Scan by turning in place"""
        print("🔄 Starting scan pattern")
        
        steps = 8  # 45 degrees per step
        status_announced = False
        
        for i in range(steps):
            if not self.searching:  # Check if search was stopped
                print("⏹️ Search stopped during scan")
                return
                
            if self.navigating:  # Stop if navigating
                return
                
            # Turn 45 degrees
            print(f"🔄 Scan step {i+1}/{steps}")
            self.motor.turn_right(40)
            time.sleep(0.8)
            self.motor.stop()
            
            # Look at current view
            time.sleep(1)
            
            if i == 3 and not status_announced and self.searching and not self.navigating:
                self.speaker.speak("Still looking")
                status_announced = True
                
        if self.searching and not self.navigating and not self.found_object:
            self.speaker.speak(f"I couldn't find a {self.search_target}")
            self.stop_searching()
            
    def _spiral_pattern(self):
        """Search in an expanding spiral"""
        print("🔄 Starting spiral search")
        
        for distance in [1, 2]:
            if not self.searching or self.navigating:
                return
                
            self.speaker.speak("Moving forward")
            self.motor.forward(40)
            time.sleep(distance)
            self.motor.stop()
            
            # Look around
            self.motor.turn_right(40)
            time.sleep(0.8)
            self.motor.stop()
            
            time.sleep(1)
            
        if self.searching and not self.navigating and not self.found_object:
            self.speaker.speak(f"Couldn't find {self.search_target}")
            self.stop_searching()
            
    def _navigate_to_object(self, obj):
        """Navigate to a detected object"""
        if not self.searching:
            return

        self.navigating = True
        # Disable YOLO detection during navigation to keep camera frames flowing
        self.camera.is_navigating = True
        print(f"🧭 Navigating to {obj['name']} at distance {obj['distance']}m")

        self.speaker.speak(f"Moving towards the {obj['name']}")
        time.sleep(0.5)

        # First, align with object
        if obj['direction'] == 'left':
            print("↪️ Aligning left")
            self.motor.turn_left(30)
            time.sleep(0.5)
        elif obj['direction'] == 'right':
            print("↩️ Aligning right")
            self.motor.turn_right(30)
            time.sleep(0.5)

        self.motor.stop()
        time.sleep(0.5)

        # Move towards object with better distance tracking
        target_distance = 0.35  # Stop at ~1 foot (one hand length)
        approach_speed = 30  # Slower speed for better control
        max_attempts = 12  # Allow more attempts for stable approach
        attempts = 0
        last_distance = obj['distance']
        stall_counter = 0
        lost_object_counter = 0  # Track how many times we lose the object

        while self.searching and self.navigating and attempts < max_attempts:
            # Check if search was stopped
            if not self.searching:
                return

            # Get current object position
            current = self.camera.find_object(self.search_target)

            if not current:
                print("👀 Lost sight of object")
                lost_object_counter += 1

                # Allow losing sight a couple times before giving up
                if lost_object_counter >= 2:
                    self.speaker.speak("Lost sight of the object")
                    self.navigating = False
                    self.camera.is_navigating = False  # Re-enable YOLO detection
                    # Resume searching
                    if self.searching:
                        self._scan_pattern()
                    return

                # Try one more approach move before losing sight
                print(f"   Trying to reach using last known position ({lost_object_counter}/2)")
                self.motor.forward(approach_speed)
                time.sleep(0.5)
                self.motor.stop()
                time.sleep(0.5)
                attempts += 1
                continue

            # Reset lost counter when we see object again
            lost_object_counter = 0
            current_distance = current['distance']
            print(f"📏 Distance: {current_distance:.1f}m")

            # Check if we've reached the target
            if current_distance <= target_distance:
                print(f"✅ Reached {obj['name']} at {current_distance:.1f}m")
                self.motor.stop()
                self.speaker.speak(f"Reached the {obj['name']}")
                self.camera.is_navigating = False  # Re-enable YOLO detection
                self.stop_searching()
                return

            # Check if we're making progress
            distance_change = last_distance - current_distance
            if distance_change > 0.05:  # Moving closer
                print(f"✅ Making progress: -{distance_change:.2f}m")
                stall_counter = 0
            else:
                stall_counter += 1
                print(f"⚠️ Not making progress ({stall_counter}/3)")

            # Exit sooner if clearly stalled
            if stall_counter >= 3:
                print("🔄 Stalled, trying to reacquire")
                self.motor.turn_right(30)
                time.sleep(0.5)
                self.motor.stop()
                stall_counter = 0
                time.sleep(0.5)
                # Skip the rest of this iteration and continue
                attempts += 1
                continue

            # Re-align if object is not centered
            if current['direction'] != 'center':
                print(f"↪️ Re-aligning to {current['direction']}")
                if current['direction'] == 'left':
                    self.motor.turn_left(20)
                else:
                    self.motor.turn_right(20)
                time.sleep(0.3)
                self.motor.stop()
                time.sleep(0.3)

            # Move forward
            print(f"➡️ Moving forward at {approach_speed}%")
            self.motor.forward(approach_speed)
            time.sleep(0.8)
            self.motor.stop()

            last_distance = current_distance
            attempts += 1
            time.sleep(0.3)  # Brief pause to let camera update

        if self.searching and self.navigating:
            print("❌ Navigation failed - too many attempts")
            self.speaker.speak("I'm having trouble reaching the object")
            self.navigating = False
            self.camera.is_navigating = False  # Re-enable YOLO detection
            # Resume searching
            if self.searching:
                time.sleep(0.5)
                self._scan_pattern()
        
    def stop_search(self):
        """Stop searching"""
        return self.stop_searching()