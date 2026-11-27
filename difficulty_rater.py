import copy
from itertools import combinations

from board import SudokuBoard
from knuth import DancingLinks
from settings import DIFFICULTY_CLUES, MIN_CLUES


class DifficultyRater:
    # Make a copy of the board so the real one doesn't change.
    # work and candidates get filled in later.
    def __init__(self, board: SudokuBoard):
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

    # Clue counts are only a rough estimate of difficulty.
    def rate_by_clues(self):
        clues = self.count_clues()
        if clues < MIN_CLUES:
            return "Below minimum for uniqueness"

        for difficulty, (low, high) in DIFFICULTY_CLUES.items():
            if low <= clues <= high:
                return difficulty.capitalize()

        return "Outside configured ranges"

    @staticmethod
    def valid_grid(grid):
        """Check dimensions, digits and duplicate givens."""
        if len(grid) != 9 or any(len(row) != 9 for row in grid):
            return False

        for row in grid:
            for num in row:
                if type(num) is not int or not 0 <= num <= 9:
                    return False

        for house in DifficultyRater.get_houses():
            values = [grid[row][col] for col, row in house
                      if grid[row][col] != 0]
            if len(values) != len(set(values)):
                return False

        return True

    def techniques(self):
        """Ordered from simpler to more advanced techniques."""
        return [
            ("Naked Single", 1, self.naked_single),
            ("Hidden Single", 1, self.hidden_single),
            ("Pointing", 2, self.pointing),
            ("Claiming", 2, self.claiming),
            ("Naked Pair", 2, self.naked_pair),
            ("Naked Triple", 3, self.naked_triple),
            ("X-Wing", 3, self.x_wing),
            ("Swordfish", 3, self.swordfish),
        ]

    def has_contradiction(self):
        # An empty cell must have at least one candidate.
        for row in range(9):
            for col in range(9):
                if (self.work.get_cell(col, row) == 0
                        and not self.candidates[row][col]):
                    return True

        # Every missing digit must have a possible place in its house.
        for house in self.get_houses():
            placed = {self.work.get_cell(col, row) for col, row in house}
            possible = set().union(*(self.candidates[row][col]
                                     for col, row in house))
            if set(range(1, 10)) - placed - possible:
                return True

        return False

    def rate_by_human(self, validate=True):
        """Solve without guessing; validate=False is for trusted puzzles."""
        self.work = copy.deepcopy(self.board)
        self.candidates = []
        techniques = self.techniques()
        self.counts = {name: 0 for name, _, _ in techniques}
        self.hardest = None
        self.level = 0
        self.status = "invalid"
        self.steps = []

        if not self.valid_grid(self.work.board):
            return "Invalid"

        # Use a fresh solver because a successful DLX search changes its state.
        # Counting up to two distinguishes zero, one and multiple solutions.
        if validate:
            count, _, _ = DancingLinks(self.work).search_n_solutions(limit=2)
            if count == 0:
                self.status = "unsolvable"
                return "Unsolvable"
            if count > 1:
                self.status = "multiple"
                return "Multiple solutions"

        self.make_candidates()

        while self.has_empty():
            for name, level, technique in techniques:
                if technique():
                    self.counts[name] += 1
                    self.steps.append(name)
                    if level > self.level:
                        self.level = level
                        self.hardest = name
                    elif level == self.level:
                        # Prefer the later technique in the defined order.
                        order = [item[0] for item in techniques]
                        if order.index(name) > order.index(self.hardest):
                            self.hardest = name
                    break
            else:
                if self.has_contradiction():
                    self.status = "contradiction"
                    return "Contradiction"
                self.status = "stalled"
                return "Unclassified"

        if not self.valid_grid(self.work.board):
            self.status = "contradiction"
            return "Contradiction"

        self.status = "solved"
        return {0: "Beginner", 1: "Beginner", 2: "Intermediate",
                3: "Difficult"}[self.level]

    def rate(self, validate=True):
        by_human = self.rate_by_human(validate=validate)
        valid = self.valid_grid(self.board.board)
        return {
            "clues": self.count_clues() if valid else None,
            "by_clues": self.rate_by_clues() if valid else "Invalid",
            "by_human": by_human,
            "status": self.status,
            "hardest": self.hardest,
            "level": self.level,
            "remaining": sum(num == 0 for row in self.work.board
                             for num in row) if valid else None,
            "techniques": self.counts.copy(),
            "steps": len(self.steps),
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

    # A naked subset of n cells contains exactly n distinct candidates.
    # Remove those candidates from every other cell in the same house.
    def naked_subset(self, size):
        for house in self.get_houses():
            eligible = [(col, row) for col, row in house
                        if 2 <= len(self.candidates[row][col]) <= size]

            for group in combinations(eligible, size):
                values = set().union(*(self.candidates[row][col]
                                       for col, row in group))
                if len(values) != size:
                    continue

                removed = False
                for col, row in house:
                    if (col, row) in group:
                        continue
                    if self.candidates[row][col] & values:
                        self.candidates[row][col].difference_update(values)
                        removed = True

                if removed:
                    return True

        return False

    def naked_pair(self):
        return self.naked_subset(2)

    def naked_triple(self):
        return self.naked_subset(3)

    # Fish of size n: n base lines confine a digit to n cover lines.
    # Scan both row-based and column-based patterns.
    def fish(self, size):
        for transpose in (False, True):
            for num in range(1, 10):
                positions = []

                for base in range(9):
                    covers = set()
                    for cover in range(9):
                        row, col = ((cover, base) if transpose
                                    else (base, cover))
                        if num in self.candidates[row][col]:
                            covers.add(cover)
                    positions.append(covers)

                eligible = [base for base in range(9)
                            if 2 <= len(positions[base]) <= size]

                for group in combinations(eligible, size):
                    covers = set().union(*(positions[base]
                                           for base in group))
                    if len(covers) != size:
                        continue

                    removed = False
                    for base in range(9):
                        if base in group:
                            continue
                        for cover in covers:
                            row, col = ((cover, base) if transpose
                                        else (base, cover))
                            if num in self.candidates[row][col]:
                                self.candidates[row][col].discard(num)
                                removed = True

                    if removed:
                        return True

        return False

    def x_wing(self):
        return self.fish(2)

    def swordfish(self):
        return self.fish(3)
