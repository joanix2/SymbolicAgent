from __future__ import annotations

from typing import Annotated

import typer

from ..core.keyboard import human_write

app = typer.Typer()


@app.command("write")
def write_command(
    text: Annotated[str, typer.Argument(help="Texte à taper")],
    base_interval: Annotated[float, typer.Option(help="Base de délai entre frappes")] = 0.045,
    variability: Annotated[float, typer.Option(help="Variabilité aléatoire")] = 0.030,
) -> None:
    """Tape un texte avec un rythme moins mécanique."""
    human_write(text, base_interval=base_interval, variability=variability)
