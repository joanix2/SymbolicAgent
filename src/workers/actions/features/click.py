from __future__ import annotations

import random
import time
from typing import Annotated

import pyautogui
import typer

from ..core.mouse import human_move_mouse

app = typer.Typer()


@app.command("click")
def click_command(
    x: Annotated[int | None, typer.Option(help="Coordonnée X")] = None,
    y: Annotated[int | None, typer.Option(help="Coordonnée Y")] = None,
    button: Annotated[str, typer.Option(help="left, middle, right")] = "left",
    human: Annotated[bool, typer.Option(help="Ajouter un mouvement plus naturel avant clic")] = True,
) -> None:
    """Clique sur une position donnée ou la position actuelle si aucune coordonnée n'est fournie."""
    if x is not None and y is not None:
        if human:
            human_move_mouse(x, y, duration=random.uniform(0.2, 0.6), easing=random.choice(["smooth", "sigmoid"]))
            time.sleep(random.uniform(0.03, 0.10))
        pyautogui.click(x, y, button=button)
    else:
        pyautogui.click(button=button)
