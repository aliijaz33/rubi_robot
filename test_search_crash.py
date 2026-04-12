#!/usr/bin/env python3
"""
Test script to verify search for phone does not cause segmentation fault.
"""
import os
os.environ['KMP_WARNINGS'] = '0'
os.environ['OMP_NUM_THREADS'] = '1'

import time
import threading
import sys
from hardware.motor_factory import MotorFactory
from vision.camera import Camera
from intelligence.searcher import ObjectSearcher
from speech.speaker import Speaker
from config import Config

def main():
    print("=== Testing search for phone (crash test) ===")
    
    # Create motor controller
    print("Creating motor simulator...")
    motors = MotorFactory.create_motor_controller(Config.get_mode())
    
    # Initialize camera
    print("Initializing camera...")
    camera = Camera()
    vision_available = camera.initialize()
    if not vision_available:
        print("Camera not available, skipping test.")
        return 1
    camera.start_capture()
    
    # Create speaker (dummy)
    speaker = Speaker()
    
    # Create searcher
    searcher = ObjectSearcher(motors, camera, speaker)
    
    # Start search for phone
    print("Starting search for phone...")
    searcher.search_for_object('phone', pattern='scan')
    
    # Let it run for 5 seconds
    print("Waiting 5 seconds...")
    time.sleep(5)
    
    # Stop search
    print("Stopping search...")
    searcher.stop_searching()
    
    # Clean up
    camera.stop()
    print("Test completed successfully.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)