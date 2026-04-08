from __future__ import annotations

import json

import pyautogui
import typer

app = typer.Typer()


@app.command("position")
def position_command() -> None:
    """Affiche la position actuelle de la souris."""
    x, y = pyautogui.position()
    typer.echo(json.dumps({"x": x, "y": y}, indent=2))
