"""
AI functions for Shaheen-Jarvis framework.
Includes OpenRouter API integration for AI responses.
"""

import os
import requests
import json
from typing import Optional, Dict, Any


def ask_ai(question: str, model: str = "openai/gpt-3.5-turbo") -> str:
    """
    Ask a question to an AI model via OpenRouter.
    
    Args:
        question: Question to ask the AI
        model: Model to use (default: openai/gpt-3.5-turbo)
        
    Returns:
        AI response or error message
    """
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            return "Error: OpenRouter API key not configured. Please set OPENROUTER_API_KEY environment variable."
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-username/shaheen-jarvis",
            "X-Title": "Shaheen-Jarvis Framework"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                ai_response = result['choices'][0]['message']['content']
                return f"AI Response:\n{ai_response.strip()}"
            else:
                return "Error: No response from AI model"
        else:
            error_info = response.json() if response.content else {}
            return f"Error: API request failed with status {response.status_code}: {error_info.get('error', {}).get('message', 'Unknown error')}"
    
    except requests.RequestException as e:
        return f"Error: Network request failed - {str(e)}"
    except Exception as e:
        return f"Error asking AI: {str(e)}"


def chat_with_ai(message: str, context: Optional[str] = None, model: str = "openai/gpt-3.5-turbo") -> str:
    """
    Have a conversation with AI, optionally with context.
    
    Args:
        message: Message to send to AI
        context: Optional context for the conversation
        model: Model to use
        
    Returns:
        AI response or error message
    """
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            return "Error: OpenRouter API key not configured. Please set OPENROUTER_API_KEY environment variable."
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-username/shaheen-jarvis",
            "X-Title": "Shaheen-Jarvis Framework"
        }
        
        messages = []
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Context: {context}"
            })
        
        messages.append({
            "role": "user", 
            "content": message
        })
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.8
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                ai_response = result['choices'][0]['message']['content']
                return f"AI Chat:\n{ai_response.strip()}"
            else:
                return "Error: No response from AI model"
        else:
            error_info = response.json() if response.content else {}
            return f"Error: API request failed with status {response.status_code}: {error_info.get('error', {}).get('message', 'Unknown error')}"
    
    except requests.RequestException as e:
        return f"Error: Network request failed - {str(e)}"
    except Exception as e:
        return f"Error chatting with AI: {str(e)}"


def explain_code(code: str, language: str = "python") -> str:
    """
    Ask AI to explain code.
    
    Args:
        code: Code to explain
        language: Programming language (default: python)
        
    Returns:
        AI explanation or error message
    """
    prompt = f"Please explain this {language} code:\n\n```{language}\n{code}\n```\n\nProvide a clear, detailed explanation of what this code does."
    
    return ask_ai(prompt)


def generate_code(description: str, language: str = "python") -> str:
    """
    Ask AI to generate code based on description.
    
    Args:
        description: Description of what the code should do
        language: Programming language (default: python)
        
    Returns:
        AI-generated code or error message
    """
    prompt = f"Generate {language} code for the following requirement:\n\n{description}\n\nPlease provide clean, well-commented code with explanations."
    
    return ask_ai(prompt)


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """
    Ask AI to summarize text.
    
    Args:
        text: Text to summarize
        max_sentences: Maximum sentences in summary
        
    Returns:
        AI summary or error message
    """
    prompt = f"Please summarize the following text in {max_sentences} sentences or less:\n\n{text}"
    
    return ask_ai(prompt)


def get_ai_models() -> str:
    """
    Get list of available AI models from OpenRouter.
    
    Returns:
        List of available models or error message
    """
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            return "Error: OpenRouter API key not configured."
        
        url = "https://openrouter.ai/api/v1/models"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            models = result.get('data', [])
            
            if models:
                model_list = []
                model_list.append("Available AI Models:")
                
                # Group by provider
                providers = {}
                for model in models[:20]:  # Show first 20 models
                    provider = model['id'].split('/')[0] if '/' in model['id'] else 'other'
                    if provider not in providers:
                        providers[provider] = []
                    providers[provider].append(model)
                
                for provider, provider_models in sorted(providers.items()):
                    model_list.append(f"\n{provider.title()}:")
                    for model in provider_models[:5]:  # Show first 5 models per provider
                        model_list.append(f"  - {model['id']}")
                        if model.get('description'):
                            model_list.append(f"    {model['description'][:100]}...")
                
                return "\n".join(model_list)
            else:
                return "No models found"
        else:
            return f"Error fetching models: Status {response.status_code}"
    
    except Exception as e:
        return f"Error getting AI models: {str(e)}"


def translate_with_ai(text: str, target_language: str) -> str:
    """
    Translate text using AI.
    
    Args:
        text: Text to translate
        target_language: Target language
        
    Returns:
        AI translation or error message
    """
    prompt = f"Translate the following text to {target_language}:\n\n{text}\n\nProvide only the translation, no explanations."
    
    return ask_ai(prompt)


# For compatibility with the module loading system
__all__ = [
    "ask_ai",
    "chat_with_ai", 
    "explain_code",
    "generate_code",
    "summarize_text",
    "get_ai_models",
    "translate_with_ai"
]
