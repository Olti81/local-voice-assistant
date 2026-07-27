# Local Voice Assistant

A powerful, lightweight Windows desktop voice assistant combining **GPU-accelerated local Speech-to-Text (STT)** dictation and **intelligent multi-lingual Text-to-Speech (TTS)** read-aloud capabilities.

Designed for seamless background integration with any application, **Local Voice Assistant** runs silently in the system tray, automatically pastes transcribed speech directly into your active window, and reads selected text aloud using neural voices.

---

## 🌟 Key Features

- **🎙️ Global Dictation (Push-to-Talk Speech-to-Text)**
  - Powered locally by [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) (Whisper `base` model) with **NVIDIA CUDA GPU acceleration** (`float16`).
  - **Push-to-Talk**: Hold down **`Ctrl + F9`** or **`Ctrl + Shift + <`** to record your voice. Release the keys when you finish talking to automatically transcribe and **paste text** into your active window.
- **🔊 Auto-Detect Read Aloud (Text-to-Speech)**
  - Powered by Microsoft's neural voices via [`edge-tts`](https://github.com/rany2/edge-tts) and [`langdetect`](https://github.com/Mimino66/langdetect).
  - Select any text on your screen and press a hotkey (`Ctrl + F10` by default). The application copies the selection, detects whether it is **English** or **Norwegian**, and speaks it aloud using high-quality neural voices.
- **🖥️ Floating Status Overlay & System Tray**
  - Displays a clean, non-intrusive floating status indicator (`🎙️ Listening...` or `🔊 Reading...`) with a quick `Cancel (Esc)` button.
  - Runs quietly in the Windows system tray (`pystray`) for minimal desktop distraction.
- **⚙️ Setup & Customization GUI**
  - Built with [`CustomTkinter`](https://github.com/TomSchimansky/CustomTkinter) for modern dark-mode styling.
  - Choose your preferred microphone input device, customize English and Norwegian neural voices, and test STT/TTS in real time.
- **📊 Activity Logging & Database**
  - Automatically logs timestamps, active window titles, mode (STT vs. TTS), and text snippets to a local SQLite database (`history.db`).
- **🚀 One-Click Setup & Background Launchers**
  - Includes automated scripts to create an isolated Python virtual environment, download CUDA-enabled PyTorch, and run silently in the background without persistent console windows.

---

## 🛠️ System Requirements

- **Operating System**: Windows 10 / 11 (64-bit)
- **Python**: Python 3.10 or higher installed and added to `PATH`
- **GPU Acceleration**: NVIDIA GPU with CUDA support recommended for fast local Whisper transcription
- **Network**: Internet connection required for Edge-TTS neural voice streaming

---

## 📦 Installation

1. **Clone or Download** this repository to your computer (e.g. `C:\Users\<YourUser>\Desktop\projects\local-voice-assistant`).
2. Double-click **`install.bat`**.

> **What `install.bat` does:**
> - Verifies Python installation.
> - Creates an isolated virtual environment (`venv/`).
> - Downloads CUDA 12.1-enabled PyTorch (`torch`).
> - Installs all application dependencies from `requirements.txt`.
> - Primes the STT model (`faster-whisper` base model) in `.models/whisper`.

---

## 🚀 Running the Assistant

You can launch the assistant in several ways depending on your workflow:

| Launcher Script | Mode | Description |
| :--- | :--- | :--- |
| **`run.vbs`** *(Recommended)* | **Silent Background** | Launches the assistant without leaving an open Command Prompt window. Perfect for daily use. |
| **`debug.bat`** | **Debug / Console** | Launches the assistant inside a visible Command Prompt window. Use this if you want to inspect logs or troubleshoot errors. |
| **`launch.bat`** | **Background Process** | Directly invokes `pythonw.exe` inside the virtual environment. |
| **`stop.bat`** | **Stop Application** | Forcefully closes all running background instances of the voice assistant (`pythonw.exe`). |

---

## ⌨️ How to Use

### 1. Dictation Mode (STT)
1. Place your cursor inside any text area (Notepad, Browser, Word, Discord, Code Editor, etc.).
2. Press and hold **`Ctrl + F9`** or **`Ctrl + Shift + <`**.
3. The floating overlay **`🎙️ Listening...`** appears on screen. Speak clearly into your microphone while holding the keys.
4. Release the keys when you are finished talking.
5. The audio is transcribed in seconds and **auto-pasted directly** into your active application.
6. Press **`Esc`** or click **`Cancel (Esc)`** on the overlay at any time to discard the recording.

### 2. Read Aloud Mode (TTS)
1. Highlight/select any text on screen with your mouse or keyboard.
2. Press **`Ctrl + F10`** (or your custom hotkey).
3. The floating overlay **`🔊 Reading...`** appears, and the assistant automatically detects the language and speaks the text aloud.
4. Press **`Esc`**, click **`Cancel (Esc)`**, or press **`Ctrl + F10`** again to immediately stop audio playback.

### 3. System Tray & Test Menu
1. Right-click the circular tray icon near the system clock.
2. Select **Test & Settings** to open the interactive test window where you can:
   - Type custom text to test TTS voices.
   - Record and preview STT transcriptions with live text output.

---

## ⚙️ Configuration (`config.json`)

Settings are stored in `config.json` in the root directory:

```json
{
    "show_tutorial_on_startup": true,
    "hotkey_dictation": "<ctrl>+<f9>",
    "hotkey_read_aloud": "<ctrl>+<f10>",
    "mic_device_name": "Default Microphone",
    "voice_en": "en-US-JennyNeural",
    "voice_no": "nb-NO-PernilleNeural"
}
```

### Options Breakdown:
- **`show_tutorial_on_startup`**: If `true`, displays the setup dialog when launching the assistant.
- **`hotkey_dictation`**: `pynput` hotkey string for triggering speech dictation (default: `<ctrl>+<f9>`).
- **`hotkey_read_aloud`**: `pynput` hotkey string for triggering text-to-speech read aloud (default: `<ctrl>+<f10>`).
- **`mic_device_name`**: Selected input microphone device name or index string (e.g. `"Default Microphone"` or `"[1] Microphone (Realtek Audio)"`).
- **`voice_en`**: Edge-TTS neural voice model for English text (e.g. `en-US-JennyNeural`, `en-US-AriaNeural`, `en-US-GuyNeural`, `en-US-ChristopherNeural`).
- **`voice_no`**: Edge-TTS neural voice model for Norwegian text (e.g. `nb-NO-PernilleNeural`, `nb-NO-FinnNeural`).

---

## 📁 Directory Structure

```text
local-voice-assistant/
├── engines/
│   ├── stt_engine.py      # Speech-to-Text engine (faster-whisper PyAudio integration)
│   └── tts_engine.py      # Text-to-Speech engine (edge-tts + langdetect + pygame playback)
├── ui/
│   ├── overlay.py         # Floating status overlay window (CustomTkinter Toplevel)
│   ├── settings.py        # Test & Settings UI window
│   └── tutorial.py        # Startup hardware & voice configuration dialog
├── utils/
│   └── os_context.py      # OS automation utilities (Active window detection, clipboard, keyboard input)
├── .models/               # Local directory storing pre-downloaded Whisper models
├── config.json            # Application configuration file
├── database.py            # SQLite database manager for activity logging
├── history.db             # SQLite database storing transcription and TTS usage history
├── main.py                # Core application entry point, system tray, & hotkey listeners
├── requirements.txt       # Python package dependencies
├── install.bat            # Automated environment & dependency installer
├── launch.bat             # Background runner script
├── debug.bat              # Console debug launcher script
├── run.vbs                # Quiet background VBScript wrapper
└── stop.bat               # Process termination script
```

---

## ❓ Troubleshooting

### Application Crashes or Fails to Start
- Run **`debug.bat`** to see real-time error output in a console window.
- Check **`error.log`** in the project directory for detailed crash tracebacks.

### Microphone Not Found / No Speech Transcribed
- Open **Test & Settings** from the system tray or enable `show_tutorial_on_startup: true` in `config.json` to select the specific microphone hardware index.

### Force Stopping Background Instances
- If multiple instances of the assistant are running in the background, run **`stop.bat`** to terminate all `pythonw.exe` processes.

---

## 📜 License

Distributed under the MIT License. Feel free to modify and extend for personal or production workflows.
