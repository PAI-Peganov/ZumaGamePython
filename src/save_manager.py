from __future__ import annotations
import json
import pygame
from settings import COLORS

class SaveManager:
    def __init__(self, filename: str = "save.json"):
        self.filename = filename

    def _color_to_i(self, c: tuple[int, int, int]) -> int:
        return COLORS.index(c) if c in COLORS else 0

    def _i_to_color(self, i: int) -> tuple[int, int, int]:
        return COLORS[max(0, min(len(COLORS) - 1, int(i)))]

    def save(self, snapshot: dict) -> None:
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

    def load(self) -> dict | None:
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
