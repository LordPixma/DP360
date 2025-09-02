# Makefile helpers (use with `make` on systems with GNU make)
# On Windows, prefer VS Code tasks, but WSL or Git Bash can use this.

VENV=.venv
PY=$(VENV)/Scripts/python.exe
PIP=$(VENV)/Scripts/pip.exe
ACTIVATE=. .venv/Scripts/activate

.PHONY: venv install migrate upgrade run test

venv:
	py -3 -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

migrate:
	$(ACTIVATE) && set FLASK_APP=app:create_app && set FLASK_ENV=development && flask db migrate -m "init"

upgrade:
	$(ACTIVATE) && set FLASK_APP=app:create_app && set FLASK_ENV=development && flask db upgrade

run:
	$(ACTIVATE) && set FLASK_APP=app:create_app && set FLASK_ENV=development && flask run

test:
	$(PY) -m pytest -q
