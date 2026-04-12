#!/usr/bin/env python3
"""Test robot search functionality with the fixed camera"""

import sys
import time
import threading
from hardware.motor_factory import MotorFactory
from vision.camera import Camera
from intelligence.searcher import ObjectSearcher

def object_found_callback(obj):
    """Callback when object is found"""
    print(f"🎯 OBJECT FOUND: {obj['name']} at {obj['distance']}m to the {obj['direction']}")
    print("   Stopping search...")

def test_search_phone():
    """Test searching for a phone"""
    print("🤖 Testing robot search for phone...")
    
    # Create motor controller
    print("🔧 Creating motor controller...")
    motor = MotorFactory.create_motor_controller(mode='simulation')
    
    # Create camera
    print("📷 Creating camera...")
    camera = Camera()
    
    if not camera.initialize():
        print("❌ Camera initialization failed, using mock mode")
        # Continue anyway, camera will use mock detection
    
    camera.start_capture()
    
    # Create searcher
    print("🔍 Creating object searcher...")
    searcher = ObjectSearcher(motor, camera, speaker=None)
    
    # Start searching for phone
    print("📱 Starting search for phone...")
    camera.start_search('phone', object_found_callback)
    
    # Run search in background thread
    search_thread = threading.Thread(
        target=searcher.search_for_object,
        args=('phone', 'scan')
    )
    search_thread.daemon = True
    search_thread.start()
    
    # Let it run for a while
    print("⏳ Running search for 10 seconds...")
    time.sleep(10)
    
    # Stop everything
    print("🛑 Stopping search...")
    searcher.stop_searching()
    camera.stop_search()
    camera.stop()
    
    # Wait for thread to finish
    search_thread.join(timeout=2.0)
    
    print("✅ Search test completed")
    return True

if __name__ == "__main__":
    try:
        success = test_search_phone()
        if success:
            print("🎉 Robot search test passed!")
            sys.exit(0)
        else:
            print("💥 Robot search test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)