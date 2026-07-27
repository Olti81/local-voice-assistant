import os
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
import torch
import pyaudio
import numpy as np
import time
import threading
from faster_whisper import WhisperModel

MODEL_DIR = "./.models/whisper"

def prime_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    WhisperModel("base", device="cuda", compute_type="float16", download_root=MODEL_DIR)
    print("[OK] STT Model primed.")

class STTEngine:
    def __init__(self):
        self.model = WhisperModel("base", device="cuda", compute_type="float16", download_root=MODEL_DIR)
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False

    def start_recording(self):
        import json
        self.is_recording = True
        self.frames = []
        
        # Pull selected mic from config
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
        except Exception:
            config = {}
            
        mic_config = config.get("mic_device_name", "Default Microphone")
        mic_idx = None
        
        # If a specific mic was chosen, parse the [ID] out of the string
        if mic_config != "Default Microphone" and mic_config.startswith("["):
            try:
                mic_idx = int(mic_config.split("]")[0][1:])
            except Exception:
                mic_idx = None

        # Pass the specific mic index to PyAudio
        self.stream = self.p.open(
            format=pyaudio.paInt16, 
            channels=1, 
            rate=16000, 
            input=True, 
            input_device_index=mic_idx,
            frames_per_buffer=1024
        )
        
        def _record():
            while self.is_recording:
                try:
                    data = self.stream.read(1024, exception_on_overflow=False)
                    self.frames.append(np.frombuffer(data, dtype=np.int16))
                except Exception:
                    break
                
        threading.Thread(target=_record, daemon=True).start()

    def stop_recording_and_transcribe(self):
        self.is_recording = False
        
        # Give the background audio thread 100ms to exit cleanly
        time.sleep(0.1)
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
        
        if not self.frames: return ""
        
        audio_data = np.concatenate(self.frames).astype(np.float32) / 32768.0
        segments, _ = self.model.transcribe(audio_data, beam_size=5)
        return " ".join([segment.text for segment in segments]).strip()

    def cancel_recording(self):
        self.is_recording = False
        time.sleep(0.1)
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
        self.frames = []