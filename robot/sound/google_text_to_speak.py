# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 14:19:36 2020

@author: tclemens
"""

"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
import os
import sys

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/My Project-73d3d70986a5.json"

text = sys.argv[1]
filename = "{}".format(sys.argv[2])

# Instantiates a client
client = texttospeech.TextToSpeechClient()

# Set the text input to be synthesized
synthesis_input = texttospeech.SynthesisInput(text=text)

# Build the voice request, select the language code ("en-US") and the ssml
# voice gender ("neutral")
voice = texttospeech.VoiceSelectionParams(
    language_code="en-GB-Standard-F", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16
)

# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# The response's audio_content is binary.
os.chdir("/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/")
with open("{}.wav".format(filename), "wb") as out:
    # Write the response to the output file.
    out.write(response.audio_content)
    print('Audio content written to file "{}.wav"'.format(filename))
