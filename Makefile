.PHONY: run
run: setup
	python ./song_db.py

.PHONY: setup
setup:
	pip install numpy scipy

.PHONY: clean
clean:
	rm -rf ./dist ./build ./db audio_paths.txt
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
