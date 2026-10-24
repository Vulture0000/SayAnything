@echo off
title SayAnything Voice Automation
echo Starting SayAnything...
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    python main.py
)
pause
