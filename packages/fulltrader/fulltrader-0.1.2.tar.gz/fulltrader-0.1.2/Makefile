PY ?= python3
PIP ?= $(PY) -m pip

.PHONY: setup install-dev test lint format build publish-test publish clean release

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

release:  ## Usage: make release PART=patch|minor|major or PART=set:X.Y.Z
	@[ -n "$(PART)" ] || (echo "Defina PART=patch|minor|major|set:X.Y.Z" && exit 1)
	$(PY) scripts/bump_version.py $(PART) > .version
	git add pyproject.toml src/fulltrader/__init__.py
	git commit -m "chore(release): bump to v$$(cat .version)"
	git tag v$$(cat .version)
	$(MAKE) clean build
	$(MAKE) publish
	rm -f .version

clean:
	rm -rf build/ dist/ .pytest_cache/ .ruff_cache/ *.egg-info/


