import copy

from board import SodokuBoard


class DifficultyRater:
    # Make a copy of the board so the real one doesn't change.
    # work and candidates get filled in later.
    def __init__(self, board: SodokuBoard):
        self.board = copy.deepcopy(board)

        self.work = None
        self.candidates = []

    # Go through every cell and count the empty ones (0).
    # Clues = 81 - empty.
    def count_clues(self):
        empty = 0
        for row in range(9):
            for col in range(9):
                if self.board.get_cell(col, row) == 0:
                    empty += 1

        return 81 - empty

    # 35+ clues = Beginner, 28+ = Intermediate,
    # 24+ = Difficult, 17+ = Expert, less = Invalid.
    def rate_by_clues(self):
        clues = self.count_clues()

        if clues >= 35:
            return "Beginner"
        elif clues >= 28:
            return "Intermediate"
        elif clues >= 24:
            return "Difficult"
        elif clues >= 17:
            return "Expert"
        else:
            return "Invalid"

    # Copy the board and make the candidates.
    # While there are still empty cells:
    #   singles work            -> level 1
    #   pointing/claiming/pair  -> level 2
    #   x-wing/swordfish        -> level 3
    #   nothing works           -> Expert (you'd have to guess)
    # Keep the hardest level used. That's the rating.
    
    def rate_by_human(self):
        self.work = copy.deepcopy(self.board)
        self.make_candidates()
        hardest = 1

        while self.has_empty():
            if self.naked_single() or self.hidden_single():
                level = 1
            elif self.pointing() or self.claiming() or self.naked_pair():
                level = 2
            elif self.x_wing() or self.swordfish():
                level = 3
            else:
                return "Expert"

            if level > hardest:
                hardest = level

        if hardest == 1:
            return "Beginner"
        elif hardest == 2:
            return "Intermediate"
        else:
            return "Difficult"

    # Return the clue count and both ratings together.
    def rate(self):
        return {
            "clues": self.count_clues(),
            "by_clues": self.rate_by_clues(),
            "by_human": self.rate_by_human(),
        }

    # True if any cell in work is still 0.
    def has_empty(self):
        for row in range(9):
            for col in range(9):
                if self.work.get_cell(col, row) == 0:
                    return True
        return False

    # For every empty cell, try 1 to 9 and keep the valid ones.
    # Filled cells get an empty set.
    def make_candidates(self):
        self.candidates = []
        for row in range(9):
            self.candidates.append([])
            for col in range(9):
                possible = set()
                if self.work.get_cell(col, row) == 0:
                    for num in range(1, 10):
                        if self.work.is_valid(col, row, num):
                            possible.add(num)
                self.candidates[row].append(possible)

    # List all 9 rows, 9 columns and 9 boxes (27 houses).
    @staticmethod
    def get_houses():
        houses = []
        for row in range(9):
            houses.append([(col, row) for col in range(9)])
        for col in range(9):
            houses.append([(col, row) for row in range(9)])
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for y in range(box_row * 3, box_row * 3 + 3):
                    for x in range(box_col * 3, box_col * 3 + 3):
                        box.append((x, y))
                houses.append(box)
        return houses

    # Put num in the cell and clear its candidates.
    # Remove num from the same row, column and box.
    def place(self, col, row, num):
        self.work.set_cell(col, row, num)
        self.candidates[row][col] = set()

        for i in range(9):
            self.candidates[row][i].discard(num)
            self.candidates[i][col].discard(num)

        box_col, box_row = self.work.box_coordinates(col, row)
        for x in range(box_col * 3, (box_col + 1) * 3):
            for y in range(box_row * 3, (box_row + 1) * 3):
                self.candidates[y][x].discard(num)

    # Find a cell with only 1 candidate and place it.
    def naked_single(self):
        for row in range(9):
            for col in range(9):
                if len(self.candidates[row][col]) == 1:
                    num = list(self.candidates[row][col])[0]
                    self.place(col, row, num)
                    return True
        return False

    # In each house, if a number fits in only 1 cell,
    # place it there.
    def hidden_single(self):
        for house in self.get_houses():
            for num in range(1, 10):
                spots = []
                for col, row in house:
                    if num in self.candidates[row][col]:
                        spots.append((col, row))

                if len(spots) == 1:
                    col, row = spots[0]
                    self.place(col, row, num)
                    return True
        return False

    # In a box, if a number only fits in 1 row (or column),
    # remove it from that row (or column) outside the box.
    def pointing(self):
        removed = False
        for box_row in range(3):
            for box_col in range(3):
                for num in range(1, 10):
                    rows = set()
                    cols = set()
                    for y in range(box_row * 3, box_row * 3 + 3):
                        for x in range(box_col * 3, box_col * 3 + 3):
                            if num in self.candidates[y][x]:
                                rows.add(y)
                                cols.add(x)

                    if len(rows) == 1:
                        row = list(rows)[0]
                        for col in range(9):
                            if col // 3 != box_col and \
                                    num in self.candidates[row][col]:
                                self.candidates[row][col].discard(num)
                                removed = True

                    if len(cols) == 1:
                        col = list(cols)[0]
                        for row in range(9):
                            if row // 3 != box_row and \
                                    num in self.candidates[row][col]:
                                self.candidates[row][col].discard(num)
                                removed = True

                    if removed:
                        return True
        return False

    # In a row, if a number only fits inside 1 box,
    # remove it from the rest of that box.
    # Then do the same for columns.
    def claiming(self):
        for row in range(9):
            for num in range(1, 10):
                boxes = set()
                for col in range(9):
                    if num in self.candidates[row][col]:
                        boxes.add(col // 3)

                if len(boxes) == 1:
                    box_col = list(boxes)[0]
                    box_row = row // 3
                    removed = False
                    for y in range(box_row * 3, box_row * 3 + 3):
                        for x in range(box_col * 3, box_col * 3 + 3):
                            if y != row and num in self.candidates[y][x]:
                                self.candidates[y][x].discard(num)
                                removed = True
                    if removed:
                        return True

        for col in range(9):
            for num in range(1, 10):
                boxes = set()
                for row in range(9):
                    if num in self.candidates[row][col]:
                        boxes.add(row // 3)

                if len(boxes) == 1:
                    box_row = list(boxes)[0]
                    box_col = col // 3
                    removed = False
                    for y in range(box_row * 3, box_row * 3 + 3):
                        for x in range(box_col * 3, box_col * 3 + 3):
                            if x != col and num in self.candidates[y][x]:
                                self.candidates[y][x].discard(num)
                                removed = True
                    if removed:
                        return True
        return False

    # If 2 cells in a house have the same 2 candidates,
    # remove those 2 numbers from the other cells in the house.
    def naked_pair(self):
        for house in self.get_houses():
            for i in range(9):
                col1, row1 = house[i]
                if len(self.candidates[row1][col1]) != 2:
                    continue

                for j in range(i + 1, 9):
                    col2, row2 = house[j]
                    if self.candidates[row1][col1] != \
                            self.candidates[row2][col2]:
                        continue

                    pair = self.candidates[row1][col1]
                    removed = False
                    for col, row in house:
                        if (col, row) in (house[i], house[j]):
                            continue
                        for num in pair:
                            if num in self.candidates[row][col]:
                                self.candidates[row][col].discard(num)
                                removed = True
                    if removed:
                        return True
        return False

    # Find 2 rows where a number only fits in the same 2 columns.
    # Remove it from those 2 columns in every other row.
    def x_wing(self):
        for num in range(1, 10):
            for row1 in range(9):
                cols1 = [c for c in range(9)
                         if num in self.candidates[row1][c]]
                if len(cols1) != 2:
                    continue

                for row2 in range(row1 + 1, 9):
                    cols2 = [c for c in range(9)
                             if num in self.candidates[row2][c]]
                    if cols1 != cols2:
                        continue

                    removed = False
                    for col in cols1:
                        for row in range(9):
                            if row != row1 and row != row2 and \
                                    num in self.candidates[row][col]:
                                self.candidates[row][col].discard(num)
                                removed = True
                    if removed:
                        return True
        return False

    # Same as x-wing but with 3 rows and 3 columns.
    # Remove the number from those 3 columns in the other rows.
    def swordfish(self):
        for num in range(1, 10):
            rows = []
            for row in range(9):
                cols = [c for c in range(9)
                        if num in self.candidates[row][c]]
                if 2 <= len(cols) <= 3:
                    rows.append(row)

            for a in range(len(rows)):
                for b in range(a + 1, len(rows)):
                    for c in range(b + 1, len(rows)):
                        three_rows = [rows[a], rows[b], rows[c]]

                        cols = set()
                        for row in three_rows:
                            for col in range(9):
                                if num in self.candidates[row][col]:
                                    cols.add(col)

                        if len(cols) != 3:
                            continue

                        removed = False
                        for col in cols:
                            for row in range(9):
                                if row not in three_rows and \
                                        num in self.candidates[row][col]:
                                    self.candidates[row][col].discard(num)
                                    removed = True
                        if removed:
                            return True
        return False
