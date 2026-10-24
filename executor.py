import re
import urllib.parse
import urllib.request
import webbrowser
from typing import Dict, Any

from logger import app_logger

# User agent for YouTube scraping
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def play_youtube_video(target: str) -> bool:
    """
    Searches YouTube for the target query using urllib, extracts the first video ID,
    and opens the direct video URL in the default browser.
    Falls back to opening the search page if video extraction fails.
    """
    query = (target or "").strip()
    if not query:
        app_logger.warning("play_youtube_video called with empty target.")
        return False

    app_logger.info(f"Finding top YouTube video for: '{query}'")
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"

    try:
        req = urllib.request.Request(search_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode("utf-8", errors="ignore")

        # Find the first video ID pattern (/watch?v=xxxxxxxxxxx)
        video_ids = re.findall(r"/watch\?v=([a-zA-Z0-9_-]{11})", html)

        if video_ids:
            first_video_id = video_ids[0]
            video_url = f"https://www.youtube.com/watch?v={first_video_id}"
            app_logger.info(f"Opening YouTube video: {video_url}")
            webbrowser.open(video_url)
            return True
        else:
            app_logger.warning("No direct video ID found in search HTML. Falling back to search results page.")
            webbrowser.open(search_url)
            return True

    except Exception as e:
        app_logger.error(f"Error fetching direct YouTube video: {e}. Falling back to search page.", exc_info=True)
        webbrowser.open(search_url)
        return True

def search_youtube(target: str) -> bool:
    """
    Opens YouTube search results page for the specified query.
    """
    query = (target or "").strip()
    if not query:
        app_logger.warning("search_youtube called with empty query. Opening YouTube homepage.")
        webbrowser.open("https://www.youtube.com")
        return True

    app_logger.info(f"Opening YouTube search for: '{query}'")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    webbrowser.open(url)
    return True

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
