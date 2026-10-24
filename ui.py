import sys
import time
import ctypes
import threading
import tkinter as tk
from typing import Callable, Optional

import pyautogui
from config import (
    UI_WIDTH, UI_HEIGHT, UI_BG_COLOR, UI_CARD_BG,
    UI_ACCENT_COLOR, UI_TEXT_COLOR, UI_MUTED_TEXT,
    UI_BORDER_COLOR, UI_FONT_FAMILY, UI_FONT_SIZE,
    WISPR_HOTKEY, AUTO_TRIGGER_WISPR
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
        self._bind_events()

        # Start hidden
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

    def _bind_events(self):
        # Pressing Enter triggers submission
        self.entry.bind("<Return>", self._handle_return)
        self.root.bind("<Return>", self._handle_return)

        # Pressing Escape cancels and hides
        self.root.bind("<Escape>", lambda event: self.hide_window())

    def show_window(self):
        """
        Pops up the window, forces focus to the text field,
        and optionally triggers the Wispr Flow shortcut.
        """
        if self.is_visible:
            # Already visible, re-assert focus
            self._force_focus()
            return

        app_logger.debug("Showing voice input window...")
        self.is_visible = True

        # Clear any leftover text
        self.entry_var.set("")

        # Deiconify and configure topmost
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)

        self._force_focus()

        # Schedule Wispr Flow hotkey simulation slightly after focus is established
        if AUTO_TRIGGER_WISPR:
            self.root.after(80, self._simulate_wispr_trigger)

    def _force_focus(self):
        """
        Forces Windows foreground focus to the borderless window and entry widget.
        """
        try:
            self.root.focus_force()
            self.entry.focus_set()

            # Extra measure for Windows OS to ensure foreground activation
            if sys.platform == "win32":
                hwnd = self.root.winfo_id()
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                ctypes.windll.user32.BringWindowToTop(hwnd)
        except Exception as e:
            app_logger.debug(f"Focus forcing notice: {e}")

    def _simulate_wispr_trigger(self):
        """
        Programmatically triggers the Wispr Flow dictation shortcut.
        """
        if not WISPR_HOTKEY:
            return

        try:
            keys = [k.strip() for k in WISPR_HOTKEY.split("+") if k.strip()]
            if keys:
                app_logger.info(f"Simulating Wispr Flow hotkey: '{WISPR_HOTKEY}'")
                pyautogui.hotkey(*keys)
        except Exception as e:
            app_logger.error(f"Failed to simulate Wispr Flow hotkey '{WISPR_HOTKEY}': {e}", exc_info=True)

    def hide_window(self):
        """
        Hides the window and clears state.
        """
        self.is_visible = False
        try:
            self.root.withdraw()
        except Exception as e:
            app_logger.debug(f"Error while hiding window: {e}")

    def _handle_return(self, event=None):
        """
        Handles Enter key / newline transcription.
        Retrieves text, hides the window, and invokes on_submit callback.
        """
        raw_text = self.entry_var.get().strip()
        self.hide_window()

        if raw_text:
            app_logger.info(f"Captured input from voice window: '{raw_text}'")
            if self.on_submit:
                # Dispatch submission
                self.on_submit(raw_text)
        else:
            app_logger.info("Empty input submitted. Ignoring.")
