import sys
import threading
import tkinter as tk
from typing import Optional

import keyboard
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
        Initializes UI, intent parser, and registers global hotkeys.
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

        # Register Global Trigger Hotkey
        self._register_hotkeys()

        self._is_running = True
        app_logger.info(f"System Ready! Press '{TRIGGER_HOTKEY.upper()}' to trigger voice input.")

    def _register_hotkeys(self):
        """
        Hooks global shortcuts via the `keyboard` module.
        Thread-safe: schedules GUI actions back to Tkinter's main thread via root.after.
        """
        try:
            keyboard.add_hotkey(
                TRIGGER_HOTKEY,
                lambda: self.root.after(0, self._on_trigger_hotkey_pressed),
                suppress=False
            )
            app_logger.info(f"Registered trigger hotkey: '{TRIGGER_HOTKEY}'")
        except Exception as e:
            app_logger.error(f"Failed to register global hotkey: {e}", exc_info=True)

    def _on_trigger_hotkey_pressed(self):
        """
        Invoked on main thread when trigger hotkey is pressed.
        """
        app_logger.info(f"Global hotkey '{TRIGGER_HOTKEY}' detected. Activating Voice Bar.")
        if self.ui:
            self.ui.show_window()

    def _dispatch_command_processing(self, spoken_text: str):
        """
        Runs the Gemini API parsing and intent execution in a separate daemon thread
        so the Tkinter main thread is never blocked.
        """
        worker_thread = threading.Thread(
            target=self._command_worker,
            args=(spoken_text,),
            daemon=True,
            name="IntentExecutionWorker"
        )
        worker_thread.start()

    def _command_worker(self, text: str):
        """
        Worker thread routine: parses intent with Gemini, then executes the target action.
        """
        try:
            app_logger.info(f"Processing command: \"{text}\"")
            if not self.parser:
                self.parser = IntentParser()

            intent = self.parser.parse_intent(text)
            action = intent.get("action", "unsupported")
            target = intent.get("target", "")

            # Execute
            success = execute_intent(intent)
            if success:
                app_logger.info(f"Successfully executed action '{action}' for: \"{target}\"")
            else:
                app_logger.warning(f"Execution completed with notice/failure for action '{action}'.")

        except Exception as e:
            app_logger.error(f"Error processing command worker for '{text}': {e}", exc_info=True)

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
