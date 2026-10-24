# 🎙️ SayAnything: Voice-Controlled OS Automation for Windows

A robust, ultra-fast, and bug-free Windows OS Voice Automation application powered by **Wispr Flow** for voice dictation and the **Google Gemini API** (`google-generativeai`) for structured intent classification.

---

## 🏗️ Architecture & Workflow

```mermaid
flowchart TD
    A["User presses Global Hotkey<br>(Ctrl+Alt+Space)"] --> B["SayAnything Background Listener<br>(keyboard module)"]
    B --> C["Instantly pop up Borderless, Topmost Input Window<br>(Tkinter + Win32 SetForegroundWindow)"]
    C --> D["Programmatically trigger Wispr Flow<br>(Alt+C via pyautogui)"]
    D --> E["User speaks & Wispr Flow transcribes into text box"]
    E --> F["User presses Enter or Wispr inserts Newline"]
    F --> G["Window hides instantly & dispatches text to background worker thread"]
    G --> H["Google Gemini API (response_mime_type='application/json')"]
    H --> I["Strict JSON Intent Routing"]
    I --> J{"Action Dispatcher"}
    J -->|play_youtube_video| K["urllib scrapes YouTube & opens direct video URL"]
    J -->|search_youtube| L["webbrowser opens YouTube search results"]
    J -->|open_vscode| M["subprocess launches VS Code (code [target])"]
    J -->|search_web| N["webbrowser opens Google search results"]
    J -->|unsupported| O["Log warning to console & error.log"]
```

---

## ✨ Features

- **Global Hotkey Trigger (`Ctrl+Alt+Space`)**: Runs in the background and activates instantly from anywhere in Windows.
- **Raycast/Spotlight-Style Floating Bar**: Custom dark-mode borderless modal with vibrant accent glow, always-on-top, and forced foreground focus.
- **Hands-Free Wispr Flow Integration**: Programmatically triggers Wispr Flow (`Alt+C` by default) immediately upon bar activation so you can speak right away.
- **Structured JSON Intent Engine**: Strictly configured via Gemini's `response_mime_type="application/json"` with zero markdown formatting errors.
- **Direct Video Auto-Player**: Scrapes YouTube via `urllib` to find the exact top video and immediately opens the watch URL (`https://www.youtube.com/watch?v=...`).
- **Resilient Multi-Threaded Design**: Network calls and Gemini requests run on worker threads so the GUI never freezes.
- **Robust Error Logging**: Comprehensive `try/except` guards around every operation. Errors and stack traces are logged to `error.log` without crashing the daemon.
- **Graceful Termination (`Ctrl+Shift+Q`)**: Clean unhooking of global keyboard hooks and UI teardown.
