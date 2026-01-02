import pygame
from src.utils import clamp


class GamePath:
    def __init__(self, points: list[tuple[float, float]]):
        self.points = [pygame.Vector2(p) for p in points]
        self._seg_lens: list[float] = []
        self._cum: list[float] = [0.0]

        total = 0.0
        for i in range(len(self.points) - 1):
            L = (self.points[i + 1] - self.points[i]).length()
            self._seg_lens.append(L)
            total += L
            self._cum.append(total)
        self.length = total

    def pos_at(self, s: float, extrapolate: bool = True) -> pygame.Vector2:
        if s <= 0:
            return self.points[0]

        if s >= self.length:
            return self.points[-1]

        dist = 0.0
        for i in range(len(self.points) - 1):
            a = self.points[i]
            b = self.points[i + 1]
            seg_len = a.distance_to(b)

            if dist + seg_len >= s:
                t = (s - dist) / seg_len
                return a.lerp(b, t)

            dist += seg_len

        return self.points[-1]
