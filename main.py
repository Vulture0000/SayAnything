import sys
import time
import signal
import threading
import tkinter as tk
from typing import Optional

import keyboard
from config import TRIGGER_HOTKEY, EXIT_HOTKEY, GEMINI_API_KEY
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

        # Initialize Intent Parser
        try:
            self.parser = IntentParser()
        except Exception as e:
            app_logger.warning(
                f"IntentParser warning during init: {e}. "
                "The application will still run, but commands will fail if GEMINI_API_KEY is not set."
            )

        # Initialize Tkinter root on the main thread
        self.root = tk.Tk()

        # Initialize UI
        self.ui = VoiceInputWindow(
            root=self.root,
            on_submit=self._dispatch_command_processing
        )

        # Register Global Hotkeys
        self._register_hotkeys()

        # Handle SIGINT / SIGTERM for clean shutdown when running in terminal
        signal.signal(signal.SIGINT, lambda sig, frame: self.root.after(0, self.shutdown))
        signal.signal(signal.SIGTERM, lambda sig, frame: self.root.after(0, self.shutdown))

        self._is_running = True
        app_logger.info(f"System Ready! Press '{TRIGGER_HOTKEY.upper()}' to trigger voice input.")
        app_logger.info(f"Press '{EXIT_HOTKEY.upper()}' at any time to gracefully exit.")

    def _register_hotkeys(self):
        """
        Hooks global shortcuts via the `keyboard` module.
        Thread-safe: schedules GUI actions back to Tkinter's main thread via root.after.
        """
        try:
            # Global trigger hotkey (e.g. Ctrl+Alt+Space)
            keyboard.add_hotkey(
                TRIGGER_HOTKEY,
                lambda: self.root.after(0, self._on_trigger_hotkey_pressed),
                suppress=False
            )
            app_logger.info(f"Registered trigger hotkey: '{TRIGGER_HOTKEY}'")

            # Graceful exit hotkey (e.g. Ctrl+Shift+Q)
            keyboard.add_hotkey(
                EXIT_HOTKEY,
                lambda: self.root.after(0, self.shutdown),
                suppress=False
            )
            app_logger.info(f"Registered graceful exit hotkey: '{EXIT_HOTKEY}'")

        except Exception as e:
            app_logger.error(
                f"Failed to register global hotkey: {e}. "
                "Note: On Windows, global keyboard hooks may require Administrator privileges "
                "if interacting with elevated application windows.",
                exc_info=True
            )

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
        finally:
            self.shutdown()

    def shutdown(self):
        """
        Performs a clean, graceful shutdown of the application.
        """
        if not self._is_running:
            return

        self._is_running = False
        app_logger.info("Shutting down Voice-Controlled OS Automation...")

        # Unhook global keyboard listeners
        try:
            keyboard.unhook_all_hotkeys()
            app_logger.debug("Keyboard hotkeys successfully unhooked.")
        except Exception as e:
            app_logger.debug(f"Notice while unhooking keyboard: {e}")

        # Destroy Tkinter window
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            app_logger.debug(f"Notice while destroying UI: {e}")

        app_logger.info("Application exited cleanly. Goodbye!")
        sys.exit(0)


def main():
    app = VoiceAutomationApp()
    app.initialize()
    app.run()


if __name__ == "__main__":
    main()
