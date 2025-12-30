from __future__ import annotations
import pygame

class Skull:
    def __init__(self, pos: tuple[int, int], radius: int = 34):
        self.pos = pygame.Vector2(pos)
        self.radius = radius

    def draw(self, screen: pygame.Surface) -> None:
        x, y = int(self.pos.x), int(self.pos.y)
        base = (210, 210, 220)
        dark = (70, 70, 85)

        pygame.draw.circle(screen, base, (x, y), self.radius)
        pygame.draw.circle(screen, dark, (x, y), self.radius, 3)

        pygame.draw.circle(screen, dark, (x - 12, y - 6), 8)
        pygame.draw.circle(screen, dark, (x + 12, y - 6), 8)
        pygame.draw.rect(screen, dark, pygame.Rect(x - 10, y + 10, 20, 10), border_radius=3)
