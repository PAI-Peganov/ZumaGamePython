import unittest
import pygame
from src.game_path import GamePath


class TestGamePath(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.points = [(0, 0), (100, 0)]
        self.path = GamePath(self.points)

    def test_length(self):
        self.assertEqual(self.path.length, 100)

    def test_pos_start(self):
        self.assertEqual(self.path.pos_at(0), self.points[0])

    def test_pos_end(self):
        self.assertEqual(self.path.pos_at(self.path.length), self.points[-1])

    def test_pos_middle(self):
        p = self.path.pos_at(50)
        self.assertEqual(p, pygame.Vector2(50, 0))
