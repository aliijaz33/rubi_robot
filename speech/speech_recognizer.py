"""
Speech recognition module for Rubi robot
"""

import speech_recognition as sr
import threading
import time
from .speaker import Speaker

class SpeechRecognizer:
    """Handles voice commands for Rubi robot"""

    def __init__(self, motor_controller):
        self.motor = motor_controller
        self.speaker = Speaker()
        self.recognizer = sr.Recognizer()

        # Set reference in speaker so it can track speaking time
        self.speaker.recognizer = self

        # Use the built-in microphone (index 0)
        self.microphone = sr.Microphone(device_index=0)

        self.listening = False
        self.wake_word = "rubi"

        # Track when speaker last spoke to avoid audio feedback
        self.last_speak_time = 0
        self.speaker_cooldown = 2.0  # Wait 3 seconds after speaker finishes (for wake word detection only)
        self.speech_guard_period = 1.5  # Completely ignore any recognition during this period (increased from 1.5)

        # Adjust recognizer settings for maximum distance sensitivity
        # Much lower energy threshold makes microphone extremely sensitive (default is 300)
        self.recognizer.energy_threshold = 100  # Very low for distant/quiet voices
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0  # Increased to wait longer for speech to start
        self.recognizer.phrase_threshold = 0.3  # Lower threshold for phrase detection
        self.recognizer.non_speaking_duration = 0.5  # Shorter non-speaking duration
        
        # Adjust for ambient noise with longer calibration for better accuracy
        print("🎤 Calibrating microphone for ambient noise (ULTRA sensitive for distance)...")
        with self.microphone as source:
            print("   Please wait... (5 seconds for optimal calibration)")
            self.recognizer.adjust_for_ambient_noise(source, duration=5)
            print(f"   Energy threshold set to: {self.recognizer.energy_threshold}")
        print("✅ Microphone ready! (ULTRA sensitive for distant/quiet voices)")
        
    def listen_for_wake_word(self):
        """Listen for the wake word 'Rubi'"""
        # Don't listen while speaker is active
        if self.speaker.is_speaking:
            return False

        # Wait for microphone to settle after speaker finishes
        time_since_speak = time.time() - self.last_speak_time
        if time_since_speak < self.speech_guard_period:
            # During speech guard period, completely ignore any audio
            return False
        if time_since_speak < self.speaker_cooldown:
            # During cooldown period, still listen but with reduced sensitivity
            pass  # We'll still try to listen but be more careful

        with self.microphone as source:
            try:
                print("👂 Listening for 'Rubi' (enhanced for distance)...")
                # Increased timeout from 1 to 2 seconds, phrase_time_limit from 2 to 3 seconds
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)

                text = self.recognizer.recognize_google(audio).lower()
                print(f"📝 Heard: '{text}'")

                # Check for wake word
                if "rubi" in text or "ruby" in text or "rooby" in text or "hello rubi" in text:
                    print("🔊 Wake word detected!")
                    return True
                return False

            except sr.WaitTimeoutError:
                return False
            except sr.UnknownValueError:
                return False
            except sr.RequestError as e:
                print(f"❌ Service error: {e}")
                return False
                
    def listen_for_command(self):
        """Listen for a command after wake word"""
        # Don't listen while speaker is active
        if self.speaker.is_speaking:
            time.sleep(0.1)
            return "speaker_active"  # Different return value for speaker active

        # Wait for speech guard period to pass
        time_since_speak = time.time() - self.last_speak_time
        if time_since_speak < self.speech_guard_period:
            # During speech guard period, completely ignore any audio
            time.sleep(0.1)
            return "speaker_active"  # Different return value for speech guard

        # For commands, listen immediately after guard period
        # Set timeout to 3 seconds for precise 45-second total sleep timeout (15 × 3s = 45s)
        with self.microphone as source:
            try:
                print("🎯 Listening for command (ULTRA sensitive for distance)...")
                # Timeout of 3 seconds for precise sleep timing
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)

                command = self.recognizer.recognize_google(audio).lower()
                print(f"📝 Command: '{command}'")

                # Don't filter - just return what we heard
                return command

            except sr.WaitTimeoutError:
                print("⏰ No command heard (timeout after 3 seconds)")
                return "audio_timeout"  # Different return value for actual audio timeout
            except sr.UnknownValueError:
                print("❌ Could not understand audio (possibly too quiet or unclear)")
                return "unknown"
            except sr.RequestError as e:
                print(f"❌ Service error: {e}")
                return None


    def mark_speaker_active(self):
        """Track when speaker was last used to prevent audio feedback"""
        self.last_speak_time = time.time()

    def process_command(self, command):
        """Process the voice command and control motors
        Returns:
            bool: True if robot should stay in command mode, False if should exit to wake word listening
        """
        if not command or command in ["timeout", "unknown"]:
            return True
            
        print(f"⚙️ Processing: '{command}'")
        
        # Check for stop command first (always process stop even if robot is active)
        if any(word in command for word in ["stop", "halt", "brake", "stop now", "stop searching"]):
            print("🛑 STOP command - stopping all movement and search")
            
            # Check if robot is actually doing something before speaking
            robot_was_active = self._is_robot_active()
            
            self.motor.stop()
            
            # Stop any ongoing search
            if hasattr(self, 'searcher') and self.searcher:
                self.searcher.stop_searching()
                
            # Only speak if robot was actually doing something
            if robot_was_active:
                self.speaker.speak("Stopping")
            else:
                print("   🤖 Robot was already stopped, not speaking")
                
            return True
            
        # If robot is actively performing a task (searching, navigating, moving),
        # we should still allow movement commands to change direction
        # but block other commands like "find" or "what do you see"
        robot_is_active = self._is_robot_active()
        
        # Define movement command keywords
        movement_keywords = ["forward", "backward", "back", "left", "right", "move", "go", "turn", "rotate", "spin", "ahead", "straight", "proceed", "advance", "reverse", "retreat"]
        
        # Check if this is a movement command
        is_movement_command = any(keyword in command for keyword in movement_keywords)
        
        # If robot is active and this is NOT a movement command, ignore it
        # (except stop which was already handled above)
        if robot_is_active and not is_movement_command:
            print("🤖 Robot is busy (searching/navigating), ignoring non-movement command")
            # Don't speak to avoid interrupting
            return True
            
        # Check for sleep commands before movement commands (important for "go to sleep")
        if any(word in command for word in ["sleep", "go to sleep", "go to sleep mode", "enter sleep mode", "sleep mode", "goodnight", "good night", "bye", "goodbye", "see you", "rest", "take a break"]):
            print("😴 SLEEP command - returning to wake word listening")
            self.speaker.speak("Going to sleep")
            # Signal to exit command mode
            return False
            
        # Check for movement commands with multiple synonyms
        # Check more specific commands first to avoid misclassification
        # "move backward" should be recognized as backward, not forward
        backward_keywords = ["backward", "back", "move back", "go back", "move backward", "reverse", "backwards", "retreat"]
        forward_keywords = ["forward", "go", "move", "move forward", "go forward", "move ahead", "ahead", "straight", "proceed", "advance"]
        left_keywords = ["left", "turn left", "go left", "move left", "rotate left", "spin left"]
        right_keywords = ["right", "turn right", "go right", "move right", "rotate right", "spin right"]
        
        # Check backward first (more specific) to avoid "move backward" matching "move" in forward_keywords
        if any(keyword in command for keyword in backward_keywords):
            print("⬅️ BACKWARD command")
            self.motor.backward(60)
            self.speaker.speak("Moving backward")
            
        elif any(keyword in command for keyword in forward_keywords):
            print("➡️ FORWARD command")
            self.motor.forward(60)
            self.speaker.speak("Moving forward")
            
        elif any(keyword in command for keyword in left_keywords):
            print("↪️ LEFT command")
            self.motor.turn_left(40)
            self.speaker.speak("Turning left")
            
        elif any(keyword in command for keyword in right_keywords):
            print("↩️ RIGHT command")
            self.motor.turn_right(40)
            self.speaker.speak("Turning right")
            
        elif "what do you see" in command or "what can you see" in command or "describe" in command or "tell me" in command:
            print("👀 Processing vision query")
            self.speaker.speak("Let me look around")
            
            # Get camera description
            camera = None
            if hasattr(self, 'camera') and self.camera:
                camera = self.camera
            elif hasattr(self, 'searcher') and self.searcher and hasattr(self.searcher, 'camera') and self.searcher.camera:
                camera = self.searcher.camera
            
            if camera:
                description = camera.describe_scene()
                print(f"📝 Scene description: {description}")
                self.speaker.speak(description)
            else:
                self.speaker.speak("I can see the room around me")
                
        elif "find" in command or "look for" in command or "search" in command:
            # Extract object to find
            target = None
            object_map = {
                "chair": ["chair", "stool", "seat"],
                "person": ["person", "people", "human"],
                "table": ["table", "desk"],
                "couch": ["couch", "sofa"],
                "phone": ["phone", "cell phone", "mobile"],
                "bottle": ["bottle", "water bottle"],
                "cup": ["cup", "mug"],
                "book": ["book"],
                "laptop": ["laptop"],
                "tv": ["tv", "television", "monitor"]
            }
            
            for obj_type, keywords in object_map.items():
                if any(keyword in command for keyword in keywords):
                    target = obj_type
                    break
            
            if target:
                print(f"🔍 Search command for {target}")
                if hasattr(self, 'searcher'):
                    self.searcher.search_for_object(target, pattern='scan')
                    if hasattr(self, 'debug_window'):
                        self.debug_window.set_status(f"Searching for {target}...")
                else:
                    # Fallback to simple find
                    if hasattr(self, 'camera'):
                        found = self.camera.find_object(target)
                        if found:
                            message = f"I found a {found['name']} to your {found['direction']}"
                            self.speaker.speak(message)
                        else:
                            self.speaker.speak(f"I don't see any {target} nearby")
                    else:
                        self.speaker.speak("I can't see without a camera")
            else:
                self.speaker.speak("What should I look for?")
                
        elif "hello" in command or "hi" in command:
            print("👋 HELLO")
            self.speaker.speak("Hello")
            
        else:
            print(f"❓ Unknown: {command}")
            self.speaker.speak("Unknown command")
        
        # Default: stay in command mode
        return True
            
    def _is_robot_active(self):
        """Check if robot is currently performing any task (moving, searching, navigating)"""
        # Check if motor is moving
        if hasattr(self.motor, 'get_state'):
            try:
                state = self.motor.get_state()
                # Check if either motor has non-zero speed
                if state.get('left_speed', 0) != 0 or state.get('right_speed', 0) != 0:
                    return True
            except:
                pass
        
        # Check if searcher is searching or navigating
        if hasattr(self, 'searcher'):
            if getattr(self.searcher, 'searching', False) or getattr(self.searcher, 'navigating', False):
                return True
        
        # Check if camera is searching
        if hasattr(self, 'camera'):
            if getattr(self.camera, 'is_searching', False):
                return True
        
        return False

    def start_listening_loop(self):
        """Continuous listening loop in background thread"""
        self.listening = True
        print("🎤 Voice control active - Say 'Rubi' then a command")
        
        def listen_loop():
            # Welcome message
            try:
                print("🔊 Speaker: Saying 'Hello, I am Rubi the robot'")
                self.speaker.speak("Hello, I am Rubi the robot")
                self.mark_speaker_active()
            except Exception as e:
                print(f"❌ Speaker error on startup: {e}")

            command_timeout_count = 0
            MAX_TIMEOUTS = 15  # 15 timeouts * 3 seconds each = 45 seconds (exact)

            while self.listening:
                if self.listen_for_wake_word():
                    command_timeout_count = 0
                    try:
                        print("🔊 Speaker: Saying 'Yes'")
                        self.speaker.speak("Yes")
                        self.mark_speaker_active()
                    except Exception as e:
                        print(f"❌ Speaker error: {e}")

                    # Wait for speech to complete before listening for commands
                    time.sleep(1.0)  # Give time for "Yes" to finish speaking
                    
                    # Stay in command listening mode until timeout
                    command_loop_active = True
                    while command_loop_active and self.listening:
                        command = self.listen_for_command()

                        if command and command not in ["audio_timeout", "speaker_active", "unknown"]:
                            print(f"✅ Command received: {command}")
                            should_stay_in_command_mode = self.process_command(command)
                            self.mark_speaker_active()
                            command_timeout_count = 0
                            
                            # Check if process_command wants to exit command mode (sleep command)
                            if not should_stay_in_command_mode:
                                print("🔄 Exiting command mode as requested by sleep command")
                                command_loop_active = False

                        elif command == "audio_timeout":
                            # This is a real audio timeout (5 seconds of no speech)
                            # Check if robot is active before counting timeout
                            if self._is_robot_active():
                                print("🤖 Robot is active, resetting timeout counter")
                                command_timeout_count = 0
                                time.sleep(0.5)
                                continue
                            
                            command_timeout_count += 1
                            print(f"⏰ Command timeout #{command_timeout_count}/{MAX_TIMEOUTS} (3 seconds no speech)")
                            if command_timeout_count >= MAX_TIMEOUTS:
                                print("🔄 Exiting command mode after 45 seconds of inactivity, listening for wake word again")
                                command_loop_active = False
                            else:
                                # Wait briefly before next command listen
                                time.sleep(0.5)
                                continue

                        elif command == "speaker_active":
                            # Speaker is active or in speech guard period - don't count as timeout
                            # Just wait briefly and continue listening
                            time.sleep(0.1)
                            continue

                        elif command == "unknown":
                            print("❌ Command not understood, waiting for next command...")
                            # Continue listening for more commands
                            time.sleep(0.5)

                    time.sleep(0.5)

                time.sleep(0.1)
                
        thread = threading.Thread(target=listen_loop)
        thread.daemon = True
        thread.start()
        
    def stop_listening(self):
        """Stop the listening loop"""
        self.listening = False
        self.speaker.speak("Goodbye")
        print("🎤 Voice control stopped")