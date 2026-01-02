import unittest
import pygame
from src.chain import BallChain
from src.game_path import GamePath


class TestBallChain(unittest.TestCase):
    def setUp(self):
        pygame.init()
        path = GamePath([(0, 0), (300, 0)])
        self.chain = BallChain(
            path=path,
            colors=[(255, 0, 0)],
            ball_radius=10,
            spacing=22,
            speed=0,
            count=4
        )

    def test_chain_length(self):
        self.assertEqual(len(self.chain.balls), 5)

    def test_pop_matches(self):
        removed = self.chain.pop_color_group(2)
        self.assertTrue(len(removed) == 4)
