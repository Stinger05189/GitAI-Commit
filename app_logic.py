# app_logic.py
# Copyright (c) 2025 GitAI-Commit. All rights reserved.

"""
The Controller module bridging the UI, Config, and Git logic.
"""

import re
import tiktoken
from typing import List, Dict, Any
from openai import OpenAI  # NEW IMPORT
from git_utils import GitManager
from config_manager import ConfigManager

class AppLogic:
    def __init__(self):
        self.config = ConfigManager()
        
        # Initialize Git with the last used path
        initial_path = self.config.get("last_repo_path")
        self.git = GitManager(initial_path)

        # Definitions
        self.lockfiles = {
            "package-lock.json", "yarn.lock", "pnpm-lock.yaml", 
            "Cargo.lock", "go.sum", "composer.lock", "Gemfile.lock"
        }
        
        # Regex for sensitive files
        self.sensitive_patterns = [
            r"\.env.*",           # Environment files
            r".*_rsa$",           # Private keys
            r".*\.pem$",          # Certificates
            r"config\.js$",       # Often contains keys in older projects
            r"secrets\..*"        # Explicit secret files
        ]

    def load_repo_data(self) -> Dict[str, Any]:
        """Fetches current state, filters noise, and checks security."""
        if not self.git.set_repo_path(self.git.repo_path):
            return {"error": "Invalid Repository"}

        # 1. Get List of Files
        all_files = self.git.get_staged_files()

        # 2. Identify Lockfiles & Security Risks
        found_lockfiles = [f for f in all_files if f in self.lockfiles]
        security_warnings = self._scan_for_secrets(all_files)

        # 3. Get Smart Diff (Excluding lockfiles to save tokens)
        diff_text = self.git.get_staged_diff(exclude_files=found_lockfiles)
        
        # 4. Fallback: If diff is massive (> 12k chars), use stat only
        if len(diff_text) > 12000:
            diff_text = "(Diff too large. Using summary.)\n" + self.git._run_command("git diff --cached --stat")

        # 5. Calculate Tokens (Simulated Prompt)
        # We estimate based on a theoretical prompt structure to be safe
        est_prompt = f"{diff_text}\n{str(all_files)}\n{self.git.get_recent_history()}"
        token_count = self._count_tokens(est_prompt)

        return {
            "files": all_files,
            "diff_text": diff_text,
            "history": self.git.get_recent_history(),
            "repo_name": self.git.repo_path,
            "token_count": token_count,
            "warnings": security_warnings,
            "lockfiles_excluded": found_lockfiles
        }

    def _scan_for_secrets(self, file_list: List[str]) -> List[str]:
        warnings = []
        for filename in file_list:
            for pattern in self.sensitive_patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    warnings.append(filename)
                    break
        return warnings

    def _count_tokens(self, text: str) -> int:
        try:
            # cl100k_base is used by GPT-3.5/4/Mistral
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            return 0

    def generate_commit_message(self, hint: str, model: str) -> str:
        """Constructs prompt and calls OpenRouter API."""
        
        # 1. Validation
        api_key = self.config.get("api_key")
        if not api_key:
            return "Error: API Key is missing. Please add it in the settings."

        # 2. Refresh data
        data = self.load_repo_data()
        if "error" in data:
            return f"Error: {data['error']}"
        
        if not data["diff_text"]:
            return "Error: No staged changes to commit."

        # 3. Construct Prompts (IMPROVED)
        system_prompt = (
            "You are a senior developer and git expert. You write commit messages that strictly adhere to the 'Conventional Commits' specification.\n\n"
            "## RULES\n"
            "1. **Header Format**: <type>(<scope>): <subject>\n"
            "   - Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.\n"
            "   - Scope: Optional, based on file names/modules (e.g., 'auth', 'ui', 'api').\n"
            "   - Subject: Imperative mood ('add' not 'added'), lowercase, max 50 chars, no period.\n"
            "2. **Body**:\n"
            "   - Required for non-trivial changes.\n"
            "   - Wrap lines strictly at 72 characters.\n"
            "   - Use bullet points (-) for listing specific changes.\n"
            "   - Focus on the 'why' and 'what', not just code translation.\n"
            "3. **Output**:\n"
            "   - Return ONLY the raw message. No Markdown code blocks (```). No conversational filler.\n"
        )

        user_content = (
            f"## CONTEXT HINT (User Intent - Priority High)\n{hint if hint else 'None'}\n\n"
            f"## RECENT HISTORY (For style consistency)\n{data['history']}\n\n"
            f"## STAGED FILE LIST\n{str(data['files'])}\n\n"
            f"## CODE DIFF\n{data['diff_text']}"
        )

        # 4. API Call
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
            )
            
            raw_msg = response.choices[0].message.content.strip()
            return self._clean_output(raw_msg)

        except Exception as e:
            return f"API Error: {str(e)}"

    def _clean_output(self, text: str) -> str:
        """Removes quotes and markdown wrappers often added by LLMs."""
        # Remove surrounding quotes if present
        text = text.strip('"\'')
        # Remove markdown code blocks
        text = text.replace("```git commit", "").replace("```", "").strip()
        return text

    def save_setting(self, key: str, value: str):
        """Pass-through to config manager."""
        self.config.save_config(key, value)

    def update_repo_path(self, new_path: str) -> bool:
        """Updates git path and saves to config."""
        if self.git.set_repo_path(new_path):
            self.save_setting("last_repo_path", new_path)
            return True
        return False

    def finalize_commit(self, message: str) -> str:
        """Executes the commit and returns the git output."""
        if not message.strip():
            return "Error: Commit message is empty."
        
        return self.git.commit_with_message(message)