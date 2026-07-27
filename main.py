import os
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
import json
import threading
from pynput import keyboard
import pystray
from PIL import Image, ImageDraw
import customtkinter as ctk

from ui.tutorial import show_tutorial
from ui.overlay import UIManager
from ui.settings import SettingsUI
from engines.stt_engine import STTEngine
from engines.tts_engine import TTSEngine
from utils.os_context import get_active_window_title, get_selected_text, paste_text
import database

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def create_tray_icon():
    image = Image.new('RGB', (64, 64), color=(30, 30, 30))
    dc = ImageDraw.Draw(image)
    dc.ellipse((16, 16, 48, 48), fill=(100, 180, 255))
    return image

class AssistantApp:
    def __init__(self):
        database.init_db()
        self.config = load_config()
        
        # 1. Master Tkinter Root (Lives forever on the Main Thread)
        ctk.set_appearance_mode("dark")
        self.root = ctk.CTk()
        self.root.withdraw() # Hide the permanent root window
        
        self.stt = STTEngine()
        self.tts = TTSEngine()
        
        # Pass the master root to the UI managers
        self.ui = UIManager(self.root, self.cancel_action)
        self.settings_ui = SettingsUI(self.root, self.tts, self.stt)
        
        self.is_recording = False
        self.is_reading = False
        self.hotkey_listener = None
        self.tray_icon = None

    def start_dictation(self):
        if not self.is_recording:
            self.is_recording = True
            self.ui.show_overlay("Mic")
            self.stt.start_recording()

    def stop_dictation(self):
        if self.is_recording:
            self.is_recording = False
            self.ui.hide_overlay()
            text = self.stt.stop_recording_and_transcribe()
            if text:
                paste_text(text)
                database.log_activity("STT", get_active_window_title(), text)

    def toggle_read_aloud(self):
        if self.tts.is_playing:
            self.cancel_action()
            return

        text = get_selected_text()
        if text.strip():
            self.is_reading = True
            self.ui.show_overlay("Speaker")
            database.log_activity("TTS", get_active_window_title(), text)
            self.tts.play_text(text, on_complete=self.ui.hide_overlay)

    def cancel_action(self):
        if self.is_recording:
            self.is_recording = False
            self.stt.cancel_recording()
        if self.tts.is_playing:
            self.tts.stop_audio()
        self.ui.hide_overlay()

    def _listen_for_hotkeys(self):
        dictation_raw_list = [
            self.config.get("hotkey_dictation", "<ctrl>+<f9>"),
            self.config.get("hotkey_dictation_alt", "<ctrl>+<shift>+<"),
            "<ctrl>+<shift>+,"
        ]

        dictation_hotkey_sets = []
        for raw_hk in dictation_raw_list:
            if raw_hk:
                try:
                    hk_set = set(keyboard.HotKey.parse(raw_hk))
                    if hk_set and hk_set not in dictation_hotkey_sets:
                        dictation_hotkey_sets.append(hk_set)
                except Exception:
                    pass

        try:
            read_aloud_keys = set(keyboard.HotKey.parse(self.config.get("hotkey_read_aloud", "<ctrl>+<f10>")))
        except Exception:
            read_aloud_keys = set(keyboard.HotKey.parse("<ctrl>+<f10>"))

        current_keys = set()
        read_aloud_triggered = False

        def _on_press(key):
            nonlocal read_aloud_triggered
            try:
                canonical = listener.canonical(key)
            except Exception:
                canonical = key
            current_keys.add(key)
            current_keys.add(canonical)

            if any(hk_set.issubset(current_keys) for hk_set in dictation_hotkey_sets):
                if not self.is_recording:
                    self.start_dictation()

            if read_aloud_keys.issubset(current_keys):
                if not read_aloud_triggered:
                    read_aloud_triggered = True
                    self.toggle_read_aloud()

        def _on_release(key):
            nonlocal read_aloud_triggered
            try:
                canonical = listener.canonical(key)
            except Exception:
                canonical = key
            current_keys.discard(key)
            current_keys.discard(canonical)

            if self.is_recording and not any(hk_set.issubset(current_keys) for hk_set in dictation_hotkey_sets):
                self.stop_dictation()

            if not read_aloud_keys.issubset(current_keys):
                read_aloud_triggered = False

        listener = keyboard.Listener(on_press=_on_press, on_release=_on_release)
        self.hotkey_listener = listener
        listener.start()
        listener.join()

    def open_settings(self, icon, item):
        self.settings_ui.run()

    def quit_app(self, icon, item):
        if self.tray_icon:
            self.tray_icon.stop()
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        self.root.quit()
        os._exit(0)

    def _run_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Local Voice Assistant", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Test & Settings", self.open_settings),
            pystray.MenuItem("Quit", self.quit_app)
        )
        self.tray_icon = pystray.Icon("voice_assistant", create_tray_icon(), "Voice Assistant", menu)
        self.tray_icon.run()

    def run(self):
        # Push all background tasks to daemon threads
        threading.Thread(target=self._listen_for_hotkeys, daemon=True).start()
        threading.Thread(target=self._run_tray, daemon=True).start()
        
        # Lock the Main Thread with the Tkinter event loop
        self.root.mainloop()

if __name__ == "__main__":
    try:
        show_tutorial()
        app = AssistantApp()
        app.run()
    except Exception as e:
        import traceback
        import time
        from tkinter import messagebox
        
        # Log to error.log
        try:
            with open("error.log", "a", encoding="utf-8") as f:
                f.write(f"\n--- Crash at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                traceback.print_exc(file=f)
        except Exception:
            pass
            
        # Show error dialog
        try:
            root = ctk.CTk()
            root.withdraw()
            messagebox.showerror(
                "Voice Assistant Error",
                f"The application encountered an error and had to close.\n\nError: {e}\n\nDetails have been saved to 'error.log'."
            )
            root.destroy()
        except Exception:
            pass