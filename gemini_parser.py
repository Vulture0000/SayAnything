import json
from typing import Dict, Any
from config import GEMINI_API_KEY, GEMINI_MODEL
from logger import app_logger

# Valid actions as specified in the architecture
VALID_ACTIONS = {
    "play_youtube_video",
    "search_youtube",
    "open_vscode",
    "search_web",
    "unsupported"
}

SYSTEM_INSTRUCTION = """You are a strict, ultra-accurate JSON-only routing engine for a Windows OS Voice Automation assistant.
Your sole job is to classify the user's spoken command into one of the following exact actions and extract the target parameter:

1. "play_youtube_video":
   - Use when the user wants to directly play, listen to, or watch a specific video/song/track.
   - Examples: "play hotel california", "put on lofi hip hop", "play the latest interstellar trailer on youtube"
   - Target: The cleaned video/song query (e.g., "hotel california", "lofi hip hop").

2. "search_youtube":
   - Use when the user explicitly asks to search or browse YouTube for tutorials, videos, or channels.
   - Examples: "search youtube for python tutorials", "look up blender beginner guide on youtube"
   - Target: The topic to search on YouTube (e.g., "python tutorials").

3. "open_vscode":
   - Use when the user asks to open Visual Studio Code or Code.
   - Examples: "open vscode", "launch visual studio code in my projects folder", "open code at C:\\Dev\\App"
   - Target: The extracted folder/file path if mentioned, or an empty string "" if none specified.

4. "search_web":
   - Use when the user wants to search Google or ask a general query/fact.
   - Examples: "search the web for weather in Tokyo", "google latest stock price of Apple", "who won the 2022 World Cup"
   - Target: The cleaned search query.

5. "unsupported":
   - Use if the user command does not fit any of the above categories or is unintelligible.
   - Target: The original text or explanation.

You MUST respond strictly with valid JSON conforming to this schema:
{
  "action": "play_youtube_video" | "search_youtube" | "open_vscode" | "search_web" | "unsupported",
  "target": "<extracted search query, folder path, or topic>"
}
Do NOT output any markdown fences, thoughts, or commentary. Only the raw JSON object.
"""

class IntentParser:
    """
    Interfaces with the Google Gemini API to parse voice input into structured JSON actions.
    """
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or GEMINI_MODEL
        self._model = None
        self._initialized = False

    def _ensure_initialized(self):
        if self._initialized:
            return

        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            raise ValueError(
                "Gemini API Key is missing or default placeholder. "
                "Please set GEMINI_API_KEY in your .env file."
            )

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            # Configure GenerativeModel with JSON response mime type
            self._model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=SYSTEM_INSTRUCTION,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                )
            )
            self._initialized = True
            app_logger.info(f"Gemini Intent Parser initialized with model: {self.model_name}")
        except Exception as e:
            app_logger.error(f"Failed to initialize Gemini API: {e}", exc_info=True)
            raise

    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Sends the transcribed voice text to Gemini and parses the structured JSON response.
        Returns a dict with 'action' and 'target'.
        """
        cleaned_text = (text or "").strip()
        if not cleaned_text:
            return {"action": "unsupported", "target": "Empty voice input"}

        try:
            self._ensure_initialized()
            app_logger.info(f"Sending prompt to Gemini: '{cleaned_text}'")

            response = self._model.generate_content(cleaned_text)
            response_text = (response.text or "").strip()
            app_logger.debug(f"Gemini raw response: {response_text}")

            # Parse JSON
            parsed_data = json.loads(response_text)

            action = parsed_data.get("action", "unsupported")
            target = parsed_data.get("target", "")

            # Sanitize and validate
            if action not in VALID_ACTIONS:
                app_logger.warning(f"Unknown action '{action}' returned from Gemini, falling back to unsupported.")
                action = "unsupported"

            if not isinstance(target, str):
                target = str(target)

            result = {
                "action": action,
                "target": target.strip()
            }
            app_logger.info(f"Parsed intent: action='{result['action']}', target='{result['target']}'")
            return result

        except ValueError as ve:
            app_logger.error(f"Configuration Error: {ve}")
            return {"action": "unsupported", "target": f"Config Error: {ve}"}
        except json.JSONDecodeError as jde:
            app_logger.error(f"Failed to parse JSON from Gemini response: {jde}", exc_info=True)
            return {"action": "unsupported", "target": f"JSON Decode Error: {jde}"}
        except Exception as e:
            app_logger.error(f"Unexpected error during intent parsing: {e}", exc_info=True)
            return {"action": "unsupported", "target": f"Gemini Error: {e}"}
