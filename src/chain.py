from __future__ import annotations
import random
import pygame
from ball import Ball
from ball_path import BallPath
from settings import COINS_PER_BALL

class BallChain:
    def __init__(self, path: BallPath, colors: list[tuple[int,int,int]], ball_radius: int, spacing: float, speed: float, count: int):
        self.path = path
        self.colors = colors
        self.ball_radius = ball_radius
        self.spacing = spacing
        self.base_speed = speed

        self.balls: list[Ball] = [Ball(random.choice(self.colors), ball_radius) for _ in range(count)]
        self.head_s = 0.0
        self._recalc_positions()

    def set_head_start(self, s: float) -> None:
        self.head_s = s
        self._recalc_positions()

    def _recalc_positions(self) -> None:
        for i, b in enumerate(self.balls):
            s = self.head_s - i * self.spacing
            b.pos = self.path.pos_at(s, extrapolate=True)

    def update(self, dt: float, speed_mult: float, direction: int) -> None:
        if not self.balls:
            return
        self.head_s += self.base_speed * speed_mult * direction * dt
        if self.head_s < 0:
            self.head_s = 0
        self._recalc_positions()

    def head_reached_end(self) -> bool:
        return bool(self.balls) and self.head_s >= self.path.length - self.ball_radius * 0.6

    def try_insert(self, proj_pos: pygame.Vector2, proj_r: int, proj_color: tuple[int,int,int]) -> int | None:
        hit = None
        best = 10**18
        for i, b in enumerate(self.balls):
            dx = proj_pos.x - b.pos.x
            dy = proj_pos.y - b.pos.y
            rr = proj_r + b.radius
            d2 = dx*dx + dy*dy
            if d2 <= rr*rr and d2 < best:
                best = d2
                hit = i

        if hit is None:
            return None

        self.balls.insert(hit, Ball(proj_color, self.ball_radius))
        self._recalc_positions()
        return hit

    def pop_color_group(self, idx: int) -> list[tuple[pygame.Vector2, tuple[int,int,int], int]]:
        if not self.balls or idx < 0 or idx >= len(self.balls):
            return []

        c = self.balls[idx].color
        l = idx
        r = idx
        while l - 1 >= 0 and self.balls[l - 1].color == c:
            l -= 1
        while r + 1 < len(self.balls) and self.balls[r + 1].color == c:
            r += 1

        if (r - l + 1) < 3:
            return []

        removed = []
        for b in self.balls[l:r+1]:
            removed.append((b.pos.copy(), b.color, b.radius))

        del self.balls[l:r+1]
        self._recalc_positions()

        # цепная реакция на стыке
        if self.balls:
            check = min(max(l - 1, 0), len(self.balls) - 1)
            removed.extend(self.pop_color_group(check))

        return removed

    def bomb_remove(self, idx: int, radius_lr: int) -> list[tuple[pygame.Vector2, tuple[int,int,int], int]]:
        if not self.balls:
            return []
        l = max(0, idx - radius_lr)
        r = min(len(self.balls) - 1, idx + radius_lr)

        removed = []
        for b in self.balls[l:r+1]:
            removed.append((b.pos.copy(), b.color, b.radius))
        del self.balls[l:r+1]
        self._recalc_positions()

        # попробуем добить совпадения после взрыва
        if self.balls:
            check = min(max(l - 1, 0), len(self.balls) - 1)
            removed.extend(self.pop_color_group(check))
        return removed

    def coins_for_removed(self, removed_count: int) -> int:
        return removed_count * COINS_PER_BALL
