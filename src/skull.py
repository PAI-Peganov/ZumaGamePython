import pygame


class Skull:
    def __init__(self, pos: pygame.Vector2, radius: int = 34):
        self.pos = pos.copy()
        self.radius = radius

    def draw(self, screen: pygame.Surface) -> None:
        x, y = int(self.pos.x), int(self.pos.y)
        base = (210, 210, 220)
        dark = (70, 70, 85)

        pygame.draw.circle(screen, base, self.pos, self.radius)
        pygame.draw.circle(screen, dark, self.pos, self.radius, 3)

        pygame.draw.circle(
            screen, dark, (x - self.radius // 3, y - self.radius // 6),
            self.radius // 4
        )
        pygame.draw.circle(
            screen, dark, (x + self.radius // 3, y - self.radius // 6),
            self.radius // 4)
        pygame.draw.rect(
            screen, dark, pygame.Rect(
                x - self.radius // 3, y + self.radius // 3,
                self.radius // 3 * 2, self.radius // 3
            ), border_radius=3
        )
