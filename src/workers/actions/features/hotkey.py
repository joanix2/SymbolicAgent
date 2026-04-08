from __future__ import annotations

from typing import Annotated

import typer

from ..core.keyboard import press_keys

app = typer.Typer()


@app.command("hotkey")
def hotkey_command(
    keys: Annotated[list[str], typer.Argument(help="Suite de touches, ex: ctrl shift p")],
) -> None:
    """Joue une combinaison de touches."""
    press_keys(keys)
