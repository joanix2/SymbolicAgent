from __future__ import annotations

import math
import random
import time
from typing import Literal

import pyautogui
import typer

from .models import Box


def ease_linear(t: float) -> float:
    return t


def ease_sigmoid(t: float) -> float:
    return 1.0 / (1.0 + math.exp(-10.0 * (t - 0.5)))


def ease_smootherstep(t: float) -> float:
    return t * t * t * (t * (t * 6 - 15) + 10)


def pick_easing(name: str):
    if name == "linear":
        return ease_linear
    if name == "sigmoid":
        return ease_sigmoid
    if name == "smooth":
        return ease_smootherstep
    raise typer.BadParameter(f"Courbe inconnue: {name}")


# -----------------------------
# Courbe de Bézier cubique
# -----------------------------

def _bezier_control_points(
    start: tuple[float, float],
    end: tuple[float, float],
    spread: float = 0.12,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Génère deux points de contrôle perpendiculaires à l'axe start→end."""
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    dist = math.hypot(dx, dy) or 1.0
    # Vecteur perpendiculaire unitaire
    perp_x, perp_y = -dy / dist, dx / dist

    o1 = random.uniform(-spread, spread) * dist
    o2 = random.uniform(-spread, spread) * dist
    p1 = (sx + dx * 0.30 + perp_x * o1, sy + dy * 0.30 + perp_y * o1)
    p2 = (sx + dx * 0.70 + perp_x * o2, sy + dy * 0.70 + perp_y * o2)
    return p1, p2


def _cubic_bezier_point(
    t: float,
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
) -> tuple[float, float]:
    u = 1.0 - t
    bx = u**3 * p0[0] + 3*u**2*t * p1[0] + 3*u*t**2 * p2[0] + t**3 * p3[0]
    by = u**3 * p0[1] + 3*u**2*t * p1[1] + 3*u*t**2 * p2[1] + t**3 * p3[1]
    return bx, by


# -----------------------------
# Bruit Brownien (pont Brownien)
# -----------------------------

def _brownian_bridge(steps: int, sigma: float) -> list[tuple[float, float]]:
    """Marche aléatoire 2D ancrée à 0 aux deux extrémités (pont Brownien)."""
    if steps <= 1:
        return [(0.0, 0.0)]
    raw_x, raw_y = [0.0], [0.0]
    for _ in range(steps - 1):
        raw_x.append(raw_x[-1] + random.gauss(0.0, sigma))
        raw_y.append(raw_y[-1] + random.gauss(0.0, sigma))
    end_x, end_y = raw_x[-1], raw_y[-1]
    n = steps - 1
    return [
        (raw_x[i] - end_x * i / n, raw_y[i] - end_y * i / n)
        for i in range(steps)
    ]


# -----------------------------
# Mouvement souris "humain"
# -----------------------------

def human_move_mouse(
    x: int,
    y: int,
    duration: float = 0.5,
    easing: str = "smooth",
    jitter: float = 1.5,
    steps: int | None = None,
    bezier_spread: float = 0.12,
    brownian_sigma: float = 0.4,
) -> None:
    start_x, start_y = pyautogui.position()
    distance = math.hypot(x - start_x, y - start_y)

    if steps is None:
        steps = max(12, min(120, int(distance / 10)))

    ease_fn = pick_easing(easing)
    p0 = (float(start_x), float(start_y))
    p3 = (float(x), float(y))
    p1, p2 = _bezier_control_points(p0, p3, spread=bezier_spread)
    brown = _brownian_bridge(steps, sigma=brownian_sigma)

    prev_x, prev_y = start_x, start_y

    for i in range(1, steps + 1):
        t = ease_fn(i / steps)
        nx, ny = _cubic_bezier_point(t, p0, p1, p2, p3)

        # Pont Brownien superposé
        nx += brown[i - 1][0]
        ny += brown[i - 1][1]

        # Micro-jitter uniforme résiduel (plus fort en milieu de trajectoire)
        wobble = 1.0 - abs(0.5 - i / steps) * 2.0
        nx += random.uniform(-jitter * 0.4, jitter * 0.4) * wobble
        ny += random.uniform(-jitter * 0.4, jitter * 0.4) * wobble

        ix, iy = int(round(nx)), int(round(ny))
        if (ix, iy) != (prev_x, prev_y):
            pyautogui.moveTo(ix, iy)
            prev_x, prev_y = ix, iy

        time.sleep(duration / steps * random.uniform(0.85, 1.20))

    pyautogui.moveTo(x, y)


def click_box_center(box: Box, button: Literal["left", "middle", "right"] = "left", human: bool = True) -> None:
    target_x, target_y = box.cx, box.cy
    if human:
        target_x += random.randint(-2, 2)
        target_y += random.randint(-2, 2)
        human_move_mouse(target_x, target_y, duration=random.uniform(0.25, 0.7), easing=random.choice(["smooth", "sigmoid"]))
        time.sleep(random.uniform(0.03, 0.12))
    pyautogui.click(target_x, target_y, button=button)