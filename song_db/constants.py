# Imports
import os.path
from collections import OrderedDict


# Path constants
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")

DB_DIR = os.path.join(BASE_DIR, "db")
REFS_DB_DIR = os.path.join(DB_DIR, "refs")
QUERIES_DB_DIR = os.path.join(DB_DIR, "queries")

DB_INDEX_FILE = os.path.join(BASE_DIR, "audio_paths.txt")

FEATURES_FILE = os.path.join(BASE_DIR, "features.npy")

SONGS_DIR = os.path.join(BASE_DIR, "songs")
REFS_SONGS_DIR = os.path.join(SONGS_DIR, "refs")
QUERIES_SONGS_DIR = os.path.join(SONGS_DIR, "queries")


# Data constants
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

SAMPLE_RATE = 22050


# Song constants
DEFAULT_SPLIT_LEN = 6*SAMPLE_RATE


# Annotation constants
DEFAULT_BEAT_WIDTH = SAMPLE_RATE//2

ANNOTATED_SONG_NAMES = OrderedDict(
    ourref01=("ourquery1", "ourquery2"),
    ourref02=("ourquery3", "ourquery4"),
)

ARTIST_REF_PAIRS = [
    (artist, ref_name)
    for artist in ARTISTS
    for ref_name in ANNOTATED_SONG_NAMES
]
