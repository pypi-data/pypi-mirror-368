"""
Shaheen-Jarvis Framework
A modular, extensible Python assistant framework.
"""

__version__ = "0.1.0"
__author__ = "Engr. Hamza"

from .core.jarvis_engine import Shaheen_Jarvis

# Backward compatibility
Jarvis = Shaheen_Jarvis

__all__ = ["Shaheen_Jarvis", "Jarvis"]
