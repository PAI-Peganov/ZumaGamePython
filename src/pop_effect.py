from __future__ import annotations
import pygame

class PopEffect:
    def __init__(self, pos: pygame.Vector2, color: tuple[int, int, int], radius: int, duration: float = 0.35):
        self.pos = pos.copy()
        self.color = color
        self.radius = radius
        self.duration = duration
        self.t = 0.0
        self.alive = True

    def update(self, dt: float) -> None:
        self.t += dt
        if self.t >= self.duration:
            self.alive = False

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return
        k = min(1.0, self.t / self.duration)
        alpha = int(255 * (1.0 - k))
        r = int(self.radius * (1.0 + 0.6 * k))
        surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (r + 1, r + 1), r)
        screen.blit(surf, (self.pos.x - r - 1, self.pos.y - r - 1))
