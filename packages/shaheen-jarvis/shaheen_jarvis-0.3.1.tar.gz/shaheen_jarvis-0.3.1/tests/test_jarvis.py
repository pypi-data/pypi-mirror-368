"""
Basic tests for Shaheen-Jarvis framework.
"""

import pytest
import sys
import os

# Add the parent directory to sys.path so we can import jarvis
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.jarvis_engine import Jarvis
from jarvis.core.config_manager import ConfigManager


def test_jarvis_initialization():
    """Test that Jarvis initializes correctly."""
    jarvis = Jarvis()
    assert jarvis is not None
    assert hasattr(jarvis, 'functions')
    assert hasattr(jarvis, 'aliases')
    assert hasattr(jarvis, 'config')


def test_function_registration():
    """Test function registration and calling."""
    jarvis = Jarvis()
    
    def test_func():
        return "Test function called"
    
    # Register function
    jarvis.register('test_func', test_func, description="A test function")
    
    # Check if function is registered
    assert 'test_func' in jarvis.functions
    assert 'test_func' in jarvis.function_metadata
    
    # Call function
    result = jarvis.call('test_func')
    assert result == "Test function called"


def test_function_aliases():
    """Test function aliases."""
    jarvis = Jarvis()
    
    def test_func():
        return "Test function called"
    
    # Register function with aliases
    jarvis.register('test_func', test_func, aliases=['tf', 'test'])
    
    # Check aliases
    assert 'tf' in jarvis.aliases
    assert 'test' in jarvis.aliases
    assert jarvis.aliases['tf'] == 'test_func'
    assert jarvis.aliases['test'] == 'test_func'
    
    # Call using alias
    result = jarvis.call('tf')
    assert result == "Test function called"


def test_config_manager():
    """Test configuration manager."""
    config = ConfigManager()
    
    # Test setting and getting values
    config.set('test.key', 'test_value')
    assert config.get('test.key') == 'test_value'
    
    # Test default values
    assert config.get('nonexistent.key', 'default') == 'default'


def test_basic_functions():
    """Test that basic functions are loaded."""
    jarvis = Jarvis()
    
    # Check if some basic functions are available
    expected_functions = ['tell_time', 'tell_date', 'tell_joke', 'get_random_quote']
    
    for func_name in expected_functions:
        if func_name in jarvis.functions:
            # Test calling the function
            result = jarvis.call(func_name)
            assert result is not None
            assert isinstance(result, str)


def test_natural_language_dispatch():
    """Test natural language command dispatch."""
    jarvis = Jarvis()
    
    # Test some natural language commands
    commands = [
        "what time",
        "tell me a joke",
        "what's the date"
    ]
    
    for command in commands:
        result = jarvis.dispatch(command)
        assert result is not None
        assert isinstance(result, str)


if __name__ == '__main__':
    # Run basic tests
    print("Running basic Jarvis tests...")
    
    try:
        test_jarvis_initialization()
        print("✓ Jarvis initialization test passed")
        
        test_function_registration()
        print("✓ Function registration test passed")
        
        test_function_aliases()
        print("✓ Function aliases test passed")
        
        test_config_manager()
        print("✓ Configuration manager test passed")
        
        test_basic_functions()
        print("✓ Basic functions test passed")
        
        test_natural_language_dispatch()
        print("✓ Natural language dispatch test passed")
        
        print("\nAll tests passed! 🎉")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
