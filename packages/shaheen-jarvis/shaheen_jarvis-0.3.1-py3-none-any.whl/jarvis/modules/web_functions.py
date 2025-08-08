"""
Web-related functions for Shaheen-Jarvis framework.
Includes web search, weather, news, Wikipedia, translation, currency conversion, etc.
"""

import os
import requests
import webbrowser
import wikipedia
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup


def search_web(query: str) -> str:
    """
    Search the web for a query.
    
    Args:
        query: Search query
        
    Returns:
        Search results or error message
    """
    # Try multiple search methods
    
    # Method 1: Try DuckDuckGo API (quick timeout)
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'pretty': '1',
            'no_redirect': '1'
        }
        
        response = requests.get(url, params=params, timeout=3)
        if response.status_code == 200:
            data = response.json()
            
            # Check for instant answer
            if data.get('AbstractText'):
                return f"Search result for '{query}':\n{data['AbstractText']}"
            
            # Check for definition
            if data.get('Definition'):
                return f"Definition of '{query}':\n{data['Definition']}"
            
            # Check for related topics
            if data.get('RelatedTopics'):
                topics = data['RelatedTopics'][:3]  # Get first 3 topics
                results = []
                for topic in topics:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append(topic['Text'])
                
                if results:
                    return f"Search results for '{query}':\n" + "\n".join(results)
    except:
        pass  # Try next method
    
    # Method 2: Try Wikipedia search as fallback
    try:
        wikipedia.set_lang("en")
        # Search Wikipedia for the query
        search_results = wikipedia.search(query, results=3)
        if search_results:
            try:
                # Get summary of first result
                summary = wikipedia.summary(search_results[0], sentences=2)
                return f"Search result for '{query}' (from Wikipedia):\n{summary}\n\nOther results: {', '.join(search_results[1:3]) if len(search_results) > 1 else 'None'}"
            except:
                return f"Search results for '{query}' (from Wikipedia):\n" + "\n".join(f"- {result}" for result in search_results[:3])
    except:
        pass  # Try next method
    
    # Method 3: Open browser search as final fallback
    try:
        import urllib.parse
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(search_url)
        return f"Opened web search for '{query}' in your browser. I couldn't get direct results due to connectivity issues, but your browser search should show results."
    except Exception as e:
        return f"Unable to search for '{query}'. Please try using your web browser directly. Error: {str(e)}"


def open_url(url: str) -> str:
    """
    Open a URL in the default web browser.
    
    Args:
        url: URL to open
        
    Returns:
        Success or error message
    """
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        webbrowser.open(url)
        return f"Opened {url} in your default browser"
    
    except Exception as e:
        return f"Error opening URL: {str(e)}"


def get_weather(city: str = "New York") -> str:
    """
    Get weather information for a city.
    
    Args:
        city: City name (default: New York)
        
    Returns:
        Weather information or error message
    """
    try:
        # Use OpenWeatherMap API if API key is available
        api_key = os.getenv('WEATHER_API_KEY')
        
        if api_key:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                description = data['weather'][0]['description']
                
                return f"Weather in {city}:\nTemperature: {temp}°C (feels like {feels_like}°C)\nConditions: {description.title()}\nHumidity: {humidity}%"
            else:
                return f"Could not get weather data for {city}"
        
        else:
            # Fallback: scrape weather from a public source
            return f"Weather API key not configured. Please set WEATHER_API_KEY environment variable to get detailed weather information for {city}."
    
    except Exception as e:
        return f"Error getting weather: {str(e)}"


def news_headlines(category: str = "general") -> str:
    """
    Get news headlines.
    
    Args:
        category: News category (general, business, entertainment, health, science, sports, technology)
        
    Returns:
        News headlines or error message
    """
    try:
        # Use NewsAPI if API key is available
        api_key = os.getenv('NEWS_API_KEY')
        
        if api_key:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'category': category,
                'country': 'us',
                'apiKey': api_key,
                'pageSize': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    headlines = []
                    for i, article in enumerate(articles[:5], 1):
                        headlines.append(f"{i}. {article['title']}")
                    
                    return f"Top {category} news headlines:\n" + "\n".join(headlines)
                else:
                    return f"No {category} news found"
            else:
                return "Could not fetch news headlines"
        
        else:
            return "News API key not configured. Please set NEWS_API_KEY environment variable to get news headlines."
    
    except Exception as e:
        return f"Error getting news: {str(e)}"


def wikipedia_summary(topic: str) -> str:
    """
    Get Wikipedia summary for a topic.
    
    Args:
        topic: Topic to search for
        
    Returns:
        Wikipedia summary or error message
    """
    try:
        # Set language to English
        wikipedia.set_lang("en")
        
        # Get summary (limit to 2 sentences)
        summary = wikipedia.summary(topic, sentences=2)
        
        # Get page URL
        page = wikipedia.page(topic)
        url = page.url
        
        return f"Wikipedia summary for '{topic}':\n{summary}\n\nRead more: {url}"
    
    except wikipedia.exceptions.DisambiguationError as e:
        # Handle disambiguation
        options = e.options[:5]  # Show first 5 options
        return f"Multiple results found for '{topic}'. Did you mean one of these?\n" + "\n".join(f"- {option}" for option in options)
    
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for '{topic}'"
    
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"


def translate_text(text: str, target_language: str = "es") -> str:
    """
    Translate text to another language (basic implementation).
    
    Args:
        text: Text to translate
        target_language: Target language code (es, fr, de, etc.)
        
    Returns:
        Translation or error message
    """
    try:
        # Use a free translation API
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': text,
            'langpair': f'en|{target_language}'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if data.get('responseStatus') == 200:
                translation = data['responseData']['translatedText']
                return f"Translation ({target_language}):\n{translation}"
            else:
                return "Translation service error"
        
        return "Could not connect to translation service"
    
    except Exception as e:
        return f"Error translating text: {str(e)}"


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert currency amounts.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code (USD, EUR, etc.)
        to_currency: Target currency code
        
    Returns:
        Conversion result or error message
    """
    try:
        # Use a free currency API
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            
            if to_currency.upper() in rates:
                rate = rates[to_currency.upper()]
                converted_amount = amount * rate
                
                return f"{amount} {from_currency.upper()} = {converted_amount:.2f} {to_currency.upper()}\nExchange rate: 1 {from_currency.upper()} = {rate:.4f} {to_currency.upper()}"
            else:
                return f"Currency '{to_currency}' not found"
        
        return "Could not get exchange rates"
    
    except Exception as e:
        return f"Error converting currency: {str(e)}"


def track_package(tracking_number: str, carrier: str = "auto") -> str:
    """
    Track a package (basic implementation).
    
    Args:
        tracking_number: Package tracking number
        carrier: Shipping carrier (auto, ups, fedex, usps)
        
    Returns:
        Tracking information or message
    """
    # This is a placeholder implementation
    # In a real application, you would integrate with carrier APIs
    
    return f"Package tracking for {tracking_number}:\nTo track your package, please visit the carrier's website directly:\n- UPS: https://www.ups.com/track\n- FedEx: https://www.fedex.com/apps/fedextrack/\n- USPS: https://tools.usps.com/go/TrackConfirmAction"


# For compatibility with the module loading system
__all__ = [
    "search_web",
    "open_url",
    "get_weather",
    "news_headlines",
    "wikipedia_summary",
    "translate_text",
    "convert_currency",
    "track_package"
]
