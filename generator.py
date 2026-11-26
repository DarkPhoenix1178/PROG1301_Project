import random

from board import SodokuBoard
from settings import DIFFICULTY_CLUES
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
        self.fill_board(board)

        return board

    def remove_clues(self, board: SodokuBoard, target):
        cells = [(col, row) for row in range(9) for col in range(9)]

        self.rng.shuffle(cells)
        remaining = 81

        for col, row in cells:
            if remaining == target:
                break

            value = board.get_cell(col, row)
            board.set_cell(col, row, 0)

            if self.has_unique_solution(board):
                remaining -= 1
            else:
                board.set_cell(col, row, value)
        return remaining

    def generate_puzzle(self, difficulty="medium"):
        low, high = DIFFICULTY_CLUES[difficulty]
        target = self.rng.randint(low, high)

        best_board = None
        best_remaining = 81

        for _ in range(5):
            board = self.generate_solution()
            remaining = self.remove_clues(board, target)

            if remaining == target:
                return board

            if remaining < best_remaining:
                best_board = board
                best_remaining = remaining

        return best_board

    @staticmethod
    def has_unique_solution(board: SodokuBoard):
        solver = DancingLinks(board)
        count, _, _ = solver.search_n_solutions(limit=2)

        return count == 1



