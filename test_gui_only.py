#!/usr/bin/env python3
"""
Simple test to check if GUI opens
"""

import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hardware.motor_factory import MotorFactory
from config import Config

def main():
    print("Testing GUI only...")
    print("Creating motor simulator...")
    
    motors = MotorFactory.create_motor_controller(Config.get_mode())
    
    print("Opening GUI window - this should appear now...")
    print("If you don't see a window, there's a Tkinter issue.")
    
    # This should open the GUI and block
    motors.start_gui()
    
    print("GUI closed. Test complete.")

if __name__ == "__main__":
    main()#!/usr/bin/env python3
"""
Simple test to check if GUI opens
"""

import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hardware.motor_factory import MotorFactory
from config import Config

def main():
    print("Testing GUI only...")
    print("Creating motor simulator...")
    
    motors = MotorFactory.create_motor_controller(Config.get_mode())
    
    print("Opening GUI window - this should appear now...")
    print("If you don't see a window, there's a Tkinter issue.")
    
    # This should open the GUI and block
    motors.start_gui()
    
    print("GUI closed. Test complete.")

if __name__ == "__main__":
    main()