# GitAI-Commit

**GitAI-Commit** is a lightweight, modern desktop GUI application that automates the generation of semantic, Conventional Commit messages using Large Language Models (LLMs) via the OpenRouter API.

It analyzes your staged git changes, filters out noise (like lockfiles), scans for security risks (secrets), and prompts an AI to write a professional commit message for you.

## ✨ Features

*   **GUI Interface:** Clean, dark-mode interface built with `customtkinter`.
*   **Model Agnostic:** Works with any model on OpenRouter (GPT-4o, Claude 3.5 Sonnet, Mistral, Llama 3, etc.).
*   **Smart Context:** automatically reads `git diff`, staged files, and recent commit history to match your project's style.
*   **Token Optimization:** automatically filters out massive lockfiles (`package-lock.json`, `yarn.lock`) to save API costs.
*   **Security Guardrails:** warns you if you attempt to stage sensitive files like `.env` or private keys.
*   **Workflow Tools:** "Stage All" button, editable output preview, and direct "Commit" action.

---

## 🛠️ Installation (Running from Source)

### Prerequisites
*   Python 3.10 or higher.
*   Git installed and available in your system PATH.
*   An API Key from [OpenRouter](https://openrouter.ai/).

### 1. Clone & Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/git-ai-commit.git
cd git-ai-commit

# Create a virtual environment
python -m venv .venv

# Activate the environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install customtkinter openai tiktoken pyinstaller
```

### 3. Run the App
```bash
python main.py
```

---

## 📦 Building a Standalone Executable (.exe)

You can package the application into a single `.exe` file to run on computers without Python installed.

### 1. Prepare the Icon (Optional)
Ensure you have `app_icon.ico` in the root directory.

### 2. Run PyInstaller
Run the following command in your terminal (with the `.venv` activated):

```powershell
pyinstaller --noconsole --onefile --name "GitAI-Commit" --icon="app_icon.ico" --add-data "app_icon.ico;." --collect-all customtkinter --collect-all tiktoken main.py
```

*Note: On Linux/Mac, replace the semicolon `;` in `--add-data` with a colon `:`.*

### 3. Locate the App
The executable will be generated in the **`dist/`** folder.

---

## 🚀 Usage Guide

1.  **Open the App:** Run the `.exe` or `python main.py`.
2.  **Configuration:**
    *   Enter your **OpenRouter API Key** in the sidebar.
    *   Select or type your desired **Model** (e.g., `mistralai/mistral-7b-instruct` for speed, `anthropic/claude-3-haiku` for logic).
    *   These settings are saved automatically to `~/.git-ai-commit-config.json`.
3.  **Select Repository:** If the app isn't already pointing to your repo, click "Change Repo".
4.  **Stage Files:**
    *   Click **Stage All** in the app, or use `git add .` in your terminal.
    *   *Note: The app only looks at staged changes.*
5.  **Generate:**
    *   (Optional) Add a "Context Hint" if the change is complex (e.g., "Fixes login bug #402").
    *   Click **Generate Message**.
6.  **Commit:**
    *   Review the generated message in the text box. Edit it if necessary.
    *   Click **Commit Changes**.

---

## 📂 Project Structure

*   **`main.py`**: The GUI entry point and UI layout logic.
*   **`app_logic.py`**: The controller. Handles data processing, API calls, and security checks.
*   **`git_utils.py`**: Handles low-level subprocess calls to the Git executable.
*   **`config_manager.py`**: Handles loading/saving user settings to JSON.
*   **`app_icon.svg/ico`**: Application assets.

---

## ⚠️ Troubleshooting

**"Error: No staged changes to commit"**
The AI needs to know *what* you want to commit. You must stage files first. Use the **Stage All** button in the app or run `git add <file>` in your terminal.

**Antivirus Flags the .exe**
Because the `.exe` is unsigned and built with PyInstaller, Windows Defender might flag it as a "False Positive". You may need to create an exception for the file.

**App crashes on startup**
Ensure you used the `--collect-all customtkinter` flag when building. CustomTkinter requires its theme JSON files to be bundled explicitly.