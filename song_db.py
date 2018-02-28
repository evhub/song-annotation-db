# Imports
import os
import os.path
from collections import OrderedDict

import numpy as np
from scipy.io import wavfile

# Data constants
BEAT_TIME = 0.5
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
SONG_NAMES = OrderedDict(
    ourref01=("ourquery1", "ourquery2"),
    ourref02=("ourquery3", "ourquery4"),
)
SAMPLE_RATE = 22050

# Path constants
BASE_DIR = os.path.dirname(__file__)

DATA_DIR = os.path.join(BASE_DIR, "data")

DB_DIR = os.path.join(BASE_DIR, "db")
REFS_DIR = os.path.join(DB_DIR, "refs")
QUERIES_DIR = os.path.join(DB_DIR, "queries")

DB_INDEX_FILE = os.path.join(BASE_DIR, "audio_paths.txt")

FEATURES_FILE = os.path.join(BASE_DIR, "features.npy")

# Song ordering
ARTIST_REF_PAIRS = [
    (artist, ref_name)
    for artist in ARTISTS
    for ref_name in SONG_NAMES
]

def pair_to_label(song_pair):
    """Convert an artist_ref_pair identifying a song into an integer label for that song."""
    return ARTIST_REF_PAIRS.index(song_pair)

def label_to_pair(song_label):
    """Convert a label produced by pair_to_label back into the identifying artist_ref_pair."""
    return ARTIST_REF_PAIRS[song_label]

# Path handling
def annotation_file(song_path):
    """Get the path to the annotation file for the given song."""
    base_path, audio_file = os.path.split(song_path)
    return os.path.join(base_path, audio_file.replace("0", "") + ".csv")

def audio_file(song_path):
    """Get the path to the audio file for the given song."""
    return song_path + ".wav"

def get_song_path(artist, song_name):
    """Get the path to the given song."""
    return os.path.join(DATA_DIR, artist, "{}_{}".format(artist, song_name))

def db_file(song_pair, query_index, beat_index):
    """Get the name of the database file to save the given song_pair of the given index."""
    fname = "{}_{}_{}.wav".format(pair_to_label(song_pair), query_index, beat_index)
    return os.path.join(REFS_DIR, fname), os.path.join(QUERIES_DIR, fname)

# Beat extraction
BEAT_WIDTH = int(BEAT_TIME*SAMPLE_RATE)

def get_beats(artist, song_name):
    """Return an array of beats and a list of their corresponding names."""
    song_path = get_song_path(artist, song_name)
    sample_rate, audio = wavfile.read(audio_file(song_path))
    assert sample_rate == SAMPLE_RATE, (sample_rate, SAMPLE_RATE)

    annotations = np.genfromtxt(annotation_file(song_path), delimiter=",")
    beats = annotations.shape[0]

    beat_names = []
    beat_array = np.zeros((beats, BEAT_WIDTH), dtype=audio.dtype)
    for i, (time, beat_name) in enumerate(annotations):
        start = int((time - BEAT_TIME/2)*SAMPLE_RATE)
        if start < 0:
            start = 0
        stop = start + BEAT_WIDTH
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

def get_pairs_for_ref(artist, ref_name):
    """Return an iterator of aligned (ref_beat_array, query_beat_array) pairs for the given ref.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    ref_beat_array, ref_beat_names = get_beats(artist, ref_name)

    for query_name in SONG_NAMES[ref_name]:
        query_beat_array, query_beat_names = get_beats(artist, query_name)

        aligned_ref = align_ref(ref_beat_array, ref_beat_names, query_beat_array, query_beat_names)
        assert aligned_ref.shape == query_beat_array.shape, (aligned_ref.shape, query_beat_array.shape)
        yield aligned_ref, query_beat_array

# Data endpoints
def get_ref_query_pairs(artist):
    """Return an iterator of all aligned (ref_beat_array, query_beat_array) pairs for the given artist.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    for ref_name in SONG_NAMES:
        yield from get_pairs_for_ref(artist, ref_name)

def data_by_song():
    """Return a dictionary mapping (artist, ref_name) pairs to iterators over their ref_query_pairs.
    Since each dictionary value is an iterator, no work is done until that value is iterated over."""
    return OrderedDict(
        ((artist, ref_name), get_pairs_for_ref(artist, ref_name))
        for artist, ref_name in ARTIST_REF_PAIRS
    )

def data_by_artist():
    """Return a dictionary mapping artists to iterators over their ref_query_pairs.
    Since each dictionary value is an iterator, no work is done until that value is iterated over."""
    return OrderedDict(
        (artist, get_ref_query_pairs(artist))
        for artist in ARTISTS
    )

# Database creation
def write_db():
    """Write the database to disk."""
    for song_pair, ref_query_pairs in data_by_song().items():
        for query_index, (ref_beat_array, query_beat_array) in enumerate(ref_query_pairs):
            for beat_index, (ref_audio, query_audio) in enumerate(zip(ref_beat_array, query_beat_array)):
                ref_fname, query_fname = db_file(song_pair, query_index, beat_index)
                wavfile.write(ref_fname, SAMPLE_RATE, ref_audio)
                wavfile.write(query_fname, SAMPLE_RATE, query_audio)

def make_db_dirs():
    """Generate the necessary database directories."""
    made_dirs = False
    for db_dir in (DB_DIR, REFS_DIR, QUERIES_DIR):
        if not os.path.exists(db_dir):
            os.mkdir(db_dir)
            made_dirs = True
    return made_dirs

if __name__ == "__main__":
    print("Generating database directories...")
    made_dirs = make_db_dirs()
    if made_dirs:
        print("Writing database...")
        write_db()
    else:
        print("Using existing database...")

# Database indexing
def index_db():
    """Return an iterator of (is_ref, path) for all the files in the database.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    for ref_file in os.listdir(REFS_DIR):
        yield 1, os.path.abspath(ref_file)
    for query_file in os.listdir(QUERIES_DIR):
        yield 0, os.path.abspath(query_file)

def write_audio_paths():
    """Write line-separated paths to all the audio files in the database."""
    with open(DB_INDEX_FILE, "w") as audio_paths_file:
        audio_paths_file.writelines(path + "\n" for (is_ref, path) in index_db())

if __name__ == "__main__":
    print("Generating database index...")
    write_audio_paths()

# Database endpoints
def read_db():
    """Return an iterator of (label, is_ref, audio) triples for all entries in the database.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    for is_ref, path in index_db():
        fname = os.path.basename(path)
        label, query_index, beat_index = map(int, os.path.splitext(fname)[0].split("_"))

        sample_rate, audio = wavfile.read(path)
        assert sample_rate == SAMPLE_RATE, (sample_rate, SAMPLE_RATE)

        yield label, is_ref, audio

# Example of reading the database
# if __name__ == "__main__":
    # print("Reading from database...")
    # for (artist, ref_name), ref_query_pairs in data_by_song().items():
    #     print("song {} of artist {}".format(ref_name, artist))
    #     for ref, query in ref_query_pairs:
    #         beats, beat_width = query.shape
    #         print("\t{} beats of width {}".format(beats, beat_width))
