"""
Main Jarvis Engine - Core functionality for the Shaheen-Jarvis framework.
Handles function registration, dispatch, plugin loading, and configuration management.
"""

import logging
import re
from typing import Dict, Callable, Any, Optional, List, Union
from functools import wraps

from .config_manager import ConfigManager
from .plugin_loader import PluginLoader
from .voice_io import VoiceIO


class Shaheen_Jarvis:
    """
    Main Jarvis class with register, dispatch, plugin loading, and config management.
    """
    
    def __init__(self, config_path: Optional[str] = None, enable_voice: bool = False):
        """
        Initialize Jarvis with configuration and optional voice support.
        
        Args:
            config_path: Path to configuration file
            enable_voice: Whether to enable voice I/O
        """
        self.functions: Dict[str, Callable] = {}
        self.aliases: Dict[str, str] = {}
        self.function_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Initialize components
        self.config = ConfigManager(config_path)
        self.plugin_loader = PluginLoader(self)
        self.voice_io = VoiceIO(self.config) if enable_voice else None
        
        # Setup logging
        self._setup_logging()
        
        # Load predefined functions
        self._load_predefined_functions()
        
        self.logger.info("Jarvis initialized successfully")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('logging.level', 'INFO')
        log_to_file = self.config.get('logging.log_to_file', True)
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self.logger = logging.getLogger(__name__)
        
        if log_to_file:
            handler = logging.FileHandler('jarvis.log')
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(handler)
    
    def _load_predefined_functions(self):
        """Load all predefined functions from modules."""
        modules_to_load = [
            ('basic_functions', 'basic'),
            ('web_functions', 'web'),
            ('system_functions', 'system'),
            ('utility_functions', 'utility'),
            ('productivity_functions', 'productivity'),
            ('ai_functions', 'ai')
        ]
        
        for module_name, category in modules_to_load:
            try:
                module = __import__(f'jarvis.modules.{module_name}', fromlist=[module_name])
                
                # Get all functions from the module
                for name in dir(module):
                    if name.startswith('_') or name in ['os', 'sys', 'json', 'requests', 'datetime', 'random', 'string', 'hashlib', 'smtplib', 'subprocess', 'platform', 'psutil', 'webbrowser', 'wikipedia', 'MIMEMultipart', 'MIMEText', 'MIMEApplication', 'Timer', 'time', 'BeautifulSoup', 'timedelta', 'List', 'Dict', 'Any', 'Optional', 'Callable', 'Union']:
                        continue
                    
                    func = getattr(module, name)
                    if callable(func):
                        description = func.__doc__ or f"{name} function from {category} module"
                        self.register(name, func, description=description, category=category)
                        
            except ImportError as e:
                self.logger.warning(f"Could not load {module_name}: {e}")
            except Exception as e:
                self.logger.error(f"Error loading {module_name}: {e}")
    
    def register(self, name: str, func: Callable, 
                 aliases: Optional[List[str]] = None,
                 description: str = "",
                 category: str = "general") -> None:
        """
        Register a function with the Jarvis system.
        
        Args:
            name: Function name
            func: The callable function
            aliases: List of alternative names for the function
            description: Description of what the function does
            category: Category for organizing functions
        """
        if not callable(func):
            raise ValueError(f"'{name}' is not callable")
        
        self.functions[name] = func
        self.function_metadata[name] = {
            'description': description or func.__doc__ or "",
            'category': category,
            'aliases': aliases or []
        }
        
        # Register aliases
        if aliases:
            for alias in aliases:
                self.aliases[alias] = name
        
        self.logger.debug(f"Registered function: {name}")
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a function.
        
        Args:
            name: Function name to unregister
            
        Returns:
            True if function was unregistered, False if not found
        """
        if name in self.functions:
            # Remove aliases
            aliases = self.function_metadata.get(name, {}).get('aliases', [])
            for alias in aliases:
                self.aliases.pop(alias, None)
            
            # Remove function and metadata
            del self.functions[name]
            del self.function_metadata[name]
            
            self.logger.debug(f"Unregistered function: {name}")
            return True
        return False
    
    def call(self, name: str, *args, **kwargs) -> Any:
        """
        Call a registered function by name.
        
        Args:
            name: Function name or alias
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            ValueError: If function is not found
        """
        # Resolve alias to actual function name
        actual_name = self.aliases.get(name, name)
        
        if actual_name not in self.functions:
            available = list(self.functions.keys()) + list(self.aliases.keys())
            raise ValueError(f"Function '{name}' not found. Available: {available}")
        
        try:
            self.logger.info(f"Calling function: {actual_name}")
            result = self.functions[actual_name](*args, **kwargs)
            self.logger.debug(f"Function {actual_name} completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error calling function {actual_name}: {e}")
            raise
    
    def dispatch(self, text: str) -> Any:
        """
        Dispatch natural language text to appropriate function.
        
        Args:
            text: Natural language command
            
        Returns:
            Result of the function call or error message
        """
        text = text.strip().lower()
        original_text = text
        
        # Simple pattern matching for common commands
        patterns = {
            r'what.*time': 'tell_time',
            r'what.*date': 'tell_date',
            r'tell.*joke': 'tell_joke',
            r'weather': 'get_weather',
            r'search.*web': 'search_web',
            r'open.*url': 'open_url',
            r'send.*email': 'send_email',
            r'system.*info': 'system_info',
            r'ip.*address': 'get_ip_address',
            r'generate.*password': 'generate_password',
            r'translate': 'translate_text',
            r'currency': 'convert_currency',
            r'play.*youtube': 'play_youtube_song',
            r'play.*music.*youtube': 'play_youtube_music',
            r'play.*music': 'play_music',
            r'open.*whatsapp': 'open_whatsapp',
            r'set.*alarm': 'set_alarm',
            r'news': 'news_headlines',
            r'wikipedia': 'wikipedia_summary',
            r'wiki': 'wikipedia_summary',
            r'search.*wiki': 'wikipedia_summary',
            r'note.*something': 'note_something',
            r'recall.*note': 'recall_note',
            r'random.*quote': 'get_random_quote',
            r'calculate': 'calculate_expression',
            r'track.*package': 'track_package',
            r'create.*todo': 'create_todo',
            r'show.*todo': 'show_todos',
        }
        
        # Check for specific command patterns first
        for pattern, func_name in patterns.items():
            if re.search(pattern, text):
                try:
                    # Handle special cases that need parameter extraction
                    if func_name == 'play_youtube_song':
                        # Extract song query from the command
                        # Pattern: "play [song] on youtube" or "play youtube [song]"
                        match = re.search(r'play\s+(.+?)\s+(?:on\s+)?youtube|play\s+youtube\s+(.+)', text)
                        if match:
                            song_query = match.group(1) or match.group(2)
                            return self.call(func_name, song_query.strip())
                        else:
                            # Generic YouTube music search
                            return self.call(func_name, "music")
                    
                    elif func_name == 'play_youtube_music':
                        # Extract artist and song from the command
                        # Pattern: "play [artist] songs on youtube" or "play [artist] [song] on youtube"
                        match = re.search(r'play\s+(.+?)\s+(?:songs?\s+)?(?:on\s+)?youtube', text)
                        if match:
                            query_part = match.group(1).strip()
                            # Split into artist and potential song
                            parts = query_part.split(' ', 1)
                            if len(parts) >= 2:
                                return self.call('play_youtube_song', query_part)
                            else:
                                return self.call('play_youtube_song', f"{parts[0]} songs")
                        else:
                            return self.call('play_youtube_song', "music")
                    
                    elif func_name == 'wikipedia_summary':
                        # Extract topic from Wikipedia commands
                        # Patterns: "wikipedia [topic]", "wiki [topic]", "search wiki [topic]", "search [topic] on wikipedia"
                        wiki_patterns = [
                            r'wikipedia\s+(.+)',
                            r'wiki\s+(.+)',
                            r'search\s+wiki\s+(.+)',
                            r'search\s+(.+?)\s+(?:on\s+)?wikipedia',
                            r'tell\s+me\s+about\s+(.+)',
                            r'what\s+is\s+(.+)',
                            r'explain\s+(.+)'
                        ]
                        
                        topic = None
                        for wiki_pattern in wiki_patterns:
                            match = re.search(wiki_pattern, text)
                            if match:
                                topic = match.group(1).strip()
                                break
                        
                        if topic:
                            return self.call(func_name, topic)
                        else:
                            return "Please specify what you'd like to search for on Wikipedia."
                    
                    elif func_name == 'search_web':
                        # Extract search query from the command
                        # Pattern: "search web for [query]"
                        match = re.search(r'search\s+web\s+for\s+(.+)', text, re.IGNORECASE)
                        if match:
                            return self.call(func_name, match.group(1).strip())
                        else:
                            return "Please specify what you'd like to search for on the web."
                    
                    elif func_name == 'calculate_expression':
                        # Extract mathematical expression from the command
                        # Patterns: "calculate [expression]", "what is [expression]"
                        calc_patterns = [
                            r'calculate\s+(.+)',
                            r'what\s+is\s+(.+)',
                            r'compute\s+(.+)',
                            r'math\s+(.+)'
                        ]
                        
                        expression = None
                        for calc_pattern in calc_patterns:
                            match = re.search(calc_pattern, text, re.IGNORECASE)
                            if match:
                                expression = match.group(1).strip()
                                break
                        
                        if expression:
                            return self.call(func_name, expression)
                        else:
                            return "Please specify what you'd like me to calculate."
                    
                    elif func_name == 'note_something':
                        # Extract note content from the command
                        # Patterns: "note [content]", "remember [content]"
                        note_patterns = [
                            r'note\s+(.+)',
                            r'remember\s+(.+)',
                            r'save\s+(.+)'
                        ]
                        
                        note_content = None
                        for note_pattern in note_patterns:
                            match = re.search(note_pattern, text, re.IGNORECASE)
                            if match:
                                note_content = match.group(1).strip()
                                break
                        
                        if note_content:
                            return self.call(func_name, note_content)
                        else:
                            return "Please tell me what you'd like me to remember."

                    else:
                        # Regular function call without parameters
                        return self.call(func_name)
                        
                except ValueError:
                    continue
        
        # If no specific pattern matches, check if it's a question or general query
        # Use AI for questions that start with common question words or seem like queries
        question_indicators = [
            r'^what.*is', r'^what.*are', r'^what.*do', r'^what.*does', r'^what.*can',
            r'^how.*to', r'^how.*do', r'^how.*does', r'^how.*can', r'^how.*is',
            r'^why.*is', r'^why.*do', r'^why.*does', r'^why.*are',
            r'^when.*is', r'^when.*do', r'^when.*does', r'^when.*are',
            r'^where.*is', r'^where.*do', r'^where.*does', r'^where.*are',
            r'^who.*is', r'^who.*are', r'^who.*was', r'^who.*were',
            r'^can.*you', r'^do.*you', r'^are.*you', r'^will.*you',
            r'^explain', r'^tell.*me.*about', r'^define'
        ]
        
        for indicator in question_indicators:
            if re.search(indicator, text):
                try:
                    return self.call('ask_ai', original_text)
                except ValueError:
                    # If ask_ai is not available, continue to fallback
                    break
        
        # Fallback: if the text contains question marks or seems like a query, try AI
        if '?' in original_text or len(original_text.split()) > 2:
            try:
                return self.call('ask_ai', original_text)
            except ValueError:
                pass
        
        return f"Sorry, I couldn't understand the command: '{original_text}'. You can ask me questions or try specific commands like 'what time is it', 'tell a joke', or 'get weather'."
    
    def list_functions(self, category: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all registered functions, optionally filtered by category.
        
        Args:
            category: Filter by category (optional)
            
        Returns:
            Dictionary of function names and their metadata
        """
        if category:
            return {
                name: metadata for name, metadata in self.function_metadata.items()
                if metadata.get('category') == category
            }
        return self.function_metadata.copy()
    
    def get_help(self, function_name: Optional[str] = None) -> str:
        """
        Get help information for a function or all functions.
        
        Args:
            function_name: Specific function to get help for (optional)
            
        Returns:
            Help information as string
        """
        if function_name:
            actual_name = self.aliases.get(function_name, function_name)
            if actual_name in self.function_metadata:
                metadata = self.function_metadata[actual_name]
                return f"{actual_name}: {metadata['description']}"
            return f"Function '{function_name}' not found"
        
        # Return help for all functions
        help_text = "Available functions:\n"
        for name, metadata in self.function_metadata.items():
            help_text += f"  {name}: {metadata['description']}\n"
        return help_text
    
    def load_plugin(self, plugin_path: str) -> bool:
        """
        Load a plugin from file or package.
        
        Args:
            plugin_path: Path to plugin file or package name
            
        Returns:
            True if plugin loaded successfully, False otherwise
        """
        return self.plugin_loader.load_plugin(plugin_path)
    
    def speak(self, text: str) -> None:
        """
        Speak text using TTS if voice is enabled.
        
        Args:
            text: Text to speak
        """
        if self.voice_io:
            self.voice_io.speak(text)
    
    def listen(self) -> Optional[str]:
        """
        Listen for voice input if voice is enabled.
        
        Returns:
            Recognized text or None if voice not enabled
        """
        if self.voice_io:
            return self.voice_io.listen()
        return None
