from __future__ import annotations
from settings import LEVELS
from level import Level

class LevelManager:
    def __init__(self):
        self.index = 0

    def current(self) -> Level:
        return Level(self.index, LEVELS[self.index])

    def next_level(self) -> bool:
        if self.index + 1 >= len(LEVELS):
            return False
        self.index += 1
        return True

    def set_index(self, i: int) -> None:
        self.index = max(0, min(len(LEVELS) - 1, i))
