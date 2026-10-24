import tkinter as tk
from typing import Callable, Optional

from config import (
    UI_WIDTH, UI_HEIGHT, UI_BG_COLOR, UI_BORDER_COLOR
)
from logger import app_logger

class VoiceInputWindow:
    """
    A lightweight, borderless, always-on-top input bar designed for voice dictation.
    Styled with modern dark aesthetics, inspired by Raycast / Spotlight.
    """
    def __init__(self, root: tk.Tk, on_submit: Callable[[str], None]):
        self.root = root
        self.on_submit = on_submit
        self.is_visible = False

        self._setup_window()

    def _setup_window(self):
        self.root.title("SayAnything Voice Bar")
        self.root.overrideredirect(True)          # Borderless
        self.root.attributes("-topmost", True)      # Always on top
        self.root.configure(bg=UI_BORDER_COLOR)

        # Center horizontally and position 22% from top of screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - UI_WIDTH) // 2
        y = int(screen_height * 0.22)
        self.root.geometry(f"{UI_WIDTH}x{UI_HEIGHT}+{x}+{y}")
