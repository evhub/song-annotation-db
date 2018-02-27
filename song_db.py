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
    "bigkrit",
    "chromeo",
    "deathcabforcutie",
    "foofighters",
    "kanyewest",
    "maroon5",
    "onedirection",
    "t.i",
    "taylorswift",
    "tompetty",
)
SONG_NAMES = {
    "ourref01": ("ourquery1", "ourquery2"),
    "ourref02": ("ourquery3", "ourquery4"),
}
BEAT_TIME = 0.5

# Utilities
def annotation_file(song_path):
    """Get the path to the annotation file for the given song."""
    base_path, audio_file = os.path.split(song_path)
    return os.path.join(base_path, audio_file.replace("0", "") + ".csv")

def audio_file(song_path):
    """Get the path to the audio file for the given song."""
    return song_path + ".wav"

def get_song_path(artist, song_name):
    """Get the path to the given song."""
    return os.path.join(DB_DIR, artist, "{}_{}".format(artist, song_name))

def audio_paths():
    """A generator of paths to all the different audio files."""
    for artist in ARTISTS:
        for ref_name, query_names in SONG_NAMES.items():
            yield audio_file(get_song_path(artist, ref_name))
            for query_name in query_names:
                yield audio_file(get_song_path(artist, query_name))

def write_audio_paths(fname="audio_paths.txt"):
    """Write line-separated paths to all the different audio files in the database."""
    with open(fname, "w") as audio_paths_file:
        audio_paths_file.writelines(path+"\n" for path in audio_paths())

def get_beats(artist, song_name):
    """Returns an array of beats and a list of their corresponding names."""
    song_path = get_song_path(artist, song_name)
    sample_rate, audio = wavfile.read(audio_file(song_path))
    annotations = np.genfromtxt(annotation_file(song_path), delimiter=",")

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

def align_ref(ref_beat_array, ref_beat_names, query_beat_array, query_beat_names):
    """Snips the beats from the given reference to match the given query."""
    aligned_ref = np.zeros(query_beat_array.shape, dtype=ref_beat_array.dtype)
    for i, (query_beat_name, query_beat) in enumerate(zip(query_beat_names, query_beat_array)):
        aligned_ref[i] = ref_beat_array[ref_beat_names.index(query_beat_name)]
    return aligned_ref

def get_ref_query_pairs(artist, ref_name=None):
    """Returns an iterator of aligned (ref_beat_array, query_beat_array) pairs.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    if ref_name is None:
        song_names = SONG_NAMES.items()
    else:
        song_names = [(ref_name, SONG_NAMES[ref_name])]
    for ref_name, query_names in song_names:
        ref_beat_array, ref_beat_names = get_beats(artist, ref_name)

        for query_name in query_names:
            query_beat_array, query_beat_names = get_beats(artist, query_name)

            aligned_ref = align_ref(ref_beat_array, ref_beat_names, query_beat_array, query_beat_names)
            assert aligned_ref.shape == query_beat_array.shape, (aligned_ref.shape, query_beat_array.shape)
            yield aligned_ref, query_beat_array

def data_dict():
    """Returns a dictionary mapping artists to iterators over their ref_query_pairs.
    Since each dictionary value is an iterator, no work is done until that value is iterated over."""
    return {artist: get_ref_query_pairs(artist) for artist in ARTISTS}

# Main
if __name__ == "__main__":
    write_audio_paths()
    for artist, ref_query_pairs in data_dict().items():
        print("artist {}".format(artist))
        for ref, query in ref_query_pairs:
            beats, beat_width = query.shape
            print("\t{} beats of width {}".format(beats, beat_width))
