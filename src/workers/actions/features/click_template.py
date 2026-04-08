from __future__ import annotations

import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import typer

from ..core.image_utils import capture_screen_bgr, load_image_bgr, match_template_boxes, nms_merge
from ..core.mouse import click_box_center

app = typer.Typer()


@app.command("click-template")
def click_template_command(
    template: Annotated[Path, typer.Argument(help="Image modèle à rechercher")],
    threshold: Annotated[float, typer.Option(help="Seuil de matching")] = 0.90,
    method: Annotated[str, typer.Option(help="Méthode OpenCV")] = "ccoeff_normed",
    grayscale: Annotated[bool, typer.Option(help="Matching en niveaux de gris")] = True,
    blur: Annotated[int, typer.Option(help="Flou gaussien")] = 0,
    iou: Annotated[float, typer.Option(help="Fusion IoU")] = 0.35,
    pick: Annotated[str, typer.Option(help="first, best, random")] = "best",
    button: Annotated[str, typer.Option(help="left, middle, right")] = "left",
) -> None:
    """Cherche un template puis clique son centre."""
    screen = capture_screen_bgr()
    templ = load_image_bgr(template)
    raw_boxes = match_template_boxes(screen, templ, threshold, method, grayscale, blur)
    boxes = nms_merge(raw_boxes, iou_threshold=iou)

    if not boxes:
        raise typer.Exit(code=1)

    if pick == "first":
        chosen = boxes[0]
    elif pick == "random":
        chosen = random.choice(boxes)
    else:
        chosen = max(boxes, key=lambda b: b.score)

    click_box_center(chosen, button=button, human=True)
    typer.echo(json.dumps(asdict(chosen) | {"cx": chosen.cx, "cy": chosen.cy}, indent=2))
