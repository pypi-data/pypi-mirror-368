#! /usr/bin/env python3


import os
import sys
from pathlib import Path

import pyttsx3
import yaml
import shutil


from silly_voice_lab.src.helpers import dprint, dpprint, get_config, Configuration
from silly_voice_lab.src.models import Character, Group
from silly_voice_lab.src.tts_converters import debug_text_converter, debug_voice_converter, eleven_labs_converter

VERSION = "0.1.1"
BASE_DIR = os.getcwd()


def get_groups(CONFIG) -> list[Group]:
    groups = []
    folder_path = Path(Path(BASE_DIR), Path(CONFIG.input_folder))
    for file in folder_path.glob("*.yaml"):
        dprint(CONFIG, f"\nReading {file.name} ...")

        with open(Path(Path(folder_path), Path(file.name)), "r", encoding="utf-8") as f:
            casting = yaml.safe_load(f)
            for group in casting:
                grp = Group(**group)
                grp.characters = [Character(**char) for char in grp.characters]
                groups.append(grp)
    return groups


def convert_text_to_speech(CONFIG: Configuration, char: Character, title: str, text: str, file_path: Path):
    # Create speech (POST /v1/text-to-speech/:voice_id)
    match CONFIG.converter:
        case "text":
            debug_text_converter(CONFIG, title, text, file_path)
        case "prod":
            eleven_labs_converter(CONFIG, char, title, text, file_path)
        case "dev":
            debug_voice_converter(CONFIG, char, title, text, file_path)


def get_scripts(CONFIG: Configuration, group: Group):
    group_folder_path = Path(Path(BASE_DIR), Path(CONFIG.input_folder), Path(group.folder))
    dprint(CONFIG, group_folder_path)
    for char in group.characters :
        dprint(CONFIG, f"\n# {char.name} is working on the scenario...")
        folder_path = Path(group_folder_path, Path(char.name))
        for file in folder_path.glob("*.yaml"):
            dprint(CONFIG, f"\nReading {file.name} ...")

            with open(Path(Path(folder_path), Path(file.name)), "r", encoding="utf-8") as f:
                scene_text = yaml.safe_load(f)
                for scene in scene_text:
                    category = scene['category']
                    dprint(CONFIG, f"\n{char.name} is recording the dialogues for {category} scenes:")
                    voice_folder_path = Path(Path(BASE_DIR), Path(CONFIG.output_folder), Path(group.name), Path(char.name), Path(category))
                    for dialogue in scene['dialogues']:
                        dprint(CONFIG, f"- {dialogue['title']}")
                        convert_text_to_speech(CONFIG, char, dialogue['title'], dialogue['text'], voice_folder_path)


def start_process(file_name: str="dialogues.cfg") -> None:
    CONFIG = get_config(file_name)
    groups = get_groups(CONFIG)
    for group in groups:
        dpprint(CONFIG, group)
        get_scripts(CONFIG, group)


def pyttsx_infos() -> None:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # for i, voice in enumerate(voices):
    #     print(f"{i}: {voice.name} ({voice.gender if hasattr(voice, 'gender') else 'unknown'})")
    voices = engine.getProperty("voices")

    print(f"|{'Language':^45} | {'Code':^30}|")
    print("|" + "-" * 79 + "|")
    for voice in voices:
        print(f"|{voice.name:45} | {str(voice.languages):30}|")
        print("|" + "-" * 78 + "|")

def get_init_files() -> None:
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


def cmd() -> None:
    if len(sys.argv) == 2:
        if sys.argv[1] == "info":
            pyttsx_infos()
        if sys.argv[1] == "init":
            get_init_files()
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        file_name = sys.argv[2]
        start_process(file_name)
        print("Done !")

    else:
        title_bar = f" Silly Voice Lab v{VERSION} - A tool for ElevenLab voice creation "
        print(f"{title_bar:=^80}")
        print(
            """
- get a basic settings to start over:                               silly_voice_lab init
- get infos about your locally installed voices (for dev mode):     silly_voice_lab info
- run the voice creation process based on your settings:            silly_voice_lab run <your_config_file.cfg>

A usefull "readme" and the source code here:
https://github.com/byoso/ElevenLabs-tools

            """
            )


if __name__ == "__main__":
    cmd()