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
        


        self.dimension = BOARD_DIMENSION
        self.win_condition = WIN_CONDITION
        self.canvas_size = 2 * MARGIN + CELL_SIZE * (self.dimension - 1)

        self.game = None
        self.game_over = False
        self.status_var = tk.StringVar()
        

        self.current_frame = None 


        self.show_main_menu()

    def clear_screen(self):
        """Destroys the current frame and unlocks window resizing to make room for the next screen."""
        if self.current_frame is not None:
            self.current_frame.destroy()
        

        self.root.resizable(True, True)

    def show_main_menu(self):
        self.clear_screen()
        
        self.current_frame = tk.Frame(self.root, padx=50, pady=50)
        self.current_frame.pack(expand=True, fill="both")

        title = tk.Label(self.current_frame, text="Gomoku AI", font=("Arial", 24, "bold"))
        title.pack(pady=(0, 30))

 
        start_btn = tk.Button(self.current_frame, text="Start New Game", font=("Arial", 14), width=15, command=self.start_new_game)
        start_btn.pack(pady=10)


        exit_btn = tk.Button(self.current_frame, text="Exit", font=("Arial", 14), width=15, command=self.root.destroy)
        exit_btn.pack(pady=10)


        self.root.update_idletasks()
        self.root.resizable(False, False)


    def start_new_game(self):
        self.clear_screen()
        self.game = game.Game(self.dimension, self.win_condition)
        self.game_over = False
        self.status_var.set("Your turn") 
        
        self._build_game_widgets()
        self.draw_board()

    def _build_game_widgets(self):
        self.current_frame = tk.Frame(self.root, padx=10, pady=10)
        self.current_frame.pack()

        top_frame = tk.Frame(self.current_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))


        status_label = tk.Label(top_frame, textvariable=self.status_var, font=("Arial", 14))
        status_label.pack(side=tk.LEFT)


        menu_btn = tk.Button(top_frame, text="Main Menu", command=self.return_to_menu)
        menu_btn.pack(side=tk.RIGHT, padx=(10, 0))

        restart_btn = tk.Button(top_frame, text="Restart", command=self.start_new_game)
        restart_btn.pack(side=tk.RIGHT)


        self.canvas = tk.Canvas(
            self.current_frame, 
            width=self.canvas_size, 
            height=self.canvas_size, 
            bg=BOARD_COLOUR, 
            highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.root.update_idletasks()
        self.root.resizable(False, False)

    def draw_board(self):
        self.canvas.delete("all")
        

        for i in range(self.dimension):
            x = MARGIN + i * CELL_SIZE
            self.canvas.create_line(x, MARGIN, x, self.canvas_size - MARGIN, width=GRID_LINE_WIDTH, fill=GRID_COLOUR)
            y = MARGIN + i * CELL_SIZE
            self.canvas.create_line(MARGIN, y, self.canvas_size - MARGIN, y, width=GRID_LINE_WIDTH, fill=GRID_COLOUR)


        board_state = self.game.current_board.get_board_state()
        for r in range(self.dimension):
            for c in range(self.dimension):
                piece = board_state[r][c]
                if piece != 0:
                    self._draw_stone(r, c, HUMAN_COLOUR if piece == 1 else AI_COLOUR)


        if self.game.last_move:
            r, c = self.game.last_move
            self._draw_last_move_marker(r, c)

    def _draw_stone(self, row, col, colour):
        x = MARGIN + col * CELL_SIZE
        y = MARGIN + row * CELL_SIZE
        r = (CELL_SIZE // 2) - STONE_PADDING
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=colour, outline="black")

    def _draw_last_move_marker(self, row, col):
        x = MARGIN + col * CELL_SIZE
        y = MARGIN + row * CELL_SIZE
        mr = 3 
        self.canvas.create_oval(x - mr, y - mr, x + mr, y + mr, fill=LAST_MOVE_MARK_COLOUR, outline=LAST_MOVE_MARK_COLOUR)

    def on_canvas_click(self, event):
        if self.game_over or self.game.current_player.name != 'human':
            return

        col = round((event.x - MARGIN) / CELL_SIZE)
        row = round((event.y - MARGIN) / CELL_SIZE)

        if not (0 <= row < self.dimension and 0 <= col < self.dimension):
            return

        if self.game.current_board.get_board_state()[row][col] != 0:
            return

        status = self.game.make_move(row, col)
        self.draw_board()

        if self._check_end_of_game(status, "You win!"):
            return

        self.status_var.set("AI is thinking...") # SC4
        self.root.update_idletasks()
        self.root.after(50, self.play_ai_turn)

    def play_ai_turn(self):
        if self.game_over:
            return

        ai_player = self.game.current_player
        x, y = ai_player.policy(self.game.current_board)

        if x is None or y is None:
            self._check_end_of_game('draw', "Draw")
            return

        status = self.game.make_move(x, y)
        self.draw_board()

        if self._check_end_of_game(status, "AI wins!"):
            return

        self.status_var.set("Your turn") # SC4

    # ==========================================
    # GAME END & SAVING (SC5, SC6, SC7, SC8)
    # ==========================================
    def _check_end_of_game(self, status: str, win_text: str):
        if status == 'win' or status == 'draw':
            self.game_over = True
            display_text = win_text if status == 'win' else "The game is a draw!"
            self.status_var.set(display_text) # SC7: Display winner
            
            # SC8: Offer to restart or exit
            response = messagebox.askquestion("Game Over", f"{display_text}\n\nWould you like to play again?", icon='question')
            if response == 'yes':
                self.start_new_game()
            else:
                self.show_main_menu()
            return True
        return False

    def return_to_menu(self):
        """SC5 & SC6: Handle returning to menu and prompting for save."""
        if not self.game_over:
            # SC6: Prompt to save if the game is still active
            save_response = messagebox.askyesnocancel("Save Game?", "Do you want to save your progress before returning to the menu?")
            
            if save_response is None:
                # User clicked Cancel, stay in the game
                return
            elif save_response is True:
                # User clicked Yes, save the game
                self.save_game()
                
        # SC5: Return to menu
        self.show_main_menu()

    def save_game(self):
        """Placeholder for saving logic."""
        messagebox.showinfo("Saved", "Game state saved successfully! (Mock)")


if __name__ == "__main__":
    root = tk.Tk()
    app = GomokuUI(root)
    root.mainloop()