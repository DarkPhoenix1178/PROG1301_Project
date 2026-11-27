from game import Sudoku
from generator import SudokuGenerator


def main():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    multi_puzzle = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 3, 0, 4, 0, 2, 0],
        [3, 0, 0, 5, 0, 0, 0, 0, 9],
        [0, 9, 0, 0, 0, 0, 0, 6, 0],
        [7, 0, 0, 0, 2, 0, 0, 0, 8],
        [0, 4, 0, 0, 3, 0, 0, 5, 0],
        [1, 0, 0, 7, 0, 8, 0, 9, 3],
        [0, 6, 0, 9, 5, 0, 0, 4, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    # game = Sudoku(puzzle).run()
    # game2 = Sudoku(multi_puzzle).run()

    hard_puzzle = [
        [1, 0, 0, 0, 0, 7, 0, 9, 0],
        [0, 3, 0, 0, 2, 0, 0, 0, 8],
        [0, 0, 9, 6, 0, 0, 5, 0, 0],
        [0, 0, 5, 3, 0, 0, 9, 0, 0],
        [0, 1, 0, 0, 8, 0, 0, 0, 2],
        [6, 0, 0, 0, 0, 4, 0, 0, 0],
        [3, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 4, 0, 0, 0, 0, 0, 0, 7],
        [0, 0, 7, 0, 0, 0, 3, 0, 0],
    ]
    expert_puzzle = [
        [0, 0, 0, 0, 0, 0, 0, 1, 0],
        [4, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 5, 0, 4, 0, 7],
        [0, 0, 8, 0, 0, 0, 3, 0, 0],
        [0, 0, 1, 0, 9, 0, 0, 0, 0],
        [3, 0, 0, 4, 0, 0, 2, 0, 0],
        [0, 5, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 8, 0, 6, 0, 0, 0],
    ]

    # Sudoku(SudokuGenerator().generate_solution()).run()
    # game2 = Sudoku(expert_puzzle).run()

    generator = SudokuGenerator()
    board = generator.generate_puzzle("expert")

    print("\n".join(map(str, board.board)))

    clues = sum(num != 0 for row in board.board for num in row)

    print(f"Clues: {clues}")
    print(f"Unique: {generator.has_unique_solution(board)}")

    game = Sudoku(board.board).run()


if __name__ == "__main__":
    main()
