import copy


class SodokuBoard:
    def __init__(self, grid):
        self.original = grid
        self.board = copy.deepcopy(self.original)

        self.active_cell = (8, 5)

    def is_valid(self, col, row, value):
        # Row and Column
        for i in range(9):
            if self.get_cell(col, i) == value:
                return False
            if self.get_cell(i, row) == value:
                return False

        # Box
        box_col, box_row = self.box_coordinates(col, row)
        for x in range(box_col * 3, (box_col + 1) * 3):
            for y in range(box_row * 3, (box_row + 1) * 3):
                if self.get_cell(x, y) == value:
                    return False

        return True

    def set_active_cell(self, col, row):
        if self.within_bounds(col, row):
            self.active_cell = (col, row)

    def get_active_cell(self):
        return self.active_cell

    def get_active_value(self):
        if not self.cell_active():
            return None

        col, row = self.active_cell
        return self.board[row][col]

    def set_active_cell_value(self, value):
        if not self.cell_active():
            return

        col, row = self.get_active_cell()
        self.board[row][col] = value

    def clear_board(self):
        self.board = copy.deepcopy(self.original)

    def is_cell_given(self, col, row):
        if not self.within_bounds(col, row):
            raise ValueError("Invalid value for col or row.")

        if self.original[row][col] == 0:
            return False

        return True

    def get_cell(self, col, row):
        if not self.within_bounds(col, row):
            raise IndexError("col or row out of bounds.")

        return self.board[row][col]

    def set_cell(self, col, row, value):
        if self.within_bounds(col, row):
            self.board[row][col] = value

    def cell_active(self):
        if self.active_cell is None:
            return False

        return True

    @staticmethod
    def within_bounds(col, row):
        if 0 <= col <= 8 and 0 <= row <= 8:
            return True
        return False

    @staticmethod
    def valid_value(value):
        if 0 <= value <= 9:
            return True

        return False

    @staticmethod
    def box_coordinates(col, row):
        return (col // 3), (row // 3)

    @staticmethod
    def box_index(col, row):
        return ((row // 3) * 3) + (col // 3)
