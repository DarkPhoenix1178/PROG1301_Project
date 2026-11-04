import copy
import time

from backtrack import SodokuBacktrackingSolver
from knuth import DancingLinks
from bitmask_backtrack import BitmaskBacktracker
from bitmask_mrv_backtrack import BitmaskMRVBacktracker
from board import SodokuBoard
import pygame as pg

from renderer import SodokuRenderer
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SOLVE_DELAY


class Sodoku:
    def __init__(self, puzzle):
        self.board = SodokuBoard(puzzle)
        self.running = True
        self.solving = False

        pg.init()
        pg.display.set_caption("Sodoku")
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.renderer = SodokuRenderer(self.screen, self.board)

        # Solvers
        start = time.perf_counter_ns()
        self.backtracker = SodokuBacktrackingSolver(self.board)
        self.b_sol = copy.copy(self.backtracker.solution)
        self.b_step = 0
        build_time = (time.perf_counter_ns() - start) * 1e-6
        print(f"Backtracker Build Time: {build_time:.4f}ms")

        start = time.perf_counter_ns()
        self.knuth = DancingLinks(self.board)
        build_time = (time.perf_counter_ns() - start) * 1e-6
        print(f"Knuth Build Time: {build_time:.4f}ms")

        start = time.perf_counter_ns()
        self.bit_backtracker = BitmaskBacktracker(self.board)
        build_time = (time.perf_counter_ns() - start) * 1e-6
        print(f"Bitmask Build Time: {build_time:.4f}ms")

        start = time.perf_counter_ns()
        self.bit_mrv_backtracker = BitmaskMRVBacktracker(self.board)
        build_time = (time.perf_counter_ns() - start) * 1e-6
        print(f"MRV Bitmask Build Time: {build_time:.4f}ms")

        self.test_solvers()

        self.last_step = pg.time.get_ticks()

    def handle_mouse(self, pos):
        self.board.set_active_cell(*self.renderer.get_board_coordinates(pos))

    def handle_keyboard(self, event):
        if event.key == pg.K_F1:
            self.solving = True

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

            if self.solving:
                continue

            if event.type == pg.MOUSEBUTTONUP:
                self.handle_mouse(event.pos)
            elif event.type == pg.KEYUP:
                self.handle_keyboard(event)

    def update_b_solve_animation(self):
        if not self.solving:
            return

        now = pg.time.get_ticks()

        if now - self.last_step < SOLVE_DELAY:
            return

        if self.b_step < len(self.b_sol):
            action, col, row, num = self.b_sol[self.b_step]

            if action:
                self.board.set_cell(col, row, num)
            else:
                self.board.set_cell(col, row, 0)

            self.b_step += 1
        else:
            self.solving = False

    def test_solvers(self):
        results = []
        #  ("Backtracking", self.backtracker),
        #     ("Bitmask", self.bit_backtracker),
        solvers = [
            ("Knuth (DLX)", self.knuth),
            ("Bitmask + MRV", self.bit_mrv_backtracker),
        ]

        for name, solver in solvers:
            # Start each test with a clean solver
            solver.reset()

            # SOLVE
            start = time.perf_counter_ns()

            if name == "Backtracking":
                solver.solve()
                solution = solver.solution.copy()
                calls = None
                backtracks = None
            else:
                solution, calls, backtracks = solver.search_solution()

            solve_time = (time.perf_counter_ns() - start) / 1e6

            # Preserve ordinary backtracking visualization
            if name == "Backtracking":
                self.b_sol = solution
                self.b_step = 0

            # RESET
            start = time.perf_counter_ns()
            solver.reset()
            reset_time = (time.perf_counter_ns() - start) / 1e6

            # COUNT SOLUTIONS
            if name == "Backtracking":
                count = None
                count_time = None
                count_calls = None
                count_backtracks = None
            else:
                start = time.perf_counter_ns()
                count, count_calls, count_backtracks = (
                    solver.search_n_solutions(limit=2)
                )
                count_time = (time.perf_counter_ns() - start) / 1e6

            results.append({
                "name": name,
                "solve": solve_time,
                "reset": reset_time,
                "count": count_time,
                "solutions": count,
                "calls": calls,
                "backtracks": backtracks,
                "count_calls": count_calls,
                "count_backtracks": count_backtracks,
            })

        # TABLE 1: EXECUTION TIMES
        print("\n" + "=" * 69)
        print("SUDOKU SOLVER BENCHMARK | EXECUTION TIMES (ms)")
        print("=" * 69)
        print(
            f"{'Algorithm':<20}"
            f"{'Solve':>12}"
            f"{'Reset':>12}"
            f"{'Count':>12}"
            f"{'Solutions':>12}"
        )
        print("-" * 69)

        for r in results:
            count = f"{r['count']:.4f}" if r["count"] is not None else "N/A"
            solutions = str(r["solutions"]) if r[
                                                   "solutions"] is not None else "N/A"

            print(
                f"{r['name']:<20}"
                f"{r['solve']:>12.4f}"
                f"{r['reset']:>12.4f}"
                f"{count:>12}"
                f"{solutions:>12}"
            )

        # TABLE 2: SEARCH STATISTICS
        print("\n" + "=" * 83)
        print("SUDOKU SOLVER BENCHMARK | SEARCH STATISTICS")
        print("=" * 83)
        print(
            f"{'Algorithm':<20}"
            f"{'Solve Calls':>15}"
            f"{'Solve BT':>12}"
            f"{'Count Calls':>18}"
            f"{'Count BT':>18}"
        )
        print("-" * 83)

        for r in results:
            values = [
                r["calls"],
                r["backtracks"],
                r["count_calls"],
                r["count_backtracks"],
            ]
            values = [f"{v:,}" if v is not None else "N/A" for v in values]

            print(
                f"{r['name']:<20}"
                f"{values[0]:>15}"
                f"{values[1]:>12}"
                f"{values[2]:>18}"
                f"{values[3]:>18}"
            )

        print("=" * 83)

    def run(self):
        while self.running:
            self.handle_events()
            self.update_b_solve_animation()
            self.renderer.draw()
            pg.display.flip()
            self.clock.tick(FPS)
