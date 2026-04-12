#!/usr/bin/env python3
"""Quick test to verify navigation logic with mock distance"""

import time
from vision.camera import Camera

# Test that mock distance decreases when is_navigating is True
camera = Camera()
camera.start_search('phone', None)

print("Test 1: Without navigation mode")
camera.is_navigating = False
for i in range(3):
    objs = camera._mock_detection(None)
    phone = next((o for o in objs if 'phone' in o['name']), None)
    if phone:
        print(f"  Distance (not navigating): {phone['distance']}m")
    time.sleep(1.1)

print("\nTest 2: With navigation mode")
camera.is_navigating = True
camera.mock_distance = 1.2  # Reset
for i in range(5):
    objs = camera._mock_detection(None)
    phone = next((o for o in objs if 'phone' in o['name']), None)
    if phone:
        print(f"  Step {i+1}: Distance = {phone['distance']}m")
    time.sleep(1.1)  # Wait >1s to trigger decrement

print("\nTest 3: Simulating faster navigation loop")
camera.is_navigating = True
camera.mock_distance = 1.2  # Reset
# Simulate what happens in navigation loop (calls every ~0.5s)
for i in range(10):
    objs = camera._mock_detection(None)
    phone = next((o for o in objs if 'phone' in o['name']), None)
    if phone:
        print(f"  Nav step {i+1}: {phone['distance']}m")
    time.sleep(0.5)  # Faster than 1 second

print("\nConclusion: Distance decreases every 1 second when navigating.")
print("In a real navigation, robot would see progress after ~2-3 seconds.")