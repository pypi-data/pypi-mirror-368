import requests
import wave
import io
import simpleaudio as sa

class tts_interface:
    def __init__(self, API_KEY, gender, accent):
        self.API_KEY = API_KEY
        self.gender = gender
        self.accent = accent
        self.TTS_URL = "https://hessiondynamics.com/tts"
    
    def tts(self, text):
        payload = {
            "text": text,
            "API": self.API_KEY,
            "gender": self.gender,
            "accent": self.accent
        }

        print("[VERA TTS] Sending TTS request...")
        response = requests.post(self.TTS_URL, json=payload)

        if response.status_code == 200:
            print("[VERA TTS] Audio received. Playing...")
            audio_bytes = io.BytesIO(response.content)

            with wave.open(audio_bytes, 'rb') as wf:
                audio_data = wf.readframes(wf.getnframes())
                play_obj = sa.play_buffer(
                    audio_data,
                    wf.getnchannels(),
                    wf.getsampwidth(),
                    wf.getframerate()
                )
                play_obj.wait_done()

            print("[VERA TTS] Playback finished.")
        else:
            print(f"[VERA TTS] Error {response.status_code}: {response.text}")
