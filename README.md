# Song Annotation Database

Database of aligned song snippets.

## Usage

1. Clone the repository,
2. put the data in `./data/`,
3. run
```
make install
```
4. then just
```python
from song_db import data_by_song
for (artist, ref_name), ref_query_pairs in data_by_song().items():
print("song {} of artist {}".format(ref_name, artist))
for ref, query in ref_query_pairs:
    beats, beat_width = query.shape
    print("\t{} beats of width {}".format(beats, beat_width))
```

## Feature Generation

Using <https://github.com/evhub/transfer_learning_music>, you can generate features for this database. To do this, run
```
cd song-annotation-db
make run
cd ../transfer_learning_music
make run
```

### Feature Summary

If you run
```
make run
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
