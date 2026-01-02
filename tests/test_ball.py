import unittest
import pygame
from src.ball import Ball
from src.game_path import GamePath


class TestBall(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.path = GamePath([(0, 0), (100, 0)])
        self.ball = Ball((255, 0, 0), 10)

    def test_update_pos(self):
        self.ball.update_pos(self.path.pos_at(50))
        self.assertEqual(self.ball.pos, pygame.Vector2(50, 0))
