import pygame as pg

from board import SodokuBoard
from settings import MARGIN, BOARD_BORDER, \
    BACKGROUND, CROSSHAIR, SELECT, SIMILAR, GIVEN, INPUT, BORDER, ERROR


class SodokuRenderer:
    def __init__(self, screen: pg.Surface, board: SodokuBoard, compact=False):
        self.screen = screen
        self.board = board
        self.compact = compact
        self.margin = 3 if compact else MARGIN
        self.border = 3 if compact else BOARD_BORDER

        self.board_length = (min(screen.get_size()) -
                             (self.margin * 2) -
                             (self.border * 2))
        self.board_length -= self.board_length % 9
        self.board_length += self.border * 2

        self.cell_size = (self.board_length - (self.border * 2)) // 9
        self.box_size = self.cell_size * 3

        self.offset = self.border + self.margin
        self.board_end = self.offset + (self.cell_size * 9)

        self.font_size = int(self.cell_size * 0.9)
        self.font = pg.font.SysFont(None, self.font_size)

    def draw_crosshair(self):
        col, row = self.board.get_active_cell()

        # Horizontal Crosshair
        h_top_left = pg.Vector2((col * self.cell_size) + self.offset,
                                self.offset)
        h_size = pg.Vector2(self.cell_size, self.cell_size * 9)

        pg.draw.rect(surface=self.screen,
                     color=CROSSHAIR,
                     rect=pg.Rect(h_top_left, h_size))

        # Vertical Crosshair
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
            rect=pg.Rect(self.margin, self.margin, self.board_length,
                         self.board_length),
            width=self.border,
            border_radius=self.border * 2
        )

        # Draw Lines
        for line in range(1, 9):
            line_width = max(2, self.border // 2) if line % 3 == 0 \
                else max(1, self.border // 10)

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

        if not self.compact and self.is_solved():
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

    def prepare_comparison(self, animations):
        """Reuse the normal renderer on six smaller surfaces."""
        width, height = self.screen.get_size()
        self.panel_width = width // 3
        self.panel_height = (height - 54) // 2
        self.panel_size = min(self.panel_width - 12, self.panel_height - 78)
        self.panels = []
        for animation in animations:
            surface = pg.Surface((self.panel_size, self.panel_size))
            renderer = SodokuRenderer(surface, animation.board, compact=True)
            self.panels.append((animation, surface, renderer))
        self.heading_font = pg.font.SysFont(None, 25)
        self.label_font = pg.font.SysFont(None, 19)
        self.info_font = pg.font.SysFont(None, 16)
        self.candidate_font = pg.font.SysFont(
            None, max(8, self.panels[0][2].cell_size // 3))

    def draw_candidates(self, surface, renderer, animation):
        if animation.candidates is None:
            return
        size = renderer.cell_size
        for row in range(9):
            for col in range(9):
                if animation.board.get_cell(col, row) != 0:
                    continue
                for num in animation.candidates[row][col]:
                    x = renderer.offset + col * size + ((num - 1) % 3 + .5) * size / 3
                    y = renderer.offset + row * size + ((num - 1) // 3 + .5) * size / 3
                    text = self.candidate_font.render(str(num), True, GIVEN)
                    surface.blit(text, text.get_rect(center=(x, y)))

    def draw_comparison(self, paused, speed):
        self.screen.fill(BACKGROUND)
        width, _ = self.screen.get_size()

        def label(text, center, font, color=GIVEN):
            image = font.render(text, True, color)
            self.screen.blit(image, image.get_rect(center=center))

        done = all(a.status != "Searching" for a, _, _ in self.panels)
        state = "Finished" if done else "Paused" if paused else "Running"
        label("Sudoku Solver Comparison", (width // 2, 15),
              self.heading_font, BORDER)
        label(f"{state} | {speed} steps/frame | Space: pause | Up/Down: speed | "
              "Right: step | F1: restart | Esc: return",
              (width // 2, 36), self.info_font)

        for i, (animation, surface, renderer) in enumerate(self.panels):
            x = (i % 3) * self.panel_width
            y = 50 + (i // 3) * self.panel_height
            center = x + self.panel_width // 2
            label(animation.name, (center, y + 9), self.label_font, BORDER)
            renderer.draw(flag_conflicts=False)
            self.draw_candidates(surface, renderer, animation)
            for col, row in animation.changed:
                rect = pg.Rect(renderer.offset + col * renderer.cell_size,
                               renderer.offset + row * renderer.cell_size,
                               renderer.cell_size, renderer.cell_size)
                color = (190, 48, 48) if animation.undo else (30, 145, 90)
                pg.draw.rect(surface, color, rect, width=2)
            self.screen.blit(surface, (center - self.panel_size // 2, y + 20))

            info_y = y + 20 + self.panel_size
            label(f"{animation.status} | Steps: {animation.steps:,}",
                  (center, info_y + 8), self.info_font)
            label(animation.last_action, (center, info_y + 23), self.info_font, INPUT)
            remaining = sum(num == 0 for row in animation.board.board for num in row)
            details = (f"Remaining: {remaining} | No guessing" if animation.candidates is not None
                       else f"Remaining: {remaining} | Undos: {animation.backtracks:,}")
            label(details, (center, info_y + 38), self.info_font)
            label(f"Benchmark solve: {animation.benchmark['solve']:.3f} ms",
                  (center, info_y + 53), self.info_font)
