import math
import pygame


class Frog:
    def __init__(self, pos: tuple[int, int]):
        self.pos = pygame.Vector2(pos)
        self.base = self._make_surface()

    def _make_surface(self) -> pygame.Surface:
        s = pygame.Surface((90, 90), pygame.SRCALPHA)
        body = (70, 190, 95)
        outline = (35, 90, 55)
        eye = (240, 240, 240)
        pupil = (20, 20, 20)

        pygame.draw.circle(s, body, (45, 45), 34)
        pygame.draw.circle(s, outline, (45, 45), 34, 3)
        pygame.draw.circle(s, body, (28, 40), 13)
        pygame.draw.circle(s, body, (62, 40), 13)
        pygame.draw.circle(s, outline, (28, 40), 13, 2)
        pygame.draw.circle(s, outline, (62, 40), 13, 2)
        pygame.draw.circle(s, eye, (28, 36), 7)
        pygame.draw.circle(s, pupil, (28, 32), 3)
        pygame.draw.circle(s, eye, (62, 36), 7)
        pygame.draw.circle(s, pupil, (62, 32), 3)

        pygame.draw.arc(
            s, (140, 90, 55), pygame.Rect(28, 10, 34, 18),
            math.radians(15), math.radians(165), 3
        )
        return s

    def angle_from_dir(self, d: pygame.Vector2) -> float:
        if d.length_squared() < 1e-9:
            return 0.0
        return -math.degrees(math.atan2(d.y, d.x)) - 90

    def mouth_pos(self, d: pygame.Vector2) -> pygame.Vector2:
        if d.length_squared() < 1e-9:
            d = pygame.Vector2(1, 0)
        return self.pos + d.normalize() * 36

    def draw(self, screen: pygame.Surface, aim_dir: pygame.Vector2) -> None:
        ang = self.angle_from_dir(aim_dir)
        img = pygame.transform.rotozoom(self.base, ang, 1.0)
        r = img.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        screen.blit(img, r)
