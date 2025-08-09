# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

VENV ?= venv
PYTHON ?= $(VENV)/bin/python3
PYTHON_VERSION ?= 3.11
MANAGE ?= $(PYTHON) ./manage.py

.PHONY: all
all: setup

.PHONY: setup
setup: $(VENV)/requirements.txt

requirements.txt: pyproject.toml | $(VENV)
	uv pip compile --python-version $(PYTHON_VERSION) --upgrade -o requirements.txt pyproject.toml

$(VENV)/requirements.txt: requirements.txt | $(VENV)
	VIRTUAL_ENV=$(VENV) uv pip install -r requirements.txt
	cp -f requirements.txt $(VENV)/requirements.txt

$(VENV):
	uv venv $(VENV)

.PHONY: clean
clean:
	find -name __pycache__ -type d -exec rm -rf '{}' \;
	find -name \*.pyc -type f -exec rm -f '{}' \;

.PHONY: distclean
distclean:
	rm -rf $(VENV)

.PHONY: editable
editable:
	VIRTUAL_ENV=$(VENV) uv pip install -e .
