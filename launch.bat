@echo off
cd /d "%~dp0"
call venv\Scripts\activate
start "" venv\Scripts\pythonw.exe main.py