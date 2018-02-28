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
```
from song_db import ...
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
partition the data instead, we get that the two partitions are
an average of
        1.0886027812957764
standard deviations apart and
        1.4080867767333984
mean absolute deviations apart.
```
