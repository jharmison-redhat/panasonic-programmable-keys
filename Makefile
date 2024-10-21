.PHONY: all
all: dev

.venv/bin/pip:
	python3.11 -m venv .venv
	.venv/bin/pip install --upgrade pip

.venv/lib/python3.11/site-packages/build/__main__.py: .venv/bin/pip
	.venv/bin/pip install setuptools wheel build

.PHONY: dev
dev: .venv/lib/python3.11/site-packages/build/__main__.py
	.venv/bin/pip install -e .[dev]

.PHONY: lint
lint: .venv/bin/tox
	.venv/bin/tox -e lint

.PHONY: format
format: .venv/bin/tox
	.venv/bin/tox -e format

.PHONY: test
test: .venv/bin/tox
	.venv/bin/tox

.PHONY: build
build: format lint test
	.venv/bin/tox -e build
