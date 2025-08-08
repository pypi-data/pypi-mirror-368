#!/usr/bin/env python3
"""
Simple Voice Command Demo
Demonstrates working voice recognition with Jarvis commands.
"""

from jarvis import Jarvis
import re


def extract_city_from_command(command):
    """Extract city name from voice command."""
    command = command.lower()
    
    # Common patterns for weather commands
    patterns = [
        r'weather.*?(?:in|for|of|at)\s+(\w+(?:\s+\w+)?)',  # "weather in/for/of/at [city]"
        r'(?:in|for|of|at)\s+(\w+(?:\s+\w+)?).*?weather',  # "in/for/of/at [city] weather"
        r'weather\s+(\w+(?:\s+\w+)?)',                     # "weather [city]"
        r'(\w+(?:\s+\w+)?)\s+weather',                     # "[city] weather"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command)
        if match:
            city = match.group(1).strip()
            # Capitalize city name properly
            city = ' '.join(word.capitalize() for word in city.split())
            print(f"🏙️ Extracted city: {city}")
            return city
    
    print("🏙️ No city found, using default: New York")
    return "New York"


def voice_command_demo():
    """Simple demo of voice commands."""
    print("🎤 Simple Voice Command Demo")
    print("=" * 32)
    
    # Initialize Jarvis with voice
    jarvis = Jarvis(enable_voice=True)
    
    if not jarvis.voice_io or not jarvis.voice_io.stt_engine:
        print("❌ Voice recognition not available")
        return
    
    print("✅ Voice recognition ready!")
    
    # Speak instructions
    jarvis.speak("Hello! Voice recognition is working. Please say a command.")
    
    print("\n🎯 Available Commands:")
    commands = [
        "what time is it",
        "tell me a joke", 
        "weather in London",
        "system information",
        "generate password"
    ]
    
    for cmd in commands:
        print(f"  • {cmd}")
    
    print("\n🎤 Say one of the commands above:")
    
    # Listen for command
    command = jarvis.listen()
    
    if command:
        print(f"✅ You said: '{command}'")
        jarvis.speak(f"I heard: {command}")
        
        # Execute the command
        try:
            if "time" in command.lower():
                result = jarvis.call("tell_time")
                
            elif "joke" in command.lower():
                result = jarvis.call("tell_joke")
                
            elif "weather" in command.lower():
                # Extract city name from the command
                city = extract_city_from_command(command)
                result = jarvis.call("get_weather", city)
                
            elif "system" in command.lower():
                result = jarvis.call("system_info")
                
            elif "password" in command.lower():
                result = jarvis.call("generate_password")
                
            else:
                # Try natural language dispatch
                result = jarvis.dispatch(command)
            
            print(f"📋 Result: {result}")
            jarvis.speak(result)
            
        except Exception as e:
            error_msg = f"Sorry, I had trouble executing that command: {str(e)}"
            print(f"❌ {error_msg}")
            jarvis.speak(error_msg)
    
    else:
        print("❌ No command recognized")
        jarvis.speak("I didn't understand that command. Please try again.")
    
    print("\n🎉 Voice demo completed!")


if __name__ == "__main__":
    voice_command_demo()
