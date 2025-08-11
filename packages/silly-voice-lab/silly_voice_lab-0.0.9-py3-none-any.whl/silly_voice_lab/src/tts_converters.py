
from pathlib import Path
import os

import pyttsx3
from pydub import AudioSegment
import requests

from .helpers import SETTINGS



def debug_voice_converter(char, title, text, file_path):
    """Génère un MP3 localement avec pyttsx3."""
    wav_path = Path(file_path) / f"{title}.wav"
    mp3_path = Path(file_path) / f"{title}.mp3"
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    engine = pyttsx3.init()
    if char.gender == "f":
        print("= female voice")
        engine.setProperty('voice', 'english+f1')
    else:
        engine.setProperty('voice', 'english+m1')
    engine.save_to_file(text, str(wav_path))
    engine.runAndWait()
    # Conversion WAV → MP3
    sound = AudioSegment.from_wav(wav_path)
    sound.export(mp3_path, format="mp3")

    # delete the wav file
    if os.path.exists(wav_path):
        os.remove(wav_path)
    print(f"Deleted temporary file: {wav_path}")


def debug_text_converter(file_path, title, text):
    # Save txt files simulating a real call to ElevenLabs
    file_path = Path(file_path) / f"debug-{title}.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    # file_path = f"{file_path}/debug-{title}.txt"
    with open(file_path, "w") as f:
        f.write(text)


def eleven_labs_converter(char, title, text, file_path):
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{char.voice_id}?output_format=mp3_44100_128",
    headers={
        "xi-api-key": f"{SETTINGS.elevenlabs_api_key}"
    },
    json={
        "text": text,
        "model_id": "eleven_multilingual_v2"
    },
    )
    if response.status_code != 200:
        print(f"Something when wrong with {char.name}")

    file_path = Path(file_path) / f"{title}.mp3"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    # Save MP3
    with open(file_path, "wb") as f:
        f.write(response.content)