import sys
import ctypes
import tkinter as tk
from typing import Callable, Optional

from config import (
    UI_WIDTH, UI_HEIGHT, UI_BG_COLOR, UI_CARD_BG,
    UI_ACCENT_COLOR, UI_TEXT_COLOR, UI_MUTED_TEXT,
    UI_BORDER_COLOR, UI_FONT_FAMILY, UI_FONT_SIZE,
    WISPR_HOTKEY
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
        self._build_widgets()
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

    def _build_widgets(self):
        # Outer container creating a 1.5px border glow
        self.outer_frame = tk.Frame(
            self.root,
            bg=UI_BORDER_COLOR,
            padx=1,
            pady=1
        )
        self.outer_frame.pack(fill=tk.BOTH, expand=True)

        # Inner main container
        self.inner_frame = tk.Frame(
            self.outer_frame,
            bg=UI_BG_COLOR,
            padx=14,
            pady=8
        )
        self.inner_frame.pack(fill=tk.BOTH, expand=True)

        # Top Bar: Status indicator & badges
        self.top_bar = tk.Frame(self.inner_frame, bg=UI_BG_COLOR)
        self.top_bar.pack(fill=tk.X, pady=(0, 4))

        self.status_icon = tk.Label(
            self.top_bar,
            text="●",
            font=(UI_FONT_FAMILY, 9, "bold"),
            fg="#22c55e",  # Vibrant green pulse dot
            bg=UI_BG_COLOR
        )
        self.status_icon.pack(side=tk.LEFT, padx=(0, 6))

        self.title_label = tk.Label(
            self.top_bar,
            text="SayAnything Voice Command",
            font=(UI_FONT_FAMILY, 9, "bold"),
            fg=UI_TEXT_COLOR,
            bg=UI_BG_COLOR
        )
        self.title_label.pack(side=tk.LEFT)

        self.shortcut_badge = tk.Label(
            self.top_bar,
            text=f"Wispr: {WISPR_HOTKEY.upper()} | Esc to cancel",
            font=(UI_FONT_FAMILY, 8),
            fg=UI_MUTED_TEXT,
            bg=UI_BG_COLOR
        )
        self.shortcut_badge.pack(side=tk.RIGHT)

        # Input Card Container
        self.card_frame = tk.Frame(
            self.inner_frame,
            bg=UI_CARD_BG,
            highlightthickness=1,
            highlightbackground=UI_ACCENT_COLOR,
            highlightcolor=UI_ACCENT_COLOR,
            padx=10,
            pady=4
        )
        self.card_frame.pack(fill=tk.X, expand=True)

        # Mic Icon / Prompt Glyph
        self.mic_label = tk.Label(
            self.card_frame,
            text="🎙️",
            font=(UI_FONT_FAMILY, 12),
            bg=UI_CARD_BG,
            fg=UI_MUTED_TEXT
        )
        self.mic_label.pack(side=tk.LEFT, padx=(0, 8))

        # Text Input Entry
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            self.card_frame,
            textvariable=self.entry_var,
            font=(UI_FONT_FAMILY, UI_FONT_SIZE),
            bg=UI_CARD_BG,
            fg=UI_TEXT_COLOR,
            insertbackground=UI_ACCENT_COLOR,  # Cursor color
            relief=tk.FLAT,
            bd=0
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _force_focus(self):
        """
        Forces Windows foreground focus to the borderless window and entry widget.
        """
        try:
            self.root.focus_force()
            if hasattr(self, 'entry'):
                self.entry.focus_set()

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
