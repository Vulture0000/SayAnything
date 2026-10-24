"""
Unit / Smoke tests for SayAnything OS Automation.
Validates configuration loading, logging, URL formatting, and mock intent parsing.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock

import config
import logger
import executor
import gemini_parser

class TestSayAnything(unittest.TestCase):
    def test_01_config_defaults(self):
        """Verify default configuration parameters are populated."""
        self.assertTrue(len(config.TRIGGER_HOTKEY) > 0)
        self.assertTrue(len(config.WISPR_HOTKEY) > 0)
        self.assertTrue(len(config.EXIT_HOTKEY) > 0)
        self.assertIn("gemini", config.GEMINI_MODEL.lower())
        self.assertIsInstance(config.AUTO_TRIGGER_WISPR, bool)

    def test_02_logger(self):
        """Verify logger writes messages without throwing exceptions."""
        test_logger = logger.setup_logger("TestLogger")
        test_logger.info("Test info message")
        test_logger.warning("Test warning message")
        self.assertTrue(config.LOG_FILE.parent.exists())

    def test_03_youtube_url_formatting(self):
        """Test search query encoding and fallback behavior."""
        with patch("webbrowser.open") as mock_browser:
            executor.search_youtube("python async programming")
            mock_browser.assert_called_once()
            called_url = mock_browser.call_args[0][0]
            self.assertIn("youtube.com/results?search_query=python%20async%20programming", called_url)

    def test_04_web_search_formatting(self):
        """Test web search query encoding."""
        with patch("webbrowser.open") as mock_browser:
            executor.search_web("what is the speed of light")
            mock_browser.assert_called_once()
            called_url = mock_browser.call_args[0][0]
            self.assertIn("google.com/search?q=what%20is%20the%20speed%20of%20light", called_url)

    def test_05_vscode_execution(self):
        """Test VS Code launch dispatch."""
        with patch("subprocess.Popen") as mock_popen:
            executor.open_vscode("C:\\TestPath")
            mock_popen.assert_called_once()
            cmd_arg = mock_popen.call_args[0][0]
            self.assertIn("code", cmd_arg)
            self.assertIn("TestPath", cmd_arg)

    def test_06_intent_parser_fallback_on_empty(self):
        """Intent parser should gracefully return unsupported on empty text."""
        parser = gemini_parser.IntentParser(api_key="dummy_key")
        result = parser.parse_intent("")
        self.assertEqual(result["action"], "unsupported")

    def test_07_intent_parser_fallback_on_missing_key(self):
        """Intent parser should handle missing key gracefully."""
        parser = gemini_parser.IntentParser(api_key="")
        result = parser.parse_intent("play jazz")
        self.assertEqual(result["action"], "unsupported")
        self.assertIn("Config Error", result["target"])

    def test_08_executor_routing(self):
        """Test central executor routing for different actions."""
        with patch("executor.play_youtube_video") as mock_play, \
             patch("executor.search_youtube") as mock_search_yt, \
             patch("executor.open_vscode") as mock_code, \
             patch("executor.search_web") as mock_web:

            executor.execute_intent({"action": "play_youtube_video", "target": "hotel california"})
            mock_play.assert_called_with("hotel california")

            executor.execute_intent({"action": "search_youtube", "target": "rust vs zig"})
            mock_search_yt.assert_called_with("rust vs zig")

            executor.execute_intent({"action": "open_vscode", "target": "my_folder"})
            mock_code.assert_called_with("my_folder")

            executor.execute_intent({"action": "search_web", "target": "quantum computing"})
            mock_web.assert_called_with("quantum computing")

if __name__ == "__main__":
    unittest.main()
