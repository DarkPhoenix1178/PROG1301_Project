import copy

from board import SudokuBoard


class SudokuBacktrackingSolver:
    def __init__(self, board: SudokuBoard):
        self.board = copy.deepcopy(board)
        self.solution = []
        self.recursive_calls = 0
        self.backtracks = 0

    def find_empty(self):
        for row in range(9):
            for col in range(9):
                if self.board.get_cell(col, row) == 0:
                    return col, row
        return None

    def solve(self):
        self.recursive_calls += 1
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
            self.backtracks += 1

        return False

    def reset(self):
        self.solution = []
        self.recursive_calls = 0
        self.backtracks = 0
        self.board.clear_board()

    def search_n_solutions(self, limit=2):
        count = self._search_n_solutions(limit)
        return count, self.recursive_calls, self.backtracks

    def _search_n_solutions(self, limit):
        self.recursive_calls += 1
        if limit <= 0:
            return 0

        empty = self.find_empty()
        if empty is None:
            return 1

        col, row = empty
        count = 0
        for num in range(1, 10):
            if not self.board.is_valid(col, row, num):
                continue

            self.board.set_cell(col, row, num)
            found = self._search_n_solutions(limit - count)
            self.board.set_cell(col, row, 0)
            count += found

            if found == 0:
                self.backtracks += 1
            if count >= limit:
                break

        return count
