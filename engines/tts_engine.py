import os
import threading
import asyncio
import tempfile
import uuid
import edge_tts
from langdetect import detect, DetectorFactory

# Suppress the Pygame startup text in the console
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# Seed the detector for consistent language guessing
DetectorFactory.seed = 0

def prime_model():
    # Edge-TTS is cloud-based, so no massive local downloads are needed here!
    print("[OK] Edge-TTS Auto-Detect Engine primed.")

class TTSEngine:
    def __init__(self):
        # Initialize the Pygame audio mixer
        pygame.mixer.init()
        self.is_playing = False
        self.current_audio_file = None

    def detect_language_and_voice(self, text):
        """Analyzes the text and routes to the correct native voice based on config."""
        import json
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
        except Exception:
            config = {}

        voice_en = config.get("voice_en", "en-US-AriaNeural")
        voice_no = config.get("voice_no", "nb-NO-PernilleNeural")

        try:
            lang = detect(text)
            if lang in ['no', 'nb', 'nn']:
                print(f"[*] Detected Norwegian -> Routing to {voice_no}")
                return voice_no
            else:
                print(f"[*] Detected English -> Routing to {voice_en}")
                return voice_en
        except Exception:
            return voice_en

    def play_text(self, text, on_complete=None):
        self.is_playing = True
        voice = self.detect_language_and_voice(text)
        
        # Generate a unique temp file for this specific read-aloud
        self.current_audio_file = os.path.join(tempfile.gettempdir(), f"voice_assistant_{uuid.uuid4().hex}.mp3")

        def _play_async():
            try:
                # 1. Ask Microsoft to generate the MP3 and save it
                asyncio.run(self._generate_audio(text, voice))

                # 2. Load the file into the Pygame mixer and play
                pygame.mixer.music.load(self.current_audio_file)
                pygame.mixer.music.play()

                # 3. Keep the thread alive until the audio finishes naturally OR is canceled
                while pygame.mixer.music.get_busy() and self.is_playing:
                    pygame.time.Clock().tick(10)

            except Exception as e:
                print(f"[!] TTS Error: {e}")
            finally:
                self.is_playing = False
                # Unload to release the Windows file lock
                pygame.mixer.music.unload() 
                
                # Cleanup the temp file
                if os.path.exists(self.current_audio_file):
                    try:
                        os.remove(self.current_audio_file)
                    except Exception:
                        pass
                
                if on_complete: 
                    on_complete()

        # Run the generation and playback in a background thread
        threading.Thread(target=_play_async, daemon=True).start()

    async def _generate_audio(self, text, voice):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(self.current_audio_file)

    def stop_audio(self):
        """Instantly kills the audio playback when the cancel hotkey is pressed."""
        self.is_playing = False
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.unload()