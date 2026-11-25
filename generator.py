import random

from board import SodokuBoard
from knuth import DancingLinks


class SodokuGenerator:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def generate_solution(self):
        board = SodokuBoard([[0] * 9 for _ in range(9)])
