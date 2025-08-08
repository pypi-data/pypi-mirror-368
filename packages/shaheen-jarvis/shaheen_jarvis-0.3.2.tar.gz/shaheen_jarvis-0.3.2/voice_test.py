#!/usr/bin/env python3
"""
Simple Voice Command Test Script
Quick test for voice recognition and command execution.
"""

from jarvis import Jarvis


def test_voice_commands():
    """Test voice commands with Jarvis."""
    print("🎤 Voice Command Test")
    print("=" * 25)
    
    # Initialize Jarvis with voice
    print("Initializing Jarvis with voice support...")
    jarvis = Jarvis(enable_voice=True)

    # Use Google Speech as a fallback for this test
    jarvis.voice_io.stt_engine = None
    jarvis.voice_io._init_google_speech()
    
    if not jarvis.voice_io:
        print("❌ Voice not available")
        return
    
    print("✅ Voice support ready!")
    
    # Test commands
    test_commands = [
        ("tell_time", "What time is it?"),
        ("tell_joke", "Tell me a joke"),
        ("get_weather", "Weather information"),
        ("ask_ai", "Ask AI: What is Python?"),
    ]
    
    print("\n🔊 Testing Text-to-Speech:")
    jarvis.speak("Hello! Voice test starting now.")
    
    print("\n📋 Available test commands:")
    for func, desc in test_commands:
        print(f"  • {desc}")
    
    print("\n🎯 Voice Recognition Test:")
    print("Say one of the commands above...")
    
    try:
        # Listen for command
        command = jarvis.listen()
        
        if command:
            print(f"👤 You said: {command}")
            
            # Try to execute the command
            if "time" in command.lower():
                result = jarvis.call("tell_time")
                print(f"🔊 Result: {result}")
                jarvis.speak(result)
                
            elif "joke" in command.lower():
                result = jarvis.call("tell_joke")
                print(f"🔊 Result: {result}")
                jarvis.speak(result)
                
            elif "weather" in command.lower():
                result = jarvis.call("get_weather")
                print(f"🔊 Result: {result}")
                jarvis.speak(result)
                
            elif "ai" in command.lower() or "python" in command.lower():
                # Extract the actual question from the command
                question = command
                if "what is" in command.lower():
                    question = command  # Use the full command as the question
                elif "ask ai" in command.lower():
                    # Extract question after "ask ai"
                    question = command.lower().replace("ask ai", "").replace(":", "").strip()
                    if not question:
                        question = "What is AI?"
                else:
                    question = "What is AI?" if "ai" in command.lower() else "What is Python?"
                    
                result = jarvis.call("ask_ai", question)
                print(f"🔊 Result: {result}")
                jarvis.speak(result)
                
            else:
                # Try natural language dispatch
                result = jarvis.dispatch(command)
                print(f"🔊 Result: {result}")
                jarvis.speak(result)
        else:
            print("❌ No command recognized")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Voice test completed!")


if __name__ == "__main__":
    test_voice_commands()
