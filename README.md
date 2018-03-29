# Song Annotation Database

Database of aligned song snippets.

## Usage

1. Clone the repository,
2. copy the `data`, `songs`, and `db` folders from `/home/evhub/ttemp/song-annotation-db/`,
4. run
```
make install-universal
```
5. then see `song_db/__init__.py` for example usage of the various features of the database.

## Feature Generation

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
