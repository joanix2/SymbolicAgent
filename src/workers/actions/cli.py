from __future__ import annotations

import pyautogui
import typer

from .features.find import app as find_app
from .features.move import app as move_app
from .features.click import app as click_app
from .features.click_template import app as click_template_app
from .features.scroll import app as scroll_app
from .features.write import app as write_app
from .features.hotkey import app as hotkey_app
from .features.position import app as position_app

# Sécurité PyAutoGUI: déplacer la souris dans un coin de l'écran déclenche une exception.
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02

app = typer.Typer(help="CLI d'automatisation GUI avec détection OpenCV + mouvements plus naturels.")

app.add_typer(find_app)
app.add_typer(move_app)
app.add_typer(click_app)
app.add_typer(click_template_app)
app.add_typer(scroll_app)
app.add_typer(write_app)
app.add_typer(hotkey_app)
app.add_typer(position_app)

if __name__ == "__main__":
    app()
