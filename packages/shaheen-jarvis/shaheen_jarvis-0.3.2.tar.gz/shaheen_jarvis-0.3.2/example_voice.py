#!/usr/bin/env python3
"""
Voice features demonstration for Shaheen-Jarvis framework.
Shows text-to-speech and speech-to-text capabilities.
"""

from jarvis import Jarvis
import time


def main():
    print("🎤 Shaheen-Jarvis Voice Features Demo")
    print("=" * 42)
    
    # Initialize Jarvis with voice enabled
    print("Initializing Jarvis with voice capabilities...")
    jarvis = Jarvis(enable_voice=True)
    print(f"✓ Jarvis initialized with voice support\n")
    
    # Check if voice is available
    if jarvis.voice_io and jarvis.voice_io.is_available():
        print("✅ Voice I/O is fully available!")
    else:
        print("⚠️ Voice I/O partially available (some components may be missing)")
    
    print("\n" + "="*42)
    
    # Example 1: Text-to-Speech Demo
    print("1. Text-to-Speech (TTS) Demo:")
    print("-" * 32)
    
    try:
        # Test various phrases
        phrases = [
            "Hello! I am Jarvis, your AI assistant.",
            "I can speak any text you give me.",
            "Let me tell you the current time.",
        ]
        
        for phrase in phrases:
            print(f"Speaking: {phrase}")
            jarvis.speak(phrase)
            time.sleep(1)  # Small pause between phrases
        
        # Get and speak the current time
        time_result = jarvis.call('tell_time')
        print(f"Speaking time: {time_result}")
        jarvis.speak(time_result)
        
        print("✅ Text-to-Speech working correctly!")
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")
    
    print("\n" + "="*42)
    
    # Example 2: Combined Voice + AI
    print("2. Voice + AI Integration:")
    print("-" * 28)
    
    try:
        # Ask AI a question and speak the response
        ai_question = "What is the weather like?"
        print(f"Asking AI: {ai_question}")
        ai_response = jarvis.call('ask_ai', ai_question)
        
        print(f"AI Response: {ai_response}")
        jarvis.speak("Here's what AI says about the weather:")
        jarvis.speak(ai_response)
        
        print("✅ Voice + AI integration working!")
        
    except Exception as e:
        print(f"❌ Voice + AI Error: {e}")
    
    print("\n" + "="*42)
    
    # Example 3: Voice Commands Demo
    print("3. Voice Commands Available:")
    print("-" * 31)
    
    voice_commands = [
        "voice - Check voice status",
        "voice on - Enable voice I/O", 
        "voice off - Disable voice I/O",
        "voice 'text' - Speak the text",
        "listen - Listen for voice input",
    ]
    
    for command in voice_commands:
        print(f"  • {command}")
    
    print("\n" + "="*42)
    
    # Example 4: Interactive Voice Demo
    print("4. Try Voice Commands in CLI:")
    print("-" * 33)
    
    print("To test voice features interactively:")
    print("1. Run: python -m jarvis.cli --voice")
    print("2. Type: voice Hello from Jarvis!")
    print("3. Type: listen (if you have a microphone)")
    print("4. Say something and Jarvis will try to understand")
    print("5. Type: tell_time (and Jarvis can speak the result)")
    
    print("\n" + "="*42)
    
    # Example 5: Voice + Function Integration
    print("5. Voice-Enabled Function Calls:")
    print("-" * 35)
    
    try:
        # Get weather and speak it
        weather_result = jarvis.call('get_weather', 'London')
        print(f"Weather result: {weather_result}")
        jarvis.speak("Here's the weather information for London:")
        jarvis.speak(weather_result)
        
        # Get a joke and speak it
        joke_result = jarvis.call('tell_joke')
        print(f"Joke: {joke_result}")
        jarvis.speak("Here's a joke for you:")
        jarvis.speak(joke_result)
        
        print("✅ Voice-enabled functions working!")
        
    except Exception as e:
        print(f"❌ Voice functions error: {e}")
    
    print("\n" + "="*42)
    
    # Summary
    print("🎉 Voice Features Summary:")
    print("-" * 27)
    print("✅ Text-to-Speech (TTS) - Convert text to spoken words")
    print("✅ Speech-to-Text (STT) - Convert spoken words to text")
    print("✅ Voice-enabled CLI commands")
    print("✅ Voice + AI integration") 
    print("✅ Voice + function call integration")
    print("✅ Multiple TTS backends: pyttsx3, gTTS")
    print("✅ Multiple STT backends: Whisper, Google Speech, Sphinx")
    
    print("\n" + "="*42)
    print("🔊 Your Jarvis now has full voice capabilities!")
    print("Use --voice flag when starting CLI for voice features.")
    print("="*42)


if __name__ == '__main__':
    main()
