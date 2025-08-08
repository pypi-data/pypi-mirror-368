"""Core components of Shaheen-Jarvis framework."""

from .jarvis_engine import Shaheen_Jarvis
from .config_manager import ConfigManager
from .plugin_loader import PluginLoader
from .voice_io import VoiceIO

# Backward compatibility
Jarvis = Shaheen_Jarvis

__all__ = ["Shaheen_Jarvis", "Jarvis", "ConfigManager", "PluginLoader", "VoiceIO"]
