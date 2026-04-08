from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import cv2
import typer

from ..core.image_utils import capture_screen_bgr, load_image_bgr, match_template_boxes, nms_merge, draw_boxes
from ..core.models import Box

app = typer.Typer()


@app.command("find")
def find_command(
    template: Annotated[Path, typer.Argument(help="Image modèle à rechercher dans la capture d'écran.")],
    threshold: Annotated[float, typer.Option(help="Seuil de matching. Pour sqdiff_normed, plus bas = plus strict.")] = 0.90,
    method: Annotated[str, typer.Option(help="Méthode OpenCV: ccoeff_normed, ccorr_normed, sqdiff_normed")] = "ccoeff_normed",
    grayscale: Annotated[bool, typer.Option(help="Activer le matching en niveaux de gris.")] = True,
    blur: Annotated[int, typer.Option(help="Taille du flou gaussien impair. 0 ou 1 pour désactiver.")] = 0,
    iou: Annotated[float, typer.Option(help="Seuil IoU pour fusionner les boîtes.")] = 0.35,
    region: Annotated[str | None, typer.Option(help="Zone x,y,w,h pour limiter la capture.")] = None,
    save_annotated: Annotated[Path | None, typer.Option(help="Chemin pour sauvegarder la capture annotée.")] = None,
    output_json: Annotated[bool, typer.Option(help="Sortie JSON.")] = True,
) -> None:
    """Cherche un template dans une capture d'écran et retourne les boxes détectées."""
    region_tuple: tuple[int, int, int, int] | None = None
    offset = (0, 0)
    if region:
        try:
            x, y, w, h = [int(part.strip()) for part in region.split(",")]
            region_tuple = (x, y, w, h)
            offset = (x, y)
        except Exception as exc:
            raise typer.BadParameter("Le format de --region doit être x,y,w,h") from exc

    screen = capture_screen_bgr(region=region_tuple)
    templ = load_image_bgr(template)
    raw_boxes = match_template_boxes(
        screenshot_bgr=screen,
        template_bgr=templ,
        threshold=threshold,
        method_name=method,
        grayscale=grayscale,
        blur_ksize=blur,
        region_offset=offset,
    )
    merged = nms_merge(raw_boxes, iou_threshold=iou)

    if save_annotated:
        annotated_base = screen.copy()
        if offset != (0, 0):
            local_boxes = [Box(x=b.x - offset[0], y=b.y - offset[1], w=b.w, h=b.h, score=b.score) for b in merged]
        else:
            local_boxes = merged
        annotated = draw_boxes(annotated_base, local_boxes)
        cv2.imwrite(str(save_annotated), annotated)

    payload = {
        "count": len(merged),
        "boxes": [asdict(b) | {"cx": b.cx, "cy": b.cy} for b in merged],
    }
    if output_json:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(f"Detections: {len(merged)}")
        for idx, box in enumerate(merged, start=1):
            typer.echo(f"#{idx} x={box.x} y={box.y} w={box.w} h={box.h} cx={box.cx} cy={box.cy} score={box.score:.4f}")
