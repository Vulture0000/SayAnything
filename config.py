import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env if present
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    load_dotenv(override=True)

# Hotkey Settings
# Global trigger to invoke the input window
TRIGGER_HOTKEY = os.getenv("TRIGGER_HOTKEY", "ctrl+alt+space").strip().lower()

# Keyboard shortcut configured in Wispr Flow to toggle dictation
WISPR_HOTKEY = os.getenv("WISPR_HOTKEY", "alt+c").strip().lower()

# Graceful termination hotkey
EXIT_HOTKEY = os.getenv("EXIT_HOTKEY", "ctrl+shift+q").strip().lower()

# Whether to programmatically trigger Wispr Flow when the input bar opens
AUTO_TRIGGER_WISPR = os.getenv("AUTO_TRIGGER_WISPR", "true").strip().lower() in ("true", "1", "yes")

# Gemini API Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

# System Commands
VSCODE_COMMAND = os.getenv("VSCODE_COMMAND", "code").strip()

# Logging Configuration
LOG_FILE = BASE_DIR / "error.log"

# UI Aesthetic Configuration (Modern Raycast/Spotlight Dark Pill)
UI_WIDTH = 680
UI_HEIGHT = 90
UI_BG_COLOR = "#121217"         # Deep sleek dark background
UI_CARD_BG = "#1e1e26"          # Inner card background
UI_ACCENT_COLOR = "#6366f1"     # Indigo accent
UI_ACCENT_HOVER = "#4f46e5"
UI_TEXT_COLOR = "#f8fafc"       # Crisp white text
UI_MUTED_TEXT = "#94a3b8"       # Slate gray for status / placeholder
UI_BORDER_COLOR = "#2e2e3a"     # Subtle border outline
UI_FONT_FAMILY = "Segoe UI"
UI_FONT_SIZE = 14
