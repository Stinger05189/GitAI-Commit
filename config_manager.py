# config_manager.py
# Copyright (c) 2025 GitAI-Commit. All rights reserved.

"""
This module handles loading and saving application settings to a local JSON file.
"""

import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self):
        self.config_path = os.path.expanduser("~/.git-ai-commit-config.json")
        self.default_config = {
            "api_key": "",
            "selected_model": "mistralai/mistral-7b-instruct",
            "last_repo_path": os.getcwd(),
            "system_style": "Professional"
        }
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Loads config from disk or returns defaults if not found."""
        if not os.path.exists(self.config_path):
            return self.default_config.copy()
        
        try:
            with open(self.config_path, 'r') as f:
                saved_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**self.default_config, **saved_config}
        except (json.JSONDecodeError, IOError):
            return self.default_config.copy()

    def save_config(self, key: str, value: Any) -> None:
        """Updates a specific key and persists to disk."""
        self.config[key] = value
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get(self, key: str) -> Any:
        """Retrieves a value from the configuration."""
        return self.config.get(key, self.default_config.get(key))