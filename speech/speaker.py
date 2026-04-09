"""
Text-to-Speech module for Rubi robot
"""

import subprocess
import sys

class Speaker:
    """Handles all speech output for Rubi robot"""

    def __init__(self):
        self.is_speaking = False
        self.voice = None
        self.recognizer = None  # Will be set by SpeechRecognizer

        # Try to use Karen voice
        try:
            # Test if Karen is available
            result = subprocess.run(['say', '-v', '?'], capture_output=True, text=True)
            if 'Karen' in result.stdout:
                self.voice = 'Karen'
                print("🔊 Using Karen voice")
            else:
                self.voice = None
                print("🔊 Using default voice (Karen not found)")
        except:
            self.voice = None
            print("🔊 Text-to-Speech initialized")
        
    def speak(self, text):
        """Speak text using macOS 'say' command"""
        try:
            print(f"   🔉 Playing audio: '{text}'")
            self.is_speaking = True

            # Track that we're speaking (notify recognizer)
            if self.recognizer:
                self.recognizer.mark_speaker_active()

            # Use macOS built-in 'say' command
            if self.voice:
                subprocess.run(['say', '-v', self.voice, text], check=True)
            else:
                subprocess.run(['say', text], check=True)

            self.is_speaking = False
            print(f"   ✅ Audio complete")
        except Exception as e:
            print(f"   ❌ Audio error: {e}")
            self.is_speaking = False
        
    def speak_wake_response(self):
        """Respond to wake word"""
        self.speak("Yes")
        
    def speak_command_confirm(self, command):
        """Confirm command execution"""
        confirmations = {
            'forward': "Moving forward",
            'backward': "Moving backward",
            'left': "Turning left",
            'right': "Turning right",
            'stop': "Stopping"
        }
        if command in confirmations:
            self.speak(confirmations[command])
            
    def speak_error(self, error_type):
        """Speak error message"""
        errors = {
            'no_command': "I didn't hear a command",
            'unknown': "I don't understand",
            'not_found': "Not in sight"
        }
        if error_type in errors:
            self.speak(errors[error_type])