import pygame


class Ball:
    def __init__(self, color: tuple[int, int, int], radius: int):
        self.color = color
        self.radius = radius
        self.pos = pygame.Vector2(0, 0)

    def update_pos(self, pos: pygame.Vector2):
        self.pos = pos.copy()
