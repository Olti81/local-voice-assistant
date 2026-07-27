@echo off
color 0A
title Local Voice Assistant Installer

echo ===================================================
echo   Initializing Local Voice Assistant Setup...
echo ===================================================
echo.

echo [*] Checking system for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [!] Error: Python is not installed or not in PATH.
    pause
    exit /b
)
echo [OK] Python found.
echo.

echo [*] Setting up isolated virtual environment...
if not exist venv (
    python -m venv venv
)
echo [OK] Virtual environment ready.
echo.

echo [*] Fetching NVIDIA CUDA Libraries (PyTorch)...
echo [!] This is a ~2.5GB download and will take a few minutes.
call venv\Scripts\activate
python -m pip install torch --index-url https://download.pytorch.org/whl/cu121
echo [OK] CUDA Libraries installed.
echo.

echo [*] Installing core application dependencies...
pip install -r requirements.txt 
echo [OK] Dependencies installed.
echo.

echo [*] Downloading local AI models (Kokoro and Whisper)...
echo [!] Do not close this window. Progress will be shown below:
echo.
python -c "import engines.tts_engine as tts; import engines.stt_engine as stt; tts.prime_model(); stt.prime_model()"

echo.
echo ===================================================
echo   Installation Complete! 
echo   Double-click 'run.vbs' to start the application.
echo ===================================================
pause