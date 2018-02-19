# Version check
import sys
assert sys.version_info >= (3,), "Python 3 is required"

# Imports
import os.path

import numpy as np
from scipy.io import wavfile

# Constants
DB_DIR = os.path.join(os.path.dirname(__file__), "artists")
ARTISTS = (
    "taylorswift",
)
SONG_NAMES = {
    "ourref1": ("ourquery1", "ourquery2"),
    "ourref2": ("ourquery3", "ourquery4"),
}
BEAT_TIME = 1

# Utilities
def get_beats(artist, song_name):
    base_name = os.path.join(DB_DIR, artist, "{}_{}".format(artist, song_name))
    sample_rate, audio = wavfile.read(base_name+".wav")
    annotations = np.genfromtxt(base_name+".csv", delimiter=",")

    beats = annotations.shape[0]
    beat_width = int(BEAT_TIME*sample_rate)

    beat_names = []
    beat_array = np.zeros((beats, beat_width), dtype=audio.dtype)
    for i, (time, beat_name) in enumerate(annotations):
        start = int((time - BEAT_TIME/2)*sample_rate)
        if start < 0:
            start = 0
        stop = start + beat_width
        beat_array[i] = audio[start:stop]
        beat_names.append(float(beat_name))

    return beat_array, beat_names

# Main
if __name__ == "__main__":
    print(get_beats("taylorswift", "ourquery1"))
