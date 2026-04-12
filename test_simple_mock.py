#!/usr/bin/env python3
"""Simple test of mock detection"""

from vision.camera import Camera
import time

camera = Camera()
camera.start_search('phone', None)
camera.is_navigating = True

print("Testing mock detection with navigation...")
for i in range(5):
    objs = camera._mock_detection(None)
    phone = next((o for o in objs if 'phone' in o['name']), None)
    if phone:
        print(f"Iteration {i+1}: Phone at {phone['distance']}m")
    time.sleep(1.1)  # Wait more than 1 second to trigger distance decrement

print("Done.")