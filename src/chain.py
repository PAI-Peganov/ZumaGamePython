import random
import pygame
from ball import Ball
from game_path import GamePath
from settings import COINS_PER_BALL


class BallChain:
    def __init__(
            self, path: GamePath, colors: list[tuple[int, int, int]],
            ball_radius: int, spacing: float, speed: float, count: int
    ):
        self.path = path
        self.colors = colors
        self.ball_radius = ball_radius
        self.spacing = spacing
        self.base_speed = speed

        self.balls: list[Ball] = [
            Ball(random.choice(self.colors), ball_radius) for _ in range(count)
        ]
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
        return (
            bool(self.balls) and
            self.head_s >= self.path.length - self.ball_radius * 0.6
        )

    def try_insert(
            self, proj_pos: pygame.Vector2, proj_r: int,
            proj_color: tuple[int, int, int]
    ) -> int | None:
        hit_1 = None
        hit_2 = None
        best_1 = 10**18
        best_2 = 10**18
        for i, b in enumerate(self.balls):
            rr = proj_r + b.radius
            d2 = (proj_pos.x - b.pos.x) ** 2 + (proj_pos.y - b.pos.y) ** 2
            if d2 <= rr*rr and d2 < best_1:
                best_2 = best_1
                best_1 = d2
                hit_2 = hit_1
                hit_1 = i
            if hit_1 != i and d2 < best_2:
                best_2 = d2
                hit_2 = i

        if hit_1 is None:
            return None

        if hit_2 is not None and hit_2 > hit_1:
            hit_1 = hit_2
        self.balls.insert(hit_1, Ball(proj_color, self.ball_radius))
        self._recalc_positions()
        return hit_1

    def pop_color_group(
            self, idx: int
    ) -> list[tuple[pygame.Vector2, tuple[int, int, int], int]]:
        if not self.balls or idx < 0 or idx >= len(self.balls):
            return []

        c = self.balls[idx].color
        l = idx
        r = idx
        while l > 0 and self.balls[l - 1].color == c:
            l -= 1
        while r + 1 < len(self.balls) and self.balls[r + 1].color == c:
            r += 1
        if (r - l + 1) < 3:
            return []

        removed = []
        for b in self.balls[l:r + 1]:
            removed.append((b.pos.copy(), b.color, b.radius))

        del self.balls[l:r + 1]
        self.head_s -= self.spacing * len(removed)
        self._recalc_positions()

        if self.balls:
            check = min(max(l - 1, 0), len(self.balls) - 1)
            removed.extend(self.pop_color_group(check))

        return removed

    def bomb_remove(
            self, idx: int, radius_lr: int
    ) -> list[tuple[pygame.Vector2, tuple[int, int, int], int]]:
        if not self.balls:
            return []
        l = max(0, idx - radius_lr)
        r = min(len(self.balls) - 1, idx + radius_lr)

        removed = []
        for b in self.balls[l:r + 1]:
            removed.append((b.pos.copy(), b.color, b.radius))
        del self.balls[l:r + 1]
        self._recalc_positions()

        if self.balls:
            check = min(max(l - 1, 0), len(self.balls) - 1)
            removed.extend(self.pop_color_group(check))
        return removed
