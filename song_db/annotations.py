# Imports
import os.path
from collections import OrderedDict

import numpy as np

from .util import *


# Path handling
def get_base_path_audio_file(artist, song_name):
    """Get the base song path for the given artist and song."""
    song_path = os.path.join(DATA_DIR, artist, "{}_{}".format(artist, song_name))
    base_path, audio_file = os.path.split(song_path)
    return base_path, audio_file

def annotation_file(artist, song_name):
    """Get the path to the annotation file for the given song."""
    base_path, audio_file = get_base_path_audio_file(artist, song_name)
    annotation_path = os.path.join(base_path, audio_file + ".csv")
    for path in (annotation_path, annotation_path.replace("0", "")):
        if os.path.exists(path):
            return path
    raise IOError("could not find annotation for artist %s and song %s" % (artist, song_name))

def get_song_path(artist, song_name):
    """Get the path to the given song."""
    base_path, audio_file = get_base_path_audio_file(artist, song_name)
    audio_path = os.path.join(base_path, audio_file + ".wav")
    for path in (audio_path, audio_path.replace("0", "")):
        if os.path.exists(path):
            return path
    raise IOError("could not find annotation for artist %s and song %s" % (artist, song_name))


# Beat extraction
def get_annotations(artist, song_name):
    """Gets the annotations for the given song path."""
    return np.genfromtxt(annotation_file(artist, song_name), delimiter=",")

def get_beats(artist, song_name, beat_width=DEFAULT_BEAT_WIDTH):
    """Return an array of beats and a list of their corresponding names."""
    if beat_width is None:
        beat_width = DEFAULT_BEAT_WIDTH
    beat_time = beat_width/SAMPLE_RATE

    song_path = get_song_path(artist, song_name)
    audio = get_audio(song_path)

    annotations = get_annotations(artist, song_name)
    beats = annotations.shape[0]

    beat_names = []
    beat_array = np.zeros((beats, beat_width), dtype=audio.dtype)
    for i, (time, beat_name) in enumerate(annotations):
        start = int((time - beat_time/2)*SAMPLE_RATE)
        if start < 0:
            start = 0
        stop = start + beat_width
        beat_array[i] = audio[start:stop]
        beat_names.append(float(beat_name))

    return beat_array, beat_names


# Alignment
def align_ref(ref_beat_array, ref_beat_names, query_beat_array, query_beat_names):
    """Snip the beats from the given reference to match the given query."""
    aligned_ref = np.zeros(query_beat_array.shape, dtype=ref_beat_array.dtype)
    for i, (query_beat_name, query_beat) in enumerate(zip(query_beat_names, query_beat_array)):
        aligned_ref[i] = ref_beat_array[ref_beat_names.index(query_beat_name)]
    return aligned_ref


# Internal endpoint
def get_pairs_for_ref(artist, ref_name, beat_width=DEFAULT_BEAT_WIDTH):
    """Return an iterator of aligned (ref_beat_array, query_beat_array) pairs for the given ref.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    ref_beat_array, ref_beat_names = get_beats(artist, ref_name, beat_width)

    for query_name in ANNOTATED_SONG_NAMES[artist][ref_name]:
        query_beat_array, query_beat_names = get_beats(artist, query_name, beat_width)

        aligned_ref = align_ref(ref_beat_array, ref_beat_names, query_beat_array, query_beat_names)
        assert aligned_ref.shape == query_beat_array.shape, (aligned_ref.shape, query_beat_array.shape)
        yield aligned_ref, query_beat_array


# External endpoints
def get_ref_query_pairs(artist, beat_width=DEFAULT_BEAT_WIDTH):
    """Return an iterator of all aligned (ref_beat_array, query_beat_array) pairs for the given artist.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    for ref_name in ANNOTATED_SONG_NAMES[artist]:
        yield from get_pairs_for_ref(artist, ref_name, beat_width)

def data_by_artist(beat_width=DEFAULT_BEAT_WIDTH):
    """Return a dictionary mapping artists to iterators over their ref_query_pairs.
    Since each dictionary value is an iterator, no work is done until that value is iterated over."""
    return OrderedDict(
        (artist, get_ref_query_pairs(artist, beat_width))
        for artist in ARTISTS
    )

def data_by_song(beat_width=DEFAULT_BEAT_WIDTH):
    """Return a dictionary mapping (artist, ref_name) pairs to iterators over their ref_query_pairs.
    Since each dictionary value is an iterator, no work is done until that value is iterated over."""
    return OrderedDict(
        ((artist, ref_name), get_pairs_for_ref(artist, ref_name, beat_width))
        for artist, ref_name in ARTIST_REF_PAIRS
    )
