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
        self.microphone = sr.Microphone()
        self.listening = False
        self.wake_word = "rubi"
        
        # Adjust for ambient noise
        print("🎤 Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone ready!")
        
    def listen_for_wake_word(self):
        """Listen for the wake word 'Rubi'"""
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                text = self.recognizer.recognize_google(audio).lower()
                
                if self.wake_word in text:
                    print("🔊 Wake word detected!")
                    self.speaker.speak_wake_response()
                    return True
                return False
                    
            except sr.WaitTimeoutError:
                return False
            except sr.UnknownValueError:
                return False
            except sr.RequestError:
                print("⚠️ Speech recognition service error")
                return False
                
    def listen_for_command(self):
        """Listen for a command after wake word"""
        with self.microphone as source:
            print("🎯 Listening for command...")
            try:
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                command = self.recognizer.recognize_google(audio).lower()
                print(f"📝 Command received: {command}")
                return command
                
            except sr.WaitTimeoutError:
                print("⏰ No command heard")
                self.speaker.speak_error('no_command')
                return None
            except sr.UnknownValueError:
                print("🤔 Could not understand audio")
                self.speaker.speak_error('unknown')
                return None
            except sr.RequestError as e:
                print(f"❌ Speech service error: {e}")
                return None
                
    def process_command(self, command):
        """Process the voice command and control motors"""
        if not command:
            return
            
        # Check for movement commands
        if "forward" in command or "go forward" in command:
            print("➡️ Executing: FORWARD")
            self.speaker.speak_command_confirm('forward')
            self.motor.forward(60)
            
        elif "backward" in command or "go back" in command:
            print("⬅️ Executing: BACKWARD")
            self.speaker.speak_command_confirm('backward')
            self.motor.backward(60)
            
        elif "left" in command or "turn left" in command:
            print("↪️ Executing: TURN LEFT")
            self.speaker.speak_command_confirm('left')
            self.motor.turn_left(40)
            
        elif "right" in command or "turn right" in command:
            print("↩️ Executing: TURN RIGHT")
            self.speaker.speak_command_confirm('right')
            self.motor.turn_right(40)
            
        elif "stop" in command or "halt" in command:
            print("🛑 Executing: STOP")
            self.speaker.speak_command_confirm('stop')
            self.motor.stop()
            
        elif "what do you see" in command or "look around" in command:
            print("👀 Robot would describe what it sees (coming soon!)")
            self.speaker.speak("I'm still learning to see")
            
        elif "hello" in command or "hi" in command:
            self.speaker.speak("Hello! I'm Rubi")
            
        else:
            print(f"🤷 Unknown command: {command}")
            self.speaker.speak_error('unknown')
            
    def start_listening_loop(self):
        """Continuous listening loop in background thread"""
        self.listening = True
        
        def listen_loop():
            while self.listening:
                if self.listen_for_wake_word():
                    command = self.listen_for_command()
                    if command:
                        self.process_command(command)
                time.sleep(0.1)
                
        thread = threading.Thread(target=listen_loop)
        thread.daemon = True
        thread.start()
        self.speaker.speak("Rubi ready!")
        print("🎤 Voice control active - Say 'Rubi' then a command")
        
    def stop_listening(self):
        """Stop the listening loop"""
        self.listening = False
        self.speaker.speak("Goodbye")
        print("🎤 Voice control stopped")