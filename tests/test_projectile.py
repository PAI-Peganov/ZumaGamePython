import unittest
import pygame
from src.projectile import Projectile


class TestProjectile(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.p = Projectile(
            pos=pygame.Vector2(0, 0),
            direction=pygame.Vector2(1, 0),
            speed=100,
            color=(255, 0, 0),
            radius=5
        )

    def test_move(self):
        self.p.update(1.0, pygame.Rect(0, 0, 500, 500))
        self.assertEqual(self.p.pos.x, 100)
