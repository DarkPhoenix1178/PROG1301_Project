from game import Sodoku
from generator import SodokuGenerator


def main():
    generator = SodokuGenerator()
    board = generator.generate_puzzle("medium")

    print("\n".join(map(str, board.board)))

    clues = sum(num != 0 for row in board.board for num in row)

    print(f"Clues: {clues}")
    print(f"Unique: {generator.has_unique_solution(board)}")

    Sodoku(board.board).run()


if __name__ == "__main__":
    main()
