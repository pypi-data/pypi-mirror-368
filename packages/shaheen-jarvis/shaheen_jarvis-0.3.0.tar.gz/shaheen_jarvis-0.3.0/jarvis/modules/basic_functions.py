"""
Basic functions for Shaheen-Jarvis framework.
Includes time, date, jokes, and quotes functionality.
"""

import datetime
import random
import requests
from typing import Optional


def tell_time() -> str:
    """Get the current time."""
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}"


def tell_date() -> str:
    """Get the current date."""
    today = datetime.date.today()
    return f"Today is {today.strftime('%A, %B %d, %Y')}"


def tell_joke() -> str:
    """Tell a random joke."""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "I told my wife she was drawing her eyebrows too high. She seemed surprised.",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "I'm reading a book about anti-gravity. It's impossible to put down!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a fake noodle? An impasta!",
        "How do you organize a space party? You planet!",
        "Why did the math book look so sad? Because it had too many problems!",
        "What do you call a sleeping bull? A bulldozer!",
        "Why did the coffee file a police report? It got mugged!"
    ]
    
    try:
        # Try to get a joke from an API
        response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=3)
        if response.status_code == 200:
            joke_data = response.json()
            return f"{joke_data['setup']} - {joke_data['punchline']}"
    except:
        pass
    
    return random.choice(jokes)


def get_random_quote() -> str:
    """Get a random inspirational quote."""
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Life is what happens to you while you're busy making other plans. - John Lennon",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "It is during our darkest moments that we must focus to see the light. - Aristotle",
        "The way to get started is to quit talking and begin doing. - Walt Disney",
        "Don't let yesterday take up too much of today. - Will Rogers",
        "You learn more from failure than from success. Don't let it stop you. - Unknown",
        "If you are working on something that you really care about, you don't have to be pushed. - Steve Jobs",
        "Experience is the teacher of all things. - Julius Caesar"
    ]
    
    try:
        # Try to get a quote from an API
        response = requests.get("https://api.quotegarden.io/api/v3/quotes/random", timeout=3)
        if response.status_code == 200:
            quote_data = response.json()
            if quote_data.get('statusCode') == 200:
                quote = quote_data['data']
                return f"{quote['quoteText']} - {quote['quoteAuthor']}"
    except:
        pass
    
    return random.choice(quotes)


def calculate_expression(expression: str) -> str:
    """
    Calculate a mathematical expression safely.
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        Result of the calculation or error message
    """
    try:
        # Basic security: only allow certain characters
        allowed_chars = set('0123456789+-*/().,e ')
        if not all(c in allowed_chars for c in expression.replace(' ', '')):
            return "Error: Invalid characters in expression"
        
        # Evaluate the expression
        result = eval(expression)
        return f"{expression} = {result}"
    
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {str(e)}"


# For compatibility with the module loading system
__all__ = [
    "tell_time",
    "tell_date", 
    "tell_joke",
    "get_random_quote",
    "calculate_expression"
]
