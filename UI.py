import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import os
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

        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.show_main_menu()

    def clear_screen(self):
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

        load_btn = tk.Button(self.current_frame, text="Load Game", font=("Arial", 14), width=15, command=self.load_game_ui)
        load_btn.pack(pady=10)

        exit_btn = tk.Button(self.current_frame, text="Exit", font=("Arial", 14), width=15, command=self.root.destroy)
        exit_btn.pack(pady=10)

        self.root.update_idletasks()
        self.root.resizable(False, False)

    def _build_game_widgets(self):
        self.current_frame = tk.Frame(self.root, padx=10, pady=10)
        self.current_frame.pack()

        top_frame = tk.Frame(self.current_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
 
        status_label = tk.Label(top_frame, textvariable=self.status_var, font=("Arial", 14, "bold"))
        status_label.pack(side=tk.LEFT)

        menu_btn = tk.Button(top_frame, text="Main Menu", command=self.return_to_menu)
        menu_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_btn = tk.Button(top_frame, text="Save Game", command=self.save_game_ui)
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))

        restart_btn = tk.Button(top_frame, text="Restart", command=self.start_new_game)
        restart_btn.pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(self.current_frame, width=self.canvas_size, height=self.canvas_size, bg=BOARD_COLOUR, highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.handle_click)

    def start_new_game(self):
        self.clear_screen()
        self.game = game.Game(self.dimension, self.win_condition)
        self.game_over = False
        self.status_var.set("Your turn")
        self._build_game_widgets()
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        
        for i in range(self.dimension):
            start = MARGIN + i * CELL_SIZE
            end = MARGIN + (self.dimension - 1) * CELL_SIZE
            self.canvas.create_line(MARGIN, start, end, start, width=GRID_LINE_WIDTH, fill=GRID_COLOUR)
            self.canvas.create_line(start, MARGIN, start, end, width=GRID_LINE_WIDTH, fill=GRID_COLOUR)

        if self.game:
            for r in range(self.dimension):
                for c in range(self.dimension):
                    piece = self.game.current_board.board_array[r][c]
                    if piece != 0:
                        x = MARGIN + c * CELL_SIZE
                        y = MARGIN + r * CELL_SIZE
                        colour = HUMAN_COLOUR if piece == 1 else AI_COLOUR
                        self.canvas.create_oval(
                            x - CELL_SIZE/2 + STONE_PADDING, y - CELL_SIZE/2 + STONE_PADDING,
                            x + CELL_SIZE/2 - STONE_PADDING, y + CELL_SIZE/2 - STONE_PADDING,
                            fill=colour, outline="black"
                        )
            
            if self.game.last_move:
                r, c = self.game.last_move
                x = MARGIN + c * CELL_SIZE
                y = MARGIN + r * CELL_SIZE
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=LAST_MOVE_MARK_COLOUR, outline=LAST_MOVE_MARK_COLOUR)

    def handle_click(self, event):
        if self.game_over or self.game.current_player.name != 'human':
            return
            
        c = round((event.x - MARGIN) / CELL_SIZE)
        r = round((event.y - MARGIN) / CELL_SIZE)

        if 0 <= c < self.dimension and 0 <= r < self.dimension:
            if self.game.current_board.board_array[r][c] == 0:
                status = self.game.make_move(r, c)
                self.draw_board()
                
                if self._check_end_of_game(status, "You win!"):
                    return
                
                self.status_var.set("AI is thinking...")
                self.root.update()
                self.root.after(50, self.play_ai_turn)

    def play_ai_turn(self):
        ai_player = self.game.current_player
        x, y = ai_player.policy(self.game.current_board)

        if x is None or y is None:
            self._check_end_of_game('draw', "Draw")
            return

        status = self.game.make_move(x, y)
        self.draw_board()

        if self._check_end_of_game(status, "AI wins!"):
            return

        self.status_var.set("Your turn")

    def _check_end_of_game(self, status: str, win_text: str):
        if status == 'win' or status == 'draw':
            self.game_over = True
            display_text = win_text if status == 'win' else "The game is a draw!"
            self.status_var.set(display_text) 
            
            response = messagebox.askquestion("Game Over", f"{display_text}\n\nWould you like to play again?", icon='question')
            if response == 'yes':
                self.start_new_game()
            else:
                self.show_main_menu()
            return True
        return False

    def save_game_ui(self):
        if self.game:
            save_name = simpledialog.askstring("Save Game", "Enter a name for this save:\n(e.g., 'match_vs_ai_1')")
            
            if save_name:
                if not save_name.endswith(".json"):
                    save_name += ".json"
                    
                self.game.save_game(save_name)
                messagebox.showinfo("Saved", f"Your game has been successfully saved as:\n{save_name}")

    def load_game_ui(self):
        filename = filedialog.askopenfilename(
            title="Select a Saved Game",
            filetypes=(("JSON Save Files", "*.json"), ("All Files", "*.*"))
        )
        
        if not filename:
            return
            
        self.clear_screen()
        self.game = game.Game(self.dimension, self.win_condition)
        
        try:
            self.game.load_game(filename)
            self.game_over = False
            
            self._build_game_widgets()
            self.draw_board()

            if self.game.current_player.name == 'human':
                self.status_var.set("Your turn")
            else:
                self.status_var.set("AI is thinking...")
                self.root.update()
                self.root.after(50, self.play_ai_turn)
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load that save file!\n\nDetails: {e}")
            self.show_main_menu()

    def return_to_menu(self):
        if not self.game_over and self.game:
            response = messagebox.askyesnocancel("Quit Game", "Do you want to save the game before leaving?")
            
            if response is True:
                self.save_game_ui()
                self.show_main_menu()
            elif response is False:
                self.show_main_menu()
        else:
            self.show_main_menu()

    def on_window_close(self):
        if self.current_frame and not self.game_over and self.game:
            response = messagebox.askyesnocancel("Exit", "Do you want to save the game before exiting?")
            if response is True:
                self.save_game_ui()
                self.root.destroy()
            elif response is False:
                self.root.destroy()
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = GomokuUI(root)
    root.mainloop()