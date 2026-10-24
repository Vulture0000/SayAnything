import sys
import tkinter as tk
from typing import Optional

from config import TRIGGER_HOTKEY, EXIT_HOTKEY
from logger import app_logger
from gemini_parser import IntentParser
from executor import execute_intent
from ui import VoiceInputWindow

class VoiceAutomationApp:
    """
    Main application coordinator that orchestrates the global hotkey listener,
    floating voice input UI, Gemini intent parser, and OS execution engine.
    """
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.ui: Optional[VoiceInputWindow] = None
        self.parser: Optional[IntentParser] = None
        self._is_running = False

    def initialize(self):
        """
        Initializes UI, intent parser, and application state.
        """
        app_logger.info("=" * 60)
        app_logger.info("Initializing Voice-Controlled OS Automation (SayAnything)")
        app_logger.info("=" * 60)

        try:
            self.parser = IntentParser()
        except Exception as e:
            app_logger.warning(f"IntentParser warning during init: {e}")

        # Initialize Tkinter root on the main thread
        self.root = tk.Tk()

        # Initialize UI
        self.ui = VoiceInputWindow(
            root=self.root,
            on_submit=self._dispatch_command_processing
        )

        self._is_running = True

    def _dispatch_command_processing(self, spoken_text: str):
        pass

    def run(self):
        """
        Starts the Tkinter main loop on the primary thread.
        """
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            app_logger.info("KeyboardInterrupt received.")

def main():
    app = VoiceAutomationApp()
    app.initialize()
    app.run()

if __name__ == "__main__":
    main()
