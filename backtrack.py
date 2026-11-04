import copy

from board import SodokuBoard


class SodokuBacktrackingSolver:
    def __init__(self, board: SodokuBoard):
        self.board = copy.deepcopy(board)
        self.solution = []

    def find_empty(self):
        for row in range(9):
            for col in range(9):
                if self.board.get_cell(col, row) == 0:
                    return col, row
        return None

    def solve(self):
        empty = self.find_empty()

        if empty is None:
            return True

        col, row = empty

        for num in range(1, 10):
            if not self.board.is_valid(col, row, num):
                continue

            self.solution.append((1, col, row, num))
            self.board.set_cell(col, row, num)

            if self.solve():
                return True

            self.solution.append((0, col, row, num))
            self.board.set_cell(col, row, 0)

        return False

    def reset(self):
        self.solution = []
        self.board.clear_board()
