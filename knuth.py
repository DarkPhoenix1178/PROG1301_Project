from tkinter import constants

from board import SodokuBoard


class Node:
    def __init__(self, row_id=None):
        self.L = self
        self.R = self
        self.U = self
        self.D = self
        self.C = None
        self.row_id = row_id

    def remove_vertical(self):
        self.U.D = self.D
        self.D.U = self.U
        self.C.S -= 1

    def restore_vertical(self):
        self.U.D = self
        self.D.U = self
        self.C.S += 1

    def remove_horizontal(self):
        self.L.R = self.R
        self.R.L = self.L

    def restore_horizontal(self):
        self.L.R = self
        self.R.L = self

    def insert_right(self, node):
        node.R = self.R
        self.R.L = node
        self.R = node
        node.L = self


class ColumnHeader(Node):
    def __init__(self, name):
        super().__init__()
        self.S = 0
        self.name = name
        self.C = self

    def cover(self):
        self.remove_horizontal()
        row = self.D
        while row is not self:
            node = row.R
            while node is not row:
                node.remove_vertical()
                node = node.R
            row = row.D

    def uncover(self):
        row = self.U
        while row is not self:
            node = row.L
            while node is not row:
                node.restore_vertical()
                node = node.L
            row = row.U
        self.restore_horizontal()

    def add_node(self, row_id=None):
        node = Node(row_id)
        node.C = self

        node.U = self.U
        node.D = self

        self.U.D = node
        self.U = node

        self.S += 1
        return node


class DancingLinks:
    def __init__(self, matrix: SodokuBoard):
        self.matrix = matrix

        self.headers = {}
        self.covered = set()
        self.solution = []
        self.root = ColumnHeader("root")

        self.recursive_calls = 0
        self.backtracks = 0

        for y in range(9):
            for x in range(9):
                self.register_header(("cell", x, y))

        for i in range(9):
            for digit in range(1, 10):
                self.register_header(("row", i, digit))
                self.register_header(("col", i, digit))
                self.register_header(("box", i, digit))

        for x in range(9):
            for y in range(9):
                cell_c = ('cell', x, y)
                box_idx = (y // 3) * 3 + (x // 3)
                for digit in range(1, 10):
                    data = (x, y, digit)
                    keys = [
                        cell_c,
                        ("row", y, digit),
                        ("col", x, digit),
                        ("box", box_idx, digit)
                    ]
                    nodes = [self.headers[key].add_node(data) for key in keys]

                    for i in range(3):
                        nodes[i].insert_right(nodes[i + 1])

        for y, row in enumerate(self.matrix.board):
            for x, digit in enumerate(row):
                if digit != 0:
                    self.apply_given(x, y, digit)

    def register_header(self, key):
        self.headers[key] = ColumnHeader(key)
        self.root.L.insert_right(self.headers[key])

    def reset(self):
        self.__init__(self.matrix)

    def apply_given(self, x, y, digit):
        box_idx = (y // 3) * 3 + (x // 3)
        constraints = [
            ('cell', x, y),
            ('row', y, digit),
            ('col', x, digit),
            ('box', box_idx, digit)
        ]
        for key in constraints:
            if key in self.covered:
                raise ValueError(f"Conflicting Sodoku Clue: {key}")

        for key in constraints:
            self.headers[key].cover()
            self.covered.add(key)

    def choose_column(self):
        current = self.root.R
        smallest = current

        while current is not self.root:
            if current.S < smallest.S:
                smallest = current

            current = current.R
        return smallest

    def search_solution(self):
        solved = self._search_solution()

        solution = self.solution.copy() if solved else []
        last_recursive_calls = self.recursive_calls
        last_backtracks = self.backtracks

        return solution, last_recursive_calls, last_backtracks

    def search_n_solutions(self, limit=2):
        count = self._search_n_solutions(limit)

        last_recursive_calls = self.recursive_calls
        last_backtracks = self.backtracks

        return count, last_recursive_calls, last_backtracks

    def _search_solution(self):
        self.recursive_calls += 1
        if self.root.R == self.root:
            return True

        column = self.choose_column()

        if column.S == 0:
            return False

        column.cover()

        row = column.D
        while row is not column:
            self.solution.append(row.row_id)
            node = row.R
            while node is not row:
                node.C.cover()
                node = node.R

            if self._search_solution():
                return True

            node = row.L
            while node is not row:
                node.C.uncover()
                node = node.L

            self.solution.pop()
            self.backtracks += 1
            row = row.D

        column.uncover()
        return False

    def _search_n_solutions(self, limit=2):
        self.recursive_calls += 1
        if limit <= 0:
            return 0
        if self.root.R == self.root:
            return 1

        column = self.choose_column()

        if column.S == 0:
            return 0

        column.cover()
        count = 0

        row = column.D
        while row is not column:
            self.solution.append(row.row_id)
            node = row.R
            while node is not row:
                node.C.cover()
                node = node.R

            found = self._search_n_solutions(limit - count)
            count += found

            node = row.L
            while node is not row:
                node.C.uncover()
                node = node.L

            self.solution.pop()
            if found == 0:
                self.backtracks += 1

            if count >= limit:
                break
            row = row.D

        column.uncover()
        return count
