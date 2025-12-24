# git_utils.py
# Copyright (c) 2025 GitAI-Commit. All rights reserved.

"""
This module handles all subprocess interactions with the git client.
"""

import subprocess
import os
from typing import List

class GitManager:
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or os.getcwd()

    def set_repo_path(self, path: str) -> bool:
        """Sets the working directory and verifies it is a git repo."""
        if os.path.isdir(path) and os.path.exists(os.path.join(path, ".git")):
            self.repo_path = path
            return True
        return False

    def _run_command(self, command: str) -> str:
        """Runs a shell command in the repo context and returns output."""
        try:
            result = subprocess.check_output(
                command, 
                shell=True, 
                cwd=self.repo_path, 
                stderr=subprocess.STDOUT
            )
            return result.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return ""

    def get_staged_files(self) -> List[str]:
        """Returns a list of filenames currently staged for commit."""
        output = self._run_command("git diff --cached --name-only")
        if not output:
            return []
        return output.splitlines()

    def get_staged_diff(self) -> str:
        """Returns the full raw diff of staged changes."""
        return self._run_command("git diff --cached")

    def get_recent_history(self, n: int = 10) -> str:
        """Returns the last n commit messages for context."""
        return self._run_command(f'git log -n {n} --pretty=format:"%ad - %s"')