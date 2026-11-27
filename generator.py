import copy
import random

from board import SudokuBoard
from settings import (
    DIFFICULTY_CLUES,
    MIN_CLUES,
    MAX_GENERATION_ATTEMPTS,
    FALLBACK_PUZZLES,
)
from knuth import DancingLinks


class SudokuGenerator:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def fill_diagonal(self, board: SudokuBoard):
        for box in range(3):
            numbers = list(range(1, 10))
            self.rng.shuffle(numbers)

            for i, num in enumerate(numbers):
                col = box * 3 + i % 3
                row = box * 3 + i // 3

                board.set_cell(col, row, num)

    def fill_board(self, board: SudokuBoard):
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
        board = SudokuBoard([[0] * 9 for _ in range(9)])

        self.fill_diagonal(board)

        if self.fill_board(board):
            return SudokuBoard(board.board)

        return self.fallback_puzzle(81)

    def remove_clues(self, board: SudokuBoard, target):
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
        best_remaining = 82

        for _ in range(MAX_GENERATION_ATTEMPTS):
            board = self.generate_solution()
            remaining = self.remove_clues(board, target)

            if remaining == target:
                return SudokuBoard(board.board)

            if remaining < best_remaining:
                best_board = board
                best_remaining = remaining

        if low <= best_remaining <= high:
            return SudokuBoard(best_board.board)

        return self.fallback_puzzle(target)

    def randomize_puzzle(self, puzzle):
        # Remap the digits
        digits = list(range(1, 10))
        self.rng.shuffle(digits)
        mapping = [0] + digits

        puzzle = [
            [mapping[num] for num in row]
            for row in puzzle
        ]

        # Shuffle rows within each band
        for i in range(0, 9, 3):
            rows = puzzle[i:i + 3]
            self.rng.shuffle(rows)
            puzzle[i:i + 3] = rows

        # Shuffle columns within each stack
        for i in range(0, 9, 3):
            cols = list(range(i, i + 3))
            self.rng.shuffle(cols)

            for row in puzzle:
                row[i:i + 3] = [row[col] for col in cols]

        # Shuffle entire bands and stacks
        bands = [0, 1, 2]
        stacks = [0, 1, 2]

        self.rng.shuffle(bands)
        self.rng.shuffle(stacks)

        puzzle = [
            puzzle[band * 3 + i]
            for band in bands
            for i in range(3)
        ]

        puzzle = [
            [row[stack * 3 + i]
             for stack in stacks
             for i in range(3)]
            for row in puzzle
        ]

        # Randomly transpose the matrix
        if self.rng.choice([True, False]):
            puzzle = [list(row) for row in zip(*puzzle)]

        # Randomly reflect vertically
        if self.rng.choice([True, False]):
            puzzle.reverse()

        # Randomly reflect horizontally
        if self.rng.choice([True, False]):
            for row in puzzle:
                row.reverse()

        return puzzle

    def fallback_puzzle(self, target):
        puzzle = copy.deepcopy(self.rng.choice(FALLBACK_PUZZLES))

        solver = DancingLinks(SudokuBoard(puzzle))
        solution, _, _ = solver.search_solution()

        self.rng.shuffle(solution)

        for col, row, num in solution[:target - MIN_CLUES]:
            puzzle[row][col] = num

        puzzle = self.randomize_puzzle(puzzle)

        return SudokuBoard(puzzle)

    @staticmethod
    def has_unique_solution(board: SudokuBoard):
        solver = DancingLinks(board)
        count, _, _ = solver.search_n_solutions(limit=2)

        return count == 1
