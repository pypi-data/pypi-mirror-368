#!/usr/bin/env python3
"""
Improved Voice Recognition Test Script
Better testing for speech recognition with debugging info.
"""

from jarvis import Shaheen_Jarvis
import time


def test_improved_voice():
    """Test improved voice recognition."""
    print("🎤 IMPROVED Voice Recognition Test")
    print("=" * 40)
    
    # Initialize Jarvis with voice
    print("Initializing Jarvis with improved voice support...")
    jarvis = Shaheen_Jarvis(enable_voice=True)
    
    if not jarvis.voice_io:
        print("❌ Voice I/O not available")
        return
    
    # Check voice components
    print(f"TTS Engine: {'✅' if jarvis.voice_io.tts_engine else '❌'}")
    print(f"STT Engine: {'✅' if jarvis.voice_io.stt_engine else '❌'}")
    print(f"Microphone: {'✅' if hasattr(jarvis.voice_io, 'microphone') else '❌'}")
    
    if not jarvis.voice_io.stt_engine:
        print("❌ Speech recognition not available - please check microphone permissions")
        return
    
    print("\n🔊 Testing Text-to-Speech first...")
    jarvis.speak("Voice recognition test starting. Please make sure your microphone is working.")
    
    print("\n🎯 Voice Recognition Test - Multiple Attempts")
    print("Available test phrases:")
    test_phrases = [
        "what time is it",
        "tell me a joke", 
        "hello jarvis",
        "weather information",
        "help me"
    ]
    
    for phrase in test_phrases:
        print(f"  • Say: '{phrase}'")
    
    # Multiple test attempts
    print("📝 Speak 'quit', 'exit', or press Ctrl+C/Q to stop listening.")
    print("👂 Awaiting voice commands... (Ctrl+C to exit)")

    while True:
        try:
            # Test voice recognition
            result = jarvis.listen()
            
            if result:
                print(f"🎉 SUCCESS! You said: '{result}'")
                
                # Exit condition
                if "quit" in result.lower() or "exit" in result.lower():
                    print("🛑 Exiting Voice Test.")
                    break
                
                # Try to execute the command directly
                try:
                    response = jarvis.dispatch(result)
                    print(f"⚡ Response: {response}")
                    jarvis.speak(response)
                    
                except Exception as cmd_error:
                    print(f"⚠️ Command execution error: {cmd_error}")
                    jarvis.speak(f"I heard you say: {result}, but I had trouble executing that command.")
                
            else:
                print("❌ No speech recognized. Please try again.")
                jarvis.speak("I didn't catch that. Please try speaking again, a bit louder and clearer.")
                
        except KeyboardInterrupt:
            print("🛑 Interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            jarvis.speak("An error occurred. Please try again.")

        time.sleep(2)  # Brief pause between attempts
    
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    # Final test with immediate feedback
    print("🔧 Final Test - Say 'test complete' to finish:")
    try:
        final_result = jarvis.listen()
        if final_result:
            print(f"✅ Final result: '{final_result}'")
            jarvis.speak(f"Perfect! I heard you say: {final_result}. Voice recognition test completed successfully!")
        else:
            print("❌ Final test failed")
            jarvis.speak("Voice recognition test completed. Some issues were detected.")
    except Exception as e:
        print(f"❌ Final test error: {e}")
    
    print("\n🎉 Voice Recognition Test Completed!")
    print("If you heard responses, TTS is working.")
    print("If commands were recognized, STT is working.")


def quick_voice_demo():
    """Quick demonstration of working voice features."""
    print("\n🚀 Quick Voice Demo")
    print("=" * 20)
    
    jarvis = Shaheen_Jarvis(enable_voice=True)
    
    if jarvis.voice_io and jarvis.voice_io.tts_engine:
        demo_phrases = [
            "Voice recognition system initialized",
            "Text to speech is working perfectly",
            "Please test speech recognition now"
        ]
        
        for phrase in demo_phrases:
            print(f"Speaking: {phrase}")
            jarvis.speak(phrase)
            time.sleep(1)
        
        print("✅ TTS Demo completed")
    else:
        print("❌ TTS not available")


if __name__ == "__main__":
    # Run quick demo first
    quick_voice_demo()
    
    # Then run full test
    test_improved_voice()
