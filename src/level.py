from __future__ import annotations

class Level:
    def __init__(self, index: int, cfg: dict):
        self.index = index
        self.cfg = cfg

    @property
    def time_limit(self) -> float:
        return float(self.cfg["time"])

    @property
    def chain_speed(self) -> float:
        return float(self.cfg["speed"])

    @property
    def initial_balls(self) -> int:
        return int(self.cfg["balls"])

    @property
    def color_count(self) -> int:
        return int(self.cfg["colors"])
