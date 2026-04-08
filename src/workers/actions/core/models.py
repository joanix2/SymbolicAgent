from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Box:
    x: int
    y: int
    w: int
    h: int
    score: float

    @property
    def x2(self) -> int:
        return self.x + self.w

    @property
    def y2(self) -> int:
        return self.y + self.h

    @property
    def cx(self) -> int:
        return self.x + self.w // 2

    @property
    def cy(self) -> int:
        return self.y + self.h // 2
