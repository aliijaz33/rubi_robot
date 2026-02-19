#!/usr/bin/env python3
"""
Test script for Rubi robot with voice control and vision
"""

import time
from hardware.motor_factory import MotorFactory
from speech.speech_recognizer import SpeechRecognizer
from vision.camera import Camera
from config import Config

def main():
    """Main test function"""
    
    print("\n" + "="*60)
    print("   🤖 RUBI ROBOT - WITH VOICE CONTROL & VISION")
    print("="*60)
    print("\n📝 Instructions:")
    print("  • GUI window will open showing the robot")
    print("  • Use arrow keys to drive manually")
    print("  • Voice commands:")
    print("    - 'Rubi' → 'Yes?' → forward/backward/left/right/stop")
    print("    - 'Rubi what do you see' - describes scene")
    print("    - 'Rubi find chair' - looks for chair")
    print("    - 'Rubi find person' - looks for people")
    print("  • Close the window to exit\n")
    
    input("Press Enter to start the simulator...")
    
    # Create motor controller
    print("\n🔄 Creating robot simulator...")
    motors = MotorFactory.create_motor_controller(Config.get_mode())
    
    # Initialize camera
    print("\n📷 Initializing camera...")
    camera = Camera()
    vision_available = camera.initialize()
    if vision_available:
        camera.start_capture()
        print("✅ Vision system ready!")
    else:
        print("⚠️ Vision disabled - continuing without camera")
    
    # Create speech recognizer
    print("\n🎤 Initializing speech recognition...")
    speech = SpeechRecognizer(motors)
    
    # Attach camera to speech recognizer for vision commands
    if vision_available:
        speech.camera = camera
    
    print("\n✅ All systems ready!")
    print("🖥️  Opening GUI window...\n")
    
    # Start voice recognition in background
    speech.start_listening_loop()
    
    print("🎮 Controls active:")
    print("   • Keyboard: Arrow keys + Space")
    print("   • Voice: Say 'Rubi' then command")
    if vision_available:
        print("   • Vision: 'what do you see', 'find chair', 'find person'")
    
    # Start the GUI (this blocks until window is closed)
    motors.start_gui()
    
    # Clean up
    print("\n🔄 Shutting down...")
    speech.stop_listening()
    if vision_available:
        camera.stop()
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()