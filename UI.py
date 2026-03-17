import tkinter as tk
from tkinter import messagebox

import game

BOARD_DIMENSION = 10
WIN_CONDITION = 5
CELL_SIZE = 42
MARGIN = 30
GRID_LINE_WIDTH = 2
STONE_PADDING = 5
HUMAN_COLOUR = "black"
AI_COLOUR = "white"
BOARD_COLOUR = "#D8A35D"
GRID_COLOUR = "#333333"
LAST_MOVE_MARK_COLOUR = "red"


class GomokuUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gomoku AI")
        self.root.resizable(False, False)

        self.dimension = BOARD_DIMENSION
        self.win_condition = WIN_CONDITION
        self.canvas_size = 2 * MARGIN + CELL_SIZE * (self.dimension - 1)

        self.game = None
        self.game_over = False

        self.status_var = tk.StringVar()
        self.status_var.set("Your turn")

        self._build_widgets()
        self.start_new_game()

    def _build_widgets(self):
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack()

        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            top_frame,
            text=f"Board size: {self.dimension} x {self.dimension} | Win condition: {self.win_condition}",
            font=("Arial", 12, "bold")
        ).pack(side="left")

        tk.Button(
            top_frame,
            text="New Game",
            command=self.start_new_game,
            font=("Arial", 10)
        ).pack(side="right")

        self.canvas = tk.Canvas(
            main_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=BOARD_COLOUR,
            highlightthickness=1,
            highlightbackground="#888888"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        bottom_frame = tk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=(8, 0))

        tk.Label(
            bottom_frame,
            textvariable=self.status_var,
            anchor="w",
            font=("Arial", 11)
        ).pack(side="left")

    def start_new_game(self):
        self.game = game.Game(self.dimension, self.win_condition)
        self.game_over = False
        self.status_var.set("Your turn")
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")

        for i in range(self.dimension):
            pos = MARGIN + i * CELL_SIZE
            self.canvas.create_line(MARGIN, pos, self.canvas_size - MARGIN, pos, width=GRID_LINE_WIDTH, fill=GRID_COLOUR)
            self.canvas.create_line(pos, MARGIN, pos, self.canvas_size - MARGIN, width=GRID_LINE_WIDTH, fill=GRID_COLOUR)

        for x in range(self.dimension):
            for y in range(self.dimension):
                piece = self.game.current_board.board_array[x][y]
                if piece != 0:
                    self._draw_stone(x, y, piece)

        if self.game.last_move is not None:
            x, y = self.game.last_move
            cx, cy = self._grid_to_canvas(x, y)
            size = 5
            self.canvas.create_line(cx - size, cy, cx + size, cy, fill=LAST_MOVE_MARK_COLOUR, width=2)
            self.canvas.create_line(cx, cy - size, cx, cy + size, fill=LAST_MOVE_MARK_COLOUR, width=2)

    def _draw_stone(self, x: int, y: int, piece: int):
        cx, cy = self._grid_to_canvas(x, y)
        colour = HUMAN_COLOUR if piece == self.game.player_1.piece else AI_COLOUR

        self.canvas.create_oval(
            cx - CELL_SIZE // 2 + STONE_PADDING,
            cy - CELL_SIZE // 2 + STONE_PADDING,
            cx + CELL_SIZE // 2 - STONE_PADDING,
            cy + CELL_SIZE // 2 - STONE_PADDING,
            fill=colour,
            outline="#222222"
        )

    def _grid_to_canvas(self, x: int, y: int):
        return MARGIN + y * CELL_SIZE, MARGIN + x * CELL_SIZE

    def _canvas_to_grid(self, px: int, py: int):
        row = round((py - MARGIN) / CELL_SIZE)
        col = round((px - MARGIN) / CELL_SIZE)
        if 0 <= row < self.dimension and 0 <= col < self.dimension:
            return row, col
        return None, None

    def on_canvas_click(self, event):
        # Ignore clicks if game over, or if the current player is not a human
        if self.game_over or self.game.current_player.name != 'human':
            return

        x, y = self._canvas_to_grid(event.x, event.y)
        if x is None or y is None:
            return
        if self.game.current_board.board_array[x][y] != 0:
            return

        # Execute human turn
        status = self.game.make_move(x, y)
        self.draw_board()

        if self._check_end_of_game(status, "You win!"):
            return

        # Advance to AI turn safely so the UI thread doesn't lock
        self.status_var.set("AI is thinking...")
        self.root.update_idletasks()
        self.root.after(50, self.play_ai_turn)

    def play_ai_turn(self):
        if self.game_over:
            return

        ai_player = self.game.current_player
        
        # Game class exposes the current player and board, let the AI calculate its move
        x, y = ai_player.policy(self.game.current_board)

        if x is None or y is None:
            self.game_over = True
            self.status_var.set("No valid AI move. Draw.")
            messagebox.showinfo("Game Over", "Draw")
            return

        # Execute AI turn
        status = self.game.make_move(x, y)
        self.draw_board()

        if self._check_end_of_game(status, "AI wins!"):
            return

        self.status_var.set("Your turn")

    def _check_end_of_game(self, status: str, win_text: str):
        if status == 'win':
            self.game_over = True
            self.status_var.set(win_text)
            messagebox.showinfo("Game Over", win_text)
            return True

        if status == 'draw':
            self.game_over = True
            self.status_var.set("Draw")
            messagebox.showinfo("Game Over", "Draw")
            return True

        return False


if __name__ == "__main__":
    root = tk.Tk()
    app = GomokuUI(root)
    root.mainloop()