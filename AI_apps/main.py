import random
import sys

import pygame


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 760
FPS = 60

BG = (15, 24, 33)
PANEL = (25, 39, 51)
CELL = (33, 50, 64)
CELL_HOVER = (42, 63, 77)
LINE = (49, 68, 82)
TEXT = (239, 244, 239)
MUTED = (147, 165, 175)
MINT = (113, 226, 177)
CORAL = (255, 128, 119)
GOLD = (246, 195, 99)

WIN_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def get_winner(board):
    for line in WIN_LINES:
        first = board[line[0]]
        if first and first == board[line[1]] == board[line[2]]:
            return first
    if all(board):
        return "D"
    return None


def _minimax(board, current_mark, ai_mark, human_mark, depth=0):
    result = get_winner(board)
    if result == ai_mark:
        return 10 - depth
    if result == human_mark:
        return depth - 10
    if result == "D":
        return 0

    scores = []
    next_mark = human_mark if current_mark == ai_mark else ai_mark
    for index, value in enumerate(board):
        if value is None:
            board[index] = current_mark
            scores.append(
                _minimax(board, next_mark, ai_mark, human_mark, depth + 1)
            )
            board[index] = None

    return max(scores) if current_mark == ai_mark else min(scores)


def find_best_move(board, ai_mark="O"):
    human_mark = "X" if ai_mark == "O" else "O"
    best_score = -float("inf")
    best_moves = []

    for index, value in enumerate(board):
        if value is None:
            board[index] = ai_mark
            score = _minimax(board, human_mark, ai_mark, human_mark, 1)
            board[index] = None
            if score > best_score:
                best_score = score
                best_moves = [index]
            elif score == best_score:
                best_moves.append(index)

    return random.choice(best_moves) if best_moves else None


class TicTacToe:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tic-Tac-Toe | After Hours Arcade")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = {
            "title": pygame.font.SysFont("segoeui", 38, bold=True),
            "heading": pygame.font.SysFont("segoeui", 19, bold=True),
            "body": pygame.font.SysFont("segoeui", 16),
            "small": pygame.font.SysFont("segoeui", 13),
            "score": pygame.font.SysFont("segoeui", 30, bold=True),
            "mark": pygame.font.SysFont("segoeui", 76, bold=True),
        }
        self.mode = "ai"
        self.board = [None] * 9
        self.scores = {"X": 0, "O": 0, "D": 0}
        self.outcome = None
        self.running = True

        self.board_rect = pygame.Rect(54, 148, 528, 528)
        self.grid_rect = pygame.Rect(78, 172, 480, 480)
        self.sidebar_rect = pygame.Rect(610, 148, 336, 528)
        self.cells = self._make_cell_rects()
        self.mode_buttons = {
            "ai": pygame.Rect(632, 290, 140, 42),
            "local": pygame.Rect(784, 290, 140, 42),
        }
        self.new_round_button = pygame.Rect(632, 554, 292, 48)
        self.reset_button = pygame.Rect(632, 615, 292, 36)

    def _make_cell_rects(self):
        gap = 12
        cell_size = (self.grid_rect.width - 2 * gap) // 3
        return [
            pygame.Rect(
                self.grid_rect.x + col * (cell_size + gap),
                self.grid_rect.y + row * (cell_size + gap),
                cell_size,
                cell_size,
            )
            for row in range(3)
            for col in range(3)
        ]

    def _draw_text(self, text, font, color, position, anchor="topleft"):
        image = self.fonts[font].render(text, True, color)
        rect = image.get_rect()
        setattr(rect, anchor, position)
        self.screen.blit(image, rect)

    def _draw_header(self):
        self._draw_text("AFTER HOURS  /  ARCADE  No. 01", "small", MINT, (56, 34))
        self._draw_text("Tic-Tac-Toe", "title", TEXT, (54, 55))
        self._draw_text("A small game. Big rivalry.", "body", MUTED, (57, 103))
        pygame.draw.line(self.screen, LINE, (54, 128), (946, 128), 1)
        self._draw_text("BEST OF YOURSELF", "small", MUTED, (944, 55), "topright")

    def _draw_board(self):
        mouse_position = pygame.mouse.get_pos()
        pygame.draw.rect(self.screen, PANEL, self.board_rect, border_radius=20)

        for index, rect in enumerate(self.cells):
            is_hovered = (
                self.outcome is None
                and self.board[index] is None
                and rect.collidepoint(mouse_position)
                and not (self.mode == "ai" and self._is_ai_turn())
            )
            fill = CELL_HOVER if is_hovered else CELL
            pygame.draw.rect(self.screen, fill, rect, border_radius=14)

            mark = self.board[index]
            if mark == "X":
                self._draw_x(rect, MINT)
            elif mark == "O":
                self._draw_o(rect, CORAL)

        if self.outcome in ("X", "O"):
            self._draw_winning_line(self.outcome)

    def _draw_x(self, rect, color):
        inset = 48
        pygame.draw.line(
            self.screen,
            color,
            (rect.left + inset, rect.top + inset),
            (rect.right - inset, rect.bottom - inset),
            10,
        )
        pygame.draw.line(
            self.screen,
            color,
            (rect.right - inset, rect.top + inset),
            (rect.left + inset, rect.bottom - inset),
            10,
        )

    def _draw_o(self, rect, color):
        pygame.draw.circle(
            self.screen,
            color,
            rect.center,
            43,
            10,
        )

    def _draw_winning_line(self, mark):
        winning_line = next(
            (
                line
                for line in WIN_LINES
                if all(self.board[index] == mark for index in line)
            ),
            None,
        )
        if winning_line:
            start = self.cells[winning_line[0]].center
            end = self.cells[winning_line[2]].center
            pygame.draw.line(self.screen, GOLD, start, end, 6)

    def _draw_sidebar(self):
        pygame.draw.rect(self.screen, PANEL, self.sidebar_rect, border_radius=20)
        self._draw_text("MATCH", "small", MUTED, (632, 169))

        status_rect = pygame.Rect(632, 194, 292, 76)
        pygame.draw.rect(self.screen, (32, 51, 63), status_rect, border_radius=12)
        status, detail, status_color = self._status_copy()
        pygame.draw.circle(self.screen, status_color, (651, 218), 5)
        self._draw_text(status, "heading", TEXT, (666, 205))
        self._draw_text(detail, "small", MUTED, (650, 239))

        self._draw_text("CHOOSE YOUR TABLE", "small", MUTED, (632, 277))
        for mode, rect in self.mode_buttons.items():
            selected = self.mode == mode
            fill = MINT if selected else (37, 55, 68)
            color = BG if selected else TEXT
            pygame.draw.rect(self.screen, fill, rect, border_radius=10)
            label = "VS COMPUTER" if mode == "ai" else "2 PLAYERS"
            self._draw_text(label, "small", color, rect.center, "center")

        self._draw_text("SCOREBOARD", "small", MUTED, (632, 354))
        self._draw_score_tile("X", "YOU" if self.mode == "ai" else "PLAYER 1", 632)
        self._draw_score_tile("O", "CPU" if self.mode == "ai" else "PLAYER 2", 731)
        self._draw_score_tile("D", "DRAWS", 830)

        self._draw_text("YOUR NEXT MOVE", "small", MUTED, (632, 485))
        if self.mode == "ai":
            hint = "You play X. The computer plays O."
        else:
            hint = "X starts. Take turns after each move."
        self._draw_text(hint, "small", TEXT, (632, 508))

        pygame.draw.rect(
            self.screen,
            MINT,
            self.new_round_button,
            border_radius=11,
        )
        self._draw_text(
            "NEW ROUND",
            "body",
            BG,
            self.new_round_button.center,
            "center",
        )
        self._draw_text(
            "RESET SCORE",
            "small",
            MUTED,
            self.reset_button.center,
            "center",
        )

    def _draw_score_tile(self, mark, label, x):
        rect = pygame.Rect(x, 378, 94, 88)
        pygame.draw.rect(self.screen, (32, 51, 63), rect, border_radius=11)
        mark_color = MINT if mark == "X" else CORAL if mark == "O" else GOLD
        self._draw_text(mark, "small", mark_color, (x + 10, 387))
        self._draw_text(str(self.scores[mark]), "score", TEXT, (x + 10, 400))
        self._draw_text(label, "small", MUTED, (x + 10, 443))

    def _draw_footer(self):
        self._draw_text(
            "R  NEW ROUND     M  SWITCH MODE     ESC  QUIT",
            "small",
            MUTED,
            (54, 710),
        )
        self._draw_text("BUILT FOR ONE MORE GAME", "small", MUTED, (946, 710), "topright")

    def _status_copy(self):
        if self.outcome == "D":
            return "IT'S A DRAW", "Nobody blinked first.", GOLD
        if self.outcome in ("X", "O"):
            if self.mode == "ai":
                won = "YOU WIN" if self.outcome == "X" else "COMPUTER WINS"
            else:
                won = f"PLAYER {1 if self.outcome == 'X' else 2} WINS"
            return won, "Run it back?", GOLD
        if self._is_ai_turn():
            return "COMPUTER THINKING", "The machine is choosing...", CORAL
        if self.mode == "ai":
            return "YOUR TURN", "Place an X on the board.", MINT
        player = 1 if self._next_mark() == "X" else 2
        color = MINT if player == 1 else CORAL
        return f"PLAYER {player}'S TURN", "Place your mark on the board.", color

    def _next_mark(self):
        return "X" if self.board.count("X") == self.board.count("O") else "O"

    def _is_ai_turn(self):
        return self.mode == "ai" and self._next_mark() == "O" and self.outcome is None

    def _play_move(self, index, mark):
        if self.outcome is not None or self.board[index] is not None:
            return
        self.board[index] = mark
        self.outcome = get_winner(self.board)
        if self.outcome:
            self.scores[self.outcome] += 1

    def _start_new_round(self):
        self.board = [None] * 9
        self.outcome = None

    def _set_mode(self, mode):
        if mode != self.mode:
            self.mode = mode
            self._start_new_round()

    def _handle_click(self, position):
        for mode, rect in self.mode_buttons.items():
            if rect.collidepoint(position):
                self._set_mode(mode)
                return

        if self.new_round_button.collidepoint(position):
            self._start_new_round()
            return

        if self.reset_button.collidepoint(position):
            self.scores = {"X": 0, "O": 0, "D": 0}
            self._start_new_round()
            return

        if self.outcome is not None or self._is_ai_turn():
            return

        for index, rect in enumerate(self.cells):
            if rect.collidepoint(position) and self.board[index] is None:
                self._play_move(index, self._next_mark())
                if self.mode == "ai" and self.outcome is None:
                    ai_move = find_best_move(self.board)
                    if ai_move is not None:
                        self._play_move(ai_move, "O")
                return

    def _handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_r:
            self._start_new_round()
        elif key == pygame.K_m:
            self._set_mode("local" if self.mode == "ai" else "ai")

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self._handle_click(event.pos)

            self.screen.fill(BG)
            self._draw_header()
            self._draw_board()
            self._draw_sidebar()
            self._draw_footer()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        return 0


def main():
    return TicTacToe().run()


if __name__ == "__main__":
    sys.exit(main())