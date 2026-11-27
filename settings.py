import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 770, 870
FPS = 10000
SOLVE_DELAY = 1  # in ms

MARGIN = 15
BOARD_BORDER = 10

BORDER = pg.Color(17, 17, 17)
GIVEN = pg.Color(52, 72, 97)
INPUT = pg.Color(50, 90, 175)
ERROR = pg.Color(245, 190, 190)
SELECT = pg.Color(187, 222, 251)
CROSSHAIR = pg.Color(226, 235, 243)
SIMILAR = pg.Color(195, 215, 235)
BACKGROUND = pg.Color(255, 255, 255)

DIFFICULTY_CLUES = {
    "easy": (40, 45),
    "medium": (32, 39),
    "hard": (26, 31),
    "expert": (22, 25),
}

MIN_CLUES = 17
MAX_GENERATION_ATTEMPTS = 5

FALLBACK_PUZZLES = [
    [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 2, 0, 3, 0],
        [0, 0, 0, 0, 0, 3, 0, 2, 0],
        [0, 0, 1, 0, 4, 0, 0, 0, 0],
        [0, 0, 5, 0, 0, 0, 0, 6, 0],
        [0, 3, 0, 0, 0, 0, 0, 0, 4],
        [0, 7, 0, 0, 8, 0, 0, 0, 9],
        [6, 2, 0, 0, 0, 7, 0, 0, 0],
    ],
    [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 2, 0, 3, 0],
        [0, 0, 0, 0, 0, 4, 2, 5, 0],
        [0, 0, 6, 0, 0, 0, 0, 0, 0],
        [0, 1, 7, 0, 0, 0, 0, 8, 0],
        [0, 0, 0, 0, 7, 0, 0, 0, 6],
        [4, 0, 0, 0, 6, 0, 0, 0, 0],
        [9, 0, 0, 8, 0, 0, 0, 1, 0],
    ],
]
