"""
Plugin Loader for Shaheen-Jarvis framework.
Handles loading plugins from local paths or packages.
"""

import os
import sys
import importlib
import importlib.util
from typing import Optional, List, Dict, Any
import logging


class PluginLoader:
    """Handles loading and managing plugins for Jarvis."""
    
    def __init__(self, jarvis_instance):
        """
        Initialize plugin loader.
        
        Args:
            jarvis_instance: Reference to the main Jarvis instance
        """
        self.jarvis = jarvis_instance
        self.loaded_plugins: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    def load_plugin(self, plugin_path: str) -> bool:
        """
        Load a plugin from file path or package name.
        
        Args:
            plugin_path: Path to plugin file or package name
            
        Returns:
            True if plugin loaded successfully, False otherwise
        """
        try:
            if os.path.isfile(plugin_path) and plugin_path.endswith('.py'):
                return self._load_plugin_from_file(plugin_path)
            else:
                return self._load_plugin_from_package(plugin_path)
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_path}: {e}")
            return False
    
    def _load_plugin_from_file(self, file_path: str) -> bool:
        """
        Load plugin from a Python file.
        
        Args:
            file_path: Path to the plugin Python file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            plugin_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Load module from file
            spec = importlib.util.spec_from_file_location(plugin_name, file_path)
            if spec is None or spec.loader is None:
                self.logger.error(f"Could not load spec for plugin {file_path}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return self._initialize_plugin(plugin_name, module)
        
        except Exception as e:
            self.logger.error(f"Error loading plugin from file {file_path}: {e}")
            return False
    
    def _load_plugin_from_package(self, package_name: str) -> bool:
        """
        Load plugin from an installed package.
        
        Args:
            package_name: Name of the package to load
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            module = importlib.import_module(package_name)
            return self._initialize_plugin(package_name, module)
        
        except ImportError as e:
            self.logger.error(f"Could not import package {package_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading plugin from package {package_name}: {e}")
            return False
    
    def _initialize_plugin(self, plugin_name: str, module) -> bool:
        """
        Initialize a loaded plugin module.
        
        Args:
            plugin_name: Name of the plugin
            module: The loaded module
            
        Returns:
            True if initialized successfully, False otherwise
        """
        try:
            # Check if plugin has required structure
            if not hasattr(module, 'init'):
                self.logger.error(f"Plugin {plugin_name} missing 'init' function")
                return False
            
            # Get plugin metadata if available
            metadata = getattr(module, 'metadata', {
                'name': plugin_name,
                'version': '1.0.0',
                'description': 'No description available'
            })
            
            # Initialize plugin
            module.init(self.jarvis)
            
            # Store plugin reference
            self.loaded_plugins[plugin_name] = {
                'module': module,
                'metadata': metadata
            }
            
            self.logger.info(f"Successfully loaded plugin: {plugin_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error initializing plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            True if unloaded successfully, False otherwise
        """
        if plugin_name not in self.loaded_plugins:
            self.logger.warning(f"Plugin {plugin_name} not found")
            return False
        
        try:
            plugin_info = self.loaded_plugins[plugin_name]
            module = plugin_info['module']
            
            # Call cleanup function if available
            if hasattr(module, 'cleanup'):
                module.cleanup(self.jarvis)
            
            # Remove plugin
            del self.loaded_plugins[plugin_name]
            
            self.logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """
        List all loaded plugins.
        
        Returns:
            Dictionary of plugin names and their metadata
        """
        return {
            name: info['metadata'] 
            for name, info in self.loaded_plugins.items()
        }
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin metadata or None if not found
        """
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]['metadata']
        return None
    
    def load_plugins_from_directory(self, directory: str) -> List[str]:
        """
        Load all plugins from a directory.
        
        Args:
            directory: Directory path containing plugin files
            
        Returns:
            List of successfully loaded plugin names
        """
        loaded = []
        
        if not os.path.isdir(directory):
            self.logger.warning(f"Plugin directory not found: {directory}")
            return loaded
        
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_path = os.path.join(directory, filename)
                plugin_name = os.path.splitext(filename)[0]
                
                if self.load_plugin(plugin_path):
                    loaded.append(plugin_name)
        
        self.logger.info(f"Loaded {len(loaded)} plugins from {directory}")
        return loaded
    
    def auto_load_plugins(self) -> None:
        """
        Auto-load plugins specified in configuration.
        """
        # Load from configured directories
        plugin_dirs = self.jarvis.config.get('plugins.plugin_directories', [])
        for directory in plugin_dirs:
            self.load_plugins_from_directory(directory)
        
        # Load specific plugins
        auto_load = self.jarvis.config.get('plugins.auto_load', [])
        for plugin in auto_load:
            self.load_plugin(plugin)
