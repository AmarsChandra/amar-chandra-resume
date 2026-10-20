.PHONY: build clean

PYTHON ?= python3

build:
	$(PYTHON) scripts/build.py

clean:
	$(PYTHON) -c "import shutil; shutil.rmtree('dist', ignore_errors=True)"
