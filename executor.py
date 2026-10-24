import urllib.parse
import webbrowser
from typing import Dict, Any

from logger import app_logger

def search_web(target: str) -> bool:
    """
    Executes a Google web search in the default browser for the target query.
    """
    query = (target or "").strip()
    if not query:
        app_logger.warning("search_web called with empty query. Opening Google homepage.")
        webbrowser.open("https://www.google.com")
        return True

    app_logger.info(f"Executing web search for: '{query}'")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    webbrowser.open(url)
    return True
