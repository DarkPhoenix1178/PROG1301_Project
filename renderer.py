import pygame as pg

from board import SodokuBoard
from settings import SCREEN_HEIGHT, SCREEN_WIDTH, MARGIN, BOARD_BORDER, \
    BACKGROUND, CROSSHAIR, SELECT, SIMILAR, GIVEN, INPUT, BORDER


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

        # Horizontal Crosshair
        h_top_left = pg.Vector2((col * self.cell_size) + self.offset,
                                self.offset)
        h_size = pg.Vector2(self.cell_size, self.board_length - MARGIN)

        pg.draw.rect(surface=self.screen,
                     color=CROSSHAIR,
                     rect=pg.Rect(h_top_left, h_size))

        # Vertical Crosshair
        v_top_left = pg.Vector2(self.offset,
                                (row * self.cell_size) + self.offset)
        v_size = pg.Vector2(self.board_length - MARGIN, self.cell_size)
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
                text_location = pg.Vector2((col + 0.5) * self.cell_size +
                                           BOARD_BORDER,
                                           (row + 0.5) * self.cell_size)
                self.screen.blit(text, text_location)

    def draw(self):
        self.screen.fill(BACKGROUND)

        if self.board.cell_active():
            self.draw_crosshair()
            self.draw_matching_numbers()
            self.draw_active_cell()

        self.draw_board()
        self.draw_numbers()

    def get_board_coordinates(self, pos):
        col = (pos[0] - self.offset) // self.cell_size
        row = (pos[1] - self.offset) // self.cell_size
        return col, row
