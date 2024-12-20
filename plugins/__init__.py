# plugins/__init__.py
import os
import importlib
import json

def load_plugins(app):
    plugins_dir = os.path.dirname(__file__)
    for folder in os.listdir(plugins_dir):
        plugin_path = os.path.join(plugins_dir, folder)
        if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, "__init__.py")):
            try:
                module = importlib.import_module(f"plugins.{folder}")
                if hasattr(module, "initialize"):
                    module.initialize(app)
                    print(f"Loaded plugin: {folder}")
                else:
                    print(f"Skipped {folder}: No 'initialize' function found.")
            except Exception as e:
                print(f"Failed to load plugin {folder}: {e}")