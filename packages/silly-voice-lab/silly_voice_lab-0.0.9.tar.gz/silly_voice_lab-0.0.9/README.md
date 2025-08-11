# silly-voice-lab

A simple tool to create voiced dialogues with **ElevenLabs** for your projects.

## How it works

- Choose a working folder
then: `pip install silly_voice_lab`

- run `silly-voice-lab` to know more, `silly-voice-lab init` to get a strting pack.

Now that you have a dialogues.cfg file, configure it:

**dialogues.cfg**
```sh
[secrets]
# enter your own ElevenLab api key here
elevenlabs_api_key=your_api_key

[folders]
input_folder=scenario
output_folder=voices

[app]
debug=1
# converter can be [text | prod | dev]
converter=dev
```

- run the voice processing with `silly-voice-lab run`


## about the converters
- text: does not create real audio files, just text placeholders, usefull to test
- dev: use a local rough speech-to-text, usefull to prototype a project with real voices (but crappy voices !)
- prod: uses elevenlabs api to create the voices, you need a valid ElevenLab api key to do that.
