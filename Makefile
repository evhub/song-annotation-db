.PHONY: install-universal
install-universal: setup
	pip install coconut-develop
	rm -rf ./song_db_universal
	cp -r ./song_db ./song_db_universal
	rename -E "s/\.py$$/\.coco/" ./song_db_universal/*.py
	coconut ./song_db_universal --no-tco --jobs sys
	pip install -e .

.PHONY: install
install: setup
	pip install -e .

.PHONY: run-universal
run-universal: install-universal
	python -c "from song_db_universal import run_all; run_all()"

.PHONY: run
run: setup
	python3 -c "from song_db import run_all; run_all()"

.PHONY: setup
setup:
	pip install numpy scipy

.PHONY: clean
clean:
	rm -rf ./song_db_universal ./dist ./build
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

.PHONY: wipe
wipe: clean
	rm -rf ./db audio_paths.txt
