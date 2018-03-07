.PHONY: run
run: install
	python3 ./song_db.py

.PHONY: install
install: setup
	pip install -e .

.PHONY: setup
setup:
	pip install numpy scipy

.PHONY: py2
py2: setup
	pip install coconut-develop
	cp ./song_db.py ./song_db2.coco
	coconut ./song_db2.coco
	pip install -e .
	python ./song_db2.py

.PHONY: clean
clean:
	rm -rf ./dist ./build ./db audio_paths.txt
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
