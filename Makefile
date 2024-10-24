clean:
	rm -rf maptypes/__pycache__ maptypes/ssmap/__pycache__ maptypes/bsmap/__pycache__ maptypes/bstmap/__pycache__ maptypes/benchmarks/__pycache__

test:
	python -m unittest -v maptypes/ssmap/test.py maptypes/bsmap/test.py maptypes/bstmap/test.py

benchmark:
	richbench maptypes/benchmarks
