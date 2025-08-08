"""
Command Line Interface for Shaheen-Jarvis framework.
Provides interactive mode, history, and color output.
"""

import sys
import os
import cmd
from typing import List, Optional
import argparse
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows
init(autoreset=True)

from .core.jarvis_engine import Shaheen_Jarvis


class JarvisCLI(cmd.Cmd):
    """Interactive command line interface for Jarvis."""
    
    intro = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                     {Fore.YELLOW}Shaheen-Jarvis v0.1.0{Fore.CYAN}                     ║
║                  {Fore.GREEN}Your AI Assistant Framework{Fore.CYAN}                   ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}Welcome to Jarvis! Type 'help' for available commands or 'functions' to see all functions.
Type 'quit' or 'exit' to leave.{Style.RESET_ALL}
"""
    
    prompt = f"{Fore.BLUE}jarvis> {Style.RESET_ALL}"
    
    def __init__(self, enable_voice: bool = False, config_path: Optional[str] = None):
        """
        Initialize CLI with Jarvis instance.
        
        Args:
            enable_voice: Whether to enable voice I/O
            config_path: Path to configuration file
        """
        super().__init__()
        self.jarvis = Shaheen_Jarvis(config_path=config_path, enable_voice=enable_voice)
        self.history: List[str] = []
        
        # Load command history if available
        self._load_history()
    
    def _load_history(self):
        """Load command history from file."""
        try:
            if os.path.exists('.jarvis_history'):
                with open('.jarvis_history', 'r', encoding='utf-8') as f:
                    self.history = [line.strip() for line in f.readlines()]
        except Exception:
            pass
    
    def _save_history(self):
        """Save command history to file."""
        try:
            with open('.jarvis_history', 'w', encoding='utf-8') as f:
                for command in self.history[-100:]:  # Keep last 100 commands
                    f.write(f"{command}\n")
        except Exception:
            pass
    
    def _add_to_history(self, command: str):
        """Add command to history."""
        if command and command not in ['help', 'history', 'quit', 'exit']:
            self.history.append(command)
            self._save_history()
    
    def _print_success(self, message: str):
        """Print success message in green."""
        print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")
    
    def _print_error(self, message: str):
        """Print error message in red."""
        print(f"{Fore.RED}{message}{Style.RESET_ALL}")
    
    def _print_info(self, message: str):
        """Print info message in cyan."""
        print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")
    
    def default(self, line: str):
        """Handle unknown commands by trying to dispatch them to Jarvis."""
        if not line.strip():
            return
        
        try:
            # First try as a function call
            if '(' in line and ')' in line:
                # Parse function call: function_name(args)
                func_name = line.split('(')[0].strip()
                if func_name in self.jarvis.functions:
                    result = self.jarvis.call(func_name)
                    if result:
                        self._print_success(str(result))
                    self._add_to_history(line)
                    return
            
            # Try as direct function name
            if line in self.jarvis.functions or line in self.jarvis.aliases:
                result = self.jarvis.call(line)
                if result:
                    self._print_success(str(result))
                self._add_to_history(line)
                return
            
            # Try natural language dispatch
            result = self.jarvis.dispatch(line)
            if result:
                self._print_info(str(result))
            self._add_to_history(line)
        
        except Exception as e:
            self._print_error(f"Error: {str(e)}")
    
    def do_functions(self, line: str):
        """List all available functions."""
        functions = self.jarvis.list_functions()
        
        if not functions:
            self._print_info("No functions registered.")
            return
        
        # Group by category
        categories = {}
        for name, metadata in functions.items():
            category = metadata.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append((name, metadata))
        
        print(f"\n{Fore.YELLOW}Available Functions:{Style.RESET_ALL}")
        for category, funcs in sorted(categories.items()):
            print(f"\n{Fore.MAGENTA}{category.title()}:{Style.RESET_ALL}")
            for name, metadata in sorted(funcs):
                description = metadata.get('description', 'No description')
                aliases = metadata.get('aliases', [])
                alias_text = f" (aliases: {', '.join(aliases)})" if aliases else ""
                print(f"  {Fore.CYAN}{name}{Style.RESET_ALL}{alias_text}")
                print(f"    {description}")
    
    def do_help_function(self, line: str):
        """Get help for a specific function. Usage: help_function <function_name>"""
        if not line:
            self._print_error("Usage: help_function <function_name>")
            return
        
        help_text = self.jarvis.get_help(line)
        self._print_info(help_text)
    
    def do_call(self, line: str):
        """Call a function directly. Usage: call <function_name> [args]"""
        if not line:
            self._print_error("Usage: call <function_name> [args]")
            return
        
        parts = line.split(' ', 1)
        func_name = parts[0]
        
        try:
            result = self.jarvis.call(func_name)
            if result:
                self._print_success(str(result))
        except Exception as e:
            self._print_error(f"Error calling {func_name}: {str(e)}")
    
    def do_plugins(self, line: str):
        """List loaded plugins."""
        plugins = self.jarvis.plugin_loader.list_plugins()
        
        if not plugins:
            self._print_info("No plugins loaded.")
            return
        
        print(f"\n{Fore.YELLOW}Loaded Plugins:{Style.RESET_ALL}")
        for name, metadata in plugins.items():
            version = metadata.get('version', 'Unknown')
            description = metadata.get('description', 'No description')
            print(f"  {Fore.CYAN}{name}{Style.RESET_ALL} v{version}")
            print(f"    {description}")
    
    def do_load_plugin(self, line: str):
        """Load a plugin. Usage: load_plugin <plugin_path>"""
        if not line:
            self._print_error("Usage: load_plugin <plugin_path>")
            return
        
        if self.jarvis.load_plugin(line):
            self._print_success(f"Plugin loaded successfully: {line}")
        else:
            self._print_error(f"Failed to load plugin: {line}")
    
    def do_config(self, line: str):
        """Show configuration or set config value. Usage: config [key] [value]"""
        parts = line.split(' ', 2)
        
        if not parts or not parts[0]:
            # Show all config
            config = self.jarvis.config.get_all()
            print(f"\n{Fore.YELLOW}Configuration:{Style.RESET_ALL}")
            self._print_dict(config)
        
        elif len(parts) == 1:
            # Show specific key
            value = self.jarvis.config.get(parts[0])
            print(f"{parts[0]}: {value}")
        
        elif len(parts) >= 2:
            # Set config value
            key, value = parts[0], ' '.join(parts[1:])
            self.jarvis.config.set(key, value)
            if self.jarvis.config.save():
                self._print_success(f"Configuration updated: {key} = {value}")
            else:
                self._print_error("Failed to save configuration")
    
    def _print_dict(self, data: dict, indent: int = 0):
        """Print dictionary with indentation."""
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{'  ' * indent}{Fore.CYAN}{key}:{Style.RESET_ALL}")
                self._print_dict(value, indent + 1)
            else:
                print(f"{'  ' * indent}{Fore.CYAN}{key}:{Style.RESET_ALL} {value}")
    
    def do_history(self, line: str):
        """Show command history."""
        if not self.history:
            self._print_info("No command history.")
            return
        
        print(f"\n{Fore.YELLOW}Command History:{Style.RESET_ALL}")
        for i, command in enumerate(self.history[-20:], 1):  # Show last 20 commands
            print(f"{i:2d}. {command}")
    
    def do_voice(self, line: str):
        """Toggle voice mode or speak text. Usage: voice [on|off|<text>]"""
        if not line:
            if self.jarvis.voice_io:
                self._print_info("Voice I/O is enabled")
            else:
                self._print_info("Voice I/O is disabled")
            return
        
        if line.lower() == 'on':
            if not self.jarvis.voice_io:
                from .core.voice_io import VoiceIO
                self.jarvis.voice_io = VoiceIO(self.jarvis.config)
                self._print_success("Voice I/O enabled")
            else:
                self._print_info("Voice I/O already enabled")
        
        elif line.lower() == 'off':
            self.jarvis.voice_io = None
            self._print_success("Voice I/O disabled")
        
        else:
            # Speak the text
            if self.jarvis.voice_io:
                self.jarvis.speak(line)
                self._print_success(f"Speaking: {line}")
            else:
                self._print_error("Voice I/O not enabled")
    
    def do_listen(self, line: str):
        """Listen for voice input."""
        if not self.jarvis.voice_io:
            self._print_error("Voice I/O not enabled. Use 'voice on' to enable.")
            return
        
        self._print_info("Listening for voice input...")
        text = self.jarvis.listen()
        
        if text:
            self._print_success(f"Heard: {text}")
            # Process the voice command
            self.onecmd(text)
        else:
            self._print_error("Could not understand voice input")
    
    def do_clear(self, line: str):
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.intro)
    
    def do_quit(self, line: str):
        """Exit Jarvis."""
        self._print_success("Goodbye!")
        return True
    
    def do_exit(self, line: str):
        """Exit Jarvis."""
        return self.do_quit(line)
    
    def do_EOF(self, line: str):
        """Handle Ctrl+D."""
        print()  # New line for better formatting
        return self.do_quit(line)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='Shaheen-Jarvis AI Assistant Framework')
    parser.add_argument('--voice', action='store_true', help='Enable voice I/O')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--command', '-c', type=str, help='Execute a single command and exit')
    parser.add_argument('--version', action='version', version='Shaheen-Jarvis 0.1.0')
    
    args = parser.parse_args()
    
    try:
        cli = JarvisCLI(enable_voice=args.voice, config_path=args.config)
        
        if args.command:
            # Execute single command
            cli.onecmd(args.command)
        else:
            # Start interactive mode
            cli.cmdloop()
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error starting Jarvis: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == '__main__':
    main()
