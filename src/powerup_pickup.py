import pygame
import math


class PowerUpPickup:
    def __init__(self, pos: pygame.Vector2, kind: str):
        self.pos = pos.copy()
        self.kind = kind
        self.alive = True
        self.t = 0.0

    def update(self, dt: float, frog_pos: pygame.Vector2) -> None:
        self.t += dt
        pull = (frog_pos - self.pos)
        if pull.length_squared() > 1e-6:
            self.pos += pull.normalize() * (70.0 * dt)
        self.pos.y += math.sin(self.t * 6.0) * 10.0 * dt

        if (frog_pos - self.pos).length() < 28:
            self.alive = False

    def draw(self, screen: pygame.Surface) -> None:
        c = {
            "SLOW": (120, 220, 255),
            "REVERSE": (255, 170, 120),
            "SHOT_FAST": (170, 255, 170),
            "BOMB": (255, 120, 120),
            "BURST": (210, 160, 255),
        }.get(self.kind, (220, 220, 220))
        pygame.draw.circle(screen, c, (int(self.pos.x), int(self.pos.y)), 10)
        pygame.draw.circle(
            screen, (20, 20, 25), (int(self.pos.x), int(self.pos.y)), 10, 2
        )
