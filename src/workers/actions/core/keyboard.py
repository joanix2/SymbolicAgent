from __future__ import annotations

import math
import random
import time

import pyautogui


def estimate_keyboard_distance(a: str, b: str) -> float:
    """Approximation grossière sur clavier QWERTY pour moduler le rythme."""
    rows = [
        "1234567890-=",
        "qwertyuiop[]",
        "asdfghjkl;'",
        "zxcvbnm,./",
    ]
    pos: dict[str, tuple[float, float]] = {}
    for r_idx, row in enumerate(rows):
        x_offset = 0.5 * r_idx
        for c_idx, char in enumerate(row):
            pos[char] = (c_idx + x_offset, r_idx)

    a = a.lower()
    b = b.lower()
    if a not in pos or b not in pos:
        return 2.5
    ax, ay = pos[a]
    bx, by = pos[b]
    return math.hypot(ax - bx, ay - by)


def human_write(text: str, base_interval: float = 0.045, variability: float = 0.030) -> None:
    prev = None
    for ch in text:
        pyautogui.write(ch, interval=0)

        if ch.isspace():
            delay = random.uniform(0.04, 0.12)
        else:
            distance_factor = estimate_keyboard_distance(prev, ch) if prev else 2.0
            delay = base_interval + min(0.10, distance_factor * 0.012)
            delay += random.uniform(-variability, variability)
            delay = max(0.01, delay)

        if ch in ",.;:!?":
            delay += random.uniform(0.05, 0.14)

        time.sleep(delay)
        prev = ch


def press_keys(keys: list[str], pause_min: float = 0.03, pause_max: float = 0.12) -> None:
    if not keys:
        return
    if len(keys) == 1:
        pyautogui.press(keys[0])
        return

    for key in keys[:-1]:
        pyautogui.keyDown(key)
        time.sleep(random.uniform(pause_min, pause_max))
    pyautogui.press(keys[-1])
    time.sleep(random.uniform(pause_min, pause_max))
    for key in reversed(keys[:-1]):
        pyautogui.keyUp(key)
        time.sleep(random.uniform(0.01, 0.05))
