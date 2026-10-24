import sys
import ctypes
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
        self.hide_window()

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

    def _force_focus(self):
        """
        Forces Windows foreground focus to the borderless window and entry widget.
        """
        try:
            self.root.focus_force()

            # Extra measure for Windows OS to ensure foreground activation
            if sys.platform == "win32":
                hwnd = self.root.winfo_id()
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                ctypes.windll.user32.BringWindowToTop(hwnd)
        except Exception as e:
            app_logger.debug(f"Focus forcing notice: {e}")

    def hide_window(self):
        """
        Hides the window and clears state.
        """
        self.is_visible = False
        try:
            self.root.withdraw()
        except Exception as e:
            app_logger.debug(f"Error while hiding window: {e}")
