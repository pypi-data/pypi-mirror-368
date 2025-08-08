"""
Sample plugin for Shaheen-Jarvis framework.
Demonstrates how to create plugins with custom functions.
"""

# Plugin metadata (optional but recommended)
metadata = {
    'name': 'Sample Plugin',
    'version': '1.0.0',
    'description': 'A sample plugin demonstrating plugin functionality',
    'author': 'Jarvis Framework'
}


def hello_plugin(name: str = "World") -> str:
    """
    A sample function that says hello.
    
    Args:
        name: Name to greet (default: World)
        
    Returns:
        Greeting message
    """
    return f"Hello from the sample plugin, {name}!"


def plugin_info() -> str:
    """Get information about this plugin."""
    return f"Plugin: {metadata['name']} v{metadata['version']}\nDescription: {metadata['description']}"


def multiply_numbers(a: float, b: float) -> str:
    """
    Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Multiplication result
    """
    result = a * b
    return f"{a} × {b} = {result}"


def init(jarvis):
    """
    Initialize the plugin by registering functions with Jarvis.
    This function is required for all plugins.
    
    Args:
        jarvis: The Jarvis instance
    """
    # Register plugin functions
    jarvis.register(
        'hello_plugin', 
        hello_plugin,
        aliases=['hello', 'greet'],
        description="Say hello from the sample plugin",
        category="plugin_demo"
    )
    
    jarvis.register(
        'plugin_info',
        plugin_info,
        description="Get information about the sample plugin",
        category="plugin_demo"
    )
    
    jarvis.register(
        'multiply_numbers',
        multiply_numbers,
        aliases=['multiply', 'mult'],
        description="Multiply two numbers together",
        category="plugin_demo"
    )
    
    print(f"Sample plugin loaded: {metadata['name']} v{metadata['version']}")


def cleanup(jarvis):
    """
    Cleanup function called when plugin is unloaded (optional).
    
    Args:
        jarvis: The Jarvis instance
    """
    # Unregister functions
    jarvis.unregister('hello_plugin')
    jarvis.unregister('plugin_info')
    jarvis.unregister('multiply_numbers')
    
    print(f"Sample plugin unloaded: {metadata['name']}")
