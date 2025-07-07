# -*- coding: utf-8 -*-
.PHONY: dev prod clean lint format test

PYTHON_VERSION = 3.12.4
SRC_FOLDER = src
TEST_FOLDER = tests

VENV_ACTIVATE = . .venv/bin/activate &&
VENV_API_ACTIVATE = . .venv_api/bin/activate &&

dev:
	uv venv --python=$(PYTHON_VERSION) .venv
	$(VENV_ACTIVATE) uv sync --all-groups

dev-sync:
	uv sync --all-groups

prod:
	uv venv --python=$(PYTHON_VERSION) .venv
	$(VENV_ACTIVATE) uv sync --group=prod

prod-api:
	uv venv --python=$(PYTHON_VERSION) .venv_api
	$(VENV_API_ACTIVATE) uv sync --group=api --active

clean:
	rm -rf .venv
	rm -rf uv.lock

lint:
	.venv/bin/ruff check $(SRC_FOLDER)
	.venv/bin/ruff format $(SRC_FOLDER)
	# .venv/bin/mypy

test:
	PYTHONPATH=$(SRC_FOLDER) uv run pytest -m "not integration" --cov=src --cov-report=term --cov-report=html:coverage_html $(TEST_FOLDER)

integration-test:
	PYTHONPATH=$(SRC_FOLDER) uv run pytest -m integration --cov=src --cov-report=term --cov-report=html:coverage_html $(TEST_FOLDER)

integration: integration-test
