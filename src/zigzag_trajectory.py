from __future__ import annotations

class ZigZagTrajectory:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def build_points(self) -> list[tuple[float, float]]:
        # простая змейка от левого края к центру
        w, h = self.width, self.height
        return [
            (-120, 120),
            (w - 40, 120),
            (w - 40, 260),
            (40, 260),
            (40, 400),
            (w - 40, 400),
            (w - 40, 540),
            (40, 540),
            (w * 0.55, h * 0.55),
            (w * 0.5, h * 0.5 - 40),
        ]
