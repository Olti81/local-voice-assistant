import threading
import customtkinter as ctk

class SettingsUI:
    def __init__(self, root, tts_engine, stt_engine):
        self.root = root
        self.tts = tts_engine
        self.stt = stt_engine
        self.window = None
        self.is_recording = False

    def run(self):
        self.root.after(0, self._build_window)

    def _build_window(self):
        # Prevent opening multiple settings windows
        if self.window and self.window.winfo_exists():
            self.window.focus()
            return
            
        self.window = ctk.CTkToplevel(self.root)
        self.window.title("Voice Assistant - Test Menu")
        self.window.geometry("400x450")
        self.window.attributes("-topmost", True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # --- TTS Section ---
        ctk.CTkLabel(self.window, text="🔊 Test Text-to-Speech", font=("Arial", 16, "bold")).pack(pady=(20, 5))
        self.tts_input = ctk.CTkEntry(self.window, width=350, placeholder_text="Type something to read out loud...")
        self.tts_input.pack(pady=10)
        
        self.tts_btn = ctk.CTkButton(self.window, text="Play Audio", command=self.test_tts)
        self.tts_btn.pack(pady=5)

        ctk.CTkFrame(self.window, height=2, width=350, fg_color="gray").pack(pady=20)

        # --- STT Section ---
        ctk.CTkLabel(self.window, text="🎙️ Test Speech-to-Text", font=("Arial", 16, "bold")).pack(pady=(5, 5))
        
        self.stt_btn = ctk.CTkButton(self.window, text="Start Recording", command=self.test_stt, fg_color="#8B0000", hover_color="#600000")
        self.stt_btn.pack(pady=10)

        self.stt_result = ctk.CTkTextbox(self.window, width=350, height=100)
        self.stt_result.pack(pady=10)

    def _on_close(self):
        if self.window:
            self.window.destroy()
            self.window = None

    def test_tts(self):
        text = self.tts_input.get()
        if text.strip():
            self.tts_btn.configure(text="Playing...", state="disabled")
            self.tts.play_text(text, on_complete=self._reset_tts_btn)

    def _reset_tts_btn(self):
        self.root.after(0, lambda: self.tts_btn.configure(text="Play Audio", state="normal") if self.window and self.window.winfo_exists() else None)

    def test_stt(self):
        if not self.is_recording:
            self.is_recording = True
            self.stt_btn.configure(text="Stop & Transcribe", fg_color="#006400", hover_color="#004b00")
            self.stt.start_recording()
            self.stt_result.delete("1.0", "end")
            self.stt_result.insert("1.0", "Listening...")
        else:
            self.is_recording = False
            self.stt_btn.configure(text="Processing...", state="disabled")
            threading.Thread(target=self._process_stt, daemon=True).start()

    def _process_stt(self):
        try:
            text = self.stt.stop_recording_and_transcribe()
            self.root.after(0, self._update_stt_ui, text)
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            self.root.after(0, self._update_stt_ui, error_msg)

    def _update_stt_ui(self, text):
        if self.window and self.window.winfo_exists():
            self.stt_result.delete("1.0", "end")
            self.stt_result.insert("1.0", text if text else "No speech detected.")
            self.stt_btn.configure(text="Start Recording", fg_color="#8B0000", hover_color="#600000", state="normal")