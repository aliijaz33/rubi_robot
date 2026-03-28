#!/usr/bin/env python3
"""
Test script for Rubi robot with voice control, vision, and search capabilities
"""
# Suppress OMP warnings
import os
os.environ['KMP_WARNINGS'] = '0'
os.environ['OMP_NUM_THREADS'] = '1'

import time
from hardware.motor_factory import MotorFactory
from speech.speech_recognizer import SpeechRecognizer
from vision.camera import Camera
from vision.debug_window import VisionDebugWindow
from intelligence.searcher import ObjectSearcher
from config import Config

def main():
    """Main test function"""
    
    print("\n" + "="*60)
    print("   🤖 RUBI ROBOT - WITH SEARCH & VISION DEBUG")
    print("="*60)
    print("\n📝 Instructions:")
    print("  • GUI window will open showing the robot")
    print("  • DEBUG window shows camera feed with detections")
    print("  • Voice commands:")
    print("    - 'Rubi' → 'Yes?' → forward/backward/left/right/stop")
    print("    - 'Rubi what do you see' - describes scene")
    print("    - 'Rubi find chair' - SEARCHES for chair")
    print("    - 'Rubi find person' - SEARCHES for people")
    print("    - 'Rubi find phone' - SEARCHES for phone")
    print("  • Close the windows to exit\n")
    
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
    
    # Create object searcher
    if vision_available:
        searcher = ObjectSearcher(motors, camera, speech.speaker)
        speech.searcher = searcher
    
    # Attach camera to speech recognizer
    if vision_available:
        speech.camera = camera
    
    print("\n✅ All systems ready!")
    print("🖥️  Opening robot GUI window...\n")
    
    # Start voice recognition in background
    speech.start_listening_loop()
    
    print("🎮 Controls active:")
    print("   • Keyboard: Arrow keys + Space")
    print("   • Voice: Say 'Rubi' then command")
    if vision_available:
        print("   • Vision: 'what do you see'")
        print("   • Search: 'find chair', 'find person', 'find phone'")
        print("   • Debug window shows camera feed with detections")
    
    # Store camera and vision flag in motors for debug window
    motors.camera = camera if vision_available else None
    motors.vision_available = vision_available
    
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