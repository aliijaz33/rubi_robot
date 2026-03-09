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
    print("\n📝 Voice Commands:")
    print("  • 'Rubi' → Wake the robot, then say:")
    print("    - 'forward/backward/left/right' - Move the robot")
    print("    - 'stop' - Stop all movement")
    print("    - 'what do you see' - Describe the scene")
    print("    - 'find chair' / 'find person' - Search for objects")
    print("  • Press Ctrl+C to exit\n")
    
    input("Press Enter to start...")
    
    # Create motor controller
    print("\n🔄 Creating robot simulator...")
    motors = MotorFactory.create_motor_controller(Config.get_mode())
    
    # Initialize camera
    print("📷 Initializing camera...")
    camera = Camera()
    vision_available = camera.initialize()
    if vision_available:
        camera.start_capture()
        print("✅ Vision system ready!")
    else:
        print("⚠️ Vision disabled - continuing without camera")
    
    # Create speech recognizer
    print("🎤 Initializing speech recognition...")
    speech = SpeechRecognizer(motors)
    
    # Attach camera to speech recognizer for vision commands
    if vision_available:
        speech.camera = camera
    
    print("✅ All systems ready!\n")
    
    # Start voice recognition in background
    speech.start_listening_loop()
    
    print("🎮 GUI window will open now...")
    print("   • Use arrow keys to drive manually")
    print("   • Say 'Rubi' then commands for voice control\n")
    
    # Start the GUI - this BLOCKS until window is closed
    # The tkinter mainloop runs here
    motors.start_gui()
    
    # This code only runs after GUI window is closed
    print("\n🔄 Shutting down...")
    speech.stop_listening()
    if vision_available:
        camera.stop()
    print("👋 Goodbye!")

if __name__ == "__main__":
    main()