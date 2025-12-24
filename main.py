# main.py
# Copyright (c) 2025 GitAI-Commit. All rights reserved.

"""
The main entry point and GUI implementation using CustomTkinter.
"""


import threading
import customtkinter as ctk
import tkinter.filedialog as filedialog
from app_logic import AppLogic

# Theme Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class GitAICommitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.logic = AppLogic()

        # Window Setup
        self.title("AI Commit Generator")
        self.geometry("900x700")
        
        # Grid Layout: 2 Columns
        # Column 0: Sidebar (Settings/Controls), Column 1: Main Content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables mapped to UI
        self.var_api_key = ctk.StringVar(value=self.logic.config.get("api_key"))
        self.var_model = ctk.StringVar(value=self.logic.config.get("selected_model"))
        self.var_repo_path = ctk.StringVar(value=self.logic.config.get("last_repo_path"))
        
        self.create_sidebar()
        self.create_main_area()
        
        # Initial Data Load
        self.refresh_data()

    def create_sidebar(self):
        """Creates the left-hand configuration panel."""
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) # Spacer

        # App Title
        ctk.CTkLabel(self.sidebar_frame, text="GitAI Commit", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20)

        # API Key
        ctk.CTkLabel(self.sidebar_frame, text="OpenRouter API Key:", anchor="w").grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.entry_api = ctk.CTkEntry(self.sidebar_frame, textvariable=self.var_api_key, show="*")
        self.entry_api.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.entry_api.bind("<FocusOut>", lambda e: self.logic.save_setting("api_key", self.var_api_key.get()))

        # Model Selection
        ctk.CTkLabel(self.sidebar_frame, text="Model:", anchor="w").grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.option_model = ctk.CTkComboBox(
            self.sidebar_frame, 
            variable=self.var_model,
            values=[
                "mistralai/mistral-7b-instruct", 
                "openai/gpt-4o-mini", 
                "anthropic/claude-3-haiku", 
                "google/gemini-flash-1.5"
            ],
            command=lambda v: self.logic.save_setting("selected_model", v)
        )
        self.option_model.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="ew")

        # Repo Selection
        ctk.CTkLabel(self.sidebar_frame, text="Repository:", anchor="w").grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.btn_repo = ctk.CTkButton(self.sidebar_frame, text="Change Repo", command=self.browse_repo)
        self.btn_repo.grid(row=6, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # Path Display (Truncated)
        self.lbl_path = ctk.CTkLabel(self.sidebar_frame, textvariable=self.var_repo_path, font=("Arial", 10), text_color="gray")
        self.lbl_path.grid(row=7, column=0, padx=20, pady=0, sticky="ew")

        # Commit Button (Bottom of Sidebar)
        self.btn_commit = ctk.CTkButton(self.sidebar_frame, text="Commit Changes", fg_color="green", state="disabled")
        self.btn_commit.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

        # UPDATE: Connect command to self.on_commit_click
        self.btn_commit = ctk.CTkButton(self.sidebar_frame, text="Commit Changes", fg_color="green", state="disabled", command=self.on_commit_click)
        self.btn_commit.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

    def create_main_area(self):
        """Creates the right-hand content area."""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 1. Stats Header
        self.stats_frame = ctk.CTkFrame(self.main_frame, height=50)
        self.stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.lbl_files_count = ctk.CTkLabel(self.stats_frame, text="Files: 0", font=("Arial", 14, "bold"))
        self.lbl_files_count.pack(side="left", padx=15, pady=10)
        
        self.lbl_tokens = ctk.CTkLabel(self.stats_frame, text="Tokens: 0")
        self.lbl_tokens.pack(side="left", padx=15, pady=10)

        # NEW: Security Warning Label (Hidden by default)
        self.lbl_warning = ctk.CTkLabel(self.stats_frame, text="", text_color="#ff5555", font=("Arial", 12, "bold"))
        self.lbl_warning.pack(side="left", padx=15, pady=10)

        self.btn_refresh = ctk.CTkButton(self.stats_frame, text="Refresh", width=80, command=self.refresh_data)
        self.btn_refresh.pack(side="right", padx=10, pady=10)

        # 2. Context Hint Input
        self.entry_hint = ctk.CTkEntry(self.main_frame, placeholder_text="Optional: Context hint (e.g. 'Fixes login bug')...")
        self.entry_hint.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # 3. Output Textbox (Editable)
        self.txt_output = ctk.CTkTextbox(self.main_frame, font=("Consolas", 14))
        self.txt_output.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        
        # 4. Action Bar
        self.action_frame = ctk.CTkFrame(self.main_frame, height=50, fg_color="transparent")
        self.action_frame.grid(row=3, column=0, sticky="ew")
        
        self.btn_generate = ctk.CTkButton(self.action_frame, text="Generate Message", height=40, command=self.on_generate_click)
        self.btn_generate.pack(side="right")
        
        self.btn_copy = ctk.CTkButton(self.action_frame, text="Copy to Clipboard", height=40, fg_color="gray", command=self.copy_to_clipboard)
        self.btn_copy.pack(side="right", padx=10)

    def browse_repo(self):
        path = filedialog.askdirectory()
        if path:
            if self.logic.update_repo_path(path):
                self.var_repo_path.set(path)
                self.refresh_data()

    def refresh_data(self):
        data = self.logic.load_repo_data()
        
        if "error" in data:
            self.lbl_files_count.configure(text="Invalid Repo", text_color="red")
            self.txt_output.delete("0.0", "end")
            self.txt_output.insert("0.0", "Error: The selected folder is not a git repository.")
            return

        # Update Stats
        file_count = len(data["files"])
        self.lbl_files_count.configure(text=f"Files: {file_count}", text_color=("black", "white"))
        self.lbl_tokens.configure(text=f"Est. Tokens: ~{data['token_count']}")

        # Update Security Warning
        if data["warnings"]:
            warn_text = f"⚠️ SENSITIVE FILE: {data['warnings'][0]}"
            self.lbl_warning.configure(text=warn_text)
        else:
            self.lbl_warning.configure(text="")

        # Debug Preview (Updated to show what we filtered)
        preview = f"Repo: {data['repo_name']}\n"
        if data['lockfiles_excluded']:
            preview += f"Excluded Lockfiles: {data['lockfiles_excluded']}\n"
        
        preview += f"\n--- Diff Preview ({len(data['diff_text'])} chars) ---\n"
        
        preview += data['diff_text'][:5000] + ("..." if len(data['diff_text']) > 5000 else "")
        
        self.txt_output.delete("0.0", "end")
        self.txt_output.insert("0.0", preview)

    def on_generate_click(self):
        """UI Handler for generation button."""
        # Disable button to prevent double-click
        self.btn_generate.configure(state="disabled", text="Generating...")
        self.txt_output.delete("0.0", "end")
        self.txt_output.insert("0.0", "Thinking...")

        # Get inputs
        hint = self.entry_hint.get()
        model = self.var_model.get()

        self.logic.save_setting("selected_model", model)

        # Start thread
        thread = threading.Thread(target=self._run_generation_thread, args=(hint, model))
        thread.start()

    def on_commit_click(self):
        """Handler for the actual git commit action."""
        # 1. Get text from editable box
        message = self.txt_output.get("0.0", "end").strip()
        
        if not message:
            return

        # 2. Disable UI during operation
        self.btn_commit.configure(state="disabled", text="Committing...")
        
        # 3. Perform Commit (can be fast, but good to thread if hooks are slow)
        # For simplicity in this lightweight app, we run blocking, but wrapping in thread is safer for big repos.
        result = self.logic.finalize_commit(message)

        # 4. Handle Result
        if "main" in result or "master" in result or "[" in result: 
            # Git usually outputs "[branch sha] Message" on success
            self.txt_output.delete("0.0", "end")
            self.txt_output.insert("0.0", f"SUCCESS:\n{result}")
            
            # 5. Cleanup UI State
            self.entry_hint.delete(0, "end") # Clear the hint
            self.lbl_files_count.configure(text="Files: 0") # Reset count immediately visually
            
            # 6. Auto-refresh after 1.5 seconds to show clean state
            self.after(1500, self.refresh_data)
        else:
            # Likely an error (e.g. pre-commit hook failed)
            self.txt_output.delete("0.0", "end")
            self.txt_output.insert("0.0", f"ERROR / GIT OUTPUT:\n{result}")
        
        # Reset button
        self.btn_commit.configure(state="disabled", text="Commit Changes")

    def _run_generation_thread(self, hint, model):
        """Worker thread for API call."""
        result = self.logic.generate_commit_message(hint, model)
        # Schedule UI update on main thread
        self.after(0, lambda: self._finish_generation(result))

    def _finish_generation(self, result):
        """Called on main thread when API returns."""
        self.txt_output.delete("0.0", "end")
        self.txt_output.insert("0.0", result)
        
        # Re-enable button
        self.btn_generate.configure(state="normal", text="Generate Message")
        
        # Enable commit button if result is valid
        if not result.startswith("Error"):
            self.btn_commit.configure(state="normal")

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.txt_output.get("0.0", "end").strip())

if __name__ == "__main__":
    app = GitAICommitApp()
    app.mainloop()