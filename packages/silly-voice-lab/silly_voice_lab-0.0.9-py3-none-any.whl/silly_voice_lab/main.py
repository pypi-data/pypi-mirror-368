#! /usr/bin/env python3


import os
import sys
from pathlib import Path

import pyttsx3
import yaml
import shutil


from silly_voice_lab.src.helpers import SETTINGS, dprint, dpprint
from silly_voice_lab.src.models import Character, Group
from silly_voice_lab.src.tts_converters import debug_text_converter, debug_voice_converter, eleven_labs_converter


BASE_DIR = os.getcwd()
converter = SETTINGS.converter


class TtsConverterError(Exception):
    pass


def get_groups() -> list[Group]:
    groups = []
    folder_path = Path(Path(BASE_DIR), Path(SETTINGS.input_folder))
    for file in folder_path.glob("*.yaml"):
        dprint(f"\nReading {file.name} ...")

        with open(Path(Path(folder_path), Path(file.name)), "r", encoding="utf-8") as f:
            casting = yaml.safe_load(f)
            for group in casting:
                grp = Group(**group)
                grp.characters = [Character(**char) for char in grp.characters]
                groups.append(grp)
    return groups


def convert_text_to_speech(char, title, text, file_path):
    # Create speech (POST /v1/text-to-speech/:voice_id)
    match SETTINGS.converter:
        case "text":
            debug_text_converter(file_path, title, text)
        case "prod":
            eleven_labs_converter(char, title, text, file_path)
        case "dev":
            debug_voice_converter(char, title, text, file_path)


def get_scripts(group: Group):
    group_folder_path = Path(Path(BASE_DIR), Path(SETTINGS.input_folder), Path(group.folder))
    dprint(group_folder_path)
    for char in group.characters :
        dprint(f"\n# {char.name} is working on the scenario...")
        folder_path = Path(group_folder_path, Path(char.name))
        for file in folder_path.glob("*.yaml"):
            dprint(f"\nReading {file.name} ...")

            with open(Path(Path(folder_path), Path(file.name)), "r", encoding="utf-8") as f:
                scene_text = yaml.safe_load(f)
                for scene in scene_text:
                    category = scene['category']
                    dprint(f"\n{char.name} is recording the dialogues for {category} scenes:")
                    voice_folder_path = Path(Path(BASE_DIR), Path(SETTINGS.output_folder+f"-{converter}"), Path(group.name), Path(char.name), Path(category))
                    for dialogue in scene['dialogues']:
                        dprint(f"- {dialogue['title']}")
                        convert_text_to_speech(char, dialogue['title'], dialogue['text'], voice_folder_path)


def start_process():
    groups = get_groups()
    for group in groups:
        dpprint(group)
        get_scripts(group)


def pyttsx_infos():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for i, voice in enumerate(voices):
        print(f"{i}: {voice.name} ({voice.gender if hasattr(voice, 'gender') else 'unknown'})")

def get_init_files():
    this_location = os.path.dirname(os.path.abspath(__file__))
    src_folder = this_location + "/src/init_project/"
    dest_folder = BASE_DIR
    for item in os.listdir(src_folder):
        s = os.path.join(src_folder, item)
        d = os.path.join(dest_folder, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)


def cmd():
    if len(sys.argv) > 1:
        if sys.argv[1] == "run":
            start_process()
            print("Done !")
        if sys.argv[1] == "info":
            pyttsx_infos()
        if sys.argv[1] == "init":
            get_init_files()
    else:
        print(f"{' Silly Voice Lab - Dialogue tool for ElevenLab voice creation ':=^80}")
        print(
            """
- get a basic settings to start over:                               silly_voice_lab init
- now you have a dialogues.cf file, configure it as you wish.
- get infos about your locally installed voices (for dev mode):     silly_voice_lab info
- run the voice creation process based on your settings:            silly_voice_lab run

            """
            )


if __name__ == "__main__":
    cmd()