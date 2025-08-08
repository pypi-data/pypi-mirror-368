#!/usr/bin/env python3
"""
Example script demonstrating Shaheen-Jarvis framework usage.
"""

from jarvis import Shaheen_Jarvis


def main():
    print("🤖 Shaheen-Jarvis Framework Example")
    print("=" * 40)
    
    # Initialize Jarvis
    print("Initializing Jarvis...")
    jarvis = Shaheen_Jarvis()
    print(f"✓ Jarvis initialized with {len(jarvis.functions)} functions\n")
    
    # Example 1: Call basic functions
    print("1. Basic Functions:")
    print("-" * 20)
    
    # Get current time
    time_result = jarvis.call('tell_time')
    print(f"Current time: {time_result}")
    
    # Get current date  
    date_result = jarvis.call('tell_date')
    print(f"Current date: {date_result}")
    
    # Tell a joke
    joke_result = jarvis.call('tell_joke')
    print(f"Joke: {joke_result}")
    print()
    
    # Example 2: Natural language processing
    print("2. Natural Language Commands:")
    print("-" * 30)
    
    commands = [
        "what time is it",
        "tell me a joke", 
        "what's the date today",
        "generate a password"
    ]
    
    for command in commands:
        result = jarvis.dispatch(command)
        print(f"Command: '{command}'")
        print(f"Response: {result}")
        print()
    
    # Example 3: Register custom function
    print("3. Custom Function Registration:")
    print("-" * 35)
    
    def custom_greeting(name="Friend"):
        return f"Hello {name}! Welcome to Jarvis!"
    
    # Register the custom function
    jarvis.register(
        'custom_greeting',
        custom_greeting,
        aliases=['greet', 'hello'],
        description='A custom greeting function',
        category='custom'
    )
    
    # Call the custom function
    greeting_result = jarvis.call('custom_greeting', 'Alice')
    print(f"Custom function result: {greeting_result}")
    
    # Call using alias
    alias_result = jarvis.call('greet', 'Bob')
    print(f"Using alias 'greet': {alias_result}")
    print()
    
    # Example 4: Utility functions
    print("4. Utility Functions:")
    print("-" * 22)
    
    # Generate password
    password_result = jarvis.call('generate_password', 16, True)
    print(f"Generated password: {password_result}")
    
    # Calculate expression
    calc_result = jarvis.call('calculate_expression', '2 + 3 * 4')
    print(f"Calculation: {calc_result}")
    
    # Take a note
    note_result = jarvis.call('note_something', 'Example note from demo script', 'demo')
    print(f"Note saved: {note_result}")
    print()
    
    # Example 5: List available functions
    print("5. Available Functions by Category:")
    print("-" * 37)
    
    functions = jarvis.list_functions()
    categories = {}
    
    for name, metadata in functions.items():
        category = metadata.get('category', 'general')
        if category not in categories:
            categories[category] = []
        categories[category].append(name)
    
    for category, funcs in sorted(categories.items()):
        print(f"\n{category.title()} ({len(funcs)} functions):")
        for func in sorted(funcs)[:5]:  # Show first 5 functions in each category
            print(f"  - {func}")
        if len(funcs) > 5:
            print(f"  ... and {len(funcs) - 5} more")
    
    print("\n" + "=" * 40)
    print("Example completed! Try running the CLI with:")
    print("python -m jarvis.cli")
    print("=" * 40)


if __name__ == '__main__':
    main()
