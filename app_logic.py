# app_logic.py
# Copyright (c) 2025 GitAI-Commit. All rights reserved.

"""
The Controller module bridging the UI, Config, and Git logic.
"""

from git_utils import GitManager
from config_manager import ConfigManager

class AppLogic:
    def __init__(self):
        self.config = ConfigManager()
        
        # Initialize Git with the last used path
        initial_path = self.config.get("last_repo_path")
        self.git = GitManager(initial_path)

    def load_repo_data(self):
        """Fetches current state from git."""
        # Check if the path is still valid
        if not self.git.set_repo_path(self.git.repo_path):
            return {
                "error": "Invalid Repository",
                "files": [],
                "diff_len": 0
            }

        files = self.git.get_staged_files()
        diff = self.git.get_staged_diff()
        
        return {
            "files": files,
            "diff_text": diff,
            "history": self.git.get_recent_history(),
            "repo_name": self.git.repo_path
        }

    def save_setting(self, key: str, value: str):
        """Pass-through to config manager."""
        self.config.save_config(key, value)

    def update_repo_path(self, new_path: str) -> bool:
        """Updates git path and saves to config."""
        if self.git.set_repo_path(new_path):
            self.save_setting("last_repo_path", new_path)
            return True
        return False