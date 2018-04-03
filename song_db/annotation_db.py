# Imports
import os

from .annotations import *


# Song ordering
def pair_to_label(song_pair):
    """Convert an artist_ref_pair identifying a song into an integer label for that song."""
    return ARTIST_REF_PAIRS.index(song_pair)

def label_to_pair(song_label):
    """Convert a label produced by pair_to_label back into the identifying artist_ref_pair."""
    return ARTIST_REF_PAIRS[song_label]


# Path handling
def db_file(song_pair, query_index, beat_index):
    """Get the name of the database file to save the given song_pair of the given index."""
    fname = "{}_{}_{}.wav".format(pair_to_label(song_pair), query_index, beat_index)
    return os.path.join(REFS_DB_DIR, fname), os.path.join(QUERIES_DB_DIR, fname)


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
    for db_dir in (DB_DIR, REFS_DB_DIR, QUERIES_DB_DIR):
        if not os.path.exists(db_dir):
            os.mkdir(db_dir)
            made_dirs = True
    return made_dirs


# Database indexing
def get_ref_paths():
    """Same as get_audio_paths but just for refs."""
    for ref_file in os.listdir(REFS_DB_DIR):
        ref_path = os.path.join(REFS_DB_DIR, ref_file)
        yield os.path.abspath(ref_path)

def get_query_paths():
    """Same as get_audio_paths but just for queries."""
    for query_file in os.listdir(QUERIES_DB_DIR):
        query_path = os.path.join(QUERIES_DB_DIR, query_file)
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


# Database endpoints
def index_db():
    """Return an iterator of all (label, query_index, beat_index, ref_path, query_path) tuples.
    Since this function is implemented as a generator, no work is done until it is iterated over."""
    for ref_path in get_ref_paths():
        fname = os.path.basename(ref_path)
        label, query_index, beat_index = map(int, os.path.splitext(fname)[0].split("_"))
        query_path = os.path.join(QUERIES_DB_DIR, fname)
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


# Database creation
if __name__ == "__main__":
    print("Generating database directories...")
    made_dirs = make_db_dirs()
    if made_dirs:
        print("Writing database...")
        write_db()
    else:
        print("Using existing database...")
    print("Generating database index...")
    write_audio_paths()
