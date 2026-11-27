import copy
import time
from queue import Empty, Full, Queue
from threading import Event, Thread

import pygame as pg

from backtrack import SudokuBacktrackingSolver
from knuth import DancingLinks
from bitmask_backtrack import BitmaskBacktracker
from bitmask_mrv_backtrack import BitmaskMRVBacktracker
from board import SudokuBoard
from difficulty_rater import DifficultyRater
from renderer import SudokuRenderer
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SOLVE_DELAY


SOLVERS = [
    ("Backtracking", SudokuBacktrackingSolver),
    ("Bitmask", BitmaskBacktracker),
    ("Bitmask + MRV", BitmaskMRVBacktracker),
    ("Knuth (DLX)", DancingLinks),
    ("Logical Solver", DifficultyRater),
    ("Logic + MRV", DifficultyRater),
]


class AnimationCancelled(Exception):
    pass


class SolutionTrace(list):
    """Observe the existing solver's placement/undo operations."""

    def __init__(self, publish, backtracking=False):
        super().__init__()
        self.publish = publish
        self.backtracking = backtracking

    def append(self, item):
        if self.backtracking:
            # Ordinary backtracking already emits four-element events.
            # It never reads its trace during solve(), so do not retain it.
            self.publish(("move", *item))
        else:
            super().append(item)
            self.publish(("move", 1, *item))

    def pop(self, index=-1):
        item = super().pop(index)
        self.publish(("move", 0, *item))
        return item


def solve_hybrid(rater, publish=None):
    """Try logic first; finish with MRV only if logic stalls."""
    logic = rater.rate(validate=False)
    status = logic["status"].capitalize()
    calls = backtracks = search_steps = 0
    logic["fallback_used"] = logic["status"] == "stalled"

    if logic["fallback_used"]:
        # Keep all logical placements, and search only the remaining cells.
        board = SudokuBoard(copy.deepcopy(rater.work.board))
        solver = BitmaskMRVBacktracker(board)

        if publish is not None:
            publish(("fallback",))
            solver.solution = SolutionTrace(publish)

        solution, calls, backtracks = solver.search_solution()
        search_steps = calls - 1 + backtracks

        if solution:
            rater.work.board = copy.deepcopy(solver.board.board)
            status = "Solved"
        else:
            status = "Unsolvable"

    logic["fallback_calls"] = calls
    logic["fallback_backtracks"] = backtracks
    logic["fallback_steps"] = search_steps
    return logic, status, calls, backtracks, logic["steps"] + search_steps


class AnimatedRater(DifficultyRater):
    """Capture each successful deduction without changing its algorithm."""

    def __init__(self, board, publish):
        super().__init__(board)
        self.publish = publish

    def techniques(self):
        def observe(name, technique):
            def step():
                if not technique():
                    return False
                self.publish(("logic", name, copy.deepcopy(self.work.board),
                              copy.deepcopy(self.candidates)))
                return True
            return step

        return [(name, level, observe(name, technique))
                for name, level, technique in super().techniques()]


class SolverAnimation:
    """One independent solver, with a bounded queue of real search events."""

    def __init__(self, name, solver_class, puzzle, benchmark):
        self.name = name
        self.board = SudokuBoard(copy.deepcopy(puzzle))
        self.board.active_cell = None
        self.solver_class = solver_class
        self.benchmark = benchmark
        self.events = Queue(maxsize=128)
        self.cancel = Event()
        self.status = "Searching"
        self.steps = 0
        self.backtracks = 0
        self.last_action = "Ready"
        self.changed = []
        self.undo = False
        self.candidates = None
        if solver_class is DifficultyRater:
            rater = DifficultyRater(self.board)
            rater.work = copy.deepcopy(self.board)
            rater.make_candidates()
            self.candidates = rater.candidates
        self.thread = Thread(target=self.solve, daemon=True)
        self.thread.start()

    def publish(self, event):
        while not self.cancel.is_set():
            try:
                self.events.put(event, timeout=0.05)
                return
            except Full:
                continue
        raise AnimationCancelled

    def solve(self):
        try:
            board = SudokuBoard(copy.deepcopy(self.board.original))
            if self.solver_class is DifficultyRater:
                solver = AnimatedRater(board, self.publish)
                if self.name == "Logic + MRV":
                    _, status, _, _, _ = solve_hybrid(solver, self.publish)
                else:
                    logic = solver.rate(validate=False)
                    status = logic["status"].capitalize()
            else:
                solver = self.solver_class(board)
                ordinary = self.solver_class is SudokuBacktrackingSolver
                solver.solution = SolutionTrace(self.publish, ordinary)
                if ordinary:
                    solved = solver.solve()
                else:
                    solution, _, _ = solver.search_solution()
                    solved = bool(solution) or not any(
                        0 in row for row in board.board)
                status = "Solved" if solved else "Unsolvable"
            self.publish(("done", status))
        except AnimationCancelled:
            pass
        except Exception as error:
            try:
                self.publish(("done", f"Error: {error}"))
            except AnimationCancelled:
                pass

    def advance(self):
        if self.status != "Searching":
            return
        try:
            event = self.events.get_nowait()
        except Empty:
            return

        if event[0] == "done":
            self.status = event[1]
            if self.status == "Solved" and (
                    any(0 in row for row in self.board.board)
                    or not DifficultyRater.valid_grid(self.board.board)):
                self.status = "Invalid result"
            return

        if event[0] == "fallback":
            self.candidates = None
            self.changed = []
            self.undo = False
            self.last_action = "MRV fallback"
            return

        self.steps += 1
        if event[0] == "move":
            _, action, col, row, num = event
            self.board.set_cell(col, row, num if action else 0)
            self.changed = [(col, row)]
            self.undo = not action
            self.backtracks += int(self.undo)
            self.last_action = f"Place {num}" if action else f"Undo {num}"
            if self.name == "Logic + MRV":
                self.last_action = "MRV: " + self.last_action
        else:
            _, name, grid, candidates = event
            placements = []
            eliminations = []
            for row in range(9):
                for col in range(9):
                    if grid[row][col] != self.board.get_cell(col, row):
                        placements.append((col, row))
                    elif candidates[row][col] != self.candidates[row][col]:
                        eliminations.append((col, row))
            self.board.board = grid
            self.candidates = candidates
            self.changed = placements or eliminations
            self.last_action = name


class Sudoku:
    def __init__(self, puzzle):
        self.board = SudokuBoard(puzzle)
        self.running = True
        self.solving = False

        pg.init()
        pg.display.set_caption("Sudoku")
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.renderer = SudokuRenderer(self.screen, self.board)

        self.animations = []
        self.paused = False
        self.steps_per_frame = 20
        self.last_step = pg.time.get_ticks()
        self.results = self.test_solvers()

    def handle_mouse(self, pos):
        self.board.set_active_cell(*self.renderer.get_board_coordinates(pos))

    def handle_keyboard(self, event):
        if event.key == pg.K_F1:
            self.start_comparison()
            return

        if self.solving:
            if event.key == pg.K_ESCAPE:
                self.stop_comparison()
            elif event.key == pg.K_SPACE:
                self.paused = not self.paused
            elif event.key == pg.K_UP:
                self.steps_per_frame = min(2000, self.steps_per_frame * 2)
            elif event.key == pg.K_DOWN:
                self.steps_per_frame = max(1, self.steps_per_frame // 2)
            elif event.key == pg.K_RIGHT and self.paused:
                for animation in self.animations:
                    animation.advance()
            return

        if not self.board.cell_active():
            return

        col, row = self.board.get_active_cell()
        directions = {
            pg.K_RIGHT: (1, 0),
            pg.K_d: (1, 0),
            pg.K_LEFT: (-1, 0),
            pg.K_a: (-1, 0),
            pg.K_DOWN: (0, 1),
            pg.K_s: (0, 1),
            pg.K_UP: (0, -1),
            pg.K_w: (0, -1),
        }

        if event.key in directions:
            dx, dy = directions[event.key]
            fx, fy = col + dx, row + dy
            self.board.set_active_cell(fx, fy)
            return

        if self.board.is_cell_given(col, row):
            return

        if event.unicode in list("123456789"):
            self.board.set_active_cell_value(int(event.unicode))

        if event.key in (pg.K_0, pg.K_KP0, pg.K_BACKSPACE, pg.K_DELETE):
            self.board.set_active_cell_value(0)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                self.cancel_animations()
                return

            if event.type == pg.MOUSEBUTTONUP and not self.solving:
                self.handle_mouse(event.pos)
            elif event.type == pg.KEYUP:
                self.handle_keyboard(event)

    def cancel_animations(self):
        for animation in self.animations:
            animation.cancel.set()
        self.animations = []

    def start_comparison(self):
        self.cancel_animations()
        self.solving = True
        self.paused = False
        self.last_step = pg.time.get_ticks()
        self.animations = [
            SolverAnimation(name, solver_class, self.board.original, result)
            for (name, solver_class), result in zip(SOLVERS, self.results)
        ]
        width, height = pg.display.get_desktop_sizes()[0]
        self.screen = pg.display.set_mode((min(1200, width - 40),
                                           min(920, height - 80)))
        self.comparison_renderer = SudokuRenderer(self.screen, self.board)
        self.comparison_renderer.prepare_comparison(self.animations)

    def stop_comparison(self):
        self.cancel_animations()
        self.solving = False
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.renderer = SudokuRenderer(self.screen, self.board)

    def update_b_solve_animation(self):
        if not self.solving or self.paused:
            return

        now = pg.time.get_ticks()
        if now - self.last_step < SOLVE_DELAY:
            return
        self.last_step = now

        # One event per solver per round. Drawing remains on the main thread.
        deadline = time.perf_counter_ns() + 8_000_000
        for _ in range(self.steps_per_frame):
            for animation in self.animations:
                animation.advance()
            if time.perf_counter_ns() >= deadline:
                break
            if all(a.status != "Searching" for a in self.animations):
                break

    def test_solvers(self):
        results = []
        puzzle = self.board.original
        if not DifficultyRater.valid_grid(puzzle):
            raise ValueError("Invalid Sudoku puzzle.")

        for name, solver_class in SOLVERS:
            board = SudokuBoard(copy.deepcopy(puzzle))
            start = time.perf_counter_ns()
            solver = solver_class(board)
            build_time = (time.perf_counter_ns() - start) / 1e6

            logical = solver_class is DifficultyRater
            ordinary = solver_class is SudokuBacktrackingSolver
            logic = None
            start = time.perf_counter_ns()
            if logical:
                if name == "Logic + MRV":
                    logic, status, calls, backtracks, steps = solve_hybrid(
                        solver)
                else:
                    logic = solver.rate(validate=False)
                    status = logic["status"].capitalize()
                    steps = logic["steps"]
                    calls = backtracks = None
                solved = status == "Solved"
            elif ordinary:
                solved = solver.solve()
                calls = solver.recursive_calls
                backtracks = solver.backtracks
            else:
                solution, calls, backtracks = solver.search_solution()
                solved = bool(solution) or not any(0 in row for row in puzzle)
            solve_time = (time.perf_counter_ns() - start) / 1e6

            # Check the actual output, outside the timed solve.
            if logical:
                grid = solver.work.board
            elif ordinary:
                grid = solver.board.board
                status = "Solved" if solved else "Unsolvable"
                steps = len(solver.solution)
            else:
                grid = copy.deepcopy(puzzle)
                for col, row, num in solution:
                    grid[row][col] = num
                status = "Solved" if solved else "Unsolvable"
                steps = calls - 1 + backtracks

            remaining = sum(num == 0 for row in grid for num in row)
            preserved = all(not puzzle[r][c] or puzzle[r][c] == grid[r][c]
                            for r in range(9) for c in range(9))
            if not preserved or not DifficultyRater.valid_grid(grid) or (
                    solved and remaining):
                status = "Invalid result"

            # RESET: the rater has no reset method, so reconstruct it.
            start = time.perf_counter_ns()
            if logical:
                solver = solver_class(board)
            else:
                solver.reset()
            reset_time = (time.perf_counter_ns() - start) / 1e6

            # COUNT: neither logical mode implements solution counting.
            count = count_time = count_calls = count_backtracks = None
            if not logical:
                start = time.perf_counter_ns()
                count, count_calls, count_backtracks = (
                    solver.search_n_solutions(limit=2)
                )
                count_time = (time.perf_counter_ns() - start) / 1e6

            results.append({
                "name": name, "build": build_time, "solve": solve_time,
                "total": build_time + solve_time,
                "reset": reset_time, "count": count_time, "solutions": count,
                "calls": calls, "backtracks": backtracks,
                "count_calls": count_calls,
                "count_backtracks": count_backtracks,
                "status": status, "remaining": remaining,
                "steps": steps, "logic": logic,
            })

        def table(title, columns):
            width = sum(col[1] for col in columns)
            print("\n" + "=" * width)
            print(title)
            print("=" * width)
            print("".join(f"{label:{'<' if i == 0 else '>'}{size}}"
                          for i, (label, size, _, _) in enumerate(columns)))
            print("-" * width)
            for result in results:
                values = []
                for i, (_, size, key, fmt) in enumerate(columns):
                    value = result[key]
                    text = "N/A" if value is None else format(value, fmt)
                    values.append(f"{text:{'<' if i == 0 else '>'}{size}}")
                print("".join(values))
            print("=" * width)

        table("SUDOKU SOLVER BENCHMARK | EXECUTION TIMES (ms)", [
            ("Algorithm", 20, "name", "s"), ("Build", 12, "build", ".4f"),
            ("Solve", 12, "solve", ".4f"), ("Build+Solve", 14, "total", ".4f"),
            ("Reset", 12, "reset", ".4f"),
            ("Count", 12, "count", ".4f"), ("Solutions*", 12, "solutions", "d"),
        ])
        table("SUDOKU SOLVER BENCHMARK | SEARCH STATISTICS", [
            ("Algorithm", 20, "name", "s"), ("Solve Calls", 15, "calls", ",d"),
            ("Solve BT", 12, "backtracks", ",d"),
            ("Count Calls", 15, "count_calls", ",d"),
            ("Count BT", 12, "count_backtracks", ",d"),
        ])
        table("SUDOKU SOLVER BENCHMARK | COMPLETION", [
            ("Algorithm", 20, "name", "s"), ("Status", 18, "status", "s"),
            ("Steps", 12, "steps", ",d"), ("Remaining", 12, "remaining", "d"),
        ])
        print("* Counts are capped at 2; 2 means multiple solutions.")
        print("Search steps = placements + undos; "
              "hybrid steps also include deductions.")
        print("Hybrid search calls and backtracks "
              "refer to the MRV fallback only.")
        print("Both logical modes exclude DLX uniqueness validation; "
              "reset rebuilds rater.")
        logic = results[-2]["logic"]
        hybrid = results[-1]["logic"]
        print("\nSUDOKU LOGICAL SOLVER | DIFFICULTY ANALYSIS")
        print(f"Clues: {logic['clues']} | By clues: {logic['by_clues']}")
        print(
            f"By human: {logic['by_human']} | Hardest: {logic['hardest'] or 
                                                        'None'}")
        print(
            f"Logical phase: {logic['status']} | Remaining: "
            f"{logic['remaining']}")
        print(f"{'Technique':<25}{'Applications':>15}")
        for name, count in logic["techniques"].items():
            print(f"{name:<25}{count:>15}")
        print("\nSUDOKU HYBRID SOLVER | LOGIC + MRV")
        print(
            f"Logical phase: {hybrid['status']} | Remaining: "
            f"{hybrid['remaining']}")
        print(f"MRV fallback: {'Yes' if hybrid['fallback_used'] else 'No'}")
        print(f"MRV calls: {hybrid['fallback_calls']:,} | "
              f"MRV backtracks: {hybrid['fallback_backtracks']:,}")
        print(f"MRV steps: {hybrid['fallback_steps']:,}")
        print(f"Final status: {results[-1]['status']} | "
              f"Remaining: {results[-1]['remaining']}")
        return results

    def run(self):
        try:
            while self.running:
                self.handle_events()
                if not self.running:
                    break
                if self.solving:
                    self.update_b_solve_animation()
                    self.comparison_renderer.draw_comparison(
                        self.paused, self.steps_per_frame)
                else:
                    self.renderer.draw()
                pg.display.flip()
                self.clock.tick(min(FPS, 60) if self.solving else FPS)
        finally:
            self.cancel_animations()
