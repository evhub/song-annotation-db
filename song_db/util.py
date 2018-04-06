# Imports
from .constants import *

import numpy as np
from scipy.io import wavfile


# Reading audio
def audio_file(song_path):
    """Get the path to the audio file for the given song."""
    if song_path.endswith(".wav"):
        return song_path
    else:
        return song_path + ".wav"

def get_audio(song_path):
    """Gets the audio for the given song path."""
    sample_rate, audio = wavfile.read(audio_file(song_path))
    assert sample_rate == SAMPLE_RATE, (sample_rate, SAMPLE_RATE)
    return audio


# Processing audio
def split_audio(audio, max_len=DEFAULT_SPLIT_LEN):
    """Split the given audio into chunks."""
    audio_len, = audio.shape
    audio_indices = list(range(max_len, audio_len, max_len))
    return np.split(audio, audio_indices)
