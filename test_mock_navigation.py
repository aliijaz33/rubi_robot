#!/usr/bin/env python3
"""Test mock navigation with decreasing distance"""

import time
from vision.camera import Camera

def test_mock_distance():
    """Test that mock distance decreases during navigation"""
    print("🧪 Testing mock distance simulation...")
    
    camera = Camera()
    
    # Start searching for phone
    camera.start_search('phone', lambda obj: print(f"Found: {obj['name']}"))
    camera.is_navigating = True  # Simulate navigation mode
    
    print("Initial mock detection:")
    objects1 = camera._mock_detection(None)
    for obj in objects1:
        print(f"  - {obj['name']}: {obj['distance']}m")
    
    # Simulate time passing (navigation)
    print("\nAfter 2 seconds (simulating robot moving forward):")
    time.sleep(2)
    
    objects2 = camera._mock_detection(None)
    for obj in objects2:
        print(f"  - {obj['name']}: {obj['distance']}m")
    
    # Check if distance decreased
    phone1 = next((o for o in objects1 if 'phone' in o['name']), None)
    phone2 = next((o for o in objects2 if 'phone' in o['name']), None)
    
    if phone1 and phone2:
        if phone2['distance'] < phone1['distance']:
            print(f"✅ Distance decreased from {phone1['distance']}m to {phone2['distance']}m")
        else:
            print(f"⚠️ Distance didn't decrease: {phone1['distance']}m -> {phone2['distance']}m")
    
    # Test multiple iterations
    print("\nSimulating navigation progress:")
    for i in range(5):
        time.sleep(0.5)
        objects = camera._mock_detection(None)
        phone = next((o for o in objects if 'phone' in o['name']), None)
        if phone:
            print(f"  Step {i+1}: {phone['distance']}m")
    
    print("\n✅ Mock navigation test completed")
    return True

if __name__ == "__main__":
    test_mock_distance()