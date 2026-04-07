VENV     := .venv
PYTHON   := $(VENV)/bin/python
PIP      := $(VENV)/bin/pip

.PHONY: run install venv clean

## Lance l'éditeur (capture via gnome-screenshot intégrée)
run: $(VENV)
	$(PYTHON) main.py

## Crée le venv et installe les dépendances
install: venv
	$(PIP) install --upgrade pip
	$(PIP) install pillow numpy mss

## Crée le venv s'il n'existe pas
venv:
	test -d $(VENV) || python3 -m venv $(VENV)

## Supprime le venv et les fichiers temporaires
clean:
	rm -rf $(VENV) /tmp/screenshot_symbol_editor.png __pycache__ src/__pycache__
