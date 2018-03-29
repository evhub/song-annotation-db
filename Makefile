.PHONY: run-py2
run-py2: py2
	python -c "from song_db2 import run_all; run_all()"

.PHONY: run
run: setup
	python3 -c "from song_db import run_all; run_all()"

.PHONY: install
install: setup
	pip install -e .

.PHONY: setup
setup:
	pip install numpy scipy

.PHONY: py2
py2: setup
	pip install coconut-develop
	cp -r ./song_db ./song_db2
	rename -E "s/\.py\$/\.coco/" ./song_db2/*.py
	coconut ./song_db2 --no-tco
	pip install -e .

.PHONY: clean
clean:
	rm -rf ./song_db2 ./dist ./build
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

.PHONY: wipe
wipe: clean
	rm -rf ./db audio_paths.txt
