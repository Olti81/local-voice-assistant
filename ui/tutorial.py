import json
import pyaudio
import customtkinter as ctk

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config):
    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Failed to save config: {e}")

def format_hotkey(raw_key):
    key = raw_key.lower().replace("<ctrl>", "Ctrl").replace("<alt>", "Alt").replace("<shift>", "Shift").replace("<cmd>", "Win")
    parts = key.split("+")
    formatted = []
    for p in parts:
        clean = p.strip("<>")
        if p == "<" or clean == "":
            formatted.append("<")
        elif len(clean) == 1:
            formatted.append(clean.upper())
        else:
            formatted.append(clean.upper() if clean.startswith("f") else clean.capitalize())
    return " + ".join(formatted)

def get_microphones():
    """Scans hardware for available input devices."""
    p = pyaudio.PyAudio()
    mics = ["Default Microphone"]
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            mics.append(f"[{i}] {info['name']}")
    p.terminate()
    return mics

# Voice Mappings
EN_VOICES = {
    "Aria (Female)": "en-US-AriaNeural",
    "Jenny (Female)": "en-US-JennyNeural",
    "Guy (Male)": "en-US-GuyNeural",
    "Christopher (Male)": "en-US-ChristopherNeural"
}

NO_VOICES = {
    "Pernille (Female)": "nb-NO-PernilleNeural",
    "Finn (Male)": "nb-NO-FinnNeural"
}

def show_tutorial():
    config = load_config()
    # Force defaults if config is empty
    if "hotkey_dictation" not in config: config["hotkey_dictation"] = "<ctrl>+<alt>+d"
    if "hotkey_read_aloud" not in config: config["hotkey_read_aloud"] = "<ctrl>+<alt>+r"
    if "show_tutorial_on_startup" not in config: config["show_tutorial_on_startup"] = True

    if not config.get("show_tutorial_on_startup", True):
        return

    ctk.set_appearance_mode("dark")
    window = ctk.CTk()
    window.title("Voice Assistant Setup")
    window.geometry("500x550")
    window.eval('tk::PlaceWindow . center')
    window.attributes("-topmost", True)

    ctk.CTkLabel(window, text="🎙️ Voice Assistant Setup", font=("Arial", 20, "bold")).pack(pady=(20, 10))

    # --- Hardware & Voices Section ---
    settings_frame = ctk.CTkFrame(window)
    settings_frame.pack(pady=10, padx=20, fill="x")

    # Microphone
    ctk.CTkLabel(settings_frame, text="Input Microphone:", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(15, 0))
    mic_var = ctk.StringVar(value=config.get("mic_device_name", "Default Microphone"))
    ctk.CTkOptionMenu(settings_frame, variable=mic_var, values=get_microphones(), width=400).pack(padx=15, pady=(5, 10))

    # English Voice
    inv_en = {v: k for k, v in EN_VOICES.items()}
    current_en = inv_en.get(config.get("voice_en", "en-US-AriaNeural"), "Aria (Female)")
    en_var = ctk.StringVar(value=current_en)
    
    ctk.CTkLabel(settings_frame, text="English Voice:", font=("Arial", 12, "bold")).pack(anchor="w", padx=15)
    ctk.CTkOptionMenu(settings_frame, variable=en_var, values=list(EN_VOICES.keys()), width=400).pack(padx=15, pady=(5, 10))

    # Norwegian Voice
    inv_no = {v: k for k, v in NO_VOICES.items()}
    current_no = inv_no.get(config.get("voice_no", "nb-NO-PernilleNeural"), "Pernille (Female)")
    no_var = ctk.StringVar(value=current_no)

    ctk.CTkLabel(settings_frame, text="Norwegian Voice:", font=("Arial", 12, "bold")).pack(anchor="w", padx=15)
    ctk.CTkOptionMenu(settings_frame, variable=no_var, values=list(NO_VOICES.keys()), width=400).pack(padx=15, pady=(5, 15))

    # --- Hotkeys Section ---
    hotkey_frame = ctk.CTkFrame(window)
    hotkey_frame.pack(pady=10, padx=20, fill="x")
    
    dictation_text = format_hotkey(config.get("hotkey_dictation", "<ctrl>+<f9>"))
    if config.get("hotkey_dictation_alt"):
        dictation_text += "  or  " + format_hotkey(config["hotkey_dictation_alt"])

    ctk.CTkLabel(hotkey_frame, text="Dictation (Push-to-Talk):", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
    ctk.CTkLabel(hotkey_frame, text=dictation_text, font=("Arial", 12, "bold"), text_color="#00BFFF").grid(row=0, column=1, padx=15, pady=10, sticky="e")

    ctk.CTkLabel(hotkey_frame, text="Read Aloud:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=15, pady=10, sticky="w")
    ctk.CTkLabel(hotkey_frame, text=format_hotkey(config["hotkey_read_aloud"]), font=("Arial", 12, "bold"), text_color="#00BFFF").grid(row=1, column=1, padx=15, pady=10, sticky="e")
    
    hotkey_frame.grid_columnconfigure(0, weight=1)
    hotkey_frame.grid_columnconfigure(1, weight=1)

    # --- Save & Exit ---
    show_again_var = ctk.BooleanVar(value=config["show_tutorial_on_startup"])
    ctk.CTkCheckBox(window, text="Show setup window on startup", variable=show_again_var).pack(pady=(15, 10))

    def save_and_close():
        config["show_tutorial_on_startup"] = show_again_var.get()
        config["mic_device_name"] = mic_var.get()
        config["voice_en"] = EN_VOICES[en_var.get()]
        config["voice_no"] = NO_VOICES[no_var.get()]
        save_config(config)
        window.destroy()

    ctk.CTkButton(window, text="Save & Start Engine", font=("Arial", 14, "bold"), command=save_and_close).pack(pady=10)

    window.mainloop()