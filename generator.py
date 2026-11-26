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

    def fill_board(self, board: SodokuBoard):
        for row in range(9):
            for col in range(9):
                if board.get_cell(col, row) != 0:
                    continue

                numbers = list(range(1, 10))
                self.rng.shuffle(numbers)

                for num in numbers:
                    if board.is_valid(col, row, num):
                        board.set_cell(col, row, num)

                        if self.fill_board(board):
                            return True

                    board.set_cell(col, row, 0)
                return False
        return True

    def generate_solution(self):
        board = SodokuBoard([[0] * 9 for _ in range(9)])

        self.fill_diagonal(board)
        print("\n".join(map(str, board.board)))
        self.fill_board(board)
        print()
        print("\n".join(map(str, board.board)))

        return board.board


