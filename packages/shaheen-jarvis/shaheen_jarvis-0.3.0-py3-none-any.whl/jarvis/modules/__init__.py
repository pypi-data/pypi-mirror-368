"""Predefined modules for Shaheen-Jarvis framework."""

# Import all predefined functions with error handling
try:
    from .basic_functions import *
except ImportError as e:
    print(f"Warning: Could not import basic_functions: {e}")

try:
    from .web_functions import *
except ImportError as e:
    print(f"Warning: Could not import web_functions: {e}")

try:
    from .system_functions import *
except ImportError as e:
    print(f"Warning: Could not import system_functions: {e}")

try:
    from .utility_functions import *
except ImportError as e:
    print(f"Warning: Could not import utility_functions: {e}")

try:
    from .productivity_functions import *

except ImportError as e:
    print(f"Warning: Could not import productivity_functions: {e}")

try:
    from .ai_functions import *
except ImportError as e:
    print(f"Warning: Could not import ai_functions: {e}")

__all__ = [
    "tell_time", "tell_date", "tell_joke", "get_random_quote", "calculate_expression",
    # Web functions  
    "search_web", "open_url", "get_weather", "news_headlines", 
    "wikipedia_summary", "translate_text", "convert_currency", "track_package",
    # System functions
    "system_info", "get_ip_address", "run_shell_command", "get_network_info", "get_process_info",
    # Utility functions
    "generate_password", "note_something", "recall_note", "hash_text", 
    "encode_decode_base64", "generate_uuid", "word_count", "list_notes_categories",
    # Productivity functions
    "send_email", "play_music", "set_alarm", "create_todo", "show_todos",
    # AI functions
    "ask_ai", "chat_with_ai", "explain_code", "generate_code", "summarize_text", "get_ai_models", "translate_with_ai"
]
