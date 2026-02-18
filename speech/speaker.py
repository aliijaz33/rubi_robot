"""
Text-to-Speech module for Rubi robot
"""

import pyttsx3
import threading
import random

class Speaker:
    """Handles all speech output for Rubi robot"""
    
    def __init__(self):
        # Initialize the TTS engine
        self.engine = pyttsx3.init()
        
        # Configure voice properties
        self._configure_voice()
        
        # Speaking flag to prevent overlapping speech
        self.is_speaking = False
        
        print("🔊 Text-to-Speech initialized!")
        
    def _configure_voice(self):
        """Configure voice properties (speed, volume, etc)"""
        # Get available voices
        voices = self.engine.getProperty('voices')
        
        # Try to set a female voice if available (sounds nicer)
        for voice in voices:
            if 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate (words per minute)
        self.engine.setProperty('rate', 150)
        
        # Set volume (0.0 to 1.0)
        self.engine.setProperty('volume', 0.9)
        
    def speak(self, text):
        """Speak the given text (non-blocking)"""
        def _speak():
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_speaking = False
            
        # Run in background thread
        thread = threading.Thread(target=_speak)
        thread.daemon = True
        thread.start()
        
    def speak_wake_response(self):
        """Respond when wake word detected"""
        responses = [
            "Yes?",
            "I'm listening",
            "How can I help?",
            "Rubi here",
            "Go ahead"
        ]
        self.speak(random.choice(responses))
        
    def speak_command_confirm(self, command):
        """Confirm the command being executed"""
        confirmations = {
            'forward': ["Moving forward", "Going forward", "Forward it is"],
            'backward': ["Moving backward", "Going back", "Backward"],
            'left': ["Turning left", "Going left", "Left turn"],
            'right': ["Turning right", "Going right", "Right turn"],
            'stop': ["Stopping", "Halting", "Stop"]
        }
        
        if command in confirmations:
            self.speak(random.choice(confirmations[command]))
            
    def speak_error(self, error_type):
        """Speak error messages"""
        errors = {
            'no_command': ["I didn't hear a command", "Say that again?", "I'm listening"],
            'unknown': ["I don't understand", "Not sure what that means", "Try again"],
            'not_found': ["I couldn't find that", "Not in sight", "Look somewhere else"]
        }
        
        if error_type in errors:
            self.speak(random.choice(errors[error_type]))
            
    def speak_observation(self, objects):
        """Describe what the robot sees"""
        if not objects:
            self.speak("I don't see anything interesting")
            return
            
        description = f"I see {len(objects)} objects. "
        for obj in objects[:3]:
            description += f"A {obj['name']} "
            if 'direction' in obj:
                description += f"to the {obj['direction']} "
        self.speak(description)