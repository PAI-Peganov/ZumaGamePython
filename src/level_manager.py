from settings import LEVEL_CONFIGS
from level import Level


class LevelManager:
    def __init__(self):
        self.index = 0

    def current(self) -> Level:
        return Level(self.index, LEVEL_CONFIGS[self.index])

    def next_level(self) -> bool:
        if self.index + 1 >= len(LEVEL_CONFIGS):
            return False
        self.index += 1
        return True

    def set_index(self, i: int) -> None:
        self.index = max(0, min(len(LEVEL_CONFIGS) - 1, i))
