# Imports
import os

from .util import *


# Reading songs
def get_queries_for_song(queries_dir, song_name, verbose=False):
    """Gets all the queries in the given directory for the given song."""
    song_queries_dir = os.path.join(queries_dir, song_name)
    for query_name in sorted(os.listdir(song_queries_dir)):
        if verbose:
            print("\t\tLoading query %r..." % (query_name,))

        query_path = os.path.join(song_queries_dir, query_name)
        yield get_audio(query_path)

def get_refs_and_queries_for_artist(artist, verbose=False):
    """Returns an iterator of all of an artist's songs."""
    queries_dir = os.path.join(QUERIES_SONGS_DIR, artist)
    for song_name in sorted(os.listdir(queries_dir)):
        if verbose:
            print("\tLoading song %r..." % (song_name,))
        ref_path = os.path.join(REFS_SONGS_DIR, artist, song_name)
        yield (
            get_audio(ref_path),
            get_queries_for_song(queries_dir, song_name, verbose),
        )


# Internal endpoint
def get_refs_queries_groundTruth(artists, max_query_len=DEFAULT_SPLIT_LEN, verbose=False):
    """Return (refs, queries, groundTruth) for the given artists."""
    refs = []
    queries = []
    groundTruth = []

    index = 0
    for j, artist in enumerate(artists):
        for i, (ref_audio, raw_queries) in enumerate(get_refs_and_queries_for_artist(artist, verbose)):
            index += 1
            refs.append(ref_audio)

            for query_audio in raw_queries:
                for query_snip in split_audio(query_audio, max_query_len):
                    queries.append(query_snip)
                    groundTruth.append(index)

    return refs, queries, groundTruth


# External endpoints
def get_data_for_artist(artist, max_query_len=DEFAULT_SPLIT_LEN, verbose=False):
    """Return (refs, queries, groundTruth) for the given artist."""
    return get_refs_queries_groundTruth([artist], max_query_len, verbose)

def get_all_data(max_query_len=DEFAULT_SPLIT_LEN, verbose=False):
    """Return (refs, queries, groundTruth) for all artists."""
    return get_refs_queries_groundTruth(ARTISTS, max_query_len, verbose)
