import copy
import time

from backtrack import SodokuBacktrackingSolver
from knuth import DancingLinks
from bitmask_backtrack import BitmaskBacktracker
from bitmask_mrv_backtrack import BitmaskMRVBacktracker
from board import SodokuBoard
from difficulty_rater import DifficultyRater
import pygame as pg

from renderer import SodokuRenderer
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class Sodoku:
    def __init__(self, puzzle):
        self.board = SodokuBoard(puzzle)
        self.running = True

        pg.init()
        pg.display.set_caption("Sodoku")
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.renderer = SodokuRenderer(self.screen, self.board)

        self.results = self.test_solvers()

    def handle_mouse(self, pos):
        self.board.set_active_cell(*self.renderer.get_board_coordinates(pos))

    def handle_keyboard(self, event):
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

            if event.type == pg.MOUSEBUTTONUP:
                self.handle_mouse(event.pos)
            elif event.type == pg.KEYUP:
                self.handle_keyboard(event)

    def test_solvers(self):
        results = []
        puzzle = self.board.original
        if not DifficultyRater.valid_grid(puzzle):
            raise ValueError("Invalid Sudoku puzzle.")

        solvers = [
            ("Backtracking", SodokuBacktrackingSolver),
            ("Bitmask", BitmaskBacktracker),
            ("Bitmask + MRV", BitmaskMRVBacktracker),
            ("Knuth (DLX)", DancingLinks),
            ("Logical Solver", DifficultyRater),
            ("Logic + MRV", DifficultyRater),
        ]

        for name, solver_class in solvers:
            # Start with the same original givens for every solver.
            board = SodokuBoard(copy.deepcopy(puzzle))
            start = time.perf_counter_ns()
            solver = solver_class(board)
            build_time = (time.perf_counter_ns() - start) / 1e6

            # SOLVE
            logical = solver_class is DifficultyRater
            logic = None
            fallback_used = False
            start = time.perf_counter_ns()

            if logical:
                # Do not include DLX uniqueness checking in logic's solve time.
                logic = solver.rate(validate=False)
                status = logic["status"].capitalize()
                steps = logic["steps"]
                calls = backtracks = None

                if name == "Logic + MRV":
                    calls = backtracks = 0
                    if logic["status"] == "stalled":
                        fallback_used = True
                        remaining_board = SodokuBoard(solver.work.board)
                        mrv = BitmaskMRVBacktracker(remaining_board)
                        solution, calls, backtracks = mrv.search_solution()
                        steps += calls - 1 + backtracks
                        if solution:
                            solver.work.board = mrv.board.board
                            status = "Solved"
                        else:
                            status = "Unsolvable"
                solved = status == "Solved"
            elif solver_class is SodokuBacktrackingSolver:
                solved = solver.solve()
                calls = solver.recursive_calls
                backtracks = solver.backtracks
            else:
                solution, calls, backtracks = solver.search_solution()
                solved = bool(solution) or not any(0 in row for row in puzzle)

            solve_time = (time.perf_counter_ns() - start) / 1e6

            # Verify the actual result outside the timed search.
            if logical:
                grid = solver.work.board
            elif solver_class is SodokuBacktrackingSolver:
                grid = solver.board.board
                steps = len(solver.solution)
                status = "Solved" if solved else "Unsolvable"
            else:
                grid = copy.deepcopy(puzzle)
                for col, row, num in solution:
                    grid[row][col] = num
                steps = calls - 1 + backtracks
                status = "Solved" if solved else "Unsolvable"

            remaining = sum(num == 0 for row in grid for num in row)
            preserved = all(puzzle[r][c] == 0 or puzzle[r][c] == grid[r][c]
                            for r in range(9) for c in range(9))
            if (not preserved or not DifficultyRater.valid_grid(grid)
                    or (solved and remaining)):
                status = "Invalid result"

            # RESET
            start = time.perf_counter_ns()
            if logical:
                solver = solver_class(board)
            else:
                solver.reset()
            reset_time = (time.perf_counter_ns() - start) / 1e6

            # COUNT SOLUTIONS (up to two)
            count = count_time = count_calls = count_backtracks = None
            if not logical:
                start = time.perf_counter_ns()
                count, count_calls, count_backtracks = (
                    solver.search_n_solutions(limit=2)
                )
                count_time = (time.perf_counter_ns() - start) / 1e6

            results.append({
                "name": name,
                "build": build_time,
                "solve": solve_time,
                "total": build_time + solve_time,
                "reset": reset_time,
                "count": count_time,
                "solutions": count,
                "calls": calls,
                "backtracks": backtracks,
                "count_calls": count_calls,
                "count_backtracks": count_backtracks,
                "status": status,
                "remaining": remaining,
                "steps": steps,
                "logic": logic,
                "fallback_used": fallback_used,
            })

        # TABLE 1: EXECUTION TIMES
        print("\n" + "=" * 94)
        print("SUDOKU SOLVER BENCHMARK | EXECUTION TIMES (ms)")
        print("=" * 94)
        print(f"{'Algorithm':<20}{'Build':>12}{'Solve':>12}"
              f"{'Build+Solve':>14}{'Reset':>12}{'Count':>12}"
              f"{'Solutions*':>12}")
        print("-" * 94)

        for r in results:
            count = f"{r['count']:.4f}" if r["count"] is not None else "N/A"
            solutions = (str(r["solutions"])
                         if r["solutions"] is not None else "N/A")
            print(f"{r['name']:<20}{r['build']:>12.4f}{r['solve']:>12.4f}"
                  f"{r['total']:>14.4f}{r['reset']:>12.4f}"
                  f"{count:>12}{solutions:>12}")
        print("=" * 94)

        # TABLE 2: SEARCH STATISTICS
        print("\n" + "=" * 83)
        print("SUDOKU SOLVER BENCHMARK | SEARCH STATISTICS")
        print("=" * 83)
        print(f"{'Algorithm':<20}{'Solve Calls':>15}{'Solve BT':>12}"
              f"{'Count Calls':>18}{'Count BT':>18}")
        print("-" * 83)

        for r in results:
            values = [r["calls"], r["backtracks"], r["count_calls"],
                      r["count_backtracks"]]
            values = [f"{v:,}" if v is not None else "N/A" for v in values]
            print(f"{r['name']:<20}{values[0]:>15}{values[1]:>12}"
                  f"{values[2]:>18}{values[3]:>18}")
        print("=" * 83)

        # TABLE 3: COMPLETION
        print("\n" + "=" * 62)
        print("SUDOKU SOLVER BENCHMARK | COMPLETION")
        print("=" * 62)
        print(f"{'Algorithm':<20}{'Status':>18}{'Steps':>12}{'Remaining':>12}")
        print("-" * 62)
        for r in results:
            print(f"{r['name']:<20}{r['status']:>18}{r['steps']:>12,}"
                  f"{r['remaining']:>12}")
        print("=" * 62)

        # TABLE 4: LOGICAL TECHNIQUES
        logic = results[-2]["logic"]
        hybrid = results[-1]["logic"]
        print("\n" + "=" * 61)
        print("SUDOKU SOLVER BENCHMARK | LOGICAL TECHNIQUES")
        print("=" * 61)
        print(f"{'Technique':<25}{'Logic':>18}{'Logic + MRV':>18}")
        print("-" * 61)
        for name, count in logic["techniques"].items():
            print(f"{name:<25}{count:>18,}{hybrid['techniques'][name]:>18,}")
        print("=" * 61)
        print(f"Clues: {logic['clues']} | By clues: {logic['by_clues']}")
        print(f"By human: {logic['by_human']} | Hardest: {logic['hardest'] or 'None'}")
        print(f"Logical phase: {logic['status']} | Remaining: {logic['remaining']}")
        print(f"MRV fallback used: {'Yes' if results[-1]['fallback_used'] else 'No'}")
        print("* Solution counts are capped at 2; 2 means multiple solutions.")
        print("Search steps count placements and undos; logical steps count deductions.")
        print("Hybrid calls and backtracks refer to the bitmask + MRV fallback only.")
        print("Logical modes skip uniqueness checking; reset reconstructs the rater.")

        return results

    def run(self):
        while self.running:
            self.handle_events()
            self.renderer.draw()
            pg.display.flip()
            self.clock.tick(FPS)
        pg.quit()
