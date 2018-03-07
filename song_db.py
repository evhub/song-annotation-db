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

def get_audio(song_path):
    """Gets the audio for the given song path."""
    sample_rate, audio = wavfile.read(audio_file(song_path))
    assert sample_rate == SAMPLE_RATE, (sample_rate, SAMPLE_RATE)
    return audio

def get_annotations(song_path):
    """Gets the annotations for the given song path."""
    return np.genfromtxt(annotation_file(song_path), delimiter=",")

def get_beats(artist, song_name):
    """Return an array of beats and a list of their corresponding names."""
    song_path = get_song_path(artist, song_name)

    audio = get_audio(song_path)

    annotations = get_annotations(song_path)
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

if __name__ == "__main__":
    print("Reading data...")
    for (artist, ref_name), ref_query_pairs in data_by_song().items():
        print("song {} of artist {}".format(ref_name, artist))
        for ref, query in ref_query_pairs:
            beats, beat_width = query.shape
            print("\t{} beats of width {}".format(beats, beat_width))

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
def get_ref_paths():
    """Same as get_audio_paths but just for refs."""
    for ref_file in os.listdir(REFS_DIR):
        ref_path = os.path.join(REFS_DIR, ref_file)
        yield os.path.abspath(ref_path)

def get_query_paths():
    """Same as get_audio_paths but just for queries."""
    for query_file in os.listdir(QUERIES_DIR):
        query_path = os.path.join(QUERIES_DIR, query_file)
        yield os.path.abspath(query_path)

def get_audio_paths():
    """Return an iterator of paths to all the files in the database.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    yield from get_ref_paths()
    yield from get_query_paths()

def write_audio_paths():
    """Write line-separated paths to all the audio files in the database."""
    with open(DB_INDEX_FILE, "w") as audio_paths_file:
        audio_paths_file.writelines(path + "\n" for path in get_audio_paths())

if __name__ == "__main__":
    print("Generating database index...")
    write_audio_paths()

# Database endpoints
def index_db():
    """Return an iterator of all (label, query_index, beat_index, ref_path, query_path) tuples.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    for ref_path in get_ref_paths():
        fname = os.path.basename(ref_path)
        label, query_index, beat_index = map(int, os.path.splitext(fname)[0].split("_"))
        query_path = os.path.join(QUERIES_DIR, fname)
        yield label, query_index, beat_index, ref_path, query_path

def read_db():
    """Return an iterator of all (label, query_index, beat_index, ref_beat_array, query_beat_array) tuples.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    for label, query_index, beat_index, ref_path, query_path in index_db():

        sample_rate, ref_beat_array = wavfile.read(ref_path)
        assert sample_rate == SAMPLE_RATE, (sample_rate, SAMPLE_RATE)

        sample_rate, query_beat_array = wavfile.read(query_path)
        assert sample_rate == SAMPLE_RATE, (sample_rate, SAMPLE_RATE)

        yield label, query_index, beat_index, ref_beat_array, query_beat_array

# Feature handling
def get_raw_features():
    """Load in features file generated by <https://github.com/evhub/transfer_learning_music>."""
    return np.load(FEATURES_FILE)

def split_arr(arr):
    """Split the given 2D array in half."""
    n, _ = arr.shape
    a, b = arr[:n//2], arr[n//2:]
    assert a.shape == b.shape, (a.shape, b.shape)
    return a, b

def load_features():
    """Return a tuple of (ref_features, query_features) where each array is in index_db() order."""
    return split_arr(get_raw_features())

def read_features():
    """Return an iterator of all (label, query_index, beat_index, ref_feature_array, query_feature_array) tuples.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    ref_features, query_features = load_features()
    for (label, query_index, beat_index, ref_path, query_path), ref_feature_array, query_feature_array in zip(
        index_db(),
        ref_features,
        query_features,
    ):
        yield label, query_index, beat_index, ref_feature_array, query_feature_array

# Feature statistics
def mad(arr, axis):
    """Compute the mean absolute deviation of the given array along the given axis."""
    mean = np.mean(arr, axis=axis)
    return np.mean(np.abs(arr - mean), axis=axis)

def ave_dist(a, b, axis):
    """Compute the average distance between a and b along the given axis."""
    return np.mean(np.abs(a - b), axis=axis)

def scaled_dist(a, b, scale_by, axis=0):
    """Find the mean distance between a and b with the given scaling along the given axis."""
    dist = ave_dist(a, b, axis=axis)
    return np.mean(dist/scale_by)

def summarize_features():
    """Print a summary of the extracted features."""
    raw_features = get_raw_features()
    n, num_feats = raw_features.shape

    stds = np.std(raw_features, axis=0)
    mads = mad(raw_features, axis=0)

    ref_features, query_features = load_features()
    ref_query_stds = scaled_dist(ref_features, query_features, stds)
    ref_query_mads = scaled_dist(ref_features, query_features, mads)

    rand_ref, rand_query = np.random.permutation(ref_features), np.random.permutation(query_features)
    rand_ref_query_stds = scaled_dist(rand_ref, rand_query, stds)
    rand_ref_query_mads = scaled_dist(rand_ref, rand_query, mads)

    rand1, rand2 = split_arr(np.random.permutation(raw_features))
    rand_stds = scaled_dist(rand1, rand2, stds)
    rand_mads = scaled_dist(rand1, rand2, mads)

    print("""
The database contains {} entries ({} each reference and query)
with {} features per entry. Reference and query feature arrays
are an average of
\t{}
standard deviations apart and
\t{}
mean absolute deviations apart. For comparison, if we randomly
permute the reference and query features they are an average of
\t{}
standard deviations apart and
\t{}
mean absolute deviations apart. Alternatively, if we randomly
partition the whole dataset, we get that the two partitions are
an average of
\t{}
standard deviations apart and
\t{}
mean absolute deviations apart.
""".format(
    n, n//2,
    num_feats,
    ref_query_stds,
    ref_query_mads,
    rand_ref_query_stds,
    rand_ref_query_mads,
    rand_stds,
    rand_mads,
))

if __name__ == "__main__":
    if os.path.exists(FEATURES_FILE):
        print("Summarizing features...")
        summarize_features()
    else:
        print("Features not yet present.")

# Usage as an audio database
def split_query(query, max_query_len=6*SAMPLE_RATE):
    """Split the given into chunks."""
    query_len, = query.shape
    query_indices = list(range(max_query_len, query_len, max_query_len))
    return np.split(query, query_indices)

def get_refs_queries_groundTruth(artists):
    """Return (refs, queries, groundTruth) for the given artists."""
    refs = []
    queries = []
    groundTruth = []

    for j, artist in enumerate(artists):
        for i, ref_name in enumerate(SONG_NAMES):
            index = 1 + j*len(SONG_NAMES) + i

            ref_path = get_song_path(artist, ref_name)
            ref_audio = get_audio(ref_path)

            refs.append(ref_audio)

            for query_name in SONG_NAMES[ref_name]:
                query_path = get_song_path(artist, query_name)
                query_audio = get_audio(query_path)

                for query_snip in split_query(query_audio):
                    queries.append(query_snip)
                    groundTruth.append(index)

    return refs, queries, groundTruth


def get_data_for_artist(artist):
    """Return (refs, queries, groundTruth) for the given artist."""
    return get_refs_queries_groundTruth([artist])

def get_all_data():
    """Return (refs, queries, groundTruth) for all artists."""
    return get_refs_queries_groundTruth(ARTISTS)

if __name__ == "__main__":
    print("Testing audio database...")
    refs, queries, groundTruth = get_all_data()
    print(len(refs), len(queries), groundTruth)
