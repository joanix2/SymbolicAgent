from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pyautogui
import typer

from .models import Box


def capture_screen_bgr(region: tuple[int, int, int, int] | None = None) -> np.ndarray:
    """Capture l'écran et retourne une image OpenCV BGR."""
    screenshot = pyautogui.screenshot(region=region)
    rgb = np.array(screenshot)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def load_image_bgr(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise typer.BadParameter(f"Impossible de lire l'image: {path}")
    return img


def maybe_gray(img: np.ndarray, enabled: bool) -> np.ndarray:
    if not enabled:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def maybe_blur(img: np.ndarray, ksize: int) -> np.ndarray:
    if ksize <= 1:
        return img
    if ksize % 2 == 0:
        ksize += 1
    return cv2.GaussianBlur(img, (ksize, ksize), 0)


def preprocess(img: np.ndarray, grayscale: bool, blur_ksize: int) -> np.ndarray:
    out = maybe_gray(img, grayscale)
    out = maybe_blur(out, blur_ksize)
    return out


def compute_iou(a: Box, b: Box) -> float:
    inter_x1 = max(a.x, b.x)
    inter_y1 = max(a.y, b.y)
    inter_x2 = min(a.x2, b.x2)
    inter_y2 = min(a.y2, b.y2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    if inter_area == 0:
        return 0.0

    union_area = a.w * a.h + b.w * b.h - inter_area
    return inter_area / union_area if union_area > 0 else 0.0


def nms_merge(boxes: list[Box], iou_threshold: float = 0.35) -> list[Box]:
    """Fusionne les boxes proches/recouvrantes via une variante simple de NMS + merge."""
    if not boxes:
        return []

    boxes = sorted(boxes, key=lambda b: b.score, reverse=True)
    merged: list[Box] = []

    while boxes:
        current = boxes.pop(0)
        cluster = [current]
        remaining: list[Box] = []

        for other in boxes:
            if compute_iou(current, other) >= iou_threshold:
                cluster.append(other)
            else:
                remaining.append(other)

        boxes = remaining

        total_score = sum(max(b.score, 1e-6) for b in cluster)
        x = int(sum(b.x * b.score for b in cluster) / total_score)
        y = int(sum(b.y * b.score for b in cluster) / total_score)
        w = int(sum(b.w * b.score for b in cluster) / total_score)
        h = int(sum(b.h * b.score for b in cluster) / total_score)
        score = max(b.score for b in cluster)
        merged.append(Box(x=x, y=y, w=w, h=h, score=score))

    return merged


def draw_boxes(image: np.ndarray, boxes: list[Box]) -> np.ndarray:
    out = image.copy()
    for idx, box in enumerate(boxes, start=1):
        cv2.rectangle(out, (box.x, box.y), (box.x2, box.y2), (0, 255, 0), 2)
        cv2.circle(out, (box.cx, box.cy), 3, (0, 0, 255), -1)
        label = f"#{idx} {box.score:.3f}"
        cv2.putText(out, label, (box.x, max(20, box.y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return out


def match_template_boxes(
    screenshot_bgr: np.ndarray,
    template_bgr: np.ndarray,
    threshold: float,
    method_name: str,
    grayscale: bool,
    blur_ksize: int,
    region_offset: tuple[int, int] = (0, 0),
) -> list[Box]:
    methods = {
        "ccoeff_normed": cv2.TM_CCOEFF_NORMED,
        "ccorr_normed": cv2.TM_CCORR_NORMED,
        "sqdiff_normed": cv2.TM_SQDIFF_NORMED,
    }
    if method_name not in methods:
        raise typer.BadParameter(f"Méthode inconnue: {method_name}")

    img = preprocess(screenshot_bgr, grayscale=grayscale, blur_ksize=blur_ksize)
    templ = preprocess(template_bgr, grayscale=grayscale, blur_ksize=blur_ksize)

    method = methods[method_name]
    result = cv2.matchTemplate(img, templ, method)
    th, tw = templ.shape[:2]
    ox, oy = region_offset

    boxes: list[Box] = []

    if method_name == "sqdiff_normed":
        ys, xs = np.where(result <= threshold)
        score_fn = lambda v: 1.0 - float(v)
    else:
        ys, xs = np.where(result >= threshold)
        score_fn = lambda v: float(v)

    for y, x in zip(ys, xs):
        score = score_fn(result[y, x])
        boxes.append(Box(x=int(x + ox), y=int(y + oy), w=int(tw), h=int(th), score=score))

    return boxes
