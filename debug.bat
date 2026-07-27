@echo off
color 0C
title Voice Assistant Debugger
cd /d "%~dp0"

echo Starting Voice Assistant in Debug Mode...
echo =========================================
call venv\Scripts\activate
venv\Scripts\python.exe main.py

echo =========================================
echo Process Exited. 
pause