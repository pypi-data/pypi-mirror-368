#!/usr/bin/env python3
"""
Advanced example script demonstrating Shaheen-Jarvis framework with AI and weather features.
"""

from jarvis import Jarvis


def main():
    print("🚀 Shaheen-Jarvis Advanced Features Demo")
    print("=" * 45)
    
    # Initialize Jarvis
    print("Initializing Jarvis with AI and weather capabilities...")
    jarvis = Jarvis()
    print(f"✓ Jarvis initialized with {len(jarvis.functions)} functions\n")
    
    # Example 1: Weather functionality (requires WEATHER_API_KEY)
    print("1. Weather Information:")
    print("-" * 25)
    
    try:
        weather_result = jarvis.call('get_weather', 'New York')
        print(f"Weather in New York:\n{weather_result}")
        
        weather_result = jarvis.call('get_weather', 'London')
        print(f"\nWeather in London:\n{weather_result}")
        
        weather_result = jarvis.call('get_weather', 'Tokyo')
        print(f"\nWeather in Tokyo:\n{weather_result}")
    except Exception as e:
        print(f"Weather functionality error: {e}")
    
    print("\n" + "="*45)
    
    # Example 2: AI functionality (requires OPENROUTER_API_KEY)
    print("2. AI-Powered Functions:")
    print("-" * 26)
    
    try:
        # Ask AI a simple question
        ai_result = jarvis.call('ask_ai', 'What are the benefits of artificial intelligence?')
        print(f"AI Question: What are the benefits of artificial intelligence?")
        print(f"Answer: {ai_result}")
        
        print("\n" + "-"*26)
        
        # Generate code with AI
        code_request = "Create a Python function that calculates the factorial of a number"
        code_result = jarvis.call('generate_code', code_request)
        print(f"Code Generation Request: {code_request}")
        print(f"Generated Code:\n{code_result}")
        
        print("\n" + "-"*26)
        
        # Explain some code
        sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        explain_result = jarvis.call('explain_code', sample_code, 'python')
        print(f"Code Explanation Request:")
        print(f"Code: {sample_code}")
        print(f"Explanation:\n{explain_result}")
        
        print("\n" + "-"*26)
        
        # Summarize text
        long_text = """
        Artificial intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans. AI research has been highly successful in developing effective techniques for solving a wide range of problems, from game playing to medical diagnosis. The field includes machine learning, natural language processing, computer vision, robotics, and expert systems. Machine learning, a subset of AI, enables systems to automatically learn and improve from experience without being explicitly programmed. Deep learning, which uses neural networks with multiple layers, has been particularly successful in areas such as image recognition and natural language processing.
        """
        summary_result = jarvis.call('summarize_text', long_text, 2)
        print(f"Text Summarization:")
        print(f"Original text length: {len(long_text)} characters")
        print(f"Summary:\n{summary_result}")
        
    except Exception as e:
        print(f"AI functionality error: {e}")
    
    print("\n" + "="*45)
    
    # Example 3: Combined functionality demonstration
    print("3. Combined Natural Language + AI:")
    print("-" * 35)
    
    # Natural language weather queries
    weather_queries = [
        "what's the weather like today",
        "tell me about the weather",
        "weather information"
    ]
    
    for query in weather_queries:
        result = jarvis.dispatch(query)
        print(f"Query: '{query}'")
        print(f"Response: {result}")
        print()
    
    print("="*45)
    
    # Example 4: Show available AI functions
    print("4. Available AI Functions:")
    print("-" * 28)
    
    ai_functions = [name for name in jarvis.functions.keys() if any(ai_word in name.lower() for ai_word in ['ai', 'chat', 'explain', 'generate', 'summarize'])]
    
    for func_name in ai_functions:
        metadata = jarvis.function_metadata.get(func_name, {})
        description = metadata.get('description', 'No description available')
        print(f"• {func_name}: {description}")
    
    print("\n" + "="*45)
    
    # Example 5: Interactive demo
    print("5. Try some commands yourself!")
    print("-" * 32)
    print("Examples you can try in the CLI:")
    print("• python -m jarvis.cli")
    print("• Then type: get_weather London")
    print("• Or try: ask_ai \"Explain quantum computing\"")
    print("• Or: generate_code \"Sort a list in Python\"")
    print("• Or: summarize_text \"Your text here\"")
    
    print("\n" + "="*45)
    print("🎉 Advanced demo completed!")
    print("Your Jarvis framework now has:")
    print("• Weather information from OpenWeatherMap")
    print("• AI-powered responses via OpenRouter")
    print("• Natural language processing")
    print("• Code generation and explanation")
    print("• Text summarization")
    print("• And much more!")
    print("="*45)


if __name__ == '__main__':
    main()
