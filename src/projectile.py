import pygame
from utils import safe_normalize


class Projectile:
    def __init__(
        self,
        pos: pygame.Vector2,
        direction: pygame.Vector2,
        speed: float,
        color: tuple[int, int, int],
        radius: int,
        kind: str = "NORMAL",
    ):
        self.pos = pos.copy()
        self.vel = safe_normalize(direction) * speed
        self.color = color
        self.radius = radius
        self.kind = kind
        self.alive = True

    def update(self, dt: float, rect: pygame.Rect) -> None:
        self.pos += self.vel * dt
        if not rect.inflate(240, 240).collidepoint(self.pos.x, self.pos.y):
            self.alive = False
