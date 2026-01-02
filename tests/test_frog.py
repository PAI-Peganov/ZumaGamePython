import unittest
import pygame
from src.frog import Frog


class TestFrog(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.frog = Frog((100, 100))

    def test_mouth_pos(self):
        d = pygame.Vector2(1, 0)
        p = self.frog.mouth_pos(d)
        self.assertTrue(p.x > 100)


if __name__ == '__main__':
    unittest.main()
