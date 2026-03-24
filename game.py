import board
import tt
import minimax
import json
import numpy as np
from typing import Tuple, Optional
class Player:
	def __init__(self, name: str, piece: int) -> None:
		self.name = name
		self.piece = piece
	def policy(self, current_board: board.Board) -> Tuple[Optional[int], Optional[int]]:
		if self.name == 'human':
			raise ValueError(f'The human input is handled by the ui')
		if self.name == 'ai':
			return minimax.best_move(current_board, self.piece)
		raise ValueError(f'Unknown player type: {self.name}')
	
class Game:
	def __init__(self, board_dimension: int, win_condition: int = 5) -> None:
		self.board_dimension = board_dimension
		self.current_board = board.Board(board_dimension)
		self.current_board.condition = win_condition
		self.player_1 = Player('human', 1)
		self.player_2 = Player('ai', 2)
		self.players = [self.player_1, self.player_2]

		self.turn_number = 0
		self.last_move = None
		tt.clear()
	
	@property
	def current_player(self) -> Player:
		return self.players[self.turn_number % 2]

	def make_move(self, x: int, y: int) -> str:
		player = self.current_player
		self.current_board.change_state(x, y, player.piece)
		self.last_move = (x, y)
		self.turn_number += 1
		return 'win' if self.current_board.check_win_from(x, y, player.piece) else 'draw' if self.current_board.check_draw() else 'continue'


	def save_game(self, filename: str = "savegame.json") -> None:
		state = {
			"board_dimension": self.board_dimension,
			"win_condition": self.current_board.condition,
			"turn_number": self.turn_number,
			"last_move": self.last_move,
			"board_array": self.current_board.board_array.tolist()
		}
		with open(filename, 'w') as f:
			json.dump(state, f)

	def load_game(self, filename: str = "savegame.json") -> None:
		with open(filename, 'r') as f:
			state = json.load(f)
			
		self.board_dimension = state["board_dimension"]
		self.current_board.condition = state["win_condition"]
		self.turn_number = state["turn_number"]
		self.last_move = tuple(state["last_move"]) if state["last_move"] else None
		
		self.current_board.board_array = np.array(state["board_array"], dtype=np.int8)
		self.current_board.empty_count = int(np.count_nonzero(self.current_board.board_array == 0))
		
		self.current_board.current_hash = 0
		for r in range(self.board_dimension):
			for c in range(self.board_dimension):
				piece = self.current_board.board_array[r][c]
				if piece != 0:
					self.current_board.current_hash ^= tt.ZOBRIST_TABLE[(r, c, piece)]
		tt.clear()