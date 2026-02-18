#!/usr/bin/env python3
"""
Simple microphone test
"""

import speech_recognition as sr

def test_microphone():
    print("🎤 Testing microphone access...")
    
    # List all available microphones
    print("\nAvailable microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {index}: {name}")
    
    # Try to initialize microphone
    try:
        mic = sr.Microphone()
        print(f"\n✅ Default microphone: {mic.device_index}")
        
        # Test ambient noise adjustment
        recognizer = sr.Recognizer()
        with mic as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Ambient noise adjustment complete")
            
            print("\n🎤 Say something (I'll listen for 3 seconds)...")
            try:
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                print("✅ Heard something! Processing...")
                
                # Try to recognize
                text = recognizer.recognize_google(audio)
                print(f"📝 You said: {text}")
                
            except sr.WaitTimeoutError:
                print("⏰ No speech detected (timeout)")
            except sr.UnknownValueError:
                print("🤔 Could not understand audio")
            except sr.RequestError as e:
                print(f"❌ Recognition error: {e}")
                
    except Exception as e:
        print(f"❌ Microphone error: {e}")

if __name__ == "__main__":
    test_microphone()