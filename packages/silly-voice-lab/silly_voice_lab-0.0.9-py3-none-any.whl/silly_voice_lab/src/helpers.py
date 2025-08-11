#! /usr/bin/env python3

import os
from dataclasses import dataclass
from pprint import pprint
import configparser

BASE_DIR = os.getcwd()

@dataclass
class Settings:
    input_folder: str = "scenario"
    output_folder: str = "voices"
    debug: bool = True
    converter: str = "dev"
    elevenlabs_api_key: str = "no_key"


def get_config():
    if not os.path.exists(BASE_DIR + "/dialogues.cfg"):
        return Settings()
    print(BASE_DIR + "/dialogues.cfg")
    config = configparser.ConfigParser()
    config.read(BASE_DIR + "/dialogues.cfg")

    output_folder = config["folders"]["output_folder"]
    input_folder = config["folders"]["input_folder"]
    elevenlabs_api_key = config["secrets"]["elevenlabs_api_key"]
    debug = config["app"]["debug"] == "1"
    converter = config["app"]["converter"]

    settings = Settings(
        output_folder=output_folder,
        input_folder=input_folder,
        elevenlabs_api_key=elevenlabs_api_key,
        debug=debug,
        converter=converter
    )
    return settings

SETTINGS = get_config()


def dprint(*args, **kwargs):
    if SETTINGS.debug:
        print(*args, **kwargs)

def dpprint(*args, **kwargs):
    if SETTINGS.debug:
        pprint(*args, **kwargs)
