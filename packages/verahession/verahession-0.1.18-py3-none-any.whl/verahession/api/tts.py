import requests
import wave

class tts_interface:
    def __init__(self, API, gender, accent):
        self.API = API
        self.gender = gender
        self.accent = accent
    
    def tts(self, text):
        # --- REQUEST PAYLOAD ---
        payload = {
            "text": text,
            "API": self.API_KEY,
            "gender": gender,
            "accent": accent
        }

        # --- SEND TO /tts ---
        print("[VERA TTS] Sending TTS request...")
        response = requests.post(TTS_URL, json=payload)

        if response.status_code == 200:
            print("[VERA TTS] Audio received. Playing...")
            audio_bytes = io.BytesIO(response.content)

            # Read WAV from memory
            with wave.open(audio_bytes, 'rb') as wf:
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )

                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)

                stream.stop_stream()
                stream.close()
                p.terminate()

            print("[VERA TTS] Playback finished.")
        else:
            print(f"[VERA TTS] Error {response.status_code}: {response.text}")