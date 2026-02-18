    #!/usr/bin/env python3
"""
Test script for Rubi robot with voice control
"""

import time
from hardware.motor_factory import MotorFactory
from speech.speech_recognizer import SpeechRecognizer
from config import Config

def main():
    """Main test function"""
    
    print("\n" + "="*60)
    print("   🤖 RUBI ROBOT - WITH VOICE CONTROL")
    print("="*60)
    print("\n📝 Instructions:")
    print("  • GUI window will open showing the robot")
    print("  • Use arrow keys to drive manually")
    print("  • OR use voice commands:")
    print("    - Say 'Rubi' then wait for response")
    print("    - Then say: forward/backward/left/right/stop")
    print("    - Try: 'Rubi hello' or 'Rubi what do you see'")
    print("  • Close the window to exit\n")
    
    input("Press Enter to start the simulator...")
    
    # Create motor controller
    print("\n🔄 Creating robot simulator...")
    motors = MotorFactory.create_motor_controller(Config.get_mode())
    
    # Create speech recognizer
    print("\n🎤 Initializing speech recognition...")
    speech = SpeechRecognizer(motors)
    
    print("✅ Simulator and speech ready!")
    print("🖥️  Opening GUI window...\n")
    
    # Start voice recognition in background
    speech.start_listening_loop()
    
    print("🎮 Controls active:")
    print("   • Keyboard: Arrow keys + Space")
    print("   • Voice: Say 'Rubi' then command")
    print("\n🎤 Try saying: 'Rubi' ... then 'forward'")
    
    # Start the GUI (this blocks until window is closed)
    motors.start_gui()
    
    # Clean up
    speech.stop_listening()
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()