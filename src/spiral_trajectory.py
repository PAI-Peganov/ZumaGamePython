import math


class SpiralTrajectory:
    def __init__(
            self, width: int, height: int, turns: float, r_start: float,
            r_end: float
    ):
        self.width = width
        self.height = height
        self.turns = turns
        self.r_start = r_start
        self.r_end = r_end

    def build_points(self) -> list[tuple[float, float]]:
        cx = self.width * 0.5
        cy = self.height * 0.5 - 40

        t_max = 2.0 * math.pi * self.turns
        n = 950
        pts: list[tuple[float, float]] = []
        for i in range(n):
            t = t_max * (i / (n - 1))
            k = i / (n - 1)
            r = self.r_start + (self.r_end - self.r_start) * k
            x = cx + r * math.cos(t)
            y = cy + r * math.sin(t)
            pts.append((x, y))
        return pts
