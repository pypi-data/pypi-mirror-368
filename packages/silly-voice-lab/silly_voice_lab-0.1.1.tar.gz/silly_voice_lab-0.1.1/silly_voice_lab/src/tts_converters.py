
from pathlib import Path
import os

import pyttsx3
from pydub import AudioSegment
import requests

from .helpers import Configuration, dprint
from .models import Character


def debug_voice_converter(CONFIG: Configuration, char: Character, title: str, text: str, file_path: Path) -> None:
    """Génère un MP3 localement avec pyttsx3."""
    title_wav = title + ".wav"
    title_mp3 = title + ".mp3"
    wav_path = Path(Path(file_path), Path(title_wav))
    mp3_path = Path(Path(file_path), Path(title_mp3))
    if os.path.exists(Path(mp3_path)):
        dprint(CONFIG, f"skiped {title_mp3}")
        return
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    engine = pyttsx3.init()
    if char.gender == "f":
        dprint(CONFIG, "= female voice")
        engine.setProperty('voice', CONFIG.female_voice_id)
    else:
        engine.setProperty('voice', CONFIG.male_voice_id)
    engine.save_to_file(text, str(wav_path))
    engine.runAndWait()
    # Conversion WAV → MP3
    sound = AudioSegment.from_wav(wav_path)
    sound.export(mp3_path, format="mp3")

    # delete the wav file
    if os.path.exists(wav_path):
        os.remove(wav_path)
    dprint(CONFIG, f"Deleted temporary file: {wav_path}")


def debug_text_converter(CONFIG: Configuration, title: str, text:str, file_path: Path) -> None:
    """Save txt files simulating a real call to ElevenLabs"""
    file_path = Path(file_path) / f"{title}.txt"
    if os.path.exists(Path(file_path)):
        dprint(CONFIG, f"skiped {title}")
        return
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        f.write(text)


def eleven_labs_converter(CONFIG: Configuration, char: Character, title: str, text:str, path:Path) -> None:
    file_path = Path(path) / f"{title}.mp3"
    if os.path.exists(Path(file_path)):
        dprint(CONFIG, f"skiped {title}")
        return
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{char.voice_id}?output_format=mp3_44100_128",
    headers={
        "xi-api-key": f"{CONFIG.elevenlabs_api_key}"
    },
    json={
        "text": text,
        "model_id": "eleven_multilingual_v2"
    },
    )
    if response.status_code != 200:
        dprint(CONFIG, f"Something when wrong with {char.name}")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    # Save MP3
    with open(file_path, "wb") as f:
        f.write(response.content)