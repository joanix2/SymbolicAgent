from __future__ import annotations

from typing import Annotated

import typer

from ..core.mouse import human_move_mouse

app = typer.Typer()


@app.command("move")
def move_command(
    x: Annotated[int, typer.Argument(help="Coordonnée X cible")],
    y: Annotated[int, typer.Argument(help="Coordonnée Y cible")],
    duration: Annotated[float, typer.Option(help="Durée approximative du mouvement")] = 0.5,
    easing: Annotated[str, typer.Option(help="Courbe: linear, sigmoid, smooth")] = "smooth",
    jitter: Annotated[float, typer.Option(help="Micro-variations latérales")] = 1.5,
) -> None:
    """Déplace la souris vers une position."""
    human_move_mouse(x, y, duration=duration, easing=easing, jitter=jitter)
