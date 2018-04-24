# Imports
import os.path

from .constants import *


# Songs
from .songs import get_data_for_artist, get_snips_for_artist

def run_songs():
    print("Testing audio database...")
    refs, queries, groundTruth = get_data_for_artist("taylorswift")
    print(len(refs), len(queries), len(groundTruth))
    refs, queries = get_snips_for_artist("taylorswift")
    print(refs.shape, queries.shape)


# Annotations
from .annotations import data_by_song

def run_annotations():
    print("Reading data...")
    for (artist, ref_name), ref_query_pairs in data_by_song().items():
        print("song {} of artist {}".format(ref_name, artist))
        for ref, query in ref_query_pairs:
            beats, beat_width = query.shape
            print("\t{} beats of width {}".format(beats, beat_width))


# Annotation db
from .annotation_db import make_db_dirs, write_db, write_audio_paths

def run_annotation_db():
    print("Generating database directories...")
    made_dirs = make_db_dirs()
    if made_dirs:
        print("Writing database...")
        write_db()
    else:
        print("Using existing database...")
    print("Generating database index...")
    write_audio_paths()


# Feature db
from .feature_db import summarize_features

def run_features():
    if os.path.exists(FEATURES_FILE):
        print("Summarizing features...")
        summarize_features()
    else:
        print("Features not yet present.")


# Main entry point
def run_all():
    run_songs()
    run_annotations()
    run_annotation_db()
    run_features()
