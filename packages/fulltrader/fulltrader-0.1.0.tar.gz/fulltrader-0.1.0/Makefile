PY ?= python3
PIP ?= $(PY) -m pip

.PHONY: setup install-dev test lint format build publish-test publish clean

setup:
	$(PIP) install -U pip
	$(PIP) install -U build hatchling

install-dev:
	$(PIP) install -e .[dev]

test:
	pytest -q

lint:
	ruff check

format:
	ruff format

build:
	$(PY) -m build

publish-test:
	$(PY) -m twine upload --repository testpypi dist/*

publish:
	$(PY) -m twine upload dist/*

clean:
	rm -rf build/ dist/ .pytest_cache/ .ruff_cache/ *.egg-info/


