import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


def recognize(content, lang, platform):
    # Instantiates a client
    sample_rate = {
        "vk": 48000,
        "tg": 16000,
    }
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=sample_rate[platform],
        language_code=lang)

    # Detects speech in the audio file
    response = client.recognize(config, audio)
    if len(response.results) > 0:
        result = response.results[0]
        return result.alternatives[0].transcript
    else:
        return "Could not recognize"
