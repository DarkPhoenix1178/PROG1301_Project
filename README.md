# PROG1301 Final Project: Sudoku Solver and Algorithm Comparison

A Python and Pygame project that studies Sudoku as a constraint satisfaction problem and compares increasingly sophisticated approaches to solving it.

## 1\. Topic of Study and Context

**Research question:** How do data representation, search heuristics, and mathematical reformulation affect the correctness and computational efficiency of Sudoku-solving algorithms?

Sudoku is a constraint satisfaction problem: each row, column, and 3×3 box must contain the digits 1–9 exactly once. Although the rules are simple, finding a solution can involve many possible assignments.

Our objective is to demonstrate how an initially straightforward recursive solution can be improved through better constraint checking, smarter search decisions, and an alternative mathematical representation of the problem. We also wanted to make these differences observable through a playable game, live solver visualizations, and numerical benchmarks.

## 2\. Project Goals and Implementation Plan

The core goals below are organized in increasing order of complexity and theoretical depth, following the *Programming Project Rubric*. Each level includes an implementation plan and evidence of correctness. The rubric does not prescribe Sudoku-specific milestones; the following mapping describes the scope of this implementation.

### Basic Goal (40%): Implement a functioning Sudoku game and Backtracking solver

**Goal:** Represent a standard 9×9 Sudoku board, enforce its rules, allow manual gameplay, and solve puzzles automatically using recursive backtracking.

**Plan:** Use object-oriented programming to separate board state, rule checking, rendering, and the main game loop. Represent empty cells with zero. Find an empty cell, try legal digits, recursively continue, and undo failed choices until a solution is found or the possibilities are exhausted.

**Correctness checks:** Verify that solved grids preserve the original clues, contain digits 1–9, have no duplicate digits in any row, column or box, and have no empty cells. Test unique, unsolvable, multiple-solution and already completed grids.

**Outcome:** The board, game interface, and standard backtracking solver are implemented. The solver passed the computational checks in Section 7; interactive UI behavior was not independently executed in the headless test environment.

### Intermediate Goals (20%): Optimize Backtracking using Bitmasking and MRV

**Goal:** Improve the baseline solver by reducing both the cost of checking constraints and the size of the search tree.

**Plan:** First replace repeated row, column and box scans with 9-bit masks. Then introduce the Minimum Remaining Values (MRV) heuristic to choose the empty cell with the fewest legal candidates. Compare both optimizations against ordinary backtracking using the same puzzles, digit order where applicable, and performance metrics.

**Correctness checks:** Verify completed grids, compare their solutions against the baseline on unique puzzles, and check that the solution counts agree for zero, one and multiple solutions. Record runtime, recursive calls and backtracks to distinguish faster operations from reduced search effort.

**Outcome:** Both optimizations are implemented and passed the sampled correctness checks. Bitmasking reduced solve time without changing the baseline's search tree on the two benchmark puzzles; MRV substantially reduced recursive calls.

### Advanced Goals (20%): Solve Sudoku using Knuth's Algorithm X and Dancing Links

**Goal:** Reformulate Sudoku as an exact cover problem and compare a structurally different search approach with the three board-based solvers.

**Plan:** Model the problem using 324 constraint columns and 729 possible placement rows. Represent the sparse matrix through circular doubly linked lists, implement reversible cover/uncover operations, and select the constraint with the fewest available rows. Implement both first-solution search and bounded solution counting.

**Correctness checks:** Verify that DLX produces the same completed grids on unique puzzles and agrees with the other solvers on solution counts. Compare search-only timing with combined initialization and solving time to account for matrix construction overhead.

**Outcome:** Algorithm X with Dancing Links is implemented and passed the sampled correctness checks. It had the fastest search-only runtime in both benchmark examples; its setup cost made Bitmask + MRV faster overall in those examples.

### Visualizations and Readability (20%)

**Goal:** Make the differences in algorithm behavior understandable and keep the source code readable.

**Plan:** Use Pygame to display the playable board and a side-by-side comparison with actual solver events, including placements, reversals and logical deductions. Provide terminal tables of timing, calls, backtracks and completion status. Separate responsibilities into modules and use descriptive names and comments, following PEP 8 conventions where possible.

**Outcome:** The game interface, comparison view and benchmark tables are implemented. All submitted Python files compile.

### Additional Features Beyond the Core Goals

The following extensions build on the four core solvers but are documented separately from the required goal progression:

* Randomized Sudoku puzzle generation with unique-solution verification.
* Four clue-based generation difficulty settings and fallback puzzles.
* Human-style logical solving and technique-based difficulty classification.
* A Logic + MRV hybrid that uses search only when logical deductions stall.
* Six simultaneous solver views, including the two additional logical approaches, with adjustable animation speed and step-by-step playback.


## 3\. Installation and Usage

### Requirements

* Python 3.10 or newer (the solvers use `int.bit_count()`).
* Pygame or Pygame Community Edition (`pygame-ce`).
* Tkinter available in the Python installation (imported by the current `knuth.py`).

Download or clone this repository, open a terminal in the project directory, and install the dependency:

```bash
python -m pip install pygame-ce
python main.py
```

If your Python installation does not include Tkinter, install the appropriate Tkinter package for your operating system. The uploaded source files should use their original module names as shown in the project structure below.

By default, `main.py` generates an expert puzzle, prints its clue count and uniqueness result, runs the solver benchmarks, and opens the game window. The benchmark output appears in the terminal before interactive gameplay begins. Especially challenging puzzles may take longer to benchmark using ordinary backtracking.

### Controls

|Control|Action|
|-|-|
|Mouse click|Select a cell|
|Arrow keys / W, A, S, D|Navigate the board|
|1–9|Enter a number in a non-given cell|
|0 / Backspace / Delete|Clear a non-given cell|
|F1|Open or restart the six-solver comparison|
|Space|Pause or resume the comparison|
|Up / Down|Increase or decrease animation speed|
|Right arrow (while paused)|Advance the comparison by one event per solver|
|Esc|Exit the comparison and return to the playable board|

The comparison always starts from the original puzzle, not the player's current entries. Green outlines in the comparison indicate placements or deductions, while red outlines indicate undo operations. The displayed benchmark solve time is measured separately from the animation.

## 4\. Project Structure

|File|Responsibility|
|-|-|
|`main.py`|Entry point, example puzzles, puzzle generation and game launch|
|`game.py`|Game loop, input handling, benchmarks, solver animations and hybrid solver|
|`board.py`|Board representation, cell operations, original clues and Sudoku rule checking|
|`renderer.py`|Game interface, highlighting, conflict detection and six-panel comparison|
|`backtrack.py`|Standard recursive backtracking|
|`bitmask_backtrack.py`|Backtracking with bitwise constraint tracking|
|`bitmask_mrv_backtrack.py`|Bitmask backtracking with Minimum Remaining Values|
|`knuth.py`|Algorithm X, Dancing Links and solution counting|
|`generator.py`|Randomized grid generation, clue removal and uniqueness checking|
|`difficulty_rater.py`|Candidate tracking, human-style deductions and difficulty allocation|
|`settings.py`|Display configuration, colors, difficulty ranges and fallback puzzles|

The project separates game presentation from board operations and solver logic. Each search solver receives an independent puzzle state so that the algorithms can be compared on the same input without changing the player's board.

## 5\. Why These Four Algorithms?

We selected the four core search algorithms because they demonstrate distinct ways of improving the same problem. The first three form a progression from a basic recursive search to faster constraint checking and then a more selective search order. The fourth reformulates Sudoku as an exact cover problem.

### 5.1 Standard Backtracking

**Implementation:** `backtrack.py`

The solver finds the first empty cell in row-major order and tries digits 1–9. It checks each candidate against its row, column, and box. If a placement leads to a dead end, the solver removes it and tries the next candidate. This continues recursively until the board is solved or all possibilities are exhausted.

**Benefits:** Simple, intuitive, and useful as a baseline for comparing the optimizations. It also records placements and reversals for visualization.

**Limitation:** Repeated constraint scans and a fixed cell-selection order can result in a large number of unnecessary attempts. The search has exponential worst-case growth in the number of empty cells.

### 5.2 Bitmask Backtracking

**Implementation:** `bitmask_backtrack.py`

Instead of repeatedly scanning a row, column, or box, the solver maintains 27 integer masks: nine for rows, nine for columns, and nine for boxes. Each of the nine bits represents a Sudoku digit.

For example, digit 5 corresponds to `1 << (5 - 1)`. Combining the three relevant masks identifies used digits, and the following expression gives the available digits:

```python
used = row_mask | col_mask | box_mask
available = 0x1FF & ~used
```

The lowest available bit is extracted with `available \& -available`. Placing or undoing a number updates the corresponding masks using bitwise operations.

**Benefits:** Faster candidate checking, compact constraint storage, and direct iteration over valid candidates.

**Limitation:** It still selects the first empty cell, so it can explore the same search tree as standard backtracking. Bitmasking primarily reduces the work performed at each recursive call rather than the number of calls.

### 5.3 Bitmask + Minimum Remaining Values (MRV)

**Implementation:** `bitmask_mrv_backtrack.py`

MRV builds on bitmask backtracking by selecting the empty cell with the fewest available candidates. The solver uses `available.bit_count()` to measure candidate counts. A cell with one candidate can be selected immediately; a detected cell with zero candidates signals a dead end.

This follows a fail-first strategy: solve the most constrained cells earlier, reducing branching and exposing impossible assignments sooner.

**Benefits:** Often substantially fewer recursive calls and backtracks while retaining the low-cost bitwise operations of the previous solver. It also requires relatively little setup.

**Limitation:** Selecting a cell requires examining candidate counts across the board, adding overhead at each recursion. MRV is a heuristic, not a guarantee of the smallest possible search tree.

### 5.4 Knuth's Algorithm X with Dancing Links (DLX)

**Implementation:** `knuth.py`

Unlike the previous approaches, DLX represents Sudoku as an **exact cover problem**. Each possible placement `(column, row, digit)` satisfies four constraints:

|Constraint|Number|
|-|-:|
|One digit per cell|81|
|Each digit appears once per row|81|
|Each digit appears once per column|81|
|Each digit appears once per 3×3 box|81|
|**Total constraint columns**|**324**|

There are 729 possible placements (81 cells × 9 digits). Each placement is represented by four linked nodes, giving 2,916 data nodes in the full sparse representation, before accounting for the givens.

The implementation uses circular doubly linked lists. Applying a given covers its constraints; during search, the solver selects the active constraint column with the fewest remaining possibilities. It covers incompatible choices, recurses, and uncovers them in reverse order when backtracking. The search succeeds when no uncovered constraint columns remain.

**Benefits:** Efficient reversible constraint updates and strong search pruning. It can select the most constrained rule, not just the most constrained cell. This makes it especially useful for repeated solution-counting and uniqueness checks once its structure is initialized.

**Limitation:** It is the most complex of the four implementations and requires more initialization and object storage. A fast search does not necessarily mean the fastest total runtime once matrix construction is included.

## 6\. Testing and Benchmark Methodology

The game benchmarks each approach on an independent copy of the same original puzzle using `time.perf\_counter\_ns()`. Timing is measured without the animation instrumentation and reported in milliseconds.

The terminal reports construction time, solve time, combined build and solve time, reset time, and (for the four search solvers) time to count solutions up to two. It also records recursive calls, backtracks, steps, completion status, and the number of remaining empty cells.

The benchmark checks that original clues are preserved, the resulting grid has valid digits and no conflicts, and a reported solution has no empty cells. Solution counts of 0, 1, and 2 represent no solution, a unique solution, and at least two solutions, respectively. Logical modes do not independently implement solution counting; their timed runs exclude DLX validation. Hybrid search-call statistics refer only to the MRV fallback. A logical deduction can eliminate multiple candidates, so its step count is not directly equivalent to a search placement or undo.

### Sample benchmark results

The following results were obtained from the submitted code using the fixed `puzzle` (30 clues) and `hard_puzzle` (23 clues) examples in `main.py`, with three runs per example. Times are medians rounded to three decimal places; exact performance varies by machine and puzzle. The test called the existing benchmark method without opening Pygame's graphical interface (Pygame was unavailable in the test environment; only import-time UI types/colors were stubbed).

**Test A: 30-clue puzzle**

|Solver|Solve (ms)|Build + solve (ms)|Calls|Backtracks|Status|
|-|-:|-:|-:|-:|-|
|Backtracking|101.717|101.791|4,209|4,157|Solved|
|Bitmask|32.887|32.985|4,209|4,157|Solved|
|Bitmask + MRV|0.525|0.620|52|0|Solved|
|Knuth (DLX)|0.372|2.399|52|0|Solved|
|Logical Solver|2.142|2.215|N/A|N/A|Solved|
|Logic + MRV|1.996|2.050|0|0|Solved|

**Test B: 23-clue hard puzzle**

|Solver|Solve (ms)|Build + solve (ms)|Calls|Backtracks|Status|
|-|-:|-:|-:|-:|-|
|Backtracking|238.969|239.024|8,970|8,911|Solved|
|Bitmask|89.930|90.480|8,970|8,911|Solved|
|Bitmask + MRV|2.483|2.770|220|161|Solved|
|Knuth (DLX)|1.547|3.548|148|89|Solved|
|Logical Solver|3.976|4.077|N/A|N/A|Stalled (57 empty)|
|Logic + MRV|7.771|7.875|218|160|Solved|

All four core solvers independently counted exactly one solution for both puzzles. All six completed grids agreed on Test A; all five completed grids agreed on Test B. Both DLX and Bitmask + MRV also returned 2 for the multiple-solution example in `main.py`.

Additional generation checks used seed 42. Each generated board passed grid validation and had exactly one solution according to both DLX and Bitmask + MRV.

|Requested difficulty|Generated clues|Unique solution|
|-|-:|-|
|Easy|45|Yes|
|Medium|33|Yes|
|Hard|31|Yes|
|Expert|23|Yes|

Both stored fallback puzzles were also confirmed to contain 17 clues and exactly one solution using DLX. These are sample checks, not exhaustive testing; the fixed 17-clue `expert_puzzle` was excluded from the benchmark tables because the full benchmark did not finish within the test time limit.

### Additional correctness checks for the core goals

The four search solvers were also tested independently with fresh board states and a solution-count limit of two. The following cases extend the checks beyond ordinary unique puzzles.

|Test case|Expected count|Backtracking|Bitmask|Bitmask + MRV|DLX|
|-|-:|-:|-:|-:|-:|
|30-clue example (`puzzle`)|1|1|1|1|1|
|23-clue example (`hard\_puzzle`)|1|1|1|1|1|
|Valid givens but no solution (30-clue example with R1C3 set to 1)|0|0|0|0|0|
|Empty grid|At least 2|2|2|2|2|
|Already completed valid grid|1|1|1|1|1|

All counts agreed with the expected results. A duplicate-clue grid (the 30-clue example with R1C3 set to 5) was also rejected by `DifficultyRater.valid\_grid()`, the validation method used before benchmarking. This does not imply that every solver independently validates malformed input; valid givens are assumed by the core search routines. These additional checks were performed externally on the submitted modules without modifying the source or running the GUI.

## 7\. Results and Conclusion: Which Algorithm Is Best?

The results demonstrate that reducing the number of search branches can have a greater impact than simply making each recursive operation faster. Standard Backtracking and Bitmask Backtracking made identical numbers of recursive calls and backtracks on both examples, but the bitmask version was faster because its constraint checks were cheaper. Adding MRV drastically reduced the search tree itself.

|Approach|Best use in this project|
|-|-|
|Backtracking|Learning recursion and establishing a baseline|
|Bitmask Backtracking|Demonstrating efficient constraint checking|
|Bitmask + MRV|Fast general-purpose solving with low initialization cost|
|Knuth's DLX|Fast exact-cover search and puzzle uniqueness verification|
|Logical Solver|Explainable deductions and human-oriented difficulty rating|
|Logic + MRV|Combining human-style reasoning with reliable search on valid puzzles|

**Bitmask + MRV is our preferred general-purpose solver** based on its lower combined build and solve time on both benchmark puzzles. **DLX is our preferred algorithm for uniqueness checking** and had the fastest search-only and count-only times on both examples; however, its setup cost also matters for each new puzzle. The hybrid is valuable for demonstrating logical reasoning with a search fallback, rather than for minimizing runtime in every case.

There is no universally fastest algorithm for all Sudoku instances. Our project illustrates the trade-off between computational cost, initialization overhead, search pruning, implementation complexity, and interpretability.

## 8\. Additional Features and Extensions

### 8.1 Human-Style Logic and Hybrid Solving

A computationally fast solution is not necessarily a useful explanation for a person. We implemented a separate logical solver to identify deductions a human could make without guessing. The solver maintains candidate sets and repeatedly applies techniques in increasing order of complexity, restarting from the simplest technique after each successful deduction.

|Level|Techniques|Purpose|
|-|-|-|
|Beginner|Naked Single, Hidden Single|Place a forced digit in a cell or house|
|Intermediate|Pointing, Claiming, Naked Pair|Eliminate candidates using box-line interactions or pairs|
|Difficult|Naked Triple, X-Wing, Swordfish|Eliminate candidates through larger subsets and row/column patterns|

The logical difficulty is based on the hardest technique required, not the number of clues alone. The solver can also detect invalid puzzles, contradictions, zero or multiple solutions when validation is enabled, and puzzles on which its implemented techniques stall. A stalled puzzle is classified as `Unclassified`, rather than automatically being labeled difficult or unsolvable.

The **Logic + MRV hybrid** first applies the same deductions. If the logical solver stalls, it passes the partially completed board to Bitmask + MRV to finish the remaining cells. The fallback retains logical placements, although it recomputes bitmask candidates instead of carrying forward all candidate eliminations. This combines explainable deductions with the ability to complete puzzles beyond the implemented human techniques.

### 8.2 Puzzle Generation and Difficulty Allocation

The generator produces a valid completed Sudoku grid by filling the three diagonal 3×3 boxes with shuffled digits, then recursively filling the remaining cells in row-major order while shuffling the candidate digits.

It then performs the following steps:

1. Choose a target number of clues within the requested difficulty range.
2. Shuffle cell positions and temporarily remove one clue at a time.
3. Use DLX to count solutions, stopping at two. Retain the removal only if exactly one solution remains.
4. Repeat until the target is achieved. After up to five attempts, accept the best generated board if it fits the difficulty range.
5. If the generated boards do not fit, use a stored 17-clue puzzle, add solution digits to reach the target, and randomize it through digit remapping, valid row/column permutations, transposition and reflections.

|Generation difficulty|Clue range|
|-|-:|
|Easy|40–45|
|Medium|32–39|
|Hard|26–31|
|Expert|22–25|

Clue count is a practical way to control generation, but it is only an approximate difficulty indicator. A puzzle with fewer clues may still be solvable using simple deductions, while another puzzle with more clues may require advanced techniques. The human-logic rating is reported separately; generation does not enforce a particular human-logic rating.

### 8.3 Extended Visualization

The core comparison is extended to six approaches by adding the Logical Solver and Logic + MRV. Each panel runs from an independent copy of the original puzzle and consumes events from its own bounded queue. Solver work is performed in background threads while rendering remains on the main thread. Users can pause, change speed and advance the animations one event at a time. Animation timings are not used for the performance comparison.

## 9\. Limitations and Future Improvements

* Run benchmarks on a larger, fixed collection of puzzles and report distributions rather than relying on individual examples.
* Extend human-style deductions and generate puzzles that satisfy a desired logic-based difficulty rating.
* Improve generation and benchmarking responsiveness for unusually hard puzzles, since startup benchmarks run synchronously.
* Add automated regression tests covering malformed, unsolvable, unique, and multiple-solution boards across all solvers.
* Complete manual GUI regression testing and a formal PEP 8 check.

