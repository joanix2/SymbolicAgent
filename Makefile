VENV     := .venv
PYTHON   := $(VENV)/bin/python
PIP      := $(VENV)/bin/pip

.PHONY: run chat install venv clean

## Lance l'éditeur (capture via gnome-screenshot intégrée)
run: $(VENV)
	$(PYTHON) main.py

## Lance l'interface de chat NLP
chat: $(VENV)
	$(PYTHON) -c "from src.workers.chat.ui import ChatApp; ChatApp().mainloop()"

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
