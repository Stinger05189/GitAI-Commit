# git_utils.py
import tempfile # NEW IMPORT
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

    def get_staged_diff(self, exclude_files: List[str] = None) -> str:
        """
        Returns the diff. Supports excluding specific files via git pathspecs.
        Example: git diff --cached -- . ":!package-lock.json"
        """
        cmd = ["git", "diff", "--cached", "--", "."]
        
        if exclude_files:
            for file in exclude_files:
                # Git pathspec to exclude a file is ":!filename"
                cmd.append(f":!{file}")

        # specific join for list command
        full_cmd = " ".join(cmd)
        return self._run_command(full_cmd)

    def get_recent_history(self, n: int = 10) -> str:
        """Returns the last n commit messages for context."""
        return self._run_command(f'git log -n {n} --pretty=format:"%ad - %s"')

    def commit_with_message(self, message: str) -> str:
        """
        Commits staged changes using the provided message.
        Uses a temp file to handle special characters/newlines safely.
        """
        # Create a temporary file to store the commit message
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tf:
            tf.write(message)
            tf_path = tf.name

        try:
            # Use -F to read message from file
            # usage of shell=True in _run_command requires careful string handling,
            # so we manually construct the command string with the file path.
            cmd = f'git commit -F "{tf_path}"'
            result = self._run_command(cmd)
            return result
        finally:
            # Cleanup temp file
            if os.path.exists(tf_path):
                os.remove(tf_path)