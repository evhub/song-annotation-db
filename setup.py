import setuptools

VERSION = "0.0.1"

setuptools.setup(
    name="song-annotation-db",
    version=VERSION,
    description="Database of aligned song snippets.",
    url="https://github.com/evhub/song-annotation-db",
    author="Evan Hubinger",
    author_email="ehubinger@g.hmc.edu",
    packages=setuptools.find_packages(),
)
