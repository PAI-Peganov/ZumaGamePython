from __future__ import annotations
import pygame
from utils import clamp

class BallPath:
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
        """Если extrapolate=True: разрешаем s < 0 и s > length (линейное продолжение)."""
        if len(self.points) < 2:
            return self.points[0].copy()

        if not extrapolate:
            s = clamp(s, 0.0, self.length)

        if s < 0.0:
            a = self.points[0]
            b = self.points[1]
            d = (b - a)
            if d.length_squared() < 1e-9:
                return a.copy()
            return a + d.normalize() * s  # s отрицательный

        if s > self.length:
            a = self.points[-2]
            b = self.points[-1]
            d = (b - a)
            if d.length_squared() < 1e-9:
                return b.copy()
            return b + d.normalize() * (s - self.length)

        seg_i = 0
        while seg_i < len(self._seg_lens) and self._cum[seg_i + 1] < s:
            seg_i += 1

        a = self.points[seg_i]
        b = self.points[seg_i + 1]
        seg_len = self._seg_lens[seg_i]
        if seg_len <= 1e-9:
            return a.copy()

        t = (s - self._cum[seg_i]) / seg_len
        return a.lerp(b, t)
