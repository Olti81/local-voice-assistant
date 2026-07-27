import time
import pyperclip
from pynput.keyboard import Controller, Key
import uiautomation as auto

keyboard_controller = Controller()

def get_active_window_title():
    try:
        window = auto.GetForegroundControl()
        return window.Name if window else "Unknown Window"
    except Exception:
        return "Unknown Window"

def get_selected_text():
    # Save current clipboard
    old_clipboard = pyperclip.paste()
    pyperclip.copy("")
    
    # Simulate Ctrl+C
    keyboard_controller.press(Key.ctrl)
    keyboard_controller.press('c')
    keyboard_controller.release('c')
    keyboard_controller.release(Key.ctrl)
    
    time.sleep(0.1) # Wait for OS to process copy
    text = pyperclip.paste()
    
    # Restore clipboard if nothing was copied
    if not text:
        pyperclip.copy(old_clipboard)
    return text

def paste_text(text):
    pyperclip.copy(text)
    time.sleep(0.1)
    
    # Simulate Ctrl+V
    keyboard_controller.press(Key.ctrl)
    keyboard_controller.press('v')
    keyboard_controller.release('v')
    keyboard_controller.release(Key.ctrl)