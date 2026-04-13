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
        self.speaker_cooldown = 1.0  # Wait 1 second after speaker finishes (for wake word detection only)

        # Adjust recognizer settings
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5
        
        # Adjust for ambient noise
        print("🎤 Calibrating microphone for ambient noise...")
        with self.microphone as source:
            print("   Please wait... (2 seconds)")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"   Energy threshold set to: {self.recognizer.energy_threshold}")
        print("✅ Microphone ready!")
        
    def listen_for_wake_word(self):
        """Listen for the wake word 'Rubi'"""
        # Don't listen while speaker is active
        if self.speaker.is_speaking:
            return False

        # Wait for microphone to settle after speaker finishes
        time_since_speak = time.time() - self.last_speak_time
        if time_since_speak < self.speaker_cooldown:
            return False

        with self.microphone as source:
            try:
                print("👂 Listening for 'Rubi'...")
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)

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
            return "timeout"

        # For commands, listen immediately after "Yes" is finished
        # No settling time needed here since we're in focused command mode
        with self.microphone as source:
            try:
                print("🎯 Listening for command...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=2)

                command = self.recognizer.recognize_google(audio).lower()
                print(f"📝 Command: '{command}'")

                # Don't filter - just return what we heard
                return command

            except sr.WaitTimeoutError:
                print("⏰ No command heard")
                return "timeout"
            except sr.UnknownValueError:
                print("❌ Could not understand")
                return "unknown"
            except sr.RequestError as e:
                print(f"❌ Service error: {e}")
                return None


    def mark_speaker_active(self):
        """Track when speaker was last used to prevent audio feedback"""
        self.last_speak_time = time.time()

    def process_command(self, command):
        """Process the voice command and control motors"""
        if not command or command in ["timeout", "unknown"]:
            return
            
        print(f"⚙️ Processing: '{command}'")
        
        # Check for stop command first
        if any(word in command for word in ["stop", "halt", "brake", "stop now", "stop searching"]):
            print("🛑 STOP command - stopping all movement and search")
            self.motor.stop()
            
            # Stop any ongoing search
            if hasattr(self, 'searcher') and self.searcher:
                self.searcher.stop_searching()
                
            self.speaker.speak("Stopping")
            return
            
        # Check for movement commands
        if "forward" in command:
            print("➡️ FORWARD command")
            self.motor.forward(60)
            self.speaker.speak("Moving forward")
            
        elif "backward" in command:
            print("⬅️ BACKWARD command")
            self.motor.backward(60)
            self.speaker.speak("Moving backward")
            
        elif "left" in command:
            print("↪️ LEFT command")
            self.motor.turn_left(40)
            self.speaker.speak("Turning left")
            
        elif "right" in command:
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
            
    def start_listening_loop(self):
        """Continuous listening loop in background thread"""
        self.listening = True
        print("🎤 Voice control active - Say 'Rubi' then a command")
        
        def listen_loop():
            # Welcome message
            try:
                print("🔊 Speaker: Saying 'Rubi ready'")
                self.speaker.speak("Rubi ready")
                self.mark_speaker_active()
            except Exception as e:
                print(f"❌ Speaker error on startup: {e}")

            command_timeout_count = 0

            while self.listening:
                if self.listen_for_wake_word():
                    command_timeout_count = 0
                    try:
                        print("🔊 Speaker: Saying 'Yes'")
                        self.speaker.speak("Yes")
                        self.mark_speaker_active()
                    except Exception as e:
                        print(f"❌ Speaker error: {e}")

                    # Stay in command listening mode until timeout
                    command_loop_active = True
                    while command_loop_active and self.listening:
                        command = self.listen_for_command()

                        if command and command not in ["timeout", "unknown"]:
                            print(f"✅ Command received: {command}")
                            self.process_command(command)
                            self.mark_speaker_active()
                            command_timeout_count = 0

                        elif command == "timeout":
                            command_timeout_count += 1
                            print(f"⏰ Command timeout #{command_timeout_count}")
                            if command_timeout_count >= 2:
                                print("🔄 Exiting command mode, listening for wake word again")
                                command_loop_active = False
                            else:
                                # Wait briefly before next command listen
                                time.sleep(0.5)
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