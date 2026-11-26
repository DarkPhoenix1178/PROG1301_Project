import random

from board import SodokuBoard
from knuth import DancingLinks


class SodokuGenerator:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def fill_diagonal(self, board: SodokuBoard):
        for box in range(3):
            numbers = list(range(1, 10))
            self.rng.shuffle(numbers)

            for i, num in enumerate(numbers):
                col = box * 3 + i % 3
                row = box * 3 + i // 3

                board.set_cell(col, row, num)

    def generate_solution(self):
        board = SodokuBoard([[0] * 9 for _ in range(9)])

        self.fill_diagonal(board)
        print("\n".join(map(str, board.board)))

