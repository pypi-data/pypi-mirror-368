# 🤖 Shaheen-Jarvis Framework

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Voice Enabled](https://img.shields.io/badge/Voice-Enabled-orange)]()
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple)]()

## 🚀 Overview

Shaheen-Jarvis is a **powerful, modular, voice-enabled AI assistant framework** built in Python. It combines traditional programmatic functions with modern AI capabilities, featuring comprehensive speech recognition, natural language processing, and extensive API integrations.

### ✨ Key Features

- 🎤 **Advanced Speech Recognition** - Full voice command support with Google Speech Recognition
- 🧠 **AI-Powered Responses** - Intelligent conversations and code generation
- 🌐 **Web Integration** - Weather, news, Wikipedia, and web search capabilities
- 🎵 **Multimedia Control** - YouTube music playback and app launching
- 📝 **Productivity Tools** - Notes, tasks, calculations, and system monitoring
- 🔧 **Extensible Plugin System** - Easy to extend with custom functionality
- 🎨 **Rich CLI Interface** - Beautiful colored output and interactive commands

## 📦 Installation

### Quick Install from PyPI
```bash
pip install shaheen-jarvis
```



## 🚀 Quick Start

### 🎤 Voice-Controlled Usage (Recommended)

```python
from jarvis import Shaheen_Jarvis

# Initialize with voice enabled
jarvis = Shaheen_Jarvis(enable_voice=True)

# Start interactive voice session
while True:
    command = jarvis.listen()  # Listen for voice input
    if command:
        response = jarvis.dispatch(command)  # Process command
        print(f"Jarvis: {response}")
        jarvis.speak(response)  # Speak the response
```

### 💻 CLI Usage

```bash
# Basic commands
jarvis time
jarvis weather "New York"
jarvis joke

# Interactive mode
jarvis --interactive

# Voice mode
jarvis --voice
```

### 🐍 Python Script Usage

```python
from jarvis import Shaheen_Jarvis

# Initialize Jarvis
jarvis = Shaheen_Jarvis()

# Basic functions
print(jarvis.call("tell_time"))
print(jarvis.call("tell_joke"))
print(jarvis.call("get_weather", "London"))

# AI-powered functions
print(jarvis.call("ask_ai", "What is quantum computing?"))
print(jarvis.call("generate_code", "Python function to sort a list"))

# Natural language dispatch
response = jarvis.dispatch("What's the weather like today?")
print(response)
```

## 🎤 Voice Commands

Shaheen-Jarvis supports comprehensive voice recognition. Here are example commands you can speak:

### ⏰ Time & Date
- "What time is it?"
- "What's the date today?"
- "Tell me the current time"

### 🌦️ Weather
- "What's the weather?"
- "Weather in London"
- "Tell me the weather in Paris"

### 🎵 Entertainment
- "Tell me a joke"
- "Play Adele songs on YouTube"
- "Open WhatsApp"
- "Random quote"

### 🔍 Search & Information
- "Wikipedia artificial intelligence"
- "Search web for latest technology"
- "What is quantum computing?"
- "Tell me about machine learning"

### 🧮 Mathematics
- "Calculate 25 plus 17"
- "What is 100 divided by 4?"
- "Compute 15 times 8"

### 📝 Productivity
- "Note buy groceries tomorrow"
- "Remember to call mom"
- "Show my tasks"
- "Create todo finish project"

### 🔧 System & Tools
- "Generate a password"
- "Get system info"
- "Get my IP address"
- "System information"

### 🤖 AI Features
- "Ask AI about Python programming"
- "Generate code for a sorting algorithm"
- "Explain neural networks"
- "What is blockchain?"

## Features

- **Core Engine**: Function registration, alias support, and dynamic dispatch
- **Predefined Functions**: Time, date, jokes, email sending, weather updates, etc.
- **Plugin Support**: Load plugins from local paths
- **Voice I/O**: Speech recognition and text-to-speech capabilities
- **Intuitive CLI**: Interactive mode, history, and color output
- **AI Integration**: OpenRouter API for AI-driven capabilities
- **Web Functions**: Weather, news, translation, and web search with fallbacks
- **System Utilities**: System info, CPU usage, RAM status, network information
- **Productivity Tools**: Notes, to-do lists, alarms, email functions with voice

## ⚙️ Configuration

Configuration is managed through a YAML file (`jarvis_config.yaml`) and environment variables. Here's a sample:

```yaml
debug: false
api_keys:
  news_api_key: ${NEWS_API_KEY}
  openai_api_key: ${OPENAI_API_KEY}
  weather_api_key: ${WEATHER_API_KEY}
voice:
  enable_voice: true
  stt_backend: whisper
  tts_backend: pyttsx3
logging:
  level: 'INFO'
  log_to_file: true
```

Make sure to set all environment variables correctly. See `.env.sample` for reference.

## 🎯 Examples

### Comprehensive Interactive Test

To test every feature through voice commands:
```bash
python interactive_voice_test.py
```

### Advanced Use

For voice-controlled commands and more complex AI interactions:
```bash
python example_advanced.py
python example_voice.py
```

## 🤝 Contribution

Please check the [GitHub repository](https://github.com/yourusername/shaheen-jarvis) for contributions and feature requests. Feel free to open issues or pull requests!

---

### © 2025 Shaheen-Jarvis
Licensed under the MIT License.

---
