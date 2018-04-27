# Song Annotation Database

Database of aligned song snippets.

## Usage

1. Clone the repository,
2. copy the `data`, `songs`, and `db` folders from `/home/evhub/ttemp/song-annotation-db/`,
4. run
```
make
```
5. then see below for all the documentation of the various features of the database.

_For example usage of all of the below functions of the database, see [`song_db/__init__.py`](https://github.com/evhub/song-annotation-db/blob/master/song_db/__init__.py)._

## Songs

If you just need access to labeled reference/query data, you probably want to use the songs database. To import the songs database, just write
```
from song_db import songs
```
which will give you access to the following functions for interfacing with the song database.

_If the above gives you a `SyntaxError`, try `from song_db_universal import songs` instead._

**songs.get_snips_for_artist**(`artist, audio_len=songs.DEFAULT_SPLIT_LEN, verbose=False`)

Returns the pair `(refs, queries)` where `refs` is an array of shape `(num_refs, audio_len)` and `queries` is an array of shape `(num_queries, audio_len)`. References and queries are split into `audio_len` chunks such that every row in each array is a clip from some reference/query of length exactly `audio_len` and no clips overlap. Only songs from the given artist are used.

**songs.get_all_snips**(`audio_len=songs.DEFAULT_SPLIT_LEN, verbose=False`)

`get_all_snips` is exactly the same as `get_snips_for_artist` except it includes all the songs in the database, not just those for one artist.

**songs.get_data_for_artist**(`artist, max_query_len=songs.DEFAULT_SPLIT_LEN, verbose=False`)

Returns the 3-tuple `(refs, queries, groundTruth)` where `refs` is a list of all the references for the given artist, `queries` is a list of all split queries (defined below) for the given artist, and `groundTruth` is a list of labels for `queries` (such that `queries` and `groundTruth` are guaranteed to have the same length). The `groundTruth` label for a query is simply the index of the reference in `refs` that the query corresponds to. The `max_query_len` parameter specifies the maximum length of a query you are willing to allow, and splits all queries into smaller query chunks of length less than or equal to the given `max_query_len`.

**songs.get_all_data**(`max_query_len=songs.DEFAULT_SPLIT_LEN, verbose=False`)

`get_all_data` is exactly the same as `get_data_for_artist` except it includes all the songs in the database, not just those for one artist.

_If you need finer-grained access to the songs database than the above functions provide, see `song_db/songs.py`._

## Annotations

If you want annotated data, you probably want to use the annotations database. To import the annotations database, just write
```
from song_db import annotations
```
which will give you access to the following functions for interfacing with the annotation database.

_If the above gives you a `SyntaxError`, try `from song_db_universal import annotations` instead._

**annotations.get_ref_query_pairs**(`artist, beat_width=annotations.DEFAULT_BEAT_WIDTH`)

Returns an iterator of `(ref_beat_array, query_beat_array)` pairs for the given artist. One pair is generated for each annotated beat in each annotated query. The `query_beat_array` is simply a segment of the query around that beat of length `beat_width` and the `ref_beat_array` is just the same length segment of the corresponding beat in the reference.

**annotations.data_by_artist**(`beat_width=annotations.DEFAULT_BEAT_WIDTH`)

Returns an ordered dictionary from artist name to the result of `get_ref_query_pairs` for that artist.

**annotations.data_by_song**(`beat_width=annotations.DEFAULT_BEAT_WIDTH`)

Returns an ordered dictionary mapping `(artist_name, reference_name)` tuples to iterators of `(ref_beat_array, query_beat_array)` pairs for the given artist and song.

_If you need finer-grained access to the annotations database than the above functions provide, see `song_db/annotations.py`._

## Features

### Feature Generation

Using <https://github.com/evhub/transfer_learning_music>, you can generate features for this database. To do this, run
```
cd song-annotation-db
make run-universal
cd ../transfer_learning_music
make run-universal
```

### Feature Summary

If you run
```
make run-universal
```
with a generated features file available, you should get (approximately) the following feature summary
```
The database contains 13566 entries (6783 each reference and query)
with 160 features per entry. Reference and query feature arrays
are an average of
        0.9619966745376587
standard deviations apart and
        1.24441397190094
mean absolute deviations apart. For comparison, if we randomly
permute the reference and query features they are an average of
        1.1164846420288086
standard deviations apart and
        1.4439947605133057
mean absolute deviations apart. Alternatively, if we randomly
partition the whole dataset, we get that the two partitions are
an average of
        1.090288519859314
standard deviations apart and
        1.4102412462234497
mean absolute deviations apart.
```
