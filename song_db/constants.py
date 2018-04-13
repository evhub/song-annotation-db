# Imports
import os.path
from collections import defaultdict, OrderedDict


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

ANNOTATED_SONG_NAMES = defaultdict(lambda: OrderedDict(
    ourref01=("ourquery1", "ourquery2"),
    ourref02=("ourquery3", "ourquery4"),
))
ANNOTATED_SONG_NAMES["taylorswift"] = OrderedDict(
    ourref01=("ourquery01a", "ourquery01a"),
    ourref02=("ourquery02a", "ourquery02a"),
    ourref03=("ourquery03a", "ourquery03a"),
    ourref04=("ourquery04a", "ourquery04a"),
    ourref05=("ourquery05a", "ourquery05a"),
    ourref06=("ourquery06a", "ourquery06a"),
    ourref07=("ourquery07a", "ourquery07a"),
    ourref08=("ourquery08a", "ourquery08a"),
    ourref09=("ourquery09a", "ourquery09a"),
    ourref10=("ourquery10a", "ourquery10a"),
)

ARTIST_REF_PAIRS = [
    (artist, ref_name)
    for artist, song_names in ANNOTATED_SONG_NAMES.items()
    for ref_name in song_names
]
