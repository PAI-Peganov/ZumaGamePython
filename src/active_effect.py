from __future__ import annotations

class ActiveEffect:
    def __init__(self, effect_type: str, time_left: float):
        self.effect_type = effect_type
        self.time_left = time_left

    def update(self, dt: float) -> None:
        self.time_left -= dt

    def alive(self) -> bool:
        return self.time_left > 0.0
