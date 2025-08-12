#! /usr/bin/env python3

import os
from pathlib import Path
from dataclasses import dataclass
from pprint import pprint
import configparser

BASE_DIR = os.getcwd()

@dataclass
class Configuration:
    input_folder: str = "scenario"
    output_folder: str = "voices"
    debug: bool = True
    converter: str = "dev"
    elevenlabs_api_key: str = "no_key"
    female_voice_id: str = "default"
    male_voice_id: str = "default"


def get_config(file_name: str="dialogues.cfg") -> Configuration:
    config_file = Path(Path(BASE_DIR), Path(file_name))
    print(config_file)
    if not os.path.exists(Path(config_file)):
        print("No config file found, initialize a project first with the command 'init'")
        exit(0)
        return Configuration()
    print(f"Config file '{file_name}' loading...")
    try:
        config = configparser.ConfigParser()
        config.read(config_file)

        output_folder = config["folders"]["output_folder"]
        input_folder = config["folders"]["input_folder"]
        elevenlabs_api_key = config["secrets"]["elevenlabs_api_key"]
        debug = config["app"]["debug"] == "1"
        converter = config["app"]["converter"]
        female_voice_id = config["dev"]["female_voice_id"]
        male_voice_id = config["dev"]["male_voice_id"]


        configuration = Configuration(
            output_folder=output_folder,
            input_folder=input_folder,
            elevenlabs_api_key=elevenlabs_api_key,
            debug=debug,
            converter=converter,
            female_voice_id=female_voice_id,
            male_voice_id=male_voice_id,
        )
    except Exception as e:
        print(f"Error reading the config file: {e}")
        exit(0)
    return configuration

def dprint(CONF: Configuration, *args, **kwargs):
    if CONF.debug:
        print(*args, **kwargs)

def dpprint(CONF: Configuration, *args, **kwargs):
    if CONF.debug:
        pprint(*args, **kwargs)
