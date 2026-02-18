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
        
        # Use the built-in microphone (index 0)
        self.microphone = sr.Microphone(device_index=0)
        
        self.listening = False
        self.wake_word = "rubi"
        
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
        with self.microphone as source:
            try:
                print("🎯 Listening for command...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=2)
                
                command = self.recognizer.recognize_google(audio).lower()
                print(f"📝 Command: '{command}'")
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
                
    def process_command(self, command):
        """Process the voice command and control motors"""
        if not command or command in ["timeout", "unknown"]:
            return
            
        print(f"⚙️ Processing: '{command}'")
        
        try:
            # Check for movement commands - each should CHANGE motor state
            if "forward" in command:
                print("➡️ FORWARD command")
                self.motor.forward(60)
                print("🔊 Speaker: Saying 'Moving forward'")
                self.speaker.speak("Moving forward")
                
            elif "backward" in command:
                print("⬅️ BACKWARD command")
                self.motor.backward(60)
                print("🔊 Speaker: Saying 'Moving backward'")
                self.speaker.speak("Moving backward")
                
            elif "left" in command:
                print("↪️ LEFT command")
                self.motor.turn_left(40)
                print("🔊 Speaker: Saying 'Turning left'")
                self.speaker.speak("Turning left")
                
            elif "right" in command:
                print("↩️ RIGHT command")
                self.motor.turn_right(40)
                print("🔊 Speaker: Saying 'Turning right'")
                self.speaker.speak("Turning right")
                
            elif "stop" in command:
                print("🛑 STOP command")
                self.motor.stop()
                print("🔊 Speaker: Saying 'Stopping'")
                self.speaker.speak("Stopping")
                
            elif "hello" in command or "hi" in command:
                print("👋 HELLO")
                print("🔊 Speaker: Saying 'Hello'")
                self.speaker.speak("Hello")
                
            else:
                print(f"❓ Unknown: {command}")
                print("🔊 Speaker: Saying 'Unknown command'")
                self.speaker.speak("Unknown command")
                
        except Exception as e:
            print(f"❌ Error processing command: {e}")
            
    def start_listening_loop(self):
        """Continuous listening loop in background thread"""
        self.listening = True
        print("🎤 Voice control active - Say 'Rubi' then a command")
        
        def listen_loop():
            # Welcome message
            try:
                print("🔊 Speaker: Saying 'Rubi ready'")
                self.speaker.speak("Rubi ready")
            except Exception as e:
                print(f"❌ Speaker error on startup: {e}")
            
            command_timeout_count = 0
            
            while self.listening:
                if self.listen_for_wake_word():
                    command_timeout_count = 0
                    try:
                        print("🔊 Speaker: Saying 'Yes'")
                        self.speaker.speak("Yes")
                    except Exception as e:
                        print(f"❌ Speaker error: {e}")
                    
                    # Stay in command listening mode until timeout
                    command_loop_active = True
                    while command_loop_active and self.listening:
                        command = self.listen_for_command()
                        
                        if command and command not in ["timeout", "unknown"]:
                            print(f"✅ Command received: {command}")
                            self.process_command(command)
                            # Continue listening for more commands
                            command_timeout_count = 0
                            
                        elif command == "timeout":
                            command_timeout_count += 1
                            print(f"⏰ Command timeout #{command_timeout_count}")
                            if command_timeout_count >= 2:
                                print("🔄 Exiting command mode, listening for wake word again")
                                command_loop_active = False
                            else:
                                # Wait for another command
                                continue
                                
                        elif command == "unknown":
                            print("❌ Command not understood, waiting for next command...")
                            # Continue listening for more commands
                            
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