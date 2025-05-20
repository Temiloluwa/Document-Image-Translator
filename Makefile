# -*- coding: utf-8 -*-
.PHONY: dev prod clean lint format test

PYTHON_VERSION = 3.12.4
SRC_FOLDER = src
TEST_FOLDER = tests

VENV_ACTIVATE = . .venv/bin/activate &&

dev:
	uv venv --python=$(PYTHON_VERSION) .venv
	$(VENV_ACTIVATE) uv sync --all-groups

dev-sync:
	uv sync --all-groups

prod:
	uv venv --python=$(PYTHON_VERSION) .venv
	$(VENV_ACTIVATE) uv sync

clean:
	rm -rf .venv
	rm -rf uv.lock

lint:
	.venv/bin/ruff check $(SRC_FOLDER)
	.venv/bin/ruff format $(SRC_FOLDER)
	# .venv/bin/mypy $(SRC_FOLDER)

test:
	cd src && uv run coverage run -m pytest ../$(TEST_FOLDER)
	cd src && uv run coverage report
	cd src && uv run coverage html -d ../coverage_html
