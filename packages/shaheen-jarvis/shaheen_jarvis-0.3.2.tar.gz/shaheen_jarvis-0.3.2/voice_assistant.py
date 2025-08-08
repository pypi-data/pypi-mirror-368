#!/usr/bin/env python3
"""
Voice-Controlled Jarvis Assistant
Takes voice input and performs actions based on spoken commands.
"""

import time
import re
from jarvis import Shaheen_Jarvis
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)


class VoiceControlledJarvis:
    """Voice-controlled assistant that listens and performs actions."""
    
    def __init__(self):
        """Initialize the voice-controlled Jarvis."""
        print(f"{Fore.CYAN}🎤 Initializing Voice-Controlled Jarvis...{Style.RESET_ALL}")
        
        # Initialize Jarvis with voice enabled
        self.jarvis = Shaheen_Jarvis(enable_voice=True)
        
        # Check if voice I/O is available
        if not self.jarvis.voice_io:
            print(f"{Fore.RED}❌ Voice I/O not available. Exiting...{Style.RESET_ALL}")
            exit(1)
        
        print(f"{Fore.GREEN}✅ Voice-Controlled Jarvis ready!{Style.RESET_ALL}")
        self.running = True
        
        # Wake words that activate the assistant
        self.wake_words = ['jarvis', 'hey jarvis', 'ok jarvis', 'computer']
        
        # Exit commands
        self.exit_commands = ['exit', 'quit', 'goodbye', 'stop', 'shutdown']
    
    def speak_and_print(self, text):
        """Print text and speak it."""
        print(f"{Fore.GREEN}🔊 Jarvis: {text}{Style.RESET_ALL}")
        self.jarvis.speak(text)
    
    def listen_for_command(self, timeout=10):
        """Listen for voice command with timeout."""
        print(f"{Fore.YELLOW}🎯 Listening for command... (speak within {timeout} seconds){Style.RESET_ALL}")
        
        try:
            # Use speech recognition to get command
            command = self.jarvis.listen()
            
            if command:
                print(f"{Fore.CYAN}👤 You said: {command}{Style.RESET_ALL}")
                return command.lower().strip()
            else:
                print(f"{Fore.RED}❌ Could not understand the command{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error listening: {e}{Style.RESET_ALL}")
            return None
    
    def process_voice_command(self, command):
        """Process the voice command and perform appropriate action."""
        if not command:
            return
        
        # Check for exit commands
        if any(exit_cmd in command for exit_cmd in self.exit_commands):
            self.speak_and_print("Goodbye! Shutting down voice assistant.")
            self.running = False
            return
        
        # Direct function calls
        function_patterns = {
            r'what.*time|tell.*time|current time': 'tell_time',
            r'what.*date|tell.*date|current date|today.*date': 'tell_date',
            r'tell.*joke|joke|funny': 'tell_joke',
            r'random quote|quote|inspire': 'get_random_quote',
            r'weather|forecast': self.handle_weather_command,
            r'calculate|math|compute': self.handle_calculation,
            r'generate password|password|create password': 'generate_password',
            r'system info|system information|computer info': 'system_info',
            r'ip address|my ip|network address': 'get_ip_address',
            r'wikipedia|wiki|search wiki': self.handle_wikipedia_search,
            r'note|remember|save note': self.handle_note_command,
            r'recall|remember|show notes': self.handle_recall_notes,
            r'todo|task|reminder': self.handle_todo_command,
            r'show todo|show tasks|my tasks': 'show_todos',
            r'play.*youtube|youtube.*play|play.*song': self.handle_youtube_music,
            r'open whatsapp|whatsapp|open whats app': 'open_whatsapp',
            r'open.*app|launch.*app|start.*app': self.handle_open_app,
            r'open.*website|open.*site|go to': self.handle_open_website,
            r'ask ai|question|what is|what are|how does|why|explain|tell me about': self.handle_ai_question,
            r'generate code|write code|code': self.handle_code_generation,
            r'explain code|code explanation': self.handle_code_explanation,
            r'summarize|summary': self.handle_text_summary,
            r'translate': self.handle_translation,
            r'help|what can you do|commands': self.show_help,
        }
        
        # Try to match command patterns
        for pattern, action in function_patterns.items():
            if re.search(pattern, command):
                if callable(action):
                    action(command)
                else:
                    # Direct function call
                    try:
                        result = self.jarvis.call(action)
                        self.speak_and_print(result)
                    except Exception as e:
                        self.speak_and_print(f"Error executing {action}: {str(e)}")
                return
        
        # Try natural language dispatch
        try:
            result = self.jarvis.dispatch(command)
            self.speak_and_print(result)
        except Exception as e:
            self.speak_and_print(f"I'm sorry, I couldn't understand or execute that command: {command}")
    
    def handle_weather_command(self, command):
        """Handle weather-related commands with improved city detection."""
        print(f"🌤️ Debug: Weather command received: '{command}'")
        
        # Try to extract city name from command with improved patterns
        city = self.extract_city_from_weather_command(command)
        
        # Handle common city aliases and variations
        city_aliases = {
            'nyc': 'New York',
            'ny': 'New York', 
            'la': 'Los Angeles',
            'sf': 'San Francisco',
            'dc': 'Washington',
            'chi': 'Chicago',
            'philly': 'Philadelphia',
            'vegas': 'Las Vegas',
            'miami': 'Miami',
            'boston': 'Boston',
            'seattle': 'Seattle',
            'london': 'London',
            'paris': 'Paris',
            'tokyo': 'Tokyo',
            'dubai': 'Dubai',
            'mumbai': 'Mumbai',
            'delhi': 'Delhi',
            'lahore': 'Lahore',
            'karachi': 'Karachi',
            'islamabad': 'Islamabad'
        }
        
        # Check if the city is an alias
        city_lower = city.lower()
        if city_lower in city_aliases:
            city = city_aliases[city_lower]
            print(f"🏙️ Debug: Converted alias '{city_lower}' to '{city}'")
        
        try:
            print(f"🌤️ Debug: Calling weather API for city: '{city}'")
            result = self.jarvis.call('get_weather', city)
            self.speak_and_print(result)
        except Exception as e:
            print(f"❌ Debug: Weather API error: {str(e)}")
            self.speak_and_print(f"Error getting weather for {city}: {str(e)}")
    
    def extract_city_from_weather_command(self, command):
        """Extract city name from weather command with improved pattern matching."""
        original_command = command
        command = command.lower()
        
        print(f"🔍 Debug: Processing weather command: '{original_command}'")
        print(f"🔍 Debug: Lowercase command: '{command}'")
        
        # Remove common words that might interfere
        command_cleaned = re.sub(r'\b(what\'s|what is|tell me|show me|get|the)\b', '', command).strip()
        print(f"🔍 Debug: Cleaned command: '{command_cleaned}'")
        
        # Enhanced patterns for weather commands with better matching
        patterns = [
            # Specific city patterns (highest priority)
            r'weather.*?(?:in|for|of|at)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)',     # "weather in/for/of/at [city]"
            r'(?:in|for|of|at)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*).*?weather',     # "in/for/of/at [city] weather"
            r'weather\s+(?:in\s+)?([a-zA-Z]+(?:\s+[a-zA-Z]+)*)',              # "weather [city]" or "weather in [city]"
            r'([a-zA-Z]+(?:\s+[a-zA-Z]+)*)\s+weather',                        # "[city] weather"
            r'weather.*?([a-zA-Z]{2,}(?:\s+[a-zA-Z]{2,})*)',                  # "weather [city]" (2+ chars)
            # Fallback patterns
            r'([a-zA-Z]+)\s*$',                                               # Single word at end
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, command_cleaned)
            if match:
                city = match.group(1).strip()
                
                # Filter out common non-city words
                excluded_words = {
                    'weather', 'forecast', 'today', 'tomorrow', 'now', 'current', 
                    'outside', 'here', 'there', 'like', 'is', 'the', 'what',
                    'how', 'tell', 'show', 'get', 'me', 'my', 'this', 'that'
                }
                
                # Check if the extracted word is not an excluded word
                city_words = city.split()
                filtered_words = [word for word in city_words if word.lower() not in excluded_words]
                
                if filtered_words:
                    city = ' '.join(filtered_words)
                    # Capitalize city name properly
                    city = ' '.join(word.capitalize() for word in city.split())
                    print(f"🏙️ Debug: Pattern {i+1} matched! Extracted city: '{city}'")
                    print(f"🏙️ Success: Using city '{city}' for weather query")
                    return city
                else:
                    print(f"🔍 Debug: Pattern {i+1} matched '{city}' but filtered out as non-city word")
        
        # Ask user for city instead of defaulting to New York
        print(f"🏙️ Debug: No city found in '{original_command}'")
        self.speak_and_print("I couldn't identify the city. Which city would you like weather for?")
        
        # Try to get city from user
        try:
            city_response = self.listen_for_command(timeout=10)
            if city_response:
                city_response = city_response.strip()
                # Clean up the response
                city_response = re.sub(r'\b(weather|for|in|the)\b', '', city_response, flags=re.IGNORECASE).strip()
                if city_response:
                    city = ' '.join(word.capitalize() for word in city_response.split())
                    print(f"🏙️ Got city from user: '{city}'")
                    return city
        except Exception as e:
            print(f"🔍 Debug: Error getting city from user: {e}")
        
        # Final fallback - but ask user first
        print(f"🏙️ Using default city: New York (you can change this in the code)")
        return "New York"
    
    def handle_calculation(self, command):
        """Handle calculation commands."""
        # Extract mathematical expression
        math_patterns = [
            r'calculate\s+(.+)',
            r'what.*is\s+(.+)',
            r'compute\s+(.+)',
            r'math\s+(.+)'
        ]
        
        expression = None
        for pattern in math_patterns:
            match = re.search(pattern, command)
            if match:
                expression = match.group(1).strip()
                break
        
        if expression:
            try:
                result = self.jarvis.call('calculate_expression', expression)
                self.speak_and_print(result)
            except Exception as e:
                self.speak_and_print(f"Error calculating: {str(e)}")
        else:
            self.speak_and_print("Please tell me what you want to calculate.")
    
    def handle_wikipedia_search(self, command):
        """Handle Wikipedia search commands."""
        # Extract search topic
        wiki_patterns = [
            r'wikipedia\s+(.+)',
            r'wiki\s+(.+)',
            r'search wiki\s+(.+)',
            r'tell me about\s+(.+)'
        ]
        
        topic = None
        for pattern in wiki_patterns:
            match = re.search(pattern, command)
            if match:
                topic = match.group(1).strip()
                break
        
        if topic:
            try:
                result = self.jarvis.call('wikipedia_summary', topic)
                self.speak_and_print(result)
            except Exception as e:
                self.speak_and_print(f"Error searching Wikipedia: {str(e)}")
        else:
            self.speak_and_print("What would you like me to search for on Wikipedia?")
    
    def handle_note_command(self, command):
        """Handle note-taking commands."""
        # Extract note content
        note_patterns = [
            r'note\s+(.+)',
            r'remember\s+(.+)',
            r'save\s+(.+)'
        ]
        
        note_content = None
        for pattern in note_patterns:
            match = re.search(pattern, command)
            if match:
                note_content = match.group(1).strip()
                break
        
        if note_content:
            try:
                result = self.jarvis.call('note_something', note_content, 'voice')
                self.speak_and_print(result)
            except Exception as e:
                self.speak_and_print(f"Error saving note: {str(e)}")
        else:
            self.speak_and_print("What would you like me to remember?")
    
    def handle_recall_notes(self, command):
        """Handle note recall commands."""
        try:
            result = self.jarvis.call('recall_note')
            self.speak_and_print(result)
        except Exception as e:
            self.speak_and_print(f"Error recalling notes: {str(e)}")
    
    def handle_todo_command(self, command):
        """Handle todo/task commands."""
        task_patterns = [
            r'todo\s+(.+)',
            r'task\s+(.+)',
            r'reminder\s+(.+)',
            r'add task\s+(.+)'
        ]
        
        task_content = None
        for pattern in task_patterns:
            match = re.search(pattern, command)
            if match:
                task_content = match.group(1).strip()
                break
        
        if task_content:
            try:
                result = self.jarvis.call('create_todo', task_content)
                self.speak_and_print(result)
            except Exception as e:
                self.speak_and_print(f"Error creating task: {str(e)}")
        else:
            self.speak_and_print("What task would you like me to add?")
    
    def handle_ai_question(self, command):
        """Handle AI question commands."""
        # Remove 'jarvis' wake word if present
        cleaned_command = re.sub(r'^(jarvis|hey jarvis|ok jarvis)\s*', '', command, flags=re.IGNORECASE).strip()
        
        # Try to extract the actual question from various patterns
        question_patterns = [
            r'ask ai\s+(.+)',
            r'ask\s+(.+)',
            r'question\s+(.+)',
            r'what is\s+(.+)',
            r'what are\s+(.+)',
            r'what does\s+(.+)',
            r'how does\s+(.+)',
            r'how do\s+(.+)', 
            r'why does\s+(.+)',
            r'why is\s+(.+)',
            r'explain\s+(.+)',
            r'tell me about\s+(.+)',
            r'(.+)'  # Fallback - use the entire cleaned command
        ]
        
        question = None
        for pattern in question_patterns:
            match = re.search(pattern, cleaned_command, re.IGNORECASE)
            if match:
                question = match.group(1).strip()
                # Don't use single words as questions unless they're meaningful
                if len(question.split()) >= 1 and question.lower() not in ['ai', 'question', 'ask']:
                    break
        
        # If still no good question, try using the whole command
        if not question or question.lower() in ['ai', 'question', 'ask']:
            question = cleaned_command
        
        if question and len(question.strip()) > 0:
            try:
                print(f"🤖 Asking AI: {question}")
                result = self.jarvis.call('ask_ai', question)
                self.speak_and_print(result)
            except Exception as e:
                self.speak_and_print(f"Error asking AI: {str(e)}")
        else:
            self.speak_and_print("What would you like to ask the AI?")
    
    def handle_code_generation(self, command):
        """Handle code generation commands."""
        code_patterns = [
            r'generate code\s+(.+)',
            r'write code\s+(.+)',
            r'code\s+(.+)'
        ]
        
        description = None
        for pattern in code_patterns:
            match = re.search(pattern, command)
            if match:
                description = match.group(1).strip()
                break
        
        if description:
            try:
                result = self.jarvis.call('generate_code', description)
                self.speak_and_print(result)
            except Exception as e:
                self.speak_and_print(f"Error generating code: {str(e)}")
        else:
            self.speak_and_print("What kind of code would you like me to generate?")
    
    def handle_code_explanation(self, command):
        """Handle code explanation commands."""
        self.speak_and_print("I can explain code, but I need you to provide the code through text input for now.")
    
    def handle_text_summary(self, command):
        """Handle text summarization commands."""
        self.speak_and_print("I can summarize text, but please provide the text through another method for now.")
    
    def handle_translation(self, command):
        """Handle translation commands."""
        self.speak_and_print("I can translate text using AI. Please provide the text and target language.")
    
    def handle_youtube_music(self, command):
        """Handle YouTube music playing commands."""
        # Extract artist and song from command
        music_patterns = [
            r'play\s+(.+)\s+(?:song|songs|music)\s+(?:on\s+)?youtube',
            r'play\s+(.+)\s+on\s+youtube',
            r'youtube\s+play\s+(.+)',
            r'play\s+(.+)\s+song',
            r'play\s+(.+)'
        ]
        
        query = None
        for pattern in music_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                break
        
        if query:
            try:
                result = self.jarvis.call('play_youtube_song', query)
                self.speak_and_print(result)
            except Exception as e:
                self.speak_and_print(f"Error playing YouTube music: {str(e)}")
        else:
            self.speak_and_print("What song would you like me to play on YouTube?")
    
    def handle_open_app(self, command):
        """Handle app opening commands."""
        app_patterns = [
            r'open\s+(.+?)\s+app',
            r'launch\s+(.+?)\s+app',
            r'start\s+(.+?)\s+app',
            r'open\s+(.+)',
            r'launch\s+(.+)',
            r'start\s+(.+)'
        ]
        
        app_name = None
        for pattern in app_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                app_name = match.group(1).strip()
                break
        
        if app_name:
            try:
                result = self.jarvis.call('open_app', app_name)
                self.speak_and_print(result)
            except Exception as e:
                self.speak_and_print(f"Error opening app: {str(e)}")
        else:
            self.speak_and_print("Which app would you like me to open?")
    
    def handle_open_website(self, command):
        """Handle website opening commands."""
        website_patterns = [
            r'open\s+(?:website\s+)?(.+\.\w+)',
            r'go\s+to\s+(.+\.\w+)',
            r'visit\s+(.+\.\w+)',
            r'open\s+(.+)\s+(?:website|site)',
            r'go\s+to\s+(.+)\s+(?:website|site)'
        ]
        
        url = None
        for pattern in website_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                url = match.group(1).strip()
                break
        
        if url:
            try:
                result = self.jarvis.call('open_website', url)
                self.speak_and_print(result)
            except Exception as e:
                self.speak_and_print(f"Error opening website: {str(e)}")
        else:
            self.speak_and_print("Which website would you like me to open?")
    
    def show_help(self, command):
        """Show available voice commands."""
        help_text = '''
        Here are some commands you can try:
        
        Time and Date:
        - What time is it?
        - Tell me the date
        
        Weather:
        - What's the weather?
        - Weather in London
        
        Multimedia:
        - Play Atif Aslam song on YouTube
        - Play romantic songs on YouTube
        - Open WhatsApp
        - Open Chrome
        - Open Calculator
        - Open website google.com
        
        Information:
        - Tell me a joke
        - Random quote
        - System information
        - My IP address
        
        Calculations:
        - Calculate 5 plus 3
        - What is 10 times 7?
        
        Notes and Tasks:
        - Note remember to buy milk
        - Show my notes
        - Todo call mom tomorrow
        - Show my tasks
        
        AI Features:
        - Ask AI what is Python?
        - Generate code to sort a list
        - What is artificial intelligence?
        - Explain machine learning
        
        Wikipedia:
        - Wikipedia artificial intelligence
        - Tell me about Python programming
        
        Other:
        - Generate password
        - Exit or quit to stop
        '''
        
        self.speak_and_print("I can help you with many tasks. Check the console for a full list of commands.")
        print(f"{Fore.BLUE}{help_text}{Style.RESET_ALL}")
    
    def run(self):
        """Main loop for voice-controlled assistant."""
        self.speak_and_print("Voice-controlled Jarvis is ready! Say 'Jarvis' followed by your command, or just start speaking.")
        self.speak_and_print("Say 'help' to hear available commands, or 'exit' to quit.")
        
        while self.running:
            try:
                print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}🎤 Say 'Jarvis' or start speaking your command...{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
                
                # Listen for voice input
                command = self.listen_for_command()
                
                if command:
                    # Check if command starts with wake word, if not, process directly
                    wake_word_used = any(wake in command for wake in self.wake_words)
                    
                    if wake_word_used:
                        # Remove wake word from command
                        for wake in self.wake_words:
                            command = command.replace(wake, '').strip()
                    
                    if command:  # If there's still a command after removing wake word
                        self.process_voice_command(command)
                    else:
                        self.speak_and_print("Yes, I'm listening. What can I do for you?")
                else:
                    print(f"{Fore.YELLOW}⏰ No command detected. Trying again...{Style.RESET_ALL}")
                
                # Small pause between listening sessions
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.speak_and_print("Voice assistant stopped by user.")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
                time.sleep(2)
        
        print(f"{Fore.GREEN}👋 Voice-controlled Jarvis shutdown complete.{Style.RESET_ALL}")


def main():
    """Main function to run the voice-controlled assistant."""
    print(f"{Fore.CYAN}")
    print("🎤" + "="*58 + "🎤")
    print("           VOICE-CONTROLLED JARVIS ASSISTANT")
    print("🎤" + "="*58 + "🎤")
    print(f"{Style.RESET_ALL}")
    
    assistant = VoiceControlledJarvis()
    assistant.run()


if __name__ == '__main__':
    main()
