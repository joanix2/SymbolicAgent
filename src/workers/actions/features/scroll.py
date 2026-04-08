from __future__ import annotations

import random
import time
from typing import Annotated

import pyautogui
import typer

from ..core.mouse import human_move_mouse

app = typer.Typer()


@app.command("scroll")
def scroll_command(
    amount: Annotated[int, typer.Argument(help="Quantité de scroll, positif ou négatif")],
    x: Annotated[int | None, typer.Option(help="Position X optionnelle")] = None,
    y: Annotated[int | None, typer.Option(help="Position Y optionnelle")] = None,
    duration: Annotated[float, typer.Option(help="Durée si déplacement préalable")] = 0.35,
) -> None:
    """Déplace éventuellement la souris, puis scrolle."""
    if x is not None and y is not None:
        human_move_mouse(x, y, duration=duration, easing="smooth", jitter=1.0)
        time.sleep(random.uniform(0.02, 0.08))
    pyautogui.scroll(amount)
