.PHONY: run
run: setup
	python3 -c "from song_db import run_all; run_all()"

.PHONY: run-py2
run-py2: py2
	python -c "from song_db2 import run_all; run_all()"

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
	rename -S .py .coco ./song_db2/*.py
	coconut ./song_db2
	pip install -e .

.PHONY: clean
clean:
	rm -rf ./dist ./build ./db audio_paths.txt
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
