import pygame as pg

from board import SodokuBoard
from settings import SCREEN_HEIGHT, SCREEN_WIDTH, MARGIN, BOARD_BORDER, \
    BACKGROUND, CROSSHAIR, SELECT, SIMILAR, GIVEN, INPUT, BORDER, ERROR


class SodokuRenderer:
    def __init__(self, screen: pg.Surface, board: SodokuBoard):
        self.screen = screen
        self.board = board

        self.board_length = (min(SCREEN_WIDTH, SCREEN_HEIGHT) -
                             (MARGIN * 2) -
                             (BOARD_BORDER * 2))
        self.board_length -= self.board_length % 9
        self.board_length += BOARD_BORDER * 2

        self.cell_size = (self.board_length - (BOARD_BORDER * 2)) // 9
        self.box_size = self.cell_size * 3

        self.offset = BOARD_BORDER + MARGIN
        self.board_end = self.offset + (self.cell_size * 9)

        self.font_size = int(self.cell_size * 0.9)
        self.font = pg.font.SysFont(None, self.font_size)

    def draw_crosshair(self):
        col, row = self.board.get_active_cell()

        # Vertical Crosshair
        h_top_left = pg.Vector2((col * self.cell_size) + self.offset,
                                self.offset)
        h_size = pg.Vector2(self.cell_size, self.cell_size * 9)

        pg.draw.rect(surface=self.screen,
                     color=CROSSHAIR,
                     rect=pg.Rect(h_top_left, h_size))

        # Horizontal Crosshair
        v_top_left = pg.Vector2(self.offset,
                                (row * self.cell_size) + self.offset)
        v_size = pg.Vector2(self.cell_size * 9, self.cell_size)

        pg.draw.rect(surface=self.screen,
                     color=CROSSHAIR,
                     rect=pg.Rect(v_top_left, v_size))

        # Box Crosshair
        box_col, box_row = self.board.box_coordinates(col, row)
        b_top_left = pg.Vector2((box_col * self.box_size) + self.offset,
                                (box_row * self.box_size) + self.offset)
        b_size = pg.Vector2(self.box_size, self.box_size)

        pg.draw.rect(surface=self.screen,
                     color=CROSSHAIR,
                     rect=pg.Rect(b_top_left, b_size))

    def draw_active_cell(self):
        col, row = self.board.get_active_cell()

        pg.draw.rect(surface=self.screen,
                     color=SELECT,
                     rect=pg.Rect((col * self.cell_size) + self.offset,
                                  (row * self.cell_size) + self.offset,
                                  self.cell_size,
                                  self.cell_size))

    def draw_matching_numbers(self):
        for row in range(9):
            for col in range(9):
                cell_value = self.board.get_cell(col, row)
                if cell_value == 0:
                    continue

                if cell_value != self.board.get_active_value():
                    continue

                pg.draw.rect(surface=self.screen,
                             color=SIMILAR,
                             rect=pg.Rect(
                                 (col * self.cell_size) + self.offset,
                                 (row * self.cell_size) + self.offset,
                                 self.cell_size,
                                 self.cell_size
                             ))

    def draw_board(self):
        # Draw main border
        pg.draw.rect(
            surface=self.screen,
            color=BORDER,
            rect=pg.Rect(MARGIN, MARGIN, self.board_length, self.board_length),
            width=BOARD_BORDER,
            border_radius=BOARD_BORDER * 2
        )

        # Draw Lines
        for line in range(1, 9):
            line_width = (BOARD_BORDER // 2) if line % 3 == 0 \
                else (BOARD_BORDER // 10)

            pos = self.offset + (self.cell_size * line)

            # Draw Vertical Lines
            pg.draw.line(
                surface=self.screen,
                color=BORDER,
                start_pos=pg.Vector2(pos, self.offset),
                end_pos=pg.Vector2(pos, self.board_end),
                width=line_width
            )

            # Draw Horizontal Lines
            pg.draw.line(
                surface=self.screen,
                color=BORDER,
                start_pos=pg.Vector2(self.offset, pos),
                end_pos=pg.Vector2(self.board_end, pos),
                width=line_width
            )

    def draw_numbers(self):
        for row in range(9):
            for col in range(9):
                cell_value = self.board.get_cell(col, row)
                if cell_value == 0:
                    continue

                text = self.font.render(
                    str(cell_value),
                    True,
                    GIVEN if self.board.is_cell_given(col, row) else INPUT
                )
                center = (self.offset + (col + 0.5) * self.cell_size,
                          self.offset + (row + 0.5) * self.cell_size)
                self.screen.blit(text, text.get_rect(center=center))

    def get_board_coordinates(self, pos):
        col = (pos[0] - self.offset) // self.cell_size
        row = (pos[1] - self.offset) // self.cell_size
        return col, row

    def find_conflicts(self):
        groups = []

        # Rows and columns
        for i in range(9):
            groups.append([(col, i) for col in range(9)])
            groups.append([(i, row) for row in range(9)])

        # Boxes
        for box_row in range(3):
            for box_col in range(3):
                groups.append([(box_col * 3 + c, box_row * 3 + r)
                               for r in range(3) for c in range(3)])

        conflicts = set()

        for group in groups:
            seen = {}

            for col, row in group:
                value = self.board.get_cell(col, row)

                if value != 0:
                    seen.setdefault(value, []).append((col, row))

            for cells in seen.values():
                if len(cells) > 1:
                    conflicts.update(cells)

        return conflicts

    def draw_conflicts(self):
        for col, row in self.find_conflicts():
            pg.draw.rect(surface=self.screen,
                         color=ERROR,
                         rect=pg.Rect((col * self.cell_size) + self.offset,
                                      (row * self.cell_size) + self.offset,
                                      self.cell_size,
                                      self.cell_size))

    def is_solved(self):
        return (all(self.board.get_cell(col, row) in range(1, 10)
                    for row in range(9) for col in range(9))
                and not self.find_conflicts())

    def draw(self, flag_conflicts=True):
        self.screen.fill(BACKGROUND)

        if self.is_solved():
            pg.draw.rect(
                surface=self.screen,
                color=(198, 239, 206),
                rect=pg.Rect(self.offset, self.offset,
                             self.cell_size * 9, self.cell_size * 9))
        elif self.board.cell_active():
            self.draw_crosshair()
            self.draw_matching_numbers()
            self.draw_active_cell()

        if flag_conflicts:
            self.draw_conflicts()

        self.draw_board()
        self.draw_numbers()