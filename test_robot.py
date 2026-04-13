#!/usr/bin/env python3
"""
Quick startup script for Rubi robot simulator.
Run with: python test_robot.py
"""

import sys
import os
import threading
import time

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hardware.motor_factory import MotorFactory
from vision.camera import Camera
from vision.debug_window import VisionDebugWindow
from speech.speech_recognizer import SpeechRecognizer
from speech.speaker import Speaker
from intelligence.searcher import ObjectSearcher
import tkinter as tk
from config import Config


def main():
    print("🤖 Initializing Rubi Robot Simulator...")
    
    # Create root Tkinter window for motor simulator
    root = tk.Tk()
    root.title("Rubi Robot Simulator")
    root.geometry("800x600")
    
    # Create speaker for text-to-speech
    speaker = Speaker()
    speaker.speak("Rubi robot initialized. Ready for commands.")
    
    # Create camera with optimized detection
    print("📷 Initializing camera...")
    camera = Camera()
    camera.initialize()
    camera.start_capture()
    
    # Create vision debug window
    print("👁️  Creating vision debug window...")
    debug_window = VisionDebugWindow(camera, root)
    
    # Ensure debug window is visible and on top
    if hasattr(debug_window, 'window') and debug_window.window:
        debug_window.window.lift()  # Bring to top
        debug_window.window.focus_force()  # Force focus
        print("✅ Debug window raised to top")
    
    # Create motor controller
    print("⚙️  Creating motor controller...")
    motor_controller = MotorFactory.create_motor_controller(
        mode=Config.get_mode(),
        debug_window=debug_window,
        root=root
    )
    
    # Start the visual simulator GUI (non-blocking since standalone=False)
    print("🖥️  Starting visual simulator GUI...")
    motor_controller.start_gui()
    
    # Create object searcher
    print("🔍 Creating object searcher...")
    searcher = ObjectSearcher(motor_controller, camera, speaker)
    
    # Create speech recognizer
    print("🎤 Creating speech recognizer...")
    recognizer = SpeechRecognizer(motor_controller)
    recognizer.searcher = searcher  # Allow voice commands to trigger searches
    
    # Start listening for voice commands in background thread
    print("👂 Starting voice recognition...")
    recognizer.start_listening_loop()
    
    # Display instructions
    print("\n" + "="*60)
    print("RUBI ROBOT READY")
    print("="*60)
    print("Voice commands:")
    print("  Say 'Rubi' to wake up, then:")
    print("  - 'what do you see' - describe current scene")
    print("  - 'find [object]' - search for object (person, phone, chair, etc.)")
    print("  - 'stop searching' - stop current search")
    print("  - 'move forward', 'turn left', etc. - manual control")
    print("  - 'stop' - stop all movement")
    print("\nManual control:")
    print("  Use arrow keys in simulator window:")
    print("  ↑ = forward, ↓ = backward, ← = left, → = right, Space = stop")
    print("="*60 + "\n")
    
    # Start the Tkinter main loop
    print("🚀 Starting GUI... (Press Ctrl+C to exit)")
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        recognizer.stop_listening()
        camera.stop()
        motor_controller.stop()
        root.quit()
        print("✅ Shutdown complete.")


if __name__ == "__main__":
    main()